"""
test_genetic.py — 基因检测检查功能测试脚本
============================================
测试 genetic_checker.py 的基因检测数据检查功能：
  1. 变异注释完整性
  2. 基因型格式正确性
  3. 等位基因频率合理性
  4. 基因-药物关联（如 CYP2D6 与药物代谢）
  5. 罕见变异标记

使用合成数据模拟临床试验基因检测结果。
"""

from __future__ import annotations

import csv
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

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
logger = logging.getLogger("test_genetic")


# ═══════════════════════════════════════════════════════════
# 1. 数据加载
# ═══════════════════════════════════════════════════════════


def load_genetic_data(csv_path: str) -> List[Dict[str, Any]]:
    """
    从 CSV 文件加载基因检测数据。

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
                "gene": row["gene"],
                "variant": row["variant"],
                "genotype": row["genotype"],
                "allele_frequency": float(row["allele_frequency"]),
                "population": row["population"],
            }
            records.append(record)
    return records


def load_genetic_rules(yaml_path: str) -> Dict[str, Any]:
    """
    加载基因检测规则配置（简化 YAML 解析）。

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

        indent = len(line) - len(line.lstrip())

        if indent == 0:
            key = stripped.split(":")[0].strip()
            current_section = key
            current_subsection = None
            current_item = None
            if key not in rules:
                rules[key] = {}
        elif indent == 2:
            if ":" in stripped:
                key = stripped.split(":", 1)[0].strip()
                val = stripped.split(":", 1)[1].strip()
                current_subsection = key
                current_item = key  # Set current_item for list items at indent 4
                if current_section and current_section not in rules:
                    rules[current_section] = {}
                if val:
                    # Inline value at indent 2 (e.g., "min: 0.0")
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            val = val.strip('"').strip("'")
                    rules[current_section][key] = val
                else:
                    # Section header at indent 2
                    if current_subsection not in rules.get(current_section, {}):
                        rules[current_section][current_subsection] = {}
        elif indent == 4:
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
                else:
                    val = {}
                current_item = key
                if current_section and current_subsection:
                    if current_subsection not in rules.get(current_section, {}):
                        rules[current_section][current_subsection] = {}
                    rules[current_section][current_subsection][key] = val
            else:
                val = stripped.lstrip("- ").strip().strip('"').strip("'")
                if current_section and current_subsection and current_item:
                    if not isinstance(rules.get(current_section, {}).get(current_subsection, {}).get(current_item), list):
                        rules[current_section][current_subsection][current_item] = []
                    rules[current_section][current_subsection][current_item].append(val)
        elif indent == 6:
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
            else:
                # List item at indent 6 (e.g., "- 美托洛尔")
                val = stripped.lstrip("- ").strip().strip('"').strip("'")
                if current_section and current_subsection and current_item:
                    target = rules.get(current_section, {}).get(current_subsection, {}).get(current_item)
                    if not isinstance(target, list):
                        rules[current_section][current_subsection][current_item] = []
                        target = rules[current_section][current_subsection][current_item]
                    target.append(val)
        elif indent == 8:
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
                    item_dict = rules.get(current_section, {}).get(current_subsection, {}).get(current_item, {})
                    if isinstance(item_dict, dict):
                        item_dict[key] = val

    return rules


# ═══════════════════════════════════════════════════════════
# 2. 自定义基因检测检查
# ═══════════════════════════════════════════════════════════


def check_variant_annotation(
    genetic_data: List[Dict[str, Any]], rules: Dict[str, Any]
) -> List[CoreGageFinding]:
    """
    检查基因变异注释完整性。

    Args:
        genetic_data: 基因检测数据
        rules: 规则配置

    Returns:
        发现列表
    """
    findings: List[CoreGageFinding] = []
    required_fields = ["subject_id", "gene", "variant", "genotype"]

    for record in genetic_data:
        subj_id = record.get("subject_id", "N/A")
        for field in required_fields:
            if not record.get(field):
                findings.append(CoreGageFinding(
                    category=CheckCategory.INTEGRITY,
                    severity=Severity.HIGH,
                    source="genetic_annotation",
                    subject_id=subj_id,
                    visit_id="N/A",
                    message=f"基因变异注释缺失: {field}",
                    details={
                        "check_id": "GENETIC_ANNOTATION",
                        "missing_field": field,
                        "record": record,
                    },
                    status=CheckStatus.PASSED,
                ))

    return findings


