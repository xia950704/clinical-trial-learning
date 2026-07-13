# Coding 检查规则脚本
# 文件名：Coding.py
# 功能：医学编码检查（MedDRA、ICD-10、ATC、LOINC）

def check_Coding(state, cfg):
    """
    医学编码检查入口函数
    
    Args:
        state: CoreGageState 对象
        cfg: CoreGageConfig 对象
    
    Returns:
        state: 更新后的 CoreGageState 对象
    """
    from coding_checker import CodingChecker
    
    # 初始化编码检查器
    checker = CodingChecker(state, cfg)
    
    # 执行检查
    findings = []
    
    # 1. MedDRA 编码检查
    meddra_findings = checker.check_meddra()
    findings.extend(meddra_findings)
    
    # 2. ICD-10 编码检查
    icd10_findings = checker.check_icd10()
    findings.extend(icd10_findings)
    
    # 3. ATC 编码检查
    atc_findings = checker.check_atc()
    findings.extend(atc_findings)
    
    # 4. LOINC 编码检查
    loinc_findings = checker.check_loinc()
    findings.extend(loinc_findings)
    
    # 收集发现
    if findings:
        collect_findings(state, findings, id="CODING")
    
    return state


def collect_findings(state, findings, id):
    """
    收集检查发现
    
    Args:
        state: CoreGageState 对象
        findings: 发现列表
        id: 检查 ID
    """
    import pandas as pd
    
    # 转换为 DataFrame
    df = pd.DataFrame(findings)
    
    # 添加到 state.issues
    if hasattr(state, 'issues') and state.issues is not None:
        state.issues = pd.concat([state.issues, df], ignore_index=True)
    else:
        state.issues = df
    
    return state
