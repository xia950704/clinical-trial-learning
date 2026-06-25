# Temporal 检查规则脚本
# 文件名：Temporal.py
# 功能：时间序列检查（访视顺序、时间锚定、时间窗、缺失时间）

def check_Temporal(state, cfg):
    """
    时间序列检查入口函数
    
    Args:
        state: CoreGageState 对象
        cfg: CoreGageConfig 对象
    
    Returns:
        state: 更新后的 CoreGageState 对象
    """
    from temporal_checker import TemporalChecker
    
    # 初始化时间序列检查器
    checker = TemporalChecker(state, cfg)
    
    # 执行检查
    findings = []
    
    # 1. 访视顺序检查
    visit_findings = checker.check_visit_order()
    findings.extend(visit_findings)
    
    # 2. 时间锚定检查
    anchor_findings = checker.check_time_anchor()
    findings.extend(anchor_findings)
    
    # 3. 时间窗检查
    window_findings = checker.check_time_window()
    findings.extend(window_findings)
    
    # 4. 缺失时间检查
    missing_findings = checker.check_missing_time()
    findings.extend(missing_findings)
    
    # 收集发现
    if findings:
        collect_findings(state, findings, id="TEMPORAL")
    
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
