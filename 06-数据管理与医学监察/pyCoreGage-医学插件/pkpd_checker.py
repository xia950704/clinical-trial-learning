"""
PK/PD 分析检查模块 (pkpd_checker.py)
=====================================
药代动力学/药效学数据检查

检查内容：
1. PK 参数合理性（AUC、Cmax、Tmax、半衰期）
2. PD 参数合理性（效应指标）
3. 时间序列一致性（采样时间）
4. 剂量-浓度关系

Author: pyCoreGage Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger("pyCoreGage")


class PKPDChecker:
    """
    PK/PD 数据检查器
    
    检查药代动力学/药效学数据的合理性和一致性
    """
    
    def __init__(self, state: Any, config: Any):
        """
        初始化 PK/PD 检查器
        
        Args:
            state: CoreGageState 对象
            config: CoreGageConfig 对象
        """
        self.state = state
        self.config = config
        self.findings: List[Dict[str, Any]] = []
        
        # PK 参数正常范围（可配置）
        self.pk_normal_ranges = {
            "AUC": {"min": 0.1, "max": 10000, "unit": "ng·h/mL"},
            "Cmax": {"min": 0.1, "max": 10000, "unit": "ng/mL"},
            "Tmax": {"min": 0, "max": 24, "unit": "h"},
            "t_half": {"min": 0.1, "max": 100, "unit": "h"},
            "CL": {"min": 0.1, "max": 1000, "unit": "L/h"},
            "Vd": {"min": 0.1, "max": 10000, "unit": "L"},
        }
        
        # PD 参数正常范围（可配置）
        self.pd_normal_ranges = {
            "EC50": {"min": 0.01, "max": 1000, "unit": "ng/mL"},
            "Emax": {"min": 0, "max": 100, "unit": "%"},
            "Hill": {"min": 0.1, "max": 10, "unit": "无量纲"},
        }
    
    def check_pk_parameters(self) -> List[Dict[str, Any]]:
        """
        检查 PK 参数合理性
        
        Returns:
            发现列表
        """
        findings = []
        
        # 从 state.domains 获取 PK 数据
        pk_data = self._get_domain_data("PK")
        if not pk_data:
            logger.warning("PK 数据域不存在")
            return findings
        
        for record in pk_data:
            subj_id = record.get("SUBJID", "N/A")
            
            # 检查 AUC
            auc = self._safe_float(record.get("AUC"))
            if auc is not None:
                if not self._in_range(auc, self.pk_normal_ranges["AUC"]):
                    findings.append({
                        "check_id": "PK_AUC_RANGE",
                        "severity": "MAJOR",
                        "description": f"AUC 超出正常范围: {auc} ng·h/mL (正常: {self.pk_normal_ranges['AUC']['min']}-{self.pk_normal_ranges['AUC']['max']})",
                        "subj_id": subj_id,
                        "vis_id": record.get("VISIT", "N/A"),
                        "record": record
                    })
            
            # 检查 Cmax
            cmax = self._safe_float(record.get("Cmax"))
            if cmax is not None:
                if not self._in_range(cmax, self.pk_normal_ranges["Cmax"]):
                    findings.append({
                        "check_id": "PK_CMAX_RANGE",
                        "severity": "MAJOR",
                        "description": f"Cmax 超出正常范围: {cmax} ng/mL (正常: {self.pk_normal_ranges['Cmax']['min']}-{self.pk_normal_ranges['Cmax']['max']})",
                        "subj_id": subj_id,
                        "vis_id": record.get("VISIT", "N/A"),
                        "record": record
                    })
            
            # 检查 Tmax
            tmax = self._safe_float(record.get("Tmax"))
            if tmax is not None:
                if not self._in_range(tmax, self.pk_normal_ranges["Tmax"]):
                    findings.append({
                        "check_id": "PK_TMAX_RANGE",
                        "severity": "MINOR",
                        "description": f"Tmax 超出正常范围: {tmax} h (正常: {self.pk_normal_ranges['Tmax']['min']}-{self.pk_normal_ranges['Tmax']['max']})",
                        "subj_id": subj_id,
                        "vis_id": record.get("VISIT", "N/A"),
                        "record": record
                    })
            
            # 检查半衰期
            t_half = self._safe_float(record.get("t_half"))
            if t_half is not None:
                if not self._in_range(t_half, self.pk_normal_ranges["t_half"]):
                    findings.append({
                        "check_id": "PK_THALF_RANGE",
                        "severity": "MINOR",
                        "description": f"半衰期超出正常范围: {t_half} h (正常: {self.pk_normal_ranges['t_half']['min']}-{self.pk_normal_ranges['t_half']['max']})",
                        "subj_id": subj_id,
                        "vis_id": record.get("VISIT", "N/A"),
                        "record": record
                    })
        
        return findings
    
    def check_pd_parameters(self) -> List[Dict[str, Any]]:
        """
        检查 PD 参数合理性
        
        Returns:
            发现列表
        """
        findings = []
        
        # 从 state.domains 获取 PD 数据
        pd_data = self._get_domain_data("PD")
        if not pd_data:
            logger.warning("PD 数据域不存在")
            return findings
        
        for record in pd_data:
            subj_id = record.get("SUBJID", "N/A")
            
            # 检查 EC50
            ec50 = self._safe_float(record.get("EC50"))
            if ec50 is not None:
                if not self._in_range(ec50, self.pd_normal_ranges["EC50"]):
                    findings.append({
                        "check_id": "PD_EC50_RANGE",
                        "severity": "MINOR",
                        "description": f"EC50 超出正常范围: {ec50} ng/mL (正常: {self.pd_normal_ranges['EC50']['min']}-{self.pd_normal_ranges['EC50']['max']})",
                        "subj_id": subj_id,
                        "vis_id": record.get("VISIT", "N/A"),
                        "record": record
                    })
            
            # 检查 Emax
            emax = self._safe_float(record.get("Emax"))
            if emax is not None:
                if not self._in_range(emax, self.pd_normal_ranges["Emax"]):
                    findings.append({
                        "check_id": "PD_EMAX_RANGE",
                        "severity": "MINOR",
                        "description": f"Emax 超出正常范围: {emax}% (正常: {self.pd_normal_ranges['Emax']['min']}-{self.pd_normal_ranges['Emax']['max']}%)",
                        "subj_id": subj_id,
                        "vis_id": record.get("VISIT", "N/A"),
                        "record": record
                    })
        
        return findings
    
    def check_sampling_time(self) -> List[Dict[str, Any]]:
        """
        检查采样时间序列一致性
        
        Returns:
            发现列表
        """
        findings = []
        
        # 从 state.domains 获取 PK 数据
        pk_data = self._get_domain_data("PK")
        if not pk_data:
            logger.warning("PK 数据域不存在")
            return findings
        
        # 按受试者分组
        subjects = {}
        for record in pk_data:
            subj_id = record.get("SUBJID", "N/A")
            if subj_id not in subjects:
                subjects[subj_id] = []
            subjects[subj_id].append(record)
        
        # 检查每个受试者的采样时间
        for subj_id, records in subjects.items():
            # 按时间排序
            records.sort(key=lambda x: x.get("SAMPLING_TIME", ""))
            
            # 检查时间是否递增
            for i in range(1, len(records)):
                prev_time = records[i-1].get("SAMPLING_TIME", "")
                curr_time = records[i].get("SAMPLING_TIME", "")
                
                if prev_time and curr_time and prev_time > curr_time:
                    findings.append({
                        "check_id": "PK_SAMPLING_TIME",
                        "severity": "MAJOR",
                        "description": f"采样时间倒序: {prev_time} > {curr_time}",
                        "subj_id": subj_id,
                        "vis_id": records[i].get("VISIT", "N/A"),
                        "record": records[i]
                    })
        
        return findings
    
    def check_dose_concentration(self) -> List[Dict[str, Any]]:
        """
        检查剂量-浓度关系合理性
        
        Returns:
            发现列表
        """
        findings = []
        
        # 从 state.domains 获取 PK 和 EX 数据
        pk_data = self._get_domain_data("PK")
        ex_data = self._get_domain_data("EX")
        
        if not pk_data or not ex_data:
            logger.warning("PK 或 EX 数据域不存在")
            return findings
        
        # 简化检查：确保有给药记录才有 PK 数据
        dosed_subjects = set(record.get("SUBJID", "") for record in ex_data)
        pk_subjects = set(record.get("SUBJID", "") for record in pk_data)
        
        # 检查有 PK 数据但无给药记录的受试者
        for subj_id in pk_subjects - dosed_subjects:
            findings.append({
                "check_id": "PK_DOSE_CONCENTRATION",
                "severity": "MAJOR",
                "description": f"有 PK 数据但无给药记录",
                "subj_id": subj_id,
                "vis_id": "N/A",
                "record": {}
            })
        
        return findings
    
    def _get_domain_data(self, domain: str) -> List[Dict[str, Any]]:
        """
        获取指定域的数据
        
        Args:
            domain: 域名称（PK、PD、EX 等）
        
        Returns:
            数据列表
        """
        if hasattr(self.state, 'domains') and self.state.domains:
            domain_key = domain.lower()
            if domain_key in self.state.domains:
                return self.state.domains[domain_key]
        
        return []
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """
        安全转换为浮点数
        
        Args:
            value: 原始值
        
        Returns:
            浮点数或 None
        """
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _in_range(self, value: float, range_dict: Dict[str, Any]) -> bool:
        """
        检查值是否在范围内
        
        Args:
            value: 值
            range_dict: 范围字典（包含 min、max）
        
        Returns:
            是否在范围内
        """
        return range_dict["min"] <= value <= range_dict["max"]


def check_PKPD(state: Any, cfg: Any) -> Any:
    """
    PK/PD 检查入口函数
    
    Args:
        state: CoreGageState 对象
        cfg: CoreGageConfig 对象
    
    Returns:
        更新后的 state 对象
    """
    checker = PKPDChecker(state, cfg)
    
    # 执行所有检查
    findings = []
    findings.extend(checker.check_pk_parameters())
    findings.extend(checker.check_pd_parameters())
    findings.extend(checker.check_sampling_time())
    findings.extend(checker.check_dose_concentration())
    
    # 收集发现
    if findings:
        from core_data import collect_findings
        collect_findings(state, findings, id="PKPD")
    
    return state