def check_genotype_format(
    genetic_data: List[Dict[str, Any]], rules: Dict[str, Any]
) -> List[CoreGageFinding]:
    """
    检查基因型格式正确性。

    支持的格式：
    - 纯合子: AA, GG, TT, CC
    - 杂合子: A/G, C/T
    - 星号命名法: 1/*4, *4/*4, *2/*2

    Args:
        genetic_data: 基因检测数据
        rules: 规则配置

    Returns:
        发现列表
    """
    findings: List[CoreGageFinding] = []

    # 定义基因型格式正则
    patterns = [
        re.compile(r"^[A-Z]{2}$"),              # 纯合子: AA, GG
        re.compile(r"^[A-Z]/[A-Z]$"),            # 杂合子: A/G, C/T
        re.compile(r"^\d+/\*\d+$"),              # 星号命名法: 1/*4
        re.compile(r"^\*\d+/\*\d+$"),            # 双星号: *4/*4
        re.compile(r"^-\d+[A-Z]/[A-Z]$"),        # 位置命名法: -1639G/A
        re.compile(r"^-\d+[A-Z]/-\d+[A-Z]$"),    # 双位置: -1639G/-1639A
    ]

    for record in genetic_data:
        subj_id = record.get("subject_id", "N/A")
        genotype = record.get("genotype", "")

        if genotype:
            is_valid = any(p.match(genotype) for p in patterns)
            if not is_valid:
                findings.append(CoreGageFinding(
                    category=CheckCategory.CONSISTENCY,
                    severity=Severity.LOW,
                    source="genetic_genotype",
                    subject_id=subj_id,
                    visit_id="N/A",
                    message=f"基因型格式异常: {genotype} (基因: {record.get('gene', 'N/A')})",
                    details={
                        "check_id": "GENETIC_GENOTYPE",
                        "genotype": genotype,
                        "gene": record.get("gene", ""),
                    },
                    status=CheckStatus.PASSED,
                ))

    return findings


def check_allele_frequency(
    genetic_data: List[Dict[str, Any]], rules: Dict[str, Any]
) -> List[CoreGageFinding]:
    """
    检查等位基因频率合理性。

    Args:
        genetic_data: 基因检测数据
        rules: 规则配置

    Returns:
        发现列表
    """
    findings: List[CoreGageFinding] = []
    af_rules = rules.get("allele_frequency", {"min": 0.0, "max": 1.0})
    min_af = af_rules.get("min", 0.0)
    max_af = af_rules.get("max", 1.0)

    for record in genetic_data:
        subj_id = record.get("subject_id", "N/A")
        af = record.get("allele_frequency")

        if af is not None:
            if af < min_af or af > max_af:
                findings.append(CoreGageFinding(
                    category=CheckCategory.CONSISTENCY,
                    severity=Severity.HIGH,
                    source="genetic_af",
                    subject_id=subj_id,
                    visit_id="N/A",
                    message=f"等位基因频率异常: {af} (正常: {min_af}-{max_af})",
                    details={
                        "check_id": "GENETIC_AF",
                        "allele_frequency": af,
                        "min": min_af,
                        "max": max_af,
                        "gene": record.get("gene", ""),
                    },
                    status=CheckStatus.PASSED,
                ))

    return findings


