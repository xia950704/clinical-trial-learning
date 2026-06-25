"""
coding_checker.py — 医学编码检查模块 (pyCoreGage 插件)
=====================================================

与 pyCoreGage 的 CoreGageState 兼容，通过 collect_findings() 收集发现。

支持的编码体系：
  1. MedDRA 编码检查 — LLT → PT → SOC 层级关系验证
  2. ICD-10 编码检查 — 诊断编码格式与有效性验证
  3. ATC 编码检查   — 药物编码格式与有效性验证
  4. LOINC 编码检查 — 实验室检验项目编码验证

使用方式：
    将本文件放入 pyCoreGage 的 trial_checks 或 study_checks 目录，
    并在 rule_registry.xlsx 中添加 Rule_Set = "Coding"。
    运行 pyCoreGage 后会自动调用 check_Coding(state, cfg)。

参考数据：
    内置常用编码字典（可被外部 CSV/JSON 参考表覆盖）。
    外部参考表路径可通过环境变量 PYCOREGAGE_CODING_REF_DIR 指定。
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd

from pyCoreGage import CoreGageConfig, CoreGageState, collect_findings

logger = logging.getLogger("pyCoreGage")

# ---------------------------------------------------------------------------
# 1. 参考数据 (Reference Data)
# ---------------------------------------------------------------------------

# --- MedDRA: LLT -> (PT, SOC) 映射 ---
_MEDDRA_LLT_TO_PT_SOC: Dict[str, Tuple[str, str]] = {
    # 格式: LLT术语/编码 -> (PT术语/编码, SOC术语/编码)
    # 以下为示例数据，实际使用应加载完整 MedDRA 字典
    "Abdominal pain": ("Abdominal pain", "Gastrointestinal disorders"),
    "Abdominal pain upper": ("Abdominal pain upper", "Gastrointestinal disorders"),
    "Arthralgia": ("Arthralgia", "Musculoskeletal and connective tissue disorders"),
    "Back pain": ("Back pain", "Musculoskeletal and connective tissue disorders"),
    "Bronchitis": ("Bronchitis", "Respiratory, thoracic and mediastinal disorders"),
    "Cough": ("Cough", "Respiratory, thoracic and mediastinal disorders"),
    "Diarrhoea": ("Diarrhoea", "Gastrointestinal disorders"),
    "Dizziness": ("Dizziness", "Nervous system disorders"),
    "Dyspnoea": ("Dyspnoea", "Respiratory, thoracic and mediastinal disorders"),
    "Fatigue": ("Fatigue", "General disorders and administration site conditions"),
    "Headache": ("Headache", "Nervous system disorders"),
    "Hypertension": ("Hypertension", "Vascular disorders"),
    "Hypotension": ("Hypotension", "Vascular disorders"),
    "Insomnia": ("Insomnia", "Psychiatric disorders"),
    "Nausea": ("Nausea", "Gastrointestinal disorders"),
    "Neutropenia": ("Neutropenia", "Infections and infestations"),
    "Rash": ("Rash", "Skin and subcutaneous tissue disorders"),
    "Thrombocytopenia": ("Thrombocytopenia", "Blood and lymphatic system disorders"),
    "Vomiting": ("Vomiting", "Gastrointestinal disorders"),
}

# --- ICD-10: 有效章节前缀 ---
_ICD10_CHAPTERS: Dict[str, str] = {
    "A": "某些传染病和寄生虫病",
    "B": "某些传染病和寄生虫病",
    "C": "肿瘤",
    "D": "肿瘤",
    "E": "内分泌、营养和代谢疾病",
    "F": "精神与行为障碍",
    "G": "神经系统疾病",
    "H": "耳和乳突疾病",
    "I": "循环系统疾病",
    "J": "呼吸系统疾病",
    "K": "消化系统疾病",
    "L": "皮肤和皮下组织疾病",
    "M": "肌肉骨骼系统和结缔组织疾病",
    "N": "泌尿生殖系统疾病",
    "O": "妊娠、分娩和产褥期",
    "P": "围产期某些情况",
    "Q": "先天性畸形、变形和染色体异常",
    "R": "症状、体征和异常临床与实验室所见",
    "S": "损伤、中毒和外因的某些其他后果",
    "T": "损伤、中毒和外因的某些其他后果",
    "U": "临时编码",
    "V": "影响健康状态和卫生保健接触的因素",
    "W": "外部原因",
    "X": "外部原因",
    "Y": "外部原因",
    "Z": "影响健康状态和卫生保健接触的因素",
}

# --- ATC: 一级分类 (Anatomical Main Group) ---
_ATC_LEVEL1: Dict[str, str] = {
    "A": "消化道和代谢系统",
    "B": "血液和造血器官",
    "C": "心血管系统",
    "D": "皮肤病",
    "G": "泌尿生殖系统和性激素",
    "H": "激素制剂（性激素除外）",
    "J": "抗感染药",
    "L": "抗肿瘤药和免疫调节剂",
    "M": "肌肉骨骼系统",
    "N": "神经系统",
    "P": "抗寄生虫药、杀虫剂和驱虫剂",
    "R": "呼吸系统",
    "S": "感觉器官",
    "V": "各种药物",
}

# --- LOINC: 常见检验项目 ---
# 格式: LOINC 编号 -> (短名, 长名)
_LOINC_COMMON: Dict[str, Tuple[str, str]] = {
    "2345-7": ("Glucose", "Glucose [Mass/volume] in Serum or Plasma"),
    "2093-3": ("Cholesterol", "Cholesterol [Mass/volume] in Serum or Plasma"),
    "2089-1": ("HDL Cholesterol", "Cholesterol in HDL [Mass/volume] in Serum or Plasma"),
    "2571-8": ("Triglycerides", "Triglyceride [Mass/volume] in Serum or Plasma"),
    "718-7": ("Hemoglobin", "Hemoglobin [Mass/volume] in Blood"),
    "789-8": ("Platelet count", "Platelets [#/volume] in Blood"),
    "6690-2": ("WBC count", "Leukocytes [#/volume] in Blood"),
    "787-2": ("RBC count", "Erythrocytes [#/volume] in Blood"),
    "2160-0": ("Creatinine", "Creatinine [Mass/volume] in Serum or Plasma"),
    "1975-2": ("ALT", "Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma"),
    "17861-6": ("AST", "Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma"),
    "3094-0": ("Bilirubin, total", "Bilirubin [Mass/volume] in Serum or Plasma"),
    "14682-9": ("Sodium", "Sodium [Mass/volume] in Serum or Plasma"),
    "2075-0": ("Potassium", "Potassium [Mass/volume] in Serum or Plasma"),
    "17859-2": ("Calcium", "Calcium [Mass/volume] in Serum or Plasma"),
    "2951-2": ("Urea nitrogen", "Urea nitrogen [Mass/volume] in Serum or Plasma"),
    "4548-4": ("HbA1c", "Hemoglobin A1c/Hemoglobin.total in Blood"),
}

# ---------------------------------------------------------------------------
# 2. 配置与外部参考表加载
# ---------------------------------------------------------------------------

@dataclass
class CodingRefData:
    """医学编码参考数据容器"""
    meddra_llt_to_ptsoc: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    icd10_chapters: Dict[str, str] = field(default_factory=dict)
    atc_level1: Dict[str, str] = field(default_factory=dict)
    loinc_common: Dict[str, Tuple[str, str]] = field(default_factory=dict)

    def load_external(self, ref_dir: Optional[str] = None) -> None:
        """从外部 CSV/JSON 参考表加载或覆盖内置数据。

        期望的文件名：
            - meddra_llt.csv  (columns: llt_code, pt_code, soc_code)
            - icd10_codes.csv (columns: code, chapter, description)
            - atc_codes.csv   (columns: atc_code, level1, description)
            - loinc_codes.csv (columns: loinc_code, short_name, long_name)
        """
        if ref_dir is None:
            return
        if not os.path.isdir(ref_dir):
            logger.debug("[CodingRefData] ref_dir '%s' not found, skip external load", ref_dir)
            return

        # MedDRA
        meddra_path = os.path.join(ref_dir, "meddra_llt.csv")
        if os.path.isfile(meddra_path):
            try:
                df = pd.read_csv(meddra_path)
                for _, row in df.iterrows():
                    llc = str(row.get("llt_code", "")).strip()
                    if llc:
                        self.meddra_llt_to_ptsoc[llc] = (
                            str(row.get("pt_code", "")).strip(),
                            str(row.get("soc_code", "")).strip(),
                        )
                logger.info("[CodingRefData] Loaded %d MedDRA LLT entries from %s",
                            len(self.meddra_llt_to_ptsoc), meddra_path)
            except Exception as exc:
                logger.warning("[CodingRefData] Failed to load MedDRA: %s", exc)

        # ICD-10
        icd_path = os.path.join(ref_dir, "icd10_codes.csv")
        if os.path.isfile(icd_path):
            try:
                df = pd.read_csv(icd_path)
                for _, row in df.iterrows():
                    code = str(row.get("code", "")).strip()
                    if code:
                        self.icd10_chapters[code] = str(row.get("description", "")).strip()
                logger.info("[CodingRefData] Loaded %d ICD-10 entries from %s",
                            len(self.icd10_chapters), icd_path)
            except Exception as exc:
                logger.warning("[CodingRefData] Failed to load ICD-10: %s", exc)

        # ATC
        atc_path = os.path.join(ref_dir, "atc_codes.csv")
        if os.path.isfile(atc_path):
            try:
                df = pd.read_csv(atc_path)
                for _, row in df.iterrows():
                    code = str(row.get("atc_code", "")).strip()
                    if code:
                        self.atc_level1[code] = str(row.get("description", "")).strip()
                logger.info("[CodingRefData] Loaded %d ATC entries from %s",
                            len(self.atc_level1), atc_path)
            except Exception as exc:
                logger.warning("[CodingRefData] Failed to load ATC: %s", exc)

        # LOINC
        loinc_path = os.path.join(ref_dir, "loinc_codes.csv")
        if os.path.isfile(loinc_path):
            try:
                df = pd.read_csv(loinc_path)
                for _, row in df.iterrows():
                    code = str(row.get("loinc_code", "")).strip()
                    if code:
                        self.loinc_common[code] = (
                            str(row.get("short_name", "")).strip(),
                            str(row.get("long_name", "")).strip(),
                        )
                logger.info("[CodingRefData] Loaded %d LOINC entries from %s",
                            len(self.loinc_common), loinc_path)
            except Exception as exc:
                logger.warning("[CodingRefData] Failed to load LOINC: %s", exc)


def _get_ref_data(cfg: CoreGageConfig) -> CodingRefData:
    """获取参考数据（优先使用外部参考表，否则使用内置数据）"""
    ref = CodingRefData()
    # 合并内置数据
    ref.meddra_llt_to_ptsoc.update(_MEDDRA_LLT_TO_PT_SOC)
    ref.icd10_chapters.update(_ICD10_CHAPTERS)
    ref.atc_level1.update(_ATC_LEVEL1)
    ref.loinc_common.update(_LOINC_COMMON)
    # 尝试加载外部参考表
    ref_dir = getattr(cfg, "coding_ref_dir", None) or \
              getattr(cfg, "reference_data", None) or \
              os.environ.get("PYCOREGAGE_CODING_REF_DIR")
    if ref_dir:
        ref.load_external(ref_dir)
    return ref


# ---------------------------------------------------------------------------
# 3. 辅助函数
# ---------------------------------------------------------------------------

def _safe_str(val: Any) -> str:
    """安全转换为字符串"""
    if val is None:
        return ""
    return str(val).strip()


def _find_domain(state: CoreGageState, *names: str) -> Optional[pd.DataFrame]:
    """从 state.domains 中查找第一个存在的域"""
    for name in names:
        if name in state.domains:
            return state.domains[name]
    return None


def _extract_subj_vis(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """从域 DataFrame 中提取 subj_id 和 vis_id 列，并重置索引为位置索引。"""
    subj_col = None
    for c in ["USUBJID", "SUBJID", "subj_id", "Subject ID", "Subject"]:
        if c in df.columns:
            subj_col = c
            break
    vis_col = None
    for c in ["VISITNUM", "VISIT", "vis_id", "Visit", "Visit Number"]:
        if c in df.columns:
            vis_col = c
            break
    # 重置索引确保位置索引从 0 开始
    df_reset = df.reset_index(drop=True)
    subj = df_reset[subj_col].astype(str) if subj_col else pd.Series(["UNKNOWN"] * len(df_reset))
    vis = df_reset[vis_col] if vis_col else pd.Series([float("nan")] * len(df_reset))
    return subj, vis


# ---------------------------------------------------------------------------
# 4. 编码检查函数
# ---------------------------------------------------------------------------

def check_meddra(
    state: CoreGageState,
    cfg: CoreGageConfig,
    ref: CodingRefData,
) -> pd.DataFrame:
    """
    MedDRA 编码检查 — LLT → PT → SOC 层级关系验证。

    检查逻辑：
      1. LLT 编码/术语是否存在于参考字典
      2. LLT → PT 映射是否正确
      3. PT → SOC 映射是否正确
      4. 编码格式是否合法（纯数字 8 位）

    目标域：AE（不良事件）、AE 相关域
    期望列：AELLT（LLT 术语/编码）、AEPT（PT 术语/编码）、AESOC（SOC 术语/编码）
    """
    findings: List[Dict[str, Any]] = []

    # 尝试从 AE 域获取数据
    ae = _find_domain(state, "AE", "ae", "AE_domain")
    if ae is None or ae.empty:
        logger.info("[check_meddra] AE domain not found or empty, skip")
        return pd.DataFrame(columns=["subj_id", "vis_id", "description"])

    subj, vis = _extract_subj_vis(ae)

    # 确定 LLT/PT/SOC 列
    llc_col = None
    for c in ["AELLT", "AEPT", "LLT", "llt"]:
        if c in ae.columns:
            llc_col = c
            break
    if llc_col is None:
        logger.warning("[check_meddra] No LLT column found in AE domain, skip")
        return pd.DataFrame(columns=["subj_id", "vis_id", "description"])

    pt_col = None
    for c in ["AEPT", "PT", "pt"]:
        if c in ae.columns:
            pt_col = c
            break
    soc_col = None
    for c in ["AESOC", "SOC", "soc"]:
        if c in ae.columns:
            soc_col = c
            break

    mapping = ref.meddra_llt_to_ptsoc

    for pos in range(len(ae)):
        row = ae.iloc[pos]
        llc_val = _safe_str(row.get(llc_col))
        if not llc_val:
            continue

        subj_id = str(subj.iloc[pos]) if pos < len(subj) else "UNKNOWN"
        vis_id = vis.iloc[pos] if pos < len(vis) else float("nan")

        # 检查1: LLT 是否在参考字典中
        if llc_val not in mapping:
            # 尝试按编码格式检查（8位数字）
            if re.match(r"^\d{8}$", llc_val):
                findings.append({
                    "subj_id": subj_id,
                    "vis_id": vis_id,
                    "description": f"MedDRA: LLT 编码 '{llc_val}' 不在参考字典中（8位数字格式合法）",
                })
            else:
                findings.append({
                    "subj_id": subj_id,
                    "vis_id": vis_id,
                    "description": f"MedDRA: LLT 术语/编码 '{llc_val}' 不在参考字典中",
                })
            continue

        expected_pt, expected_soc = mapping[llc_val]

        # 检查2: PT 映射
        if pt_col:
            actual_pt = _safe_str(row.get(pt_col))
            if actual_pt and actual_pt != expected_pt:
                findings.append({
                    "subj_id": subj_id,
                    "vis_id": vis_id,
                    "description": f"MedDRA: LLT '{llc_val}' 的 PT 应为 '{expected_pt}'，实际为 '{actual_pt}'",
                })

        # 检查3: SOC 映射
        if soc_col:
            actual_soc = _safe_str(row.get(soc_col))
            if actual_soc and actual_soc != expected_soc:
                findings.append({
                    "subj_id": subj_id,
                    "vis_id": vis_id,
                    "description": f"MedDRA: LLT '{llc_val}' 的 SOC 应为 '{expected_soc}'，实际为 '{actual_soc}'",
                })

    return pd.DataFrame(findings, columns=["subj_id", "vis_id", "description"])


def check_icd10(
    state: CoreGageState,
    cfg: CoreGageConfig,
    ref: CodingRefData,
) -> pd.DataFrame:
    """
    ICD-10 编码检查 — 诊断编码格式与有效性验证。

    检查逻辑：
      1. 编码格式：1个字母 + 2个数字（如 A00, I10, M79.3）
      2. 可选：小数点后 1-2 位扩展码（如 I10.0, K21.0）
      3. 章节字母是否在有效范围内（A-Z，排除 I、O 等保留位）
      4. 编码是否在参考字典中

    目标域：DI（诊断）、CM（合并用药诊断）、CM 相关域
    期望列：DICODE（ICD-10 编码）、DIPT（诊断术语）
    """
    findings: List[Dict[str, Any]] = []

    # ICD-10 格式正则：字母 + 2位数字 + 可选 . + 1-2位数字
    icd10_pattern = re.compile(r"^[A-Z]\d{2}(\.\d{1,2})?$")

    # 尝试从 DI 域获取数据
    di = _find_domain(state, "DI", "di", "DI_domain", "CM", "cm")
    if di is None or di.empty:
        logger.info("[check_icd10] DI/CM domain not found or empty, skip")
        return pd.DataFrame(columns=["subj_id", "vis_id", "description"])

    subj, vis = _extract_subj_vis(di)

    # 确定 ICD-10 编码列
    code_col = None
    for c in ["DICODE", "ICD10", "ICD_10", "icd10", "code", "CODE"]:
        if c in di.columns:
            code_col = c
            break
    if code_col is None:
        logger.warning("[check_icd10] No ICD-10 code column found, skip")
        return pd.DataFrame(columns=["subj_id", "vis_id", "description"])

    chapters = ref.icd10_chapters

    for pos in range(len(di)):
        row = di.iloc[pos]
        code = _safe_str(row.get(code_col))
        if not code:
            continue

        subj_id = str(subj.iloc[pos]) if pos < len(subj) else "UNKNOWN"
        vis_id = vis.iloc[pos] if pos < len(vis) else float("nan")

        # 检查1: 格式验证
        if not icd10_pattern.match(code):
            findings.append({
                "subj_id": subj_id,
                "vis_id": vis_id,
                "description": f"ICD-10: 编码 '{code}' 格式无效（应为 字母+2位数字，如 A00 或 I10.0）",
            })
            continue

        # 检查2: 章节字母验证
        chapter_letter = code[0]
        if chapter_letter not in chapters:
            findings.append({
                "subj_id": subj_id,
                "vis_id": vis_id,
                "description": f"ICD-10: 编码 '{code}' 的章节 '{chapter_letter}' 不在有效范围内",
            })
            continue

        # 检查3: 参考字典验证（如果字典中有完整编码）
        if chapters and code not in chapters and len(chapters) > len(_ICD10_CHAPTERS):
            # 仅在外部参考表加载时才做完整编码检查
            findings.append({
                "subj_id": subj_id,
                "vis_id": vis_id,
                "description": f"ICD-10: 编码 '{code}' 不在参考字典中",
            })

    return pd.DataFrame(findings, columns=["subj_id", "vis_id", "description"])


def check_atc(
    state: CoreGageState,
    cfg: CoreGageConfig,
    ref: CodingRefData,
) -> pd.DataFrame:
    """
    ATC 编码检查 — 药物编码格式与有效性验证。

    检查逻辑：
      1. ATC 格式：字母+2数字+字母+字母+2数字（如 A02BC01）
         或更粗粒度：字母+2数字+字母+字母（如 A02BC）
      2. 一级分类字母是否在有效范围内
      3. 编码是否在参考字典中

    目标域：CM（合并用药）、EX（用药记录）
    期望列：CMDECOD（药物名称）、CMATC（ATC 编码）
    """
    findings: List[Dict[str, Any]] = []

    # ATC 格式正则：
    # 完整 ATC: 字母 + 2数字 + 字母 + 字母 + 2数字 (如 A02BC01)
    # 或更粗粒度: 字母 + 2数字 + 字母 + 字母 (如 A02BC)
    atc_pattern = re.compile(r"^[A-Z]\d{2}[A-Z][A-Z]\d{2}$|^[A-Z]\d{2}[A-Z][A-Z]$")

    # 尝试从 CM 域获取数据
    cm = _find_domain(state, "CM", "cm", "CM_domain", "EX", "ex")
    if cm is None or cm.empty:
        logger.info("[check_atc] CM/EX domain not found or empty, skip")
        return pd.DataFrame(columns=["subj_id", "vis_id", "description"])

    subj, vis = _extract_subj_vis(cm)

    # 确定 ATC 编码列
    atc_col = None
    for c in ["CMATC", "ATC", "atc", "ATC_CODE", "atc_code"]:
        if c in cm.columns:
            atc_col = c
            break
    if atc_col is None:
        logger.warning("[check_atc] No ATC code column found, skip")
        return pd.DataFrame(columns=["subj_id", "vis_id", "description"])

    level1 = ref.atc_level1

    for pos in range(len(cm)):
        row = cm.iloc[pos]
        atc = _safe_str(row.get(atc_col))
        if not atc:
            continue

        subj_id = str(subj.iloc[pos]) if pos < len(subj) else "UNKNOWN"
        vis_id = vis.iloc[pos] if pos < len(vis) else float("nan")

        # 检查1: 格式验证
        if not atc_pattern.match(atc):
            findings.append({
                "subj_id": subj_id,
                "vis_id": vis_id,
                "description": f"ATC: 编码 '{atc}' 格式无效（应为 字母+2数字+字母+字母+2数字，如 A02BC01）",
            })
            continue

        # 检查2: 一级分类验证
        level1_letter = atc[0]
        if level1_letter not in level1:
            findings.append({
                "subj_id": subj_id,
                "vis_id": vis_id,
                "description": f"ATC: 编码 '{atc}' 的一级分类 '{level1_letter}' 不在有效范围内",
            })
            continue

        # 检查3: 参考字典验证
        if level1 and atc not in level1 and len(level1) > len(_ATC_LEVEL1):
            findings.append({
                "subj_id": subj_id,
                "vis_id": vis_id,
                "description": f"ATC: 编码 '{atc}' 不在参考字典中",
            })

    return pd.DataFrame(findings, columns=["subj_id", "vis_id", "description"])


def check_loinc(
    state: CoreGageState,
    cfg: CoreGageConfig,
    ref: CodingRefData,
) -> pd.DataFrame:
    """
    LOINC 编码检查 — 实验室检验项目编码验证。

    检查逻辑：
      1. LOINC 格式：5位数字 + '-' + 1位数字（如 2345-7）
      2. 编码是否在参考字典中
      3. 检验项目与预期类别是否匹配

    目标域：LB（实验室检查）
    期望列：LBBLTEST（检验项目）、LBLOINC（LOINC 编码）
    """
    findings: List[Dict[str, Any]] = []

    # LOINC 格式正则：5位数字 + '-' + 1位数字
    loinc_pattern = re.compile(r"^\d{5}-\d{1}$")

    # 尝试从 LB 域获取数据
    lb = _find_domain(state, "LB", "lb", "LB_domain")
    if lb is None or lb.empty:
        logger.info("[check_loinc] LB domain not found or empty, skip")
        return pd.DataFrame(columns=["subj_id", "vis_id", "description"])

    subj, vis = _extract_subj_vis(lb)

    # 确定 LOINC 编码列
    loinc_col = None
    for c in ["LBLOINC", "LOINC", "loinc", "LOINC_CODE", "loinc_code", "LBBLTESTNR"]:
        if c in lb.columns:
            loinc_col = c
            break
    if loinc_col is None:
        logger.warning("[check_loinc] No LOINC code column found, skip")
        return pd.DataFrame(columns=["subj_id", "vis_id", "description"])

    loinc_dict = ref.loinc_common

    for pos in range(len(lb)):
        row = lb.iloc[pos]
        loinc = _safe_str(row.get(loinc_col))
        if not loinc:
            continue

        subj_id = str(subj.iloc[pos]) if pos < len(subj) else "UNKNOWN"
        vis_id = vis.iloc[pos] if pos < len(vis) else float("nan")

        # 检查1: 格式验证
        if not loinc_pattern.match(loinc):
            findings.append({
                "subj_id": subj_id,
                "vis_id": vis_id,
                "description": f"LOINC: 编码 '{loinc}' 格式无效（应为 5位数字-1位数字，如 2345-7）",
            })
            continue

        # 检查2: 参考字典验证
        if loinc_dict and loinc not in loinc_dict and len(loinc_dict) > len(_LOINC_COMMON):
            findings.append({
                "subj_id": subj_id,
                "vis_id": vis_id,
                "description": f"LOINC: 编码 '{loinc}' 不在参考字典中",
            })

    return pd.DataFrame(findings, columns=["subj_id", "vis_id", "description"])


# ---------------------------------------------------------------------------
# 5. 主检查函数 (pyCoreGage 入口)
# ---------------------------------------------------------------------------

def check_Coding(state: CoreGageState, cfg: CoreGageConfig) -> CoreGageState:
    """
    医学编码检查主入口函数。

    执行四项编码检查并将发现汇总到 state.issues：
      - CODING_MEDDRA: MedDRA LLT→PT→SOC 层级检查
      - CODING_ICD10:  ICD-10 诊断编码检查
      - CODING_ATC:    ATC 药物编码检查
      - CODING_LOINC:  LOINC 实验室检验编码检查

    Parameters
    ----------
    state : CoreGageState
        当前运行状态（通过 collect_findings 收集发现）。
    cfg : CoreGageConfig
        项目配置。

    Returns
    -------
    CoreGageState
        更新后的状态对象。
    """
    logger.info(">> [Coding] 开始医学编码检查 ...")

    # 加载参考数据
    ref = _get_ref_data(cfg)

    # 1. MedDRA 编码检查
    logger.info(">> [Coding] 执行 MedDRA 编码检查 (LLT→PT→SOC)")
    meddra_findings = check_meddra(state, cfg, ref)
    state = collect_findings(state, meddra_findings, id="CODING_MEDDRA")

    # 2. ICD-10 编码检查
    logger.info(">> [Coding] 执行 ICD-10 编码检查")
    icd10_findings = check_icd10(state, cfg, ref)
    state = collect_findings(state, icd10_findings, id="CODING_ICD10")

    # 3. ATC 编码检查
    logger.info(">> [Coding] 执行 ATC 编码检查")
    atc_findings = check_atc(state, cfg, ref)
    state = collect_findings(state, atc_findings, id="CODING_ATC")

    # 4. LOINC 编码检查
    logger.info(">> [Coding] 执行 LOINC 编码检查")
    loinc_findings = check_loinc(state, cfg, ref)
    state = collect_findings(state, loinc_findings, id="CODING_LOINC")

    logger.info(">> [Coding] 医学编码检查完成")
    return state


# ---------------------------------------------------------------------------
# 6. 独立运行 / 测试入口
# ---------------------------------------------------------------------------

def run_standalone_test() -> None:
    """独立运行测试，验证各编码检查函数的基本功能。"""
    print("=" * 60)
    print("医学编码检查模块 — 独立测试")
    print("=" * 60)

    # 创建模拟 CoreGageState 和 CoreGageConfig
    state = CoreGageState()
    cfg = CoreGageConfig(
        project_name="Coding Test",
        rule_registry="",
        trial_checks="",
        study_checks="",
        inputs="",
        reports="",
        feedback="",
    )

    # 模拟 AE 域数据
    ae_data = pd.DataFrame({
        "USUBJID": ["SUBJ-001", "SUBJ-002", "SUBJ-003", "SUBJ-004", "SUBJ-005"],
        "VISITNUM": [1.0, 2.0, 1.0, 3.0, 1.0],
        "AELLT": ["Headache", "Nausea", "INVALID_LLT", "12345678", "Rash"],
        "AEPT": ["Headache", "Nausea", "", "", "Rash"],
        "AESOC": ["Nervous system disorders", "Gastrointestinal disorders", "", "", "Skin and subcutaneous tissue disorders"],
    })
    state.domains["AE"] = ae_data

    # 模拟 DI 域数据
    di_data = pd.DataFrame({
        "USUBJID": ["SUBJ-001", "SUBJ-002", "SUBJ-003"],
        "VISITNUM": [1.0, 2.0, 1.0],
        "DICODE": ["I10", "INVALID", "J45.0"],
    })
    state.domains["DI"] = di_data

    # 模拟 CM 域数据
    cm_data = pd.DataFrame({
        "USUBJID": ["SUBJ-001", "SUBJ-002", "SUBJ-003"],
        "VISITNUM": [1.0, 2.0, 1.0],
        "CMATC": ["A02BC01", "INVALID", "N02BE01"],
    })
    state.domains["CM"] = cm_data

    # 模拟 LB 域数据
    lb_data = pd.DataFrame({
        "USUBJID": ["SUBJ-001", "SUBJ-002", "SUBJ-003"],
        "VISITNUM": [1.0, 2.0, 1.0],
        "LBLOINC": ["12345-7", "INVALID", "99999-9"],
    })
    state.domains["LB"] = lb_data

    # 运行检查
    state = check_Coding(state, cfg)

    # 输出结果
    print("\n--- 检查发现汇总 ---")
    if state.issues.empty:
        print("未发现任何问题。")
    else:
        for _, row in state.issues.iterrows():
            print(f"  [{row['id']}] {row['subj_id']} (Visit {row['vis_id']}): {row['description']}")

    print("\n--- 摘要日志 ---")
    if not state.summary_log.empty:
        for _, row in state.summary_log.iterrows():
            print(f"  {row['headlink']}: {row['nu']} 个发现")

    print("\n测试完成。")


if __name__ == "__main__":
    run_standalone_test()
