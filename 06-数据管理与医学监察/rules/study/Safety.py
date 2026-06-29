# Safety 检查规则脚本
# 文件名：Safety.py
# 功能：安全性检查（AE 分级、SAE 识别、AESI、实验室异常）

def check_Safety(state, cfg):
    """
    安全性检查入口函数
    
    Args:
        state: CoreGageState 对象
        cfg: CoreGageConfig 对象
    
    Returns:
        state: 更新后的 CoreGageState 对象
    """
    from safety_checker import SafetyChecker
    
    # 初始化安全性检查器
    checker = SafetyChecker(state, cfg)
    
    # 执行检查
    findings = []
    
    # 1. AE 分级检查
    grading_findings = checker.check_ae_grading()
    findings.extend(grading_findings)
    
    # 2. SAE 标准检查
    sae_findings = checker.check_sae_criteria()
    findings.extend(sae_findings)
    
    # 3. AESI 检查
    aesi_findings = checker.check_aesi()
    findings.extend(aesi_findings)
    
    # 4. 实验室异常检查
    lab_findings = checker.check_lab_abnormality()
    findings.extend(lab_findings)
    
    # 收集发现
    if findings:
        collect_findings(state, findings, id="SAFETY")
    
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
