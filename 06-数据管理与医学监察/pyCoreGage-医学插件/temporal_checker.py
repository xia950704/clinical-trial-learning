"""
pyCoreGage — Temporal Sequence Checker (temporal_checker.py)
=============================================================
时间序列一致性检查模块 —— 面向临床试验数据医学监察。

与 pyCoreGage CoreGageState 兼容，通过 collect_findings() 收集并返回结构化发现。

检查项:
    1. 访视顺序检查   (VISIT_ORDER)  : 筛查 → 基线 → 给药 → 随访
    2. 时间锚定检查   (TIME_ANCHOR)  : AE 时间应在给药时间之后
    3. 时间窗检查     (TIME_WINDOW)  : 给药前 24h 内不应存在合并用药
    4. 缺失时间检查   (MISSING_TIME) : 访视缺失 / 关键字段时间缺失

典型用法:
    from temporal_checker import TemporalChecker, TemporalCheckConfig

    # 方式一: 直接传入 dict 风格数据
    checker = TemporalChecker(subject_data, config, subject_id="001-001")
    findings = checker.collect_findings()

    # 方式二: 传入 CoreGageState 实例
    checker = TemporalChecker(state, config)
    findings = checker.collect_findings()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger("pyCoreGage.temporal")

# ---------------------------------------------------------------------------
# 常量 / 枚举
# ---------------------------------------------------------------------------

VISIT_ORDER = (
    "SCREENING",   # 筛查
    "BASELINE",    # 基线
    "DOSING",      # 给药
    "FOLLOWUP",    # 随访
)

SEVERITY_LABELS = {
    "CRITICAL": "严重",
    "MAJOR":    "主要",
    "MINOR":    "次要",
    "INFO":     "信息",
}


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    MAJOR    = "MAJOR"
    MINOR    = "MINOR"
    INFO     = "INFO"


# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

@dataclass
class TemporalCheckConfig:
    """时间序列检查配置。"""
    # 时间窗: 给药前允许合并用药的时间阈值 (小时)，默认 24h
    concomitant_window_hours: float = 24.0
    # 是否允许 AE 时间早于给药时间 (部分方案允许，默认 False)
    allow_ae_before_dosing: bool = False
    # 必须存在的访视阶段 (默认全部)
    required_visits: Tuple[str, ...] = VISIT_ORDER
    # 缺失时间容忍天数 (超过该天数判定为缺失)
    missing_tolerance_days: int = 30
    # 时间字段名映射 (支持不同数据集命名风格)
    field_visit_date: str = "VISITDT"
    field_visit_name: str = "VISIT"
    field_ae_start: str = "AESTDTC"
    field_ae_end: str = "AEENDTC"
    field_dosing_date: str = "EXSTDTC"
    field_concom_start: str = "COSTDTC"
    field_concom_end: str = "COENDTC"
    # 数据集键名
    ds_visits: str = "VIS"
    ds_ae: str = "AE"
    ds_exposure: str = "EX"
    ds_concom: str = "CM"


# ---------------------------------------------------------------------------
# 时间解析辅助
# ---------------------------------------------------------------------------

def _parse_datetime(value: Any) -> Optional[datetime]:
    """解析常见日期/日期时间字符串为 datetime。"""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value))
        except (OSError, ValueError):
            pass
    s = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d",
                "%m/%d/%Y", "%d-%b-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# 数据结构 (独立 Finding，与 CoreGageFinding 兼容)
# ---------------------------------------------------------------------------

@dataclass
class TemporalFinding:
    """单条时间序列检查发现。"""
    check_id: str
    severity: Severity
    category: str
    message: str
    subject_id: str
    record: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id":   self.check_id,
            "severity":   self.severity.value,
            "category":   self.category,
            "message":    self.message,
            "subject_id": self.subject_id,
            "record":     self.record,
            "details":    self.details,
        }


# ---------------------------------------------------------------------------
# 主检查器
# ---------------------------------------------------------------------------

class TemporalChecker:
    """
    时间序列一致性检查器。

    兼容 pyCoreGage CoreGageState 接口：
        - __init__(state) 接受 CoreGageState 或 dict 风格的 subject_data
        - collect_findings() -> List[Dict] 返回结构化发现列表
    """

    def __init__(
        self,
        subject_data: Dict[str, Any],
        config: Optional[TemporalCheckConfig] = None,
        subject_id: Optional[str] = None,
    ):
        """
        参数
        ----
        subject_data : dict 或 CoreGageState
            受试者数据，键为数据集名 (VIS/AE/EX/CM)，值为记录列表。
            也接受 CoreGageState 实例（通过 .datasets 属性访问）。
        config : TemporalCheckConfig, optional
            检查配置，默认使用 TemporalCheckConfig()。
        subject_id : str, optional
            受试者 ID，用于标记发现。
        """
        self.config = config or TemporalCheckConfig()
        self._findings: List[TemporalFinding] = []

        # 兼容 CoreGageState: 若传入对象有 .datasets 属性则取之
        if hasattr(subject_data, "datasets"):
            self._data = subject_data.datasets
        elif hasattr(subject_data, "data"):
            self._data = subject_data.data
        else:
            self._data = subject_data

        # 解析 subject_id
        if subject_id:
            self._subject_id = subject_id
        else:
            self._subject_id = (
                self._data.get("SUBJID")
                or self._data.get("USUBJID")
                or getattr(subject_data, "subject_id", "UNKNOWN")
            )

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def collect_findings(self) -> List[Dict[str, Any]]:
        """
        执行全部时间序列检查并返回发现列表。

        兼容 CoreGageState 的 collect_findings() 协议。
        """
        self._findings.clear()
        logger.debug("TemporalChecker: 开始检查受试者 %s", self._subject_id)

        self._check_visit_order()
        self._check_time_anchor()
        self._check_time_window()
        self._check_missing_time()

        results = [f.to_dict() for f in self._findings]
        logger.info(
            "TemporalChecker: 受试者 %s 共发现 %d 条问题",
            self._subject_id, len(results),
        )
        return results

    # ------------------------------------------------------------------
    # 1) 访视顺序检查
    # ------------------------------------------------------------------

    def _check_visit_order(self) -> None:
        """
        检查访视是否按照 筛查 → 基线 → 给药 → 随访 顺序发生。
        """
        visits = self._data.get(self.config.ds_visits) or []
        if not visits:
            self._add_finding(
                check_id="VISIT_ORDER",
                severity=Severity.CRITICAL,
                category="访视顺序",
                message="缺少访视记录 (VIS)，无法进行访视顺序检查。",
            )
            return

        # 构建 (日期, 访视名, 记录) 列表
        parsed: List[Tuple[Optional[datetime], str, Dict]] = []
        for rec in visits:
            dt = _parse_datetime(rec.get(self.config.field_visit_date))
            name = str(rec.get(self.config.field_visit_name, "")).upper().strip()
            parsed.append((dt, name, rec))

        # 检查每个必须访视是否存在
        present = {name for _, name, _ in parsed if name}
        for req in self.config.required_visits:
            if req not in present:
                self._add_finding(
                    check_id="VISIT_ORDER",
                    severity=Severity.CRITICAL,
                    category="访视顺序",
                    message=f"缺少必须访视: {req}。",
                    details={"required_visit": req},
                )

        # 按日期排序后检查顺序
        ordered = sorted(
            [(dt, name, rec) for dt, name, rec in parsed if dt is not None],
            key=lambda x: x[0],
        )
        if len(ordered) < 2:
            return

        # 期望顺序映射
        order_map = {v: i for i, v in enumerate(VISIT_ORDER)}

        prev_dt, prev_name, _ = ordered[0]
        prev_idx = order_map.get(prev_name, -1)

        for dt, name, rec in ordered[1:]:
            curr_idx = order_map.get(name, -1)
            # 日期倒序 (后发生的访视时间早于前面的)
            if dt < prev_dt:
                self._add_finding(
                    check_id="VISIT_ORDER",
                    severity=Severity.MAJOR,
                    category="访视顺序",
                    message=(
                        f"访视时间倒序: '{name}' ({dt:%Y-%m-%d %H:%M}) "
                        f"早于前一访视 '{prev_name}' ({prev_dt:%Y-%m-%d %H:%M})。"
                    ),
                    record=rec,
                    details={"prev_visit": prev_name, "prev_date": str(prev_dt)},
                )
            # 逻辑顺序异常 (如随访出现在给药之前)
            if prev_idx >= 0 and curr_idx >= 0 and curr_idx < prev_idx:
                self._add_finding(
                    check_id="VISIT_ORDER",
                    severity=Severity.MAJOR,
                    category="访视顺序",
                    message=(
                        f"访视逻辑顺序异常: '{name}' (期望顺序 #{curr_idx}) "
                        f"出现在 '{prev_name}' (期望顺序 #{prev_idx}) 之后。"
                    ),
                    record=rec,
                    details={"prev_visit": prev_name, "prev_idx": prev_idx,
                             "curr_idx": curr_idx},
                )
            prev_dt, prev_name = dt, name
            prev_idx = curr_idx

    # ------------------------------------------------------------------
    # 2) 时间锚定检查 (AE 时间应在给药时间之后)
    # ------------------------------------------------------------------

    def _check_time_anchor(self) -> None:
        """
        检查不良事件 (AE) 的起始时间是否在给药时间之后。
        """
        ae_records = self._data.get(self.config.ds_ae) or []
        dosing_records = self._data.get(self.config.ds_exposure) or []

        if not ae_records:
            return
        if not dosing_records:
            self._add_finding(
                check_id="TIME_ANCHOR",
                severity=Severity.MINOR,
                category="时间锚定",
                message="缺少给药记录 (EX)，无法执行 AE 时间锚定检查。",
            )
            return

        # 获取首次给药时间
        dosing_times: List[datetime] = []
        for rec in dosing_records:
            dt = _parse_datetime(rec.get(self.config.field_dosing_date))
            if dt:
                dosing_times.append(dt)
        if not dosing_times:
            self._add_finding(
                check_id="TIME_ANCHOR",
                severity=Severity.MINOR,
                category="时间锚定",
                message="给药记录中无有效时间，无法执行 AE 时间锚定检查。",
            )
            return

        first_dose = min(dosing_times)

        for rec in ae_records:
            ae_start = _parse_datetime(rec.get(self.config.field_ae_start))
            if ae_start is None:
                self._add_finding(
                    check_id="TIME_ANCHOR",
                    severity=Severity.MINOR,
                    category="时间锚定",
                    message=(
                        f"AE 记录缺少有效起始时间 "
                        f"({self.config.field_ae_start}={rec.get(self.config.field_ae_start)})。"
                    ),
                    record=rec,
                )
                continue

            if ae_start < first_dose and not self.config.allow_ae_before_dosing:
                delta = first_dose - ae_start
                self._add_finding(
                    check_id="TIME_ANCHOR",
                    severity=Severity.MAJOR,
                    category="时间锚定",
                    message=(
                        f"AE 起始时间 ({ae_start:%Y-%m-%d %H:%M}) "
                        f"早于首次给药时间 ({first_dose:%Y-%m-%d %H:%M}) "
                        f"，相差 {delta.total_seconds()/3600:.1f} 小时。"
                    ),
                    record=rec,
                    details={"ae_start": str(ae_start),
                             "first_dose": str(first_dose),
                             "delta_hours": round(delta.total_seconds() / 3600, 1)},
                )

    # ------------------------------------------------------------------
    # 3) 时间窗检查 (给药前 24h 内无合并用药)
    # ------------------------------------------------------------------

    def _check_time_window(self) -> None:
        """
        检查给药前 24h 时间窗内是否存在合并用药 (CM)。
        """
        dosing_records = self._data.get(self.config.ds_exposure) or []
        concom_records = self._data.get(self.config.ds_concom) or []

        if not dosing_records:
            return
        if not concom_records:
            return

        window = timedelta(hours=self.config.concomitant_window_hours)

        for d_rec in dosing_records:
            dose_dt = _parse_datetime(d_rec.get(self.config.field_dosing_date))
            if dose_dt is None:
                continue

            window_start = dose_dt - window

            for c_rec in concom_records:
                c_start = _parse_datetime(c_rec.get(self.config.field_concom_start))
                c_end = _parse_datetime(c_rec.get(self.config.field_concom_end))

                # 合并用药时间窗与给药时间窗重叠判定
                # 若合并用药结束时间 >= 窗口起始 且 合并用药开始时间 <= 给药时间
                active_start = c_start if c_start else window_start
                active_end = c_end if c_end else (c_start if c_start else window_start)

                if active_start <= dose_dt and active_end >= window_start:
                    drug_name = c_rec.get("COSTERM", c_rec.get("CMNAME", "未知药物"))
                    self._add_finding(
                        check_id="TIME_WINDOW",
                        severity=Severity.MAJOR,
                        category="时间窗",
                        message=(
                            f"给药前 {self.config.concomitant_window_hours}h 时间窗内 "
                            f"存在合并用药 '{drug_name}' "
                            f"({active_start:%Y-%m-%d %H:%M} ~ {active_end:%Y-%m-%d %H:%M})。"
                        ),
                        record=c_rec,
                        details={
                            "dose_time": str(dose_dt),
                            "window_start": str(window_start),
                            "concom_start": str(c_start),
                            "concom_end": str(c_end),
                            "drug_name": drug_name,
                        },
                    )

    # ------------------------------------------------------------------
    # 4) 缺失时间检查
    # ------------------------------------------------------------------

    def _check_missing_time(self) -> None:
        """
        检查访视缺失和关键字段时间字段缺失。
        """
        self._check_visit_missing()
        self._check_data_missing()

    def _check_visit_missing(self) -> None:
        """检查必须访视是否缺失。"""
        visits = self._data.get(self.config.ds_visits) or []
        present = {
            str(r.get(self.config.field_visit_name, "")).upper().strip()
            for r in visits
        }
        for req in self.config.required_visits:
            if req not in present:
                self._add_finding(
                    check_id="MISSING_TIME",
                    severity=Severity.CRITICAL,
                    category="缺失时间",
                    message=f"必须访视 '{req}' 缺失。",
                    details={"required_visit": req},
                )

    def _check_data_missing(self) -> None:
        """检查关键数据集的关键时间字段缺失情况。"""
        checks: List[Tuple[str, str, Severity]] = [
            (self.config.ds_visits, self.config.field_visit_date, Severity.CRITICAL),
            (self.config.ds_ae, self.config.field_ae_start, Severity.MAJOR),
            (self.config.ds_exposure, self.config.field_dosing_date, Severity.CRITICAL),
            (self.config.ds_concom, self.config.field_concom_start, Severity.MINOR),
        ]

        for ds_key, field_name, severity in checks:
            records = self._data.get(ds_key) or []
            if not records:
                continue
            missing_count = 0
            for rec in records:
                val = rec.get(field_name)
                if val is None or (isinstance(val, str) and val.strip() == ""):
                    missing_count += 1
                elif _parse_datetime(val) is None:
                    missing_count += 1

            total = len(records)
            if missing_count > 0:
                pct = missing_count / total * 100
                self._add_finding(
                    check_id="MISSING_TIME",
                    severity=severity,
                    category="缺失时间",
                    message=(
                        f"数据集 '{ds_key}' 字段 '{field_name}' 缺失/无效: "
                        f"{missing_count}/{total} ({pct:.1f}%)。"
                    ),
                    details={"dataset": ds_key, "field": field_name,
                             "missing_count": missing_count, "total": total},
                )

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------

    def _add_finding(
        self,
        check_id: str,
        severity: Severity,
        category: str,
        message: str,
        record: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._findings.append(TemporalFinding(
            check_id=check_id,
            severity=severity,
            category=category,
            message=message,
            subject_id=self._subject_id,
            record=record or {},
            details=details or {},
        ))

    # ------------------------------------------------------------------
    # 统计摘要
    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """返回检查摘要统计。"""
        counts: Dict[str, int] = {}
        severity_counts: Dict[str, int] = {}
        for f in self._findings:
            counts[f.check_id] = counts.get(f.check_id, 0) + 1
            severity_counts[f.severity.value] = severity_counts.get(f.severity.value, 0) + 1
        return {
            "subject_id": self._subject_id,
            "total_findings": len(self._findings),
            "by_check": counts,
            "by_severity": severity_counts,
        }


# ---------------------------------------------------------------------------
# CoreGageState 适配器
# ---------------------------------------------------------------------------

class CoreGageTemporalChecker:
    """
    面向 pyCoreGage CoreGageState 的适配器。

    用法:
        from pycoregage import CoreGageState
        state = CoreGageState(subject_data)
        checker = CoreGageTemporalChecker(state)
        findings = checker.collect_findings()
    """

    def __init__(self, state: Any, config: Optional[TemporalCheckConfig] = None):
        self.state = state
        self._checker: Optional[TemporalChecker] = None
        self._config = config

    def collect_findings(self) -> List[Dict[str, Any]]:
        """
        委托给 TemporalChecker，兼容 CoreGageState.collect_findings() 协议。
        """
        subject_data = (
            self.state.datasets if hasattr(self.state, "datasets")
            else self.state.data if hasattr(self.state, "data")
            else self.state
        )
        subject_id = (
            getattr(self.state, "subject_id", None)
            or subject_data.get("SUBJID")
            or subject_data.get("USUBJID")
        )
        self._checker = TemporalChecker(subject_data, self._config, subject_id)
        return self._checker.collect_findings()

    def summary(self) -> Dict[str, Any]:
        if self._checker:
            return self._checker.summary()
        return {"error": "尚未执行 collect_findings()"}


# ---------------------------------------------------------------------------
# CLI 演示
# ---------------------------------------------------------------------------

def _demo():
    """使用模拟数据演示全部检查。"""
    sample = {
        "SUBJID": "001-001",
        "VIS": [
            {"VISIT": "SCREENING", "VISITDT": "2025-01-10 09:00:00"},
            {"VISIT": "BASELINE",  "VISITDT": "2025-01-15 10:00:00"},
            {"VISIT": "DOSING",    "VISITDT": "2025-01-20 11:00:00"},
            {"VISIT": "FOLLOWUP",  "VISITDT": "2025-02-01 09:00:00"},
        ],
        "AE": [
            {"AESTDTC": "2025-01-18 08:00:00", "AETERM": "头痛"},   # 早于给药
            {"AESTDTC": "2025-01-25 14:00:00", "AETERM": "恶心"},   # 正常
            {"AESTDTC": "",               "AETERM": "皮疹"},        # 缺失时间
        ],
        "EX": [
            {"EXSTDTC": "2025-01-20 11:00:00", "EXDOSE": 100},
        ],
        "CM": [
            {"COSTDTC": "2025-01-19 12:00:00", "COENDTC": "2025-01-21 12:00:00",
             "COSTERM": "阿司匹林"},           # 给药前 24h 内
            {"COSTDTC": "2025-01-10 08:00:00", "COENDTC": "2025-01-14 08:00:00",
             "COSTERM": "维生素C"},            # 在窗口外，应通过
        ],
    }

    checker = TemporalChecker(sample)
    findings = checker.collect_findings()

    print(f"\n{'='*60}")
    print(f"时间序列检查结果 — 受试者 {checker._subject_id}")
    print(f"{'='*60}")
    for f in findings:
        print(f"[{f['severity']:8s}] [{f['check_id']:12s}] {f['message']}")
    print(f"\n摘要: {checker.summary()}")


if __name__ == "__main__":
    _demo()
