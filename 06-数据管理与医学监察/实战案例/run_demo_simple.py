#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实战案例演示脚本（简化版）
功能：演示 pyCoreGage 医学插件的数据管理流程（不依赖外部包）
"""

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

print("=" * 80)
print("🏥 pyCoreGage 医学插件 - 实战案例演示（简化版）")
print("=" * 80)

# 1. 数据加载
print("\n📊 加载数据...")

def load_csv(filepath: str) -> List[Dict[str, str]]:
    """加载 CSV 文件"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

# 加载数据域
dm_data = load_csv("DM.csv")
ae_data = load_csv("AE.csv")
cm_data = load_csv("CM.csv")
vs_data = load_csv("VS.csv")
lb_data = load_csv("LB.csv")

print(f"  ✅ DM: {len(dm_data)} 条记录")
print(f"  ✅ AE: {len(ae_data)} 条记录")
print(f"  ✅ CM: {len(cm_data)} 条记录")
print(f"  ✅ VS: {len(vs_data)} 条记录")
print(f"  ✅ LB: {len(lb_data)} 条记录")

# 2. 时间序列检查
print("\n🔍 时间序列检查...")

def check_visit_order(dm_data: List[Dict]) -> List[Dict]:
    """检查访视顺序"""
    findings = []
    # 简化：检查是否有重复的 SUBJID
    subj_ids = [d['SUBJID'] for d in dm_data]
    duplicates = [sid for sid in subj_ids if subj_ids.count(sid) > 1]
    if duplicates:
        findings.append({
            "check_id": "VISIT_ORDER",
            "severity": "MAJOR",
            "description": f"发现重复受试者 ID: {set(duplicates)}",
            "subj_id": "N/A",
            "vis_id": "N/A"
        })
    return findings

def check_time_anchor(ae_data: List[Dict], dm_data: List[Dict]) -> List[Dict]:
    """检查 AE 时间锚定"""
    findings = []
    # 简化：检查 AE 时间是否在合理范围内
    for ae in ae_data:
        try:
            ae_date = datetime.strptime(ae['AESTDTC'], "%Y-%m-%d")
            if ae_date.year < 2024 or ae_date.year > 2026:
                findings.append({
                    "check_id": "TIME_ANCHOR",
                    "severity": "MAJOR",
                    "description": f"AE 时间异常: {ae['AESTDTC']}",
                    "subj_id": ae['SUBJID'],
                    "vis_id": "N/A"
                })
        except:
            pass
    return findings

def check_time_window(cm_data: List[Dict]) -> List[Dict]:
    """检查给药前 24h 时间窗"""
    findings = []
    # 简化：检查合并用药时间
    for cm in cm_data:
        try:
            cm_date = datetime.strptime(cm['COSTDTC'], "%Y-%m-%d")
            # 模拟检查：假设给药时间是 2024-01-01
            dosing_date = datetime(2024, 1, 1)
            if cm_date < dosing_date:
                findings.append({
                    "check_id": "TIME_WINDOW",
                    "severity": "MAJOR",
                    "description": f"给药前合并用药: {cm['CMNAME']} 在 {cm['COSTDTC']}",
                    "subj_id": cm['SUBJID'],
                    "vis_id": "N/A"
                })
        except:
            pass
    return findings

def check_missing_time(dm_data: List[Dict]) -> List[Dict]:
    """检查缺失时间"""
    findings = []
    # 简化：检查是否有缺失的日期
    for dm in dm_data:
        if not dm.get('SCRNDTC') or dm['SCRNDTC'] == '':
            findings.append({
                "check_id": "MISSING_TIME",
                "severity": "MAJOR",
                "description": f"筛选日期缺失",
                "subj_id": dm['SUBJID'],
                "vis_id": "N/A"
            })
    return findings

# 执行时间序列检查
temporal_findings = []
temporal_findings.extend(check_visit_order(dm_data))
temporal_findings.extend(check_time_anchor(ae_data, dm_data))
temporal_findings.extend(check_time_window(cm_data))
temporal_findings.extend(check_missing_time(dm_data))

print(f"  ✅ 时间序列检查完成: {len(temporal_findings)} 个发现")

# 3. 医学编码检查
print("\n🔍 医学编码检查...")

def check_meddra_coding(ae_data: List[Dict]) -> List[Dict]:
    """检查 MedDRA 编码"""
    findings = []
    # 简化：检查 AE 术语是否在示例词典中
    valid_terms = ["头痛", "恶心", "呕吐", "皮疹", "疲劳", "头晕", "腹泻", "失眠"]
    for ae in ae_data:
        if ae.get('AETERM') and ae['AETERM'] not in valid_terms:
            findings.append({
                "check_id": "MEDDRA_CODING",
                "severity": "MINOR",
                "description": f"AE 术语不在词典中: {ae['AETERM']}",
                "subj_id": ae['SUBJID'],
                "vis_id": "N/A"
            })
    return findings