def check_gene_drug_association(
    genetic_data: List[Dict[str, Any]], rules: Dict[str, Any]
) -> List[CoreGageFinding]:
    """
    检查基因-药物关联。

    根据基因型判断代谢表型（慢代谢者、中间代谢者、快代谢者），
    标记需要剂量调整的情况。

    Args:
        genetic_data: 基因检测数据
        rules: 规则配置

    Returns:
        发现列表
    """
    findings: List[CoreGageFinding] = []
    gene_drug_map = rules.get("gene_drug_associations", {})

    for record in genetic_data:
        subj_id = record.get("subject_id", "N/A")
        gene = record.get("gene", "")
        genotype = record.get("genotype", "")

        if gene not in gene_drug_map:
            continue

        gene_info = gene_drug_map[gene]
        phenotypes = gene_info.get("metabolism_phenotypes", {})
        drugs = gene_info.get("drugs", [])

        # 判断代谢表型
        phenotype = "unknown"
        for pheno_name, geno_list in phenotypes.items():
            if genotype in geno_list:
                phenotype = pheno_name
                break

        # 标记慢代谢者
        if phenotype == "poor":
            findings.append(CoreGageFinding(
                category=CheckCategory.CONSISTENCY,
                severity=Severity.HIGH,
                source="genetic_gene_drug",
                subject_id=subj_id,
                visit_id="N/A",
                message=f"{gene} 慢代谢者 ({genotype})，相关药物需剂量调整: {', '.join(drugs[:3])}",
                details={
                    "check_id": "GENETIC_Poor_METABOLIZER",
                    "gene": gene,
                    "genotype": genotype,
                    "phenotype": phenotype,
                    "related_drugs": drugs,
                },
                status=CheckStatus.PASSED,
            ))
        elif phenotype == "intermediate":
            findings.append(CoreGageFinding(
                category=CheckCategory.CONSISTENCY,
                severity=Severity.MEDIUM,
                source="genetic_gene_drug",
                subject_id=subj_id,
                visit_id="N/A",
                message=f"{gene} 中间代谢者 ({genotype})，相关药物需关注: {', '.join(drugs[:3])}",
                details={
                    "check_id": "GENETIC_INTERMEDIATE_METABOLIZER",
                    "gene": gene,
                    "genotype": genotype,
                    "phenotype": phenotype,
                    "related_drugs": drugs,
                },
                status=CheckStatus.PASSED,
            ))
        elif phenotype == "ultra_rapid":
            findings.append(CoreGageFinding(
                category=CheckCategory.CONSISTENCY,
                severity=Severity.HIGH,
                source="genetic_gene_drug",
                subject_id=subj_id,
                visit_id="N/A",
                message=f"{gene} 超快代谢者 ({genotype})，相关药物可能无效: {', '.join(drugs[:3])}",
                details={
                    "check_id": "GENETIC_ULTRA_RAPID_METABOLIZER",
                    "gene": gene,
                    "genotype": genotype,
                    "phenotype": phenotype,
                    "related_drugs": drugs,
                },
                status=CheckStatus.PASSED,
            ))

    return findings


def check_rare_variants(
    genetic_data: List[Dict[str, Any]], rules: Dict[str, Any]
) -> List[CoreGageFinding]:
    """
    标记罕见变异。

    Args:
        genetic_data: 基因检测数据
        rules: 规则配置

    Returns:
        发现列表
    """
    findings: List[CoreGageFinding] = []
    rare_rules = rules.get("rare_variant_rules", {})
    threshold = rare_rules.get("frequency_threshold", 0.01)

    for record in genetic_data:
        subj_id = record.get("subject_id", "N/A")
        af = record.get("allele_frequency", 1.0)
        gene = record.get("gene", "")
        variant = record.get("variant", "")

        if af < threshold:
            findings.append(CoreGageFinding(
                category=CheckCategory.CONSISTENCY,
                severity=Severity.LOW,
                source="genetic_rare_variant",
                subject_id=subj_id,
                visit_id="N/A",
                message=f"罕见变异标记: {gene} {variant} "
                        f"(等位基因频率: {af} < {threshold})",
                details={
                    "check_id": "GENETIC_RARE_VARIANT",
                    "gene": gene,
                    "variant": variant,
                    "allele_frequency": af,
                    "threshold": threshold,
                    "requires_validation": rare_rules.get("requires_validation", True),
                },
                status=CheckStatus.PASSED,
            ))

    return findings


def check_pharmacogene_coverage(
    genetic_data: List[Dict[str, Any]], rules: Dict[str, Any]
) -> List[CoreGageFinding]:
    """
    检查药物代谢基因覆盖度。

    Args:
        genetic_data: 基因检测数据
        rules: 规则配置

    Returns:
        发现列表
    """
    findings: List[CoreGageFinding] = []
    pharmacogenes = rules.get("pharmacogenes", [])

    detected_genes = set(record.get("gene", "") for record in genetic_data)

    for gene in pharmacogenes:
        if gene not in detected_genes:
            findings.append(CoreGageFinding(
                category=CheckCategory.CONSISTENCY,
                severity=Severity.INFO,
                source="genetic_coverage",
                subject_id="ALL",
                visit_id="N/A",
                message=f"未检测常见药物代谢基因: {gene}",
                details={
                    "check_id": "GENETIC_COVERAGE",
                    "missing_gene": gene,
                },
                status=CheckStatus.PASSED,
            ))

    return findings


# ═══════════════════════════════════════════════════════════
# 3. 主测试函数
# ═══════════════════════════════════════════════════════════


