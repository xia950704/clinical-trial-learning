"""
基因检测检查模块 (genetic_checker.py)
=====================================
基因检测数据检查

检查内容：
1. 基因变异注释完整性
2. 基因型格式检查
3. 等位基因频率合理性
4. 基因-药物关联检查

Author: pyCoreGage Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("pyCoreGage")


class GeneticChecker:
    """
    基因检测数据检查器
    
    检查基因检测数据的合理性和完整性
    """
    
    def __init__(self, state: Any, config: Any):
        """
        初始化基因检测检查器
        
        Args:
            state: CoreGageState 对象
            config: CoreGageConfig 对象
        """
        self.state = state
        self.config = config
        self.findings: List[Dict[str, Any]] = []
        
        # 常见药物代谢基因（可配置）
        self.pharmacogenes = [
            "CYP2D6", "CYP2C19", "CYP2C9", "CYP3A4", "CYP3A5",
            "CYP1A2", "CYP2B6", "CYP2A6", "CYP2E1", "CYP4F2",
            "SLCO1B1", "ABCB1", "TPMT", "DPYD", "UGT1A1",
            "VKORC1", "G6PD", "NAT2", "COMT", "OPRM1"
        ]
        
        # 基因型格式正则
        self.genotype_pattern = re.compile(r'^[A-Z]{2}$')  # 如 AA, AG, GG
        self.diploid_pattern = re.compile(r'^[A-Z]/[A-Z]$')  # 如 A/G, G/G
        
        # 等位基因频率正常范围
        self.af_normal_range = {"min": 0.0, "max": 1.0}
    
    def check_variant_annotation(self) -> List[Dict[str, Any]]:
        """
        检查基因变异注释完整性
        
        Returns:
            发现列表
        """
        findings = []
        
        # 从 state.domains 获取基因数据
        genetic_data = self._get_domain_data("GENETIC")
        if not genetic_data:
            logger.warning("基因数据域不存在")
            return findings
        
        required_fields = ["SUBJID", "GENE", "VARIANT", "GENOTYPE"]
        
        for record in genetic_data:
            subj_id = record.get("SUBJID", "N/A")
            
            # 检查必填字段
            for field in required_fields:
                if not record.get(field):
                    findings.append({
                        "check_id": "GENETIC_ANNOTATION",
                        "severity": "MAJOR",
                        "description": f"基因变异注释缺失: {field}",
                        "subj_id": subj_id,
                        "vis_id": "N/A",
                        "record": record
                    })
        
        return findings
    
    def check_genotype_format(self) -> List[Dict[str, Any]]:
        """
        检查基因型格式
        
        Returns:
            发现列表
        """
        findings = []
        
        # 从 state.domains 获取基因数据
        genetic_data = self._get_domain_data("GENETIC")
        if not genetic_data:
            logger.warning("基因数据域不存在")
            return findings
        
        for record in genetic_data:
            subj_id = record.get("SUBJID", "N/A")
            genotype = record.get("GENOTYPE", "")
            
            if genotype:
                # 检查基因型格式
                if not (self.genotype_pattern.match(genotype) or 
                       self.diploid_pattern.match(genotype)):
                    findings.append({
                        "check_id": "GENETIC_GENOTYPE",
                        "severity": "MINOR",
                        "description": f"基因型格式异常: {genotype}",
                        "subj_id": subj_id,
                        "vis_id": "N/A",
                        "record": record
                    })
        
        return findings
    
    def check_allele_frequency(self) -> List[Dict[str, Any]]:
        """
        检查等位基因频率合理性
        
        Returns:
            发现列表
        """
        findings = []
        
        # 从 state.domains 获取基因数据
        genetic_data = self._get_domain_data("GENETIC")
        if not genetic_data:
            logger.warning("基因数据域不存在")
            return findings
        
        for record in genetic_data:
            subj_id = record.get("SUBJID", "N/A")
            af = self._safe_float(record.get("AF"))
            
            if af is not None:
                if not self._in_range(af, self.af_normal_range):
                    findings.append({
                        "check_id": "GENETIC_AF",
                        "severity": "MAJOR",
                        "description": f"等位基因频率异常: {af} (正常: 0-1)",
                        "subj_id": subj_id,
                        "vis_id": "N/A",
                        "record": record
                    })
        
        return findings
    
    def check_gene_drug_association(self) -> List[Dict[str, Any]]:
        """
        检查基因-药物关联
        
        Returns:
            发现列表
        """
        findings = []
        
        # 从 state.domains 获取基因数据和用药数据
        genetic_data = self._get_domain_data("GENETIC")
        cm_data = self._get_domain_data("CM")
        
        if not genetic_data or not cm_data:
            logger.warning("基因或用药数据域不存在")
            return findings
        
        # 基因-药物关联映射（简化示例）
        gene_drug_map = {
            "CYP2D6": ["美托洛尔", "氟西汀", "帕罗西汀"],
            "CYP2C19": ["氯吡格雷", "奥美拉唑", "兰索拉唑"],
            "CYP2C9": ["华法林", "苯妥英", "甲苯磺丁脲"],
            "TPMT": ["硫唑嘌呤", "6-巯基嘌呤"],
            "DPYD": ["氟尿嘧啶", "卡培他滨"],
            "VKORC1": ["华法林"],
            "UGT1A1": ["伊立替康"],
        }
        
        # 检查有基因检测但无相关药物的受试者
        for record in genetic_data:
            subj_id = record.get("SUBJID", "N/A")
            gene = record.get("GENE", "")
            
            if gene in gene_drug_map:
                # 检查该受试者是否有相关药物
                related_drugs = gene_drug_map[gene]
                has_related_drug = False
                
                for cm_record in cm_data:
                    if cm_record.get("SUBJID") == subj_id:
                        drug_name = cm_record.get("CMNAME", "")
                        if any(drug in drug_name for drug in related_drugs):
                            has_related_drug = True
                            break
                
                if not has_related_drug:
                    findings.append({
                        "check_id": "GENETIC_GENE_DRUG",
                        "severity": "MINOR",
                        "description": f"有 {gene} 基因检测但无相关药物使用记录",
                        "subj_id": subj_id,
                        "vis_id": "N/A",
                        "record": record
                    })
        
        return findings
    
    def check_pharmacogene_coverage(self) -> List[Dict[str, Any]]:
        """
        检查药物代谢基因覆盖度
        
        Returns:
            发现列表
        """
        findings = []
        
        # 从 state.domains 获取基因数据
        genetic_data = self._get_domain_data("GENETIC")
        if not genetic_data:
            logger.warning("基因数据域不存在")
            return findings
        
        # 统计检测的基因
        detected_genes = set(record.get("GENE", "") for record in genetic_data)
        
        # 检查常见药物代谢基因是否被检测
        for gene in self.pharmacogenes:
            if gene not in detected_genes:
                findings.append({
                    "check_id": "GENETIC_COVERAGE",
                    "severity": "INFO",
                    "description": f"未检测常见药物代谢基因: {gene}",
                    "subj_id": "ALL",
                    "vis_id": "N/A",
                    "record": {}
                })
        
        return findings
    
    def _get_domain_data(self, domain: str) -> List[Dict[str, Any]]:
        """
        获取指定域的数据
        
        Args:
            domain: 域名称（GENETIC、CM 等）
        
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


def check_Genetic(state: Any, cfg: Any) -> Any:
    """
    基因检测检查入口函数
    
    Args:
        state: CoreGageState 对象
        cfg: CoreGageConfig 对象
    
    Returns:
        更新后的 state 对象
    """
    checker = GeneticChecker(state, cfg)
    
    # 执行所有检查
    findings = []
    findings.extend(checker.check_variant_annotation())
    findings.extend(checker.check_genotype_format())
    findings.extend(checker.check_allele_frequency())
    findings.extend(checker.check_gene_drug_association())
    findings.extend(checker.check_pharmacogene_coverage())
    
    # 收集发现
    if findings:
        from core_data import collect_findings
        collect_findings(state, findings, id="GENETIC")
    
    return state
