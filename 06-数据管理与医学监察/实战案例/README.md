# 实战案例：肿瘤学临床试验数据管理

本案例演示如何使用 pyCoreGage 医学插件进行临床试验数据管理。

## 📊 数据集说明

### 研究背景
- **研究类型**：多中心、随机、双盲、安慰剂对照 III 期临床试验
- **适应症**：心脏术后新发房颤
- **干预措施**：尼非卡兰 vs 胺碘酮
- **主要终点**：4 小时内房颤转复率
- **样本量**：100 例受试者（1:1 随机分组）

### 数据域说明

| 数据域 | 文件 | 记录数 | 说明 |
|--------|------|--------|------|
| **DM** | DM.csv | 100 | 受试者基本信息（筛选、入组、人口学） |
| **AE** | AE.csv | ~150 | 不良事件（术语、时间、严重性、关联性） |
| **CM** | CM.csv | ~100 | 合并用药（药物名称、剂量、时间） |
| **VS** | VS.csv | ~400 | 生命体征（血压、心率、体温） |
| **LB** | LB.csv | ~500 | 实验室检查（葡萄糖、血红蛋白、肌酐等） |

## 🔧 使用 pyCoreGage 医学插件

### 1. 安装依赖

```bash
pip install pycoregage
```

### 2. 配置规则注册表

创建 `rule_registry_medical.xlsx`，包含以下检查规则：

| 分类 | 规则 ID | 规则描述 | 严重级别 |
|------|---------|---------|---------|
| **Temporal** | VISIT_ORDER | 访视顺序检查 | MAJOR |
| **Temporal** | TIME_ANCHOR | AE 时间在给药时间之后 | MAJOR |
| **Temporal** | TIME_WINDOW | 给药前 24h 内无合并用药 | MAJOR |
| **Coding** | MEDDRA | MedDRA 编码检查 | MINOR |
| **Coding** | ICD10 | ICD-10 编码检查 | MINOR |
| **Safety** | AE_GRADING | AE 分级检查 | MAJOR |
| **Safety** | SAE_CRITERIA | SAE 标准检查 | CRITICAL |
| **Safety** | LAB_ABNORMALITY | 实验室异常检查 | MINOR |

### 3. 运行检查

```python
from medcage import MedCage

# 创建配置
config = {
    "rule_registry": "rule_registry_medical.xlsx",
    "trial_checks": "rules/trial/",
    "study_checks": "rules/study/",
    "inputs": "data/",
    "reports": "outputs/reports/",
    "feedback": "outputs/feedback/",
    "project_name": "clinical_trial_demo",
}

# 初始化医学插件
mc = MedCage(config)

# 加载数据
mc.load_data("data/")

# 运行检查
mc.run()

# 保存结果
mc.save_results("outputs/report.json")
```

### 4. 查看结果

检查结果将输出到 `outputs/reports/` 目录，包含：

- `DM_issues.xlsx` - 数据管理问题
- `MW_issues.xlsx` - 医学监察问题
- `SDTM_issues.xlsx` - SDTM 标准问题
- `ADAM_issues.xlsx` - ADaM 标准问题
- `all_open.xlsx` - 所有未解决问题
- `all_closed.xlsx` - 所有已解决问题

## 📋 预期检查结果

### 时间序列检查

| 检查项 | 预期发现 |
|--------|---------|
| **访视顺序** | 0-5 个异常（部分受试者访视时间倒序） |
| **时间锚定** | 5-10 个异常（AE 时间在给药时间之前） |
| **时间窗** | 10-20 个异常（给药前 24h 内有合并用药） |

### 医学编码检查

| 检查项 | 预期发现 |
|--------|---------|
| **MedDRA** | 0 个异常（示例数据已编码） |
| **ICD-10** | 0 个异常（示例数据已编码） |

### 安全性检查

| 检查项 | 预期发现 |
|--------|---------|
| **AE 分级** | 0-5 个异常（部分 AE 分级错误） |
| **SAE 标准** | 0-2 个异常（严重不良事件识别） |
| **实验室异常** | 20-50 个异常（超出参考范围的检验值） |

## 📁 文件结构

```
实战案例/
├── DM.csv              # 受试者基本信息
├── AE.csv              # 不良事件
├── CM.csv              # 合并用药
├── VS.csv              # 生命体征
├── LB.csv              # 实验室检查
├── README.md           # 本说明文档
└── outputs/            # 输出报告（运行后生成）
    ├── reports/
    └── feedback/
```

## ⚠️ 注意事项

1. **示例数据**：本数据集为合成数据，仅用于演示和测试
2. **生产环境**：生产环境需使用真实临床试验数据
3. **数据隐私**：真实数据需进行去标识化处理
4. **许可合规**：使用医学词典需遵守官方许可协议

---

*最后更新：2026-06-25*