def run_genetic_test() -> List[CoreGageFinding]:
    """
    运行完整的基因检测测试。

    Returns:
        发现列表
    """
    print("=" * 70)
    print("🧬 pyCoreGage 基因检测检查功能测试")
    print("=" * 70)

    # 加载数据
    data_dir = Path(__file__).parent / "data"
    rules_dir = Path(__file__).parent / "rules"

    print("\n📊 加载基因检测数据...")
    genetic_data = load_genetic_data(str(data_dir / "genetic_data.csv"))
    print(f"   总记录数: {len(genetic_data)}")
    print(f"   受试者数: {len(set(r['subject_id'] for r in genetic_data))}")
    print(f"   检测基因: {sorted(set(r['gene'] for r in genetic_data))}")
    print(f"   人群: {sorted(set(r['population'] for r in genetic_data))}")

    # 加载规则
    print("\n📋 加载基因检测规则...")
    rules = load_genetic_rules(str(rules_dir / "genetic_rules.yaml"))
    print(f"   规则节数: {len(rules)}")

    # 展示数据摘要
    print("\n" + "-" * 70)
    print("📊 基因检测数据摘要")
    print("-" * 70)
    print(f"{'受试者':>8} {'基因':>10} {'变异':>10} {'基因型':>12} {'AF':>8} {'人群':>12}")
    print("-" * 70)
    for record in genetic_data:
        print(f"{record['subject_id']:>8} {record['gene']:>10} "
              f"{record['variant']:>10} {record['genotype']:>12} "
              f"{record['allele_frequency']:>8.4f} {record['population']:>12}")

    # 运行各项检查
    print("\n🔍 运行检查...")

    all_findings: List[CoreGageFinding] = []

    # 1. 变异注释完整性
    print("  [1/6] 变异注释完整性检查...")
    ann_findings = check_variant_annotation(genetic_data, rules)
    all_findings.extend(ann_findings)
    print(f"       发现 {len(ann_findings)} 个问题")

    # 2. 基因型格式检查
    print("  [2/6] 基因型格式检查...")
    geno_findings = check_genotype_format(genetic_data, rules)
    all_findings.extend(geno_findings)
    print(f"       发现 {len(geno_findings)} 个问题")

    # 3. 等位基因频率检查
    print("  [3/6] 等位基因频率合理性检查...")
    af_findings = check_allele_frequency(genetic_data, rules)
    all_findings.extend(af_findings)
    print(f"       发现 {len(af_findings)} 个问题")

    # 4. 基因-药物关联检查
    print("  [4/6] 基因-药物关联检查...")
    gd_findings = check_gene_drug_association(genetic_data, rules)
    all_findings.extend(gd_findings)
    print(f"       发现 {len(gd_findings)} 个问题")

    # 5. 罕见变异标记
    print("  [5/6] 罕见变异标记检查...")
    rare_findings = check_rare_variants(genetic_data, rules)
    all_findings.extend(rare_findings)
    print(f"       发现 {len(rare_findings)} 个问题")

    # 6. 药物代谢基因覆盖度
    print("  [6/6] 药物代谢基因覆盖度检查...")
    cov_findings = check_pharmacogene_coverage(genetic_data, rules)
    all_findings.extend(cov_findings)
    print(f"       发现 {len(cov_findings)} 个问题")

    # 运行现有 genetic_checker.py
    print("  [7/7] 运行现有 genetic_checker.py...")
    try:
        class MockState:
            def __init__(self, domains: Dict[str, Any]):
                self.domains = domains

        # 将基因数据转换为 domains 格式
        domains = {"genetic": genetic_data}
        mock_state = MockState(domains)
        mock_config = CoreGageConfig()

        from genetic_checker import GeneticChecker
        checker = GeneticChecker(mock_state, mock_config)
        existing_findings = []
        existing_findings.extend(checker.check_variant_annotation())
        existing_findings.extend(checker.check_genotype_format())
        existing_findings.extend(checker.check_allele_frequency())
        existing_findings.extend(checker.check_gene_drug_association())
        existing_findings.extend(checker.check_pharmacogene_coverage())
        print(f"       现有检查器发现 {len(existing_findings)} 个问题")

        for ef in existing_findings:
            all_findings.append(CoreGageFinding(
                category=CheckCategory.CONSISTENCY,
                severity=Severity(ef.get("severity", "MEDIUM").lower()),
                source="genetic_existing",
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
    output_path = Path(__file__).parent / "test_genetic_output.json"
    result_data = {
        "total_findings": total,
        "by_source": {},
        "by_severity": sev_count,
        "genetic_data_summary": {
            "total_records": len(genetic_data),
            "subjects": sorted(set(r["subject_id"] for r in genetic_data)),
            "genes": sorted(set(r["gene"] for r in genetic_data)),
            "populations": sorted(set(r["population"] for r in genetic_data)),
        },
        "findings": [],
    }
    for f in all_findings:
        result_data["findings"].append(f.to_dict())
        src = f.source
        result_data["by_source"][src] = result_data["by_source"].get(src, 0) + 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n💾 详细结果已保存到: {output_path}")

    print("\n✅ 基因检测测试完成！")
    return all_findings


# ═══════════════════════════════════════════════════════════
# 4. 单元测试
# ═══════════════════════════════════════════════════════════


def test_genotype_format_check() -> None:
    """测试基因型格式检查。"""
    print("\n🧪 单元测试: 基因型格式检查")
    print("-" * 40)

    # 有效格式
    valid_genotypes = [
        ("AA", "纯合子"),
        ("A/G", "杂合子"),
        ("1/*4", "星号命名法"),
        ("*4/*4", "双星号"),
        ("-1639G/A", "位置命名法"),
    ]
    for geno, desc in valid_genotypes:
        result = check_genotype_format([
            {"subject_id": "S001", "gene": "CYP2D6", "variant": "*4",
             "genotype": geno, "allele_frequency": 0.02, "population": "East_Asian"}
        ], {})
        if result:
            print(f"  ❌ {desc} ({geno}) 被错误标记为异常")
        else:
            print(f"  ✅ {desc} ({geno}) 格式正确")

    # 无效格式
    invalid_genotypes = [
        "A-G",
        "1-4",
        "ABC",
        "A/B/C",
    ]
    for geno in invalid_genotypes:
        result = check_genotype_format([
            {"subject_id": "S001", "gene": "CYP2D6", "variant": "*4",
             "genotype": geno, "allele_frequency": 0.02, "population": "East_Asian"}
        ], {})
        if result:
            print(f"  ✅ 无效格式 ({geno}) 被正确标记")
        else:
            print(f"  ❌ 无效格式 ({geno}) 未被标记")

    print("  ✅ 基因型格式检查测试完成")


def test_allele_frequency_check() -> None:
    """测试等位基因频率检查。"""
    print("\n🧪 单元测试: 等位基因频率检查")
    print("-" * 40)

    # 正常频率
    result = check_allele_frequency([
        {"subject_id": "S001", "gene": "CYP2D6", "variant": "*4",
         "genotype": "1/*4", "allele_frequency": 0.02, "population": "East_Asian"}
    ], {})
    assert len(result) == 0, "正常频率不应被标记"
    print("  ✅ 正常频率 (0.02) 通过")

    # 异常频率 (>1.0)
    result = check_allele_frequency([
        {"subject_id": "S001", "gene": "CYP2D6", "variant": "*4",
         "genotype": "1/*4", "allele_frequency": 1.5, "population": "East_Asian"}
    ], {})
    assert len(result) == 1, "异常频率应被标记"
    print("  ✅ 异常频率 (1.5) 被正确标记")

    # 异常频率 (<0.0)
    result = check_allele_frequency([
        {"subject_id": "S001", "gene": "CYP2D6", "variant": "*4",
         "genotype": "1/*4", "allele_frequency": -0.1, "population": "East_Asian"}
    ], {})
    assert len(result) == 1, "负频率应被标记"
    print("  ✅ 负频率 (-0.1) 被正确标记")

    print("  ✅ 等位基因频率检查测试完成")


def test_rare_variant_check() -> None:
    """测试罕见变异标记。"""
    print("\n🧪 单元测试: 罕见变异标记")
    print("-" * 40)

    rules = {"rare_variant_rules": {"frequency_threshold": 0.01}}

    # 罕见变异
    result = check_rare_variants([
        {"subject_id": "S001", "gene": "DPYD", "variant": "*2",
         "genotype": "1/*2", "allele_frequency": 0.005, "population": "East_Asian"}
    ], rules)
    assert len(result) == 1
    print(f"  ✅ 罕见变异 (AF=0.005) 被标记: {result[0].message}")

    # 常见变异
    result = check_rare_variants([
        {"subject_id": "S001", "gene": "CYP2D6", "variant": "*1",
         "genotype": "1/*1", "allele_frequency": 0.65, "population": "East_Asian"}
    ], rules)
    assert len(result) == 0
    print("  ✅ 常见变异 (AF=0.65) 未被标记")

    print("  ✅ 罕见变异标记测试完成")


if __name__ == "__main__":
    # 运行单元测试
    test_genotype_format_check()
    test_allele_frequency_check()
    test_rare_variant_check()

    # 运行完整测试
    print("\n" + "=" * 70)
    findings = run_genetic_test()
    print("=" * 70)
