"""
test_lab_trends.py — 实验室趋势检查功能测试脚本
=================================================
测试 safety_checker.py 中新增的 L1→L3 实验室趋势检查功能：
  L1: _check_lab_trends_general() — 通用趋势检查
  L2: _check_lab_hepatic_toxicity() — 肝毒性检查 (Hy's Law + R-ratio)
  L3: _check_lab_statistical_outliers() — 统计异常值检测 (IQR法)

使用合成数据模拟临床试验实验室结果，包含 visit 信息。
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core_data import (
    CoreGageConfig,
    CoreGageState,
    CoreGageFinding,
    DataSource,
    Severity,
)
from safety_checker import SafetyChecker

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("test_lab_trends")


# ═══════════════════════════════════════════════════════════
# 1. 合成数据生成
# ═══════════════════════════════════════════════════════════

def generate_synthetic_lab_data() -> List[Dict[str, Any]]:
    """
    生成合成实验室数据，包含 visit 信息。
    
    数据结构:
      - subject_id: 受试者ID
      - test_code: 检验项目代码 (ALT, AST, TBIL, ALP, HGB, PLT, CR, GLU)
      - test_value: 检验值
      - test_date: 检验日期
      - visit: 访视名称
      - visit_num: 访视编号
      - uln: 正常上限
      - lln: 正常下限
    """
    records: List[Dict[str, Any]] = []
    base_date = datetime(2024, 1, 1)
    
    # 定义检验项目的正常范围
    test_ranges = {
        "ALT": {"uln": 40.0, "lln": 5.0, "normal": (10, 35)},
        "AST": {"uln": 40.0, "lln": 5.0, "normal": (10, 35)},
        "TBIL": {"uln": 21.0, "lln": 1.0, "normal": (5, 18)},
        "ALP": {"uln": 120.0, "lln": 30.0, "normal": (40, 100)},
        "HGB": {"uln": 170.0, "lln": 110.0, "normal": (120, 160)},
        "PLT": {"uln": 400.0, "lln": 100.0, "normal": (150, 350)},
        "CR": {"uln": 115.0, "lln": 40.0, "normal": (50, 100)},
        "GLU": {"uln": 7.0, "lln": 3.5, "normal": (4.0, 6.5)},
    }
    
    visits = [
        ("Baseline", 0),
        ("Week 2", 1),
        ("Week 4", 2),
        ("Week 8", 3),
        ("Week 12", 4),
    ]
    
    subjects = [f"S{str(i).zfill(3)}" for i in range(1, 21)]  # 20 subjects
    
    import random
    random.seed(42)
    
    for subj in subjects:
        for visit_name, visit_num in visits:
            visit_date = base_date + timedelta(days=visit_num * 14)
            
            for test_code, ranges in test_ranges.items():
                uln = ranges["uln"]
                lln = ranges["lln"]
                normal_low, normal_high = ranges["normal"]
                
                # 生成正常范围内的值
                if test_code == "ALT":
                    # 部分受试者ALT逐渐升高（模拟药物性肝损伤）
                    if subj in ("S001", "S002", "S003"):
                        # 基线正常，Week 4后逐渐升高
                        if visit_num <= 1:
                            val = random.uniform(normal_low, normal_high)
                        elif visit_num == 2:
                            val = random.uniform(normal_high * 1.5, normal_high * 3)
                        else:
                            val = random.uniform(normal_high * 2, uln * 4)
                    elif subj in ("S004", "S005"):
                        # 持续正常
                        val = random.uniform(normal_low, normal_high)
                    else:
                        val = random.uniform(normal_low, normal_high)
                elif test_code == "AST":
                    if subj in ("S001", "S002"):
                        if visit_num <= 1:
                            val = random.uniform(normal_low, normal_high)
                        elif visit_num == 2:
                            val = random.uniform(normal_high * 1.5, normal_high * 3)
                        else:
                            val = random.uniform(normal_high * 2, uln * 4)
                    else:
                        val = random.uniform(normal_low, normal_high)
                elif test_code == "TBIL":
                    if subj in ("S001",):
                        # S001: 酶峰后胆红素升高 → Hy's Law 候选者
                        if visit_num <= 2:
                            val = random.uniform(5, 15)
                        else:
                            val = random.uniform(uln * 2.5, uln * 5)
                    elif subj in ("S002",):
                        # S002: 酶峰后胆红素轻微升高
                        if visit_num <= 2:
                            val = random.uniform(5, 15)
                        else:
                            val = random.uniform(uln * 1.5, uln * 3)
                    else:
                        val = random.uniform(5, 18)
                elif test_code == "ALP":
                    if subj in ("S001", "S002"):
                        # 保持正常（排除胆汁淤积型）
                        val = random.uniform(40, 80)
                    else:
                        val = random.uniform(40, 100)
                else:
                    # 其他检验项目正常波动
                    val = random.uniform(normal_low, normal_high)
                
                # 偶尔生成异常值用于 L3 测试
                if test_code == "HGB" and subj == "S010" and visit_num == 3:
                    val = 80.0  # 明显低于正常
                if test_code == "PLT" and subj == "S011" and visit_num == 2:
                    val = 450.0  # 明显高于正常
                
                records.append({
                    "subject_id": subj,
                    "test_code": test_code,
                    "test_value": round(val, 2),
                    "test_date": visit_date.strftime("%Y-%m-%d"),
                    "visit": visit_name,
                    "visit_num": visit_num,
                    "uln": uln,
                    "lln": lln,
                })
    
    return records


def generate_l1_trend_data() -> List[Dict[str, Any]]:
    """
    生成专门用于 L1 趋势检查的额外数据。
    确保某些参数在特定访视有显著分布偏移。
    """
    records: List[Dict[str, Any]] = []
    base_date = datetime(2024, 1, 1)
    
    # 额外受试者，用于产生明显的趋势偏移
    for visit_name, visit_num in [("Baseline", 0), ("Week 4", 2), ("Week 8", 3)]:
        visit_date = base_date + timedelta(days=visit_num * 14)
        
        for i in range(15):  # 15个额外受试者
            subj = f"T{str(i).zfill(3)}"
            
            # CR (肌酐) — Week 8 明显升高
            if visit_name == "Baseline":
                cr_val = 60 + (i % 10) * 2
            elif visit_name == "Week 4":
                cr_val = 65 + (i % 10) * 2
            else:  # Week 8 — 明显升高
                cr_val = 110 + (i % 10) * 5
            
            records.append({
                "subject_id": subj,
                "test_code": "CR",
                "test_value": cr_val,
                "test_date": visit_date.strftime("%Y-%m-%d"),
                "visit": visit_name,
                "visit_num": visit_num,
                "uln": 115.0,
                "lln": 40.0,
            })
            
            # GLU (葡萄糖) — Week 8 明显升高
            if visit_name == "Baseline":
                glu_val = 4.5 + (i % 5) * 0.3
            elif visit_name == "Week 4":
                glu_val = 5.0 + (i % 5) * 0.3
            else:
                glu_val = 8.0 + (i % 5) * 0.5
            
            records.append({
                "subject_id": subj,
                "test_code": "GLU",
                "test_value": glu_val,
                "test_date": visit_date.strftime("%Y-%m-%d"),
                "visit": visit_name,
                "visit_num": visit_num,
                "uln": 7.0,
                "lln": 3.5,
            })
    
    return records


# ═══════════════════════════════════════════════════════════
# 2. 测试函数
# ═══════════════════════════════════════════════════════════

def run_test() -> List[CoreGageFinding]:
    """运行完整的趋势检查测试。"""
    print("=" * 70)
    print("🧪 pyCoreGage 实验室趋势检查功能测试 (L1 → L3)")
    print("=" * 70)
    
    # 生成合成数据
    print("\n📊 生成合成数据...")
    lab_data = generate_synthetic_lab_data()
    extra_data = generate_l1_trend_data()
    all_lab_data = lab_data + extra_data
    print(f"   总记录数: {len(all_lab_data)}")
    print(f"   受试者数: {len(set(r['subject_id'] for r in all_lab_data))}")
    print(f"   检验项目: {sorted(set(r['test_code'] for r in all_lab_data))}")
    print(f"   访视: {sorted(set(r['visit'] for r in all_lab_data), key=lambda v: [r for r in all_lab_data if r['visit']==v][0]['visit_num'])}")
    
    # 初始化配置和状态
    config = CoreGageConfig(
        project_id="test_lab_trends",
        protocol_id="LAB-TEST-001",
        min_severity=Severity.INFO,  # 接收所有严重级别
    )
    state = CoreGageState(config=config)
    state.set_data(DataSource.LAB, all_lab_data)
    
    # 初始化 SafetyChecker
    checker = SafetyChecker(config=config, state=state)
    
    # 运行检查
    print("\n🔍 运行检查...")
    findings = checker.check()
    
    # 分类展示结果
    print("\n" + "=" * 70)
    print("📋 检查结果汇总")
    print("=" * 70)
    
    # 按 source 分类
    by_source: Dict[str, List[CoreGageFinding]] = {}
    for f in findings:
        by_source.setdefault(f.source, []).append(f)
    
    total = len(findings)
    print(f"\n总发现数: {total}")
    
    for source, items in sorted(by_source.items()):
        print(f"\n  [{source}] {len(items)} 个发现")
        for f in items:
            print(f"    [{f.severity.value:>8}] {f.subject_id or '(group)':>8} | {f.message[:100]}")
    
    # 详细分析
    print("\n" + "=" * 70)
    print("📊 详细分析")
    print("=" * 70)
    
    # L1 趋势检查
    l1_findings = [f for f in findings if f.source == "lab_trend"]
    print(f"\n🔹 L1 通用趋势检查: {len(l1_findings)} 个发现")
    if l1_findings:
        for f in l1_findings:
            d = f.details
            print(f"  • {d.get('test_code')}: {d.get('baseline_visit')} → {d.get('current_visit')}")
            print(f"    中位数: {d.get('baseline_median')} → {d.get('current_median')} "
                  f"({d.get('median_change_pct')}% 变化)")
            print(f"    基线 Q1/Q3: {d.get('baseline_q1')}/{d.get('baseline_q3')}")
            print(f"    当前 Q1/Q3: {d.get('current_q1')}/{d.get('current_q3')}")
    else:
        print("  (无趋势偏移发现)")
    
    # L2 肝毒性检查
    l2_findings = [f for f in findings if f.source == "lab_hepatic"]
    print(f"\n🔹 L2 肝毒性检查 (Hy's Law): {len(l2_findings)} 个发现")
    if l2_findings:
        for f in l2_findings:
            d = f.details
            print(f"  • 受试者 {d.get('subject_id')}:")
            print(f"    {d.get('enzyme_name')} = {d.get('enzyme_value'):.1f} "
                  f"({d.get('enzyme_xuln'):.1f}×ULN)")
            print(f"    TBIL = {d.get('tbil_value'):.1f} "
                  f"({d.get('tbil_xuln'):.1f}×ULN)")
            print(f"    ALP = {d.get('alp_value'):.1f} "
                  f"({d.get('alp_xuln'):.1f}×ULN)")
            rr = d.get('r_ratio')
            rt = d.get('r_ratio_type')
            if rr is not None:
                print(f"    R-ratio = {rr:.2f} ({rt})")
            print(f"    严重级别: {f.severity.value}")
    else:
        print("  (无 Hy's Law 候选者)")
    
    # L3 统计异常值
    l3_findings = [f for f in findings if f.source == "lab_outlier"]
    print(f"\n🔹 L3 统计异常值检测 (IQR): {len(l3_findings)} 个发现")
    if l3_findings:
        for f in l3_findings:
            d = f.details
            print(f"  • {d.get('test_code')} | {d.get('subject_id')} | {d.get('visit')}")
            print(f"    值: {d.get('value'):.2f} | "
                  f"范围: [{d.get('lower_bound'):.2f}, {d.get('upper_bound'):.2f}]")
            print(f"    中位数: {d.get('median'):.2f} | IQR: {d.get('iqr'):.2f}")
    else:
        print("  (无统计异常值)")
    
    # 严重级别统计
    print("\n" + "=" * 70)
    print("📈 严重级别分布")
    print("=" * 70)
    sev_count: Dict[str, int] = {}
    for f in findings:
        sev_count[f.severity.value] = sev_count.get(f.severity.value, 0) + 1
    for sev in ["info", "low", "medium", "high", "critical"]:
        count = sev_count.get(sev, 0)
        bar = "█" * count
        print(f"  {sev:>10}: {count:>3} {bar}")
    
    # 保存详细结果
    output_path = Path(__file__).parent / "test_lab_trends_output.json"
    result_data = {
        "total_findings": total,
        "by_source": {},
        "by_severity": sev_count,
        "findings": [],
    }
    for f in findings:
        result_data["findings"].append(f.to_dict())
        src = f.source
        result_data["by_source"][src] = result_data["by_source"].get(src, 0) + 1
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n💾 详细结果已保存到: {output_path}")
    
    print("\n✅ 测试完成！")
    return findings


# ═══════════════════════════════════════════════════════════
# 3. 独立单元测试
# ═══════════════════════════════════════════════════════════

def test_compute_stats() -> None:
    """测试 _compute_stats 静态方法。"""
    print("\n🧪 单元测试: _compute_stats")
    print("-" * 40)
    
    # 测试1: 奇数个元素
    vals1 = [1.0, 2.0, 3.0, 4.0, 5.0]
    stats1 = SafetyChecker._compute_stats(vals1)
    print(f"  输入: {vals1}")
    print(f"  中位数: {stats1['median']} (期望: 3.0)")
    print(f"  Q1: {stats1['q1']} (期望: 2.0)")
    print(f"  Q3: {stats1['q3']} (期望: 4.0)")
    print(f"  IQR: {stats1['iqr']} (期望: 2.0)")
    assert stats1["median"] == 3.0
    assert stats1["q1"] == 2.0
    assert stats1["q3"] == 4.0
    assert stats1["iqr"] == 2.0
    
    # 测试2: 偶数个元素
    vals2 = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    stats2 = SafetyChecker._compute_stats(vals2)
    print(f"\n  输入: {vals2}")
    print(f"  中位数: {stats2['median']} (期望: 3.5)")
    print(f"  Q1: {stats2['q1']} (期望: 2.0)")
    print(f"  Q3: {stats2['q3']} (期望: 5.0)")
    print(f"  IQR: {stats2['iqr']} (期望: 3.0)")
    assert stats2["median"] == 3.5
    assert stats2["q1"] == 2.0
    assert stats2["q3"] == 5.0
    assert stats2["iqr"] == 3.0
    
    # 测试3: 空列表
    stats3 = SafetyChecker._compute_stats([])
    print(f"\n  输入: []")
    print(f"  中位数: {stats3['median']} (期望: 0.0)")
    assert stats3["median"] == 0.0
    
    print("  ✅ _compute_stats 测试通过")


def test_yaml_parsing() -> None:
    """测试 YAML 配置解析。"""
    print("\n🧪 单元测试: YAML 配置解析")
    print("-" * 40)
    
    yaml_path = Path(__file__).parent / "rules" / "hepatic_rules.yaml"
    
    # 测试简单 YAML 解析器
    parsed = SafetyChecker._simple_yaml_parse(str(yaml_path))
    print(f"  解析结果: {json.dumps(parsed, indent=2, ensure_ascii=False)}")
    
    assert parsed["hy_window_days"] == 28
    assert parsed["hys_law"]["enzyme_xuln_gte"] == 3
    assert parsed["hys_law"]["tbil_xuln_gt"] == 2
    assert parsed["hys_law"]["alp_xuln_lt"] == 2
    assert parsed["r_ratio"]["hepatocellular_gte"] == 5
    assert parsed["r_ratio"]["cholestatic_lte"] == 2
    print("  ✅ YAML 解析测试通过")
    
    # 测试 _load_hepatic_rules
    config = CoreGageConfig()
    state = CoreGageState(config=config)
    checker = SafetyChecker(config=config, state=state)
    rules = checker._load_hepatic_rules()
    print(f"\n  加载的规则: {json.dumps(rules, indent=2, ensure_ascii=False)}")
    assert rules["hy_window_days"] == 28
    assert rules["hys_law"]["enzyme_xuln_gte"] == 3
    print("  ✅ _load_hepatic_rules 测试通过")


def test_merge_dict() -> None:
    """测试 _merge_dict 静态方法。"""
    print("\n🧪 单元测试: _merge_dict")
    print("-" * 40)
    
    base = {
        "a": 1,
        "b": {"x": 10, "y": 20},
        "c": 3,
    }
    override = {
        "b": {"y": 99, "z": 30},
        "d": 4,
    }
    merged = SafetyChecker._merge_dict(base, override)
    print(f"  Base: {base}")
    print(f"  Override: {override}")
    print(f"  Merged: {merged}")
    
    assert merged["a"] == 1
    assert merged["b"]["x"] == 10  # from base
    assert merged["b"]["y"] == 99  # overridden
    assert merged["b"]["z"] == 30  # new
    assert merged["c"] == 3
    assert merged["d"] == 4
    print("  ✅ _merge_dict 测试通过")


if __name__ == "__main__":
    # 运行单元测试
    test_compute_stats()
    test_merge_dict()
    test_yaml_parsing()
    
    # 运行完整测试
    print("\n" + "=" * 70)
    findings = run_test()
    print("=" * 70)
