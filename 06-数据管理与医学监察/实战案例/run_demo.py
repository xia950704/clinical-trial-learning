# 实战案例运行脚本
# 文件名：run_demo.py
# 功能：演示 pyCoreGage 医学插件的数据管理流程

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 添加医学插件目录到路径
plugin_dir = Path(__file__).parent.parent / "pyCoreGage-医学插件"
sys.path.insert(0, str(plugin_dir))

from medcage import MedCage

def main():
    """
    主函数：运行医学插件演示
    """
    print("=" * 80)
    print("🏥 pyCoreGage 医学插件 - 实战案例演示")
    print("=" * 80)
    
    # 1. 创建配置
    config = {
        "rule_registry": "rule_registry_medical.json",
        "trial_checks": "rules/trial/",
        "study_checks": "rules/study/",
        "inputs": ".",  # 当前目录（实战案例/）
        "reports": "outputs/reports/",
        "feedback": "outputs/feedback/",
        "project_name": "clinical_trial_demo",
    }
    
    # 2. 初始化医学插件
    print("\n📋 初始化医学插件...")
    mc = MedCage(config)
    
    # 3. 加载数据
    print("\n📊 加载数据...")
    mc.load_data("data/")
    
    # 4. 运行检查
    print("\n🔍 运行检查...")
    mc.run()
    
    # 5. 保存结果
    print("\n💾 保存结果...")
    mc.save_results("outputs/report.json")
    
    # 6. 显示摘要
    print("\n📊 检查摘要:")
    print("-" * 60)
    if hasattr(mc, 'summary'):
        summary = mc.summary()
        for check_type, count in summary.items():
            print(f"  {check_type}: {count} 个发现")
    
    print("\n✅ 演示完成！")
    print(f"📁 输出目录: outputs/")
    print(f"📄 报告文件: outputs/report.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