def check_atc_coding(cm_data: List[Dict]) -> List[Dict]:
    """检查 ATC 编码"""
    findings = []
    # 简化：检查药物名称是否在示例词典中
    valid_drugs = ["二甲双胍", "美托洛尔", "卡托普利", "阿司匹林", "维生素C"]
    for cm in cm_data:
        if cm.get('CMNAME') and cm['CMNAME'] not in valid_drugs:
            findings.append({
                "check_id": "ATC_CODING",
                "severity": "MINOR",
                "description": f"药物名称不在词典中: {cm['CMNAME']}",
                "subj_id": cm['SUBJID'],
                "vis_id": "N/A"
            })
    return findings

def check_loinc_coding(lb_data: List[Dict]) -> List[Dict]:
    """检查 LOINC 编码"""
    findings = []
    # 简化：检查检验项目是否在示例词典中
    valid_tests = ["葡萄糖", "血红蛋白", "肌酐", "丙氨酸氨基转移酶", "天冬氨酸氨基转移酶"]
    for lb in lb_data:
        if lb.get('LBTESTCD') and lb['LBTESTCD'] not in valid_tests:
            findings.append({
                "check_id": "LOINC_CODING",
                "severity": "MINOR",
                "description": f"检验项目不在词典中: {lb['LBTESTCD']}",
                "subj_id": lb['SUBJID'],
                "vis_id": "N/A"
            })
    return findings

# 执行编码检查
coding_findings = []
coding_findings.extend(check_meddra_coding(ae_data))
coding_findings.extend(check_atc_coding(cm_data))
coding_findings.extend(check_loinc_coding(lb_data))

print(f"  ✅ 医学编码检查完成: {len(coding_findings)} 个发现")

# 4. 安全性检查
print("\n🔍 安全性检查...")

def check_ae_grading(ae_data: List[Dict]) -> List[Dict]:
    """检查 AE 分级"""
    findings = []
    # 简化：检查 AE 分级是否在 1-5 范围内
    for ae in ae_data:
        try:
            grade = int(ae.get('AETOXGR', 0))
            if grade < 1 or grade > 5:
                findings.append({
                    "check_id": "AE_GRADING",
                    "severity": "MAJOR",
                    "description": f"AE 分级异常: {ae.get('AETOXGR')}",
                    "subj_id": ae['SUBJID'],
                    "vis_id": "N/A"
                })
        except:
            pass
    return findings

def check_lab_abnormality(lb_data: List[Dict]) -> List[Dict]:
    """检查实验室异常"""
    findings = []
    # 简化：检查检验值是否超出参考范围
    for lb in lb_data:
        try:
            value = float(lb.get('LBORRES', 0))
            ref_low = float(lb.get('LBSTNRLO', 0))
            ref_high = float(lb.get('LBSTNRHI', 0))
            if value < ref_low or value > ref_high:
                findings.append({
                    "check_id": "LAB_ABNORMALITY",
                    "severity": "MINOR",
                    "description": f"实验室异常: {lb['LBTESTCD']} = {value} (参考范围: {ref_low}-{ref_high})",
                    "subj_id": lb['SUBJID'],
                    "vis_id": "N/A"
                })
        except:
            pass
    return findings

# 执行安全性检查
safety_findings = []
safety_findings.extend(check_ae_grading(ae_data))
safety_findings.extend(check_lab_abnormality(lb_data))

print(f"  ✅ 安全性检查完成: {len(safety_findings)} 个发现")

# 5. 汇总结果
print("\n📊 检查摘要:")
print("-" * 60)

all_findings = temporal_findings + coding_findings + safety_findings

# 按检查类型统计
check_types = {}
for finding in all_findings:
    check_id = finding['check_id']
    if check_id not in check_types:
        check_types[check_id] = 0
    check_types[check_id] += 1

for check_type, count in check_types.items():
    print(f"  {check_type}: {count} 个发现")

print(f"\n  总计: {len(all_findings)} 个发现")

# 6. 保存结果
print("\n💾 保存结果...")

# 创建输出目录
os.makedirs("outputs/reports", exist_ok=True)

# 保存结果到 JSON
report = {
    "project_name": "clinical_trial_demo",
    "timestamp": datetime.now().isoformat(),
    "summary": {
        "total_findings": len(all_findings),
        "by_check_type": check_types,
        "by_severity": {
            "MAJOR": len([f for f in all_findings if f['severity'] == 'MAJOR']),
            "MINOR": len([f for f in all_findings if f['severity'] == 'MINOR']),
            "CRITICAL": len([f for f in all_findings if f['severity'] == 'CRITICAL'])
        }
    },
    "findings": all_findings
}

with open("outputs/report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"  ✅ 报告已保存: outputs/report.json")

# 7. 显示详细发现
print("\n📋 详细发现:")
print("-" * 60)
for i, finding in enumerate(all_findings[:10], 1):  # 只显示前 10 个
    print(f"  {i}. [{finding['severity']}] {finding['check_id']}")
    print(f"     {finding['description']}")
    print(f"     受试者: {finding['subj_id']}")
    print()

if len(all_findings) > 10:
    print(f"  ... 还有 {len(all_findings) - 10} 个发现")

print("\n✅ 演示完成！")
print(f"📁 输出目录: outputs/")
print(f"📄 报告文件: outputs/report.json")
