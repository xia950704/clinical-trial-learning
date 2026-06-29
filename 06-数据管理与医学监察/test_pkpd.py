"""
test_pkpd.py — PK/PD 分析检查功能测试脚本
============================================
测试 pkpd_checker.py 的 PK/PD 数据检查功能：
  1. AUC 计算（梯形法则）
  2. Cmax 识别
  3. Tmax 识别
  4. 半衰期计算（简化：线性回归）
  5. 剂量-浓度关系检查
  6. 采样时间序列完整性

使用合成数据模拟临床试验 PK 浓度-时间曲线。
"""

from __future__ import annotations

import csv
import json
import logging
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core_data import (
    CoreGageConfig,
    CoreGageState,
    CoreGageFinding,
    DataSource,
    Severity,
    CheckCategory,
    CheckStatus,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("test_pkpd")


# ═══════════════════════════════════════════════════════════
# 1. 辅助函数：PK 参数计算
# ═══════════════════════════════════════════════════════════


def compute_auc_trapezoidal(
    times: List[float], concentrations: List[float]
) -> float:
    """
    使用梯形法则计算 AUC（药时曲线下面积）。

    Args:
        times: 采样时间点列表
        concentrations: 对应浓度列表

    Returns:
        AUC 值（ng·h/mL）
    """
    if len(times) < 2:
        return 0.0

    auc = 0.0
    for i in range(1, len(times)):
        dt = times[i] - times[i - 1]
        avg_conc = (concentrations[i] + concentrations[i - 1]) / 2.0
        auc += dt * avg_conc

    return auc


def find_cmax_tmax(
    times: List[float], concentrations: List[float]
) -> Tuple[float, float]:
    """
    识别 Cmax（最大血药浓度）和 Tmax（达峰时间）。

    Args:
        times: 采样时间点列表
        concentrations: 对应浓度列表

    Returns:
        (Cmax, Tmax) 元组
    """
    if not concentrations:
        return 0.0, 0.0

    max_idx = 0
    for i in range(1, len(concentrations)):
        if concentrations[i] > concentrations[max_idx]:
            max_idx = i

    return concentrations[max_idx], times[max_idx]


def compute_half_life_linear_regression(
    times: List[float], concentrations: List[float], cmax: float
) -> Optional[float]:
    """
    使用线性回归计算消除半衰期（简化方法）。

    在消除相（浓度下降阶段），ln(C) vs t 呈线性关系：
    ln(C) = ln(C0) - k*t
    半衰期 t1/2 = ln(2) / k

    Args:
        times: 采样时间点列表
        concentrations: 对应浓度列表
        cmax: 最大血药浓度

    Returns:
        半衰期（小时），如果无法计算则返回 None
    """
    if len(times) < 3:
        return None

    # 找到 Cmax 之后的点（消除相）
    max_idx = 0
    for i in range(1, len(concentrations)):
        if concentrations[i] > concentrations[max_idx]:
            max_idx = i

    # 取 Cmax 之后浓度 > Cmax * 0.01 的点
    post_peak = []
    for i in range(max_idx, len(times)):
        if concentrations[i] > cmax * 0.01 and concentrations[i] > 0:
            post_peak.append((times[i], concentrations[i]))

    if len(post_peak) < 3:
        return None

    # 线性回归：ln(C) = a + b*t
    n = len(post_peak)
    sum_x = sum(p[0] for p in post_peak)
    sum_y = sum(math.log(p[1]) for p in post_peak)
    sum_xy = sum(p[0] * math.log(p[1]) for p in post_peak)
    sum_x2 = sum(p[0] ** 2 for p in post_peak)

    denom = n * sum_x2 - sum_x * sum_x
    if abs(denom) < 1e-10:
        return None

    slope = (n * sum_xy - sum_x * sum_y) / denom

    if slope >= 0:
        return None  # 斜率非负，无法计算半衰期

    # t1/2 = ln(2) / |slope|
    k = abs(slope)
    return math.log(2) / k


def compute_r_squared(
    times: List[float], concentrations: List[float], cmax: float
) -> Optional[float]:
    """
    计算消除相线性回归的 R² 值。

    Args:
        times: 采样时间点列表
        concentrations: 对应浓度列表
        cmax: 最大血药浓度

    Returns:
        R² 值，如果无法计算则返回 None
    """
    if len(times) < 3:
        return None

    max_idx = 0
    for i in range(1, len(concentrations)):
        if concentrations[i] > concentrations[max_idx]:
            max_idx = i

    post_peak = []
    for i in range(max_idx, len(times)):
        if concentrations[i] > cmax * 0.01 and concentrations[i] > 0:
            post_peak.append((times[i], concentrations[i]))

    if len(post_peak) < 3:
        return None

    n = len(post_peak)
    sum_x = sum(p[0] for p in post_peak)
    sum_y = sum(math.log(p[1]) for p in post_peak)
    sum_xy = sum(p[0] * math.log(p[1]) for p in post_peak)
    sum_x2 = sum(p[0] ** 2 for p in post_peak)
    sum_y2 = sum(math.log(p[1]) ** 2 for p in post_peak)

    denom = n * sum_x2 - sum_x * sum_x
    if abs(denom) < 1e-10:
        return None

    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n

    ss_tot = sum_y2 - sum_y * sum_y / n
    ss_res = sum_y2 - intercept * sum_y - slope * sum_xy

    if ss_tot < 1e-10:
        return None

    r_squared = 1.0 - ss_res / ss_tot
    return max(0.0, min(1.0, r_squared))


# ═══════════════════════════════════════════════════════════
# 2. 数据加载
# ═══════════════════════════════════════════════════════════


def load_pk_data(csv_path: str) -> List[Dict[str, Any]]:
    """
    从 CSV 文件加载 PK 数据。

    Args:
        csv_path: CSV 文件路径

    Returns:
        数据记录列表
    """
    records: List[Dict[str, Any]] = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = {
                "subject_id": row["subject_id"],
                "sample_time": float(row["sample_time"]),
                "concentration": float(row["concentration"]),
                "dose": float(row["dose"]),
                "dose_time": float(row["dose_time"]),
                "visit": row["visit"],
            }
            records.append(record)
    return records


def load_pkpd_rules(yaml_path: str) -> Dict[str, Any]:
    """
    加载 PK/PD 规则配置（简化 YAML 解析）。

    Args:
        yaml_path: YAML 文件路径

    Returns:
        规则字典
    """
    rules: Dict[str, Any] = {}
    with open(yaml_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_section: Optional[str] = None
    current_subsection: Optional[str] = None
    current_item: Optional[str] = None

    for line in lines:
        stripped = line.rstrip()
        if not stripped or stripped.startswith("#"):
            continue

        # 计算缩进级别
        indent = len(line) - len(line.lstrip())

        if indent == 0:
            # 顶级键
            key = stripped.split(":")[0].strip()
            current_section = key
            current_subsection = None
            current_item = None
            if key not in rules:
                rules[key] = {}
        elif indent == 2:
            # 二级键（可能是节标题或键值对）
            key = stripped.split(":")[0].strip()
            val_part = stripped.split(":", 1)[1].strip() if ":" in stripped else ""
            current_subsection = key
            current_item = None
            if current_section and current_section not in rules:
                rules[current_section] = {}
            if val_part:
                # 内联值：如 "hy_window_days: 28"
                try:
                    val_part = int(val_part)
                except ValueError:
                    try:
                        val_part = float(val_part)
                    except ValueError:
                        val_part = val_part.strip('"').strip("'")
                if current_section:
                    rules[current_section][key] = val_part
            else:
                # 节标题：如 "hys_law:"
                if current_section and current_subsection:
                    if current_subsection not in rules[current_section]:
                        rules[current_section][current_subsection] = {}
        elif indent == 4:
            # 三级键或值
            if ":" in stripped:
                key = stripped.split(":")[0].strip()
                val = stripped.split(":", 1)[1].strip()
                if val:
                    # 尝试转换数字
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            val = val.strip('"').strip("'")
                else:
                    val = {}
                current_item = key
                if current_section and current_subsection:
                    if current_subsection not in rules.get(current_section, {}):
                        rules[current_section][current_subsection] = {}
                    rules[current_section][current_subsection][key] = val
            else:
                # 列表项
                val = stripped.lstrip("- ").strip().strip('"').strip("'")
                if current_section and current_subsection and current_item:
                    if not isinstance(rules.get(current_section, {}).get(current_subsection, {}).get(current_item), list):
                        rules[current_section][current_subsection][current_item] = []
                    rules[current_section][current_subsection][current_item].append(val)
        elif indent == 6:
            # 四级键或值
            if ":" in stripped:
                key = stripped.split(":")[0].strip()
                val = stripped.split(":", 1)[1].strip()
                if val:
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            val = val.strip('"').strip("'")
                if current_section and current_subsection and current_item:
                    if not isinstance(rules.get(current_section, {}).get(current_subsection, {}).get(current_item), dict):
                        rules[current_section][current_subsection][current_item] = {}
                    rules[current_section][current_subsection][current_item][key] = val

    return rules


# ═══════════════════════════════════════════════════════════
# 3. 计算 PK 参数（从原始浓度-时间数据）
# ═══════════════════════════════════════════════════════════


def compute_pk_parameters(
    raw_data: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    从原始 PK 数据计算 PK 参数。

    按受试者-访视分组，计算 AUC、Cmax、Tmax、半衰期等。

    Args:
        raw_data: 原始 PK 数据列表

    Returns:
        计算后的 PK 参数记录列表
    """
    # 按受试者-访视分组
    groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for record in raw_data:
        key = (record["subject_id"], record["visit"])
        if key not in groups:
            groups[key] = []
        groups[key].append(record)

    pk_params: List[Dict[str, Any]] = []

    for (subj_id, visit), records in groups.items():
        # 按时间排序
        records.sort(key=lambda x: x["sample_time"])

        times = [r["sample_time"] for r in records]
        concentrations = [r["concentration"] for r in records]
        dose = records[0]["dose"]

        # 计算 AUC（梯形法则）
        auc = compute_auc_trapezoidal(times, concentrations)

        # 计算 Cmax 和 Tmax
        cmax, tmax = find_cmax_tmax(times, concentrations)

        # 计算半衰期
        t_half = compute_half_life_linear_regression(times, concentrations, cmax)

        # 计算 R²
        r_squared = compute_r_squared(times, concentrations, cmax)

        param_record = {
            "SUBJID": subj_id,
            "VISIT": visit,
            "AUC": round(auc, 2),
            "Cmax": round(cmax, 2),
            "Tmax": round(tmax, 2),
            "t_half": round(t_half, 2) if t_half is not None else None,
            "dose": dose,
            "n_samples": len(records),
            "r_squared": round(r_squared, 4) if r_squared is not None else None,
            "times": times,
            "concentrations": concentrations,
        }
        pk_params.append(param_record)

    return pk_params


# ═══════════════════════════════════════════════════════════
# 4. 自定义 PK/PD 检查（扩展现有检查器）
# ═══════════════════════════════════════════════════════════


def check_auc_calculation(
    pk_params: List[Dict[str, Any]], rules: Dict[str, Any]
) -> List[CoreGageFinding]:
    """
    检查 AUC 计算结果的合理性。

    Args:
        pk_params: PK 参数列表
        rules: 规则配置

    Returns:
        发现列表
    """
    findings: List[CoreGageFinding] = []
    auc_range = rules.get("pk_parameters", {}).get("AUC", {"min": 0.1, "max": 10000})

    for param in pk_params:
        auc = param.get("AUC")
        if auc is not None:
            if auc < auc_range["min"] or auc > auc_range["max"]:
                findings.append(CoreGageFinding(
                    category=CheckCategory.CONSISTENCY,
                    severity=Severity.MEDIUM,
                    source="pkpd_auc",
                    subject_id=param["SUBJID"],
                    visit_id=param["VISIT"],
                    message=f"AUC 超出正常范围: {auc} ng·h/mL "
                            f"(正常: {auc_range['min']}-{auc_range['max']})",
                    details={
                        "check_id": "PK_AUC_RANGE",
                        "auc": auc,
                        "min": auc_range["min"],
                        "max": auc_range["max"],
                    },
                    status=CheckStatus.PASSED,
                ))

    return findings


def check_cmax_tmax(
    pk_params: List[Dict[str, Any]], rules: Dict[str, Any]
) -> List[CoreGageFinding]:
    """
    检查 Cmax 和 Tmax 的合理性。

    Args:
        pk_params: PK 参数列表
        rules: 规则配置

    Returns:
        发现列表
    """
    findings: List[CoreGageFinding] = []
    cmax_range = rules.get("pk_parameters", {}).get("Cmax", {"min": 0.1, "max": 10000})
    tmax_range = rules.get("pk_parameters", {}).get("Tmax", {"min": 0, "max": 24})

    for param in pk_params:
        cmax = param.get("Cmax")
        tmax = param.get("Tmax")

        if cmax is not None:
            if cmax < cmax_range["min"] or cmax > cmax_range["max"]:
                findings.append(CoreGageFinding(
                    category=CheckCategory.CONSISTENCY,
                    severity=Severity.MEDIUM,
                    source="pkpd_cmax",
                    subject_id=param["SUBJID"],
                    visit_id=param["VISIT"],
                    message=f"Cmax 超出正常范围: {cmax} ng/mL "
                            f"(正常: {cmax_range['min']}-{cmax_range['max']})",
                    details={
                        "check_id": "PK_CMAX_RANGE",
                        "cmax": cmax,
                        "min": cmax_range["min"],
                        "max": cmax_range["max"],
                    },
                    status=CheckStatus.PASSED,
                ))

        if tmax is not None:
            if tmax < tmax_range["min"] or tmax > tmax_range["max"]:
                findings.append(CoreGageFinding(
                    category=CheckCategory.CONSISTENCY,
                    severity=Severity.LOW,
                    source="pkpd_tmax",
                    subject_id=param["SUBJID"],
                    visit_id=param["VISIT"],
                    message=f"Tmax 超出正常范围: {tmax} h "
                            f"(正常: {tmax_range['min']}-{tmax_range['max']})",
                    details={
                        "check_id": "PK_TMAX_RANGE",
                        "tmax": tmax,
                        "min": tmax_range["min"],
                        "max": tmax_range["max"],
                    },
                    status=CheckStatus.PASSED,
                ))

    return findings


def check_half_life(
    pk_params: List[Dict[str, Any]], rules: Dict[str, Any]
) -> List[CoreGageFinding]:
    """
    检查半衰期计算的合理性。

    Args:
        pk_params: PK 参数列表
        rules: 规则配置

    Returns:
        发现列表
    """
    findings: List[CoreGageFinding] = []
    t_half_range = rules.get("pk_parameters", {}).get("t_half", {"min": 0.1, "max": 100})
    hl_rules = rules.get("half_life_rules", {})
    min_r2 = hl_rules.get("min_regression_r_squared", 0.6)

    for param in pk_params:
        t_half = param.get("t_half")
        r_squared = param.get("r_squared")

        if t_half is not None:
            if t_half < t_half_range["min"] or t_half > t_half_range["max"]:
                findings.append(CoreGageFinding(
                    category=CheckCategory.CONSISTENCY,
                    severity=Severity.LOW,
                    source="pkpd_half_life",
                    subject_id=param["SUBJID"],
                    visit_id=param["VISIT"],
                    message=f"半衰期超出正常范围: {t_half} h "
                            f"(正常: {t_half_range['min']}-{t_half_range['max']})",
                    details={
                        "check_id": "PK_THALF_RANGE",
                        "t_half": t_half,
                        "min": t_half_range["min"],
                        "max": t_half_range["max"],
                    },
                    status=CheckStatus.PASSED,
                ))

        if r_squared is not None and r_squared < min_r2:
            findings.append(CoreGageFinding(
                category=CheckCategory.CONSISTENCY,
                severity=Severity.LOW,
                source="pkpd_half_life",
                subject_id=param["SUBJID"],
                visit_id=param["VISIT"],
                message=f"半衰期线性回归 R² 过低: {r_squared} "
                        f"(要求 ≥ {min_r2})，半衰期计算可能不可靠",
                details={
                    "check_id": "PK_THALF_R2_LOW",
                    "r_squared": r_squared,
                    "min_r_squared": min_r2,
                },
                status=CheckStatus.PASSED,
            ))

    return findings


def check_dose_concentration_relationship(
    pk_params: List[Dict[str, Any]], rules: Dict[str, Any]
) -> List[CoreGageFinding]:
    """
    检查剂量-浓度关系的合理性。

    对于同一受试者的不同剂量，检查 AUC 与剂量是否成比例。

    Args:
        pk_params: PK 参数列表
        rules: 规则配置

    Returns:
        发现列表
    """
    findings: List[CoreGageFinding] = []

    # 按受试者分组
    by_subject: Dict[str, List[Dict[str, Any]]] = {}
    for param in pk_params:
        subj = param["SUBJID"]
        if subj not in by_subject:
            by_subject[subj] = []
        by_subject[subj].append(param)

    for subj_id, params in by_subject.items():
        if len(params) < 2:
            continue

        # 检查剂量比例与 AUC 比例是否一致
        doses = [p["dose"] for p in params if p.get("dose")]
        aucs = [p["AUC"] for p in params if p.get("AUC")]

        if len(doses) < 2 or len(aucs) < 2:
            continue

        # 计算剂量比例
        dose_ratio = doses[1] / doses[0] if doses[0] > 0 else 1.0
        auc_ratio = aucs[1] / aucs[0] if aucs[0] > 0 else 1.0

        # 允许 20% 的偏差
        expected_auc_ratio = dose_ratio
        tolerance = 0.2
        if abs(auc_ratio - expected_auc_ratio) / expected_auc_ratio > tolerance:
            findings.append(CoreGageFinding(
                category=CheckCategory.CONSISTENCY,
                severity=Severity.LOW,
                source="pkpd_dose_conc",
                subject_id=subj_id,
                visit_id="ALL",
                message=f"剂量-浓度关系异常: 剂量比 {dose_ratio:.2f}, "
                        f"AUC 比 {auc_ratio:.2f} (偏差 > {tolerance * 100:.0f}%)",
                details={
                    "check_id": "PK_DOSE_CONC_RATIO",
                    "dose_ratio": round(dose_ratio, 2),
                    "auc_ratio": round(auc_ratio, 2),
                    "tolerance": tolerance,
                },
                status=CheckStatus.PASSED,
            ))

    return findings


def check_sampling_time_sequence(
    raw_data: List[Dict[str, Any]], rules: Dict[str, Any]
) -> List[CoreGageFinding]:
    """
    检查采样时间序列的完整性。

    Args:
        raw_data: 原始 PK 数据
        rules: 规则配置

    Returns:
        发现列表
    """
    findings: List[CoreGageFinding] = []
    sampling_rules = rules.get("sampling_rules", {})
    min_samples = sampling_rules.get("min_samples_per_subject", 5)

    # 按受试者-访视分组
    groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for record in raw_data:
        key = (record["subject_id"], record["visit"])
        if key not in groups:
            groups[key] = []
        groups[key].append(record)

    for (subj_id, visit), records in groups.items():
        # 检查采样点数
        if len(records) < min_samples:
            findings.append(CoreGageFinding(
                category=CheckCategory.INTEGRITY,
                severity=Severity.MEDIUM,
                source="pkpd_sampling",
                subject_id=subj_id,
                visit_id=visit,
                message=f"采样点数不足: {len(records)} 个 "
                        f"(要求 ≥ {min_samples})",
                details={
                    "check_id": "PK_SAMPLING_COUNT",
                    "n_samples": len(records),
                    "min_samples": min_samples,
                },
                status=CheckStatus.PASSED,
            ))

        # 检查时间序列是否递增
        records_sorted = sorted(records, key=lambda x: x["sample_time"])
        for i in range(1, len(records_sorted)):
            prev_time = records_sorted[i - 1]["sample_time"]
            curr_time = records_sorted[i]["sample_time"]
            if curr_time < prev_time:
                findings.append(CoreGageFinding(
                    category=CheckCategory.INTEGRITY,
                    severity=Severity.HIGH,
                    source="pkpd_sampling",
                    subject_id=subj_id,
                    visit_id=visit,
                    message=f"采样时间倒序: {prev_time} > {curr_time}",
                    details={
                        "check_id": "PK_SAMPLING_TIME_ORDER",
                        "prev_time": prev_time,
                        "curr_time": curr_time,
                    },
                    status=CheckStatus.PASSED,
                ))

    return findings


# ═══════════════════════════════════════════════════════════
# 5. 主测试函数
# ═══════════════════════════════════════════════════════════


def run_pkpd_test() -> List[CoreGageFinding]:
    """
    运行完整的 PK/PD 分析测试。

    Returns:
        发现列表
    """
    print("=" * 70)
    print("🧪 pyCoreGage PK/PD 分析检查功能测试")
    print("=" * 70)

    # 加载数据
    data_dir = Path(__file__).parent / "data"
    rules_dir = Path(__file__).parent / "rules"

    print("\n📊 加载 PK 数据...")
    raw_data = load_pk_data(str(data_dir / "pk_data.csv"))
    print(f"   总记录数: {len(raw_data)}")
    print(f"   受试者数: {len(set(r['subject_id'] for r in raw_data))}")
    print(f"   访视: {sorted(set(r['visit'] for r in raw_data))}")

    # 加载规则
    print("\n📋 加载 PK/PD 规则...")
    rules = load_pkpd_rules(str(rules_dir / "pkpd_rules.yaml"))
    print(f"   规则节数: {len(rules)}")

    # 计算 PK 参数
    print("\n🔬 计算 PK 参数...")
    pk_params = compute_pk_parameters(raw_data)
    print(f"   计算了 {len(pk_params)} 组 PK 参数")

    # 展示 PK 参数摘要
    print("\n" + "-" * 70)
    print("📊 PK 参数摘要")
    print("-" * 70)
    print(f"{'受试者':>8} {'访视':>10} {'AUC':>12} {'Cmax':>12} {'Tmax':>8} {'t1/2':>8} {'R²':>8}")
    print("-" * 70)
    for param in pk_params:
        t_half_str = f"{param['t_half']:.2f}" if param["t_half"] is not None else "N/A"
        r2_str = f"{param['r_squared']:.4f}" if param["r_squared"] is not None else "N/A"
        print(f"{param['SUBJID']:>8} {param['VISIT']:>10} "
              f"{param['AUC']:>12.2f} {param['Cmax']:>12.2f} "
              f"{param['Tmax']:>8.2f} {t_half_str:>8} {r2_str:>8}")

    # 运行各项检查
    print("\n🔍 运行检查...")

    all_findings: List[CoreGageFinding] = []

    # 1. AUC 检查
    print("  [1/6] AUC 计算检查...")
    auc_findings = check_auc_calculation(pk_params, rules)
    all_findings.extend(auc_findings)
    print(f"       发现 {len(auc_findings)} 个问题")

    # 2. Cmax/Tmax 检查
    print("  [2/6] Cmax/Tmax 识别检查...")
    ct_findings = check_cmax_tmax(pk_params, rules)
    all_findings.extend(ct_findings)
    print(f"       发现 {len(ct_findings)} 个问题")

    # 3. 半衰期检查
    print("  [3/6] 半衰期计算检查...")
    hl_findings = check_half_life(pk_params, rules)
    all_findings.extend(hl_findings)
    print(f"       发现 {len(hl_findings)} 个问题")

    # 4. 剂量-浓度关系检查
    print("  [4/6] 剂量-浓度关系检查...")
    dc_findings = check_dose_concentration_relationship(pk_params, rules)
    all_findings.extend(dc_findings)
    print(f"       发现 {len(dc_findings)} 个问题")

    # 5. 采样时间序列检查
    print("  [5/6] 采样时间序列完整性检查...")
    st_findings = check_sampling_time_sequence(raw_data, rules)
    all_findings.extend(st_findings)
    print(f"       发现 {len(st_findings)} 个问题")

    # 6. 运行现有 pkpd_checker.py
    print("  [6/6] 运行现有 pkpd_checker.py...")
    try:
        # 创建 mock state 以兼容现有检查器
        class MockState:
            def __init__(self, domains: Dict[str, Any]):
                self.domains = domains

        # 将 PK 参数转换为 domains 格式
        domains = {"pk": pk_params}
        mock_state = MockState(domains)
        mock_config = CoreGageConfig()

        # 导入并运行现有检查器
        from pkpd_checker import PKPDChecker
        checker = PKPDChecker(mock_state, mock_config)
        existing_findings = []
        existing_findings.extend(checker.check_pk_parameters())
        existing_findings.extend(checker.check_sampling_time())
        existing_findings.extend(checker.check_dose_concentration())
        print(f"       现有检查器发现 {len(existing_findings)} 个问题")

        # 转换为 CoreGageFinding
        for ef in existing_findings:
            all_findings.append(CoreGageFinding(
                category=CheckCategory.CONSISTENCY,
                severity=Severity(ef.get("severity", "MEDIUM").lower()),
                source="pkpd_existing",
                subject_id=ef.get("subj_id", ""),
                visit_id=ef.get("vis_id", ""),
                message=ef.get("description", ""),
                details=ef,
                status=CheckStatus.PASSED,
            ))
    except Exception as e:
        print(f"       现有检查器运行失败: {e}")

    # 汇总结果
    print("\n" + "=" * 70)
    print("📋 检查结果汇总")
    print("=" * 70)

    total = len(all_findings)
    print(f"\n总发现数: {total}")

    # 按 source 分类
    by_source: Dict[str, List[CoreGageFinding]] = {}
    for f in all_findings:
        by_source.setdefault(f.source, []).append(f)

    for source, items in sorted(by_source.items()):
        print(f"\n  [{source}] {len(items)} 个发现")
        for f in items:
            print(f"    [{f.severity.value:>8}] {f.subject_id:>8} | {f.message[:100]}")

    # 严重级别统计
    print("\n" + "=" * 70)
    print("📈 严重级别分布")
    print("=" * 70)
    sev_count: Dict[str, int] = {}
    for f in all_findings:
        sev_count[f.severity.value] = sev_count.get(f.severity.value, 0) + 1
    for sev in ["info", "low", "medium", "high", "critical"]:
        count = sev_count.get(sev, 0)
        bar = "█" * count
        print(f"  {sev:>10}: {count:>3} {bar}")

    # 保存详细结果
    output_path = Path(__file__).parent / "test_pkpd_output.json"
    result_data = {
        "total_findings": total,
        "by_source": {},
        "by_severity": sev_count,
        "pk_parameters": pk_params,
        "findings": [],
    }
    for f in all_findings:
        result_data["findings"].append(f.to_dict())
        src = f.source
        result_data["by_source"][src] = result_data["by_source"].get(src, 0) + 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n💾 详细结果已保存到: {output_path}")

    print("\n✅ PK/PD 测试完成！")
    return all_findings


# ═══════════════════════════════════════════════════════════
# 6. 单元测试
# ═══════════════════════════════════════════════════════════


def test_auc_trapezoidal() -> None:
    """测试梯形法则 AUC 计算。"""
    print("\n🧪 单元测试: AUC 梯形法则计算")
    print("-" * 40)

    # 测试1: 简单线性下降
    times = [0, 1, 2, 3]
    concs = [100, 50, 25, 12.5]
    auc = compute_auc_trapezoidal(times, concs)
    expected = 0.5 * 1 * (100 + 50) + 0.5 * 1 * (50 + 25) + 0.5 * 1 * (25 + 12.5)
    print(f"  输入: times={times}, concs={concs}")
    print(f"  计算 AUC: {auc:.2f}")
    print(f"  期望 AUC: {expected:.2f}")
    assert abs(auc - expected) < 0.01, f"AUC 计算错误: {auc} != {expected}"
    print("  ✅ AUC 计算通过")

    # 测试2: 空数据
    auc_empty = compute_auc_trapezoidal([], [])
    assert auc_empty == 0.0
    print("  ✅ 空数据 AUC 通过")


def test_cmax_tmax() -> None:
    """测试 Cmax/Tmax 识别。"""
    print("\n🧪 单元测试: Cmax/Tmax 识别")
    print("-" * 40)

    times = [0, 0.5, 1, 2, 4, 6]
    concs = [0, 50, 100, 80, 40, 20]
    cmax, tmax = find_cmax_tmax(times, concs)
    print(f"  输入: times={times}, concs={concs}")
    print(f"  Cmax: {cmax} (期望: 100)")
    print(f"  Tmax: {tmax} (期望: 1.0)")
    assert cmax == 100.0
    assert tmax == 1.0
    print("  ✅ Cmax/Tmax 识别通过")


def test_half_life() -> None:
    """测试半衰期计算。"""
    print("\n🧪 单元测试: 半衰期计算（线性回归）")
    print("-" * 40)

    # 模拟一室模型消除相: C = C0 * e^(-k*t), k = ln(2)/t1/2
    # 设 t1/2 = 2h, k = 0.3466
    t_half_true = 2.0
    k_true = math.log(2) / t_half_true
    C0 = 100.0

    times = [2, 4, 6, 8, 10]
    concs = [C0 * math.exp(-k_true * t) for t in times]
    concs = [round(c, 4) for c in concs]

    t_half_calc = compute_half_life_linear_regression(times, concs, C0)
    print(f"  真实半衰期: {t_half_true} h")
    print(f"  计算半衰期: {t_half_calc:.4f} h")
    print(f"  误差: {abs(t_half_calc - t_half_true) if t_half_calc else 'N/A'}")

    if t_half_calc:
        assert abs(t_half_calc - t_half_true) < 0.1, f"半衰期计算误差过大: {t_half_calc}"
    print("  ✅ 半衰期计算通过")


def test_r_squared() -> None:
    """测试 R² 计算。"""
    print("\n🧪 单元测试: R² 计算")
    print("-" * 40)

    # 完美线性关系
    times = [2, 4, 6, 8]
    concs = [100 * math.exp(-0.3466 * t) for t in times]
    r2 = compute_r_squared(times, concs, 100)
    print(f"  R²: {r2:.6f} (期望: ~1.0)")
    assert r2 is not None and r2 > 0.99
    print("  ✅ R² 计算通过")


if __name__ == "__main__":
    # 运行单元测试
    test_auc_trapezoidal()
    test_cmax_tmax()
    test_half_life()
    test_r_squared()

    # 运行完整测试
    print("\n" + "=" * 70)
    findings = run_pkpd_test()
    print("=" * 70)
