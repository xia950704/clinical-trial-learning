# pyCoreGage 医学插件

> 面向临床试验数据的自动化医学检查工具

## 插件概述

pyCoreGage 医学插件（MedCage）是一个用于临床试验数据管理的自动化检查工具。它通过加载临床试验数据（EDC、实验室、不良事件、合并用药等），运行多个检查模块，自动发现数据质量问题、安全性信号和合规性问题，并以结构化的 `CoreGageFinding` 对象输出结果。

### 核心能力

- **多模块检查**：涵盖时间序列、医学编码、安全性、PK/PD、基因检测、合规性六大领域
- **纯 Python 实现**：无 pandas 依赖（可选输出格式除外），轻量级，易于集成
- **结构化输出**：所有发现以 `CoreGageFinding` 对象返回，支持 JSON/CSV/Excel 导出
- **可配置规则**：通过 YAML 配置文件自定义检查阈值和规则
- **分级严重性**：INFO → LOW → MEDIUM → HIGH → CRITICAL 五级严重性分类

## 功能列表

### 1. 时间序列检查（TemporalChecker）

| 检查项 | 说明 | 严重级别 |
|--------|------|---------|
| VISIT_ORDER | 访视顺序检查：筛查 → 基线 → 给药 → 随访 | CRITICAL/MAJOR |
| TIME_ANCHOR | AE 时间锚定：AE 起始时间应在给药时间之后 | MAJOR/MINOR |
| TIME_WINDOW | 时间窗检查：给药前 24h 内不应存在合并用药 | MAJOR |
| MISSING_TIME | 缺失时间检查：必须访视缺失、关键字段时间字段缺失 | CRITICAL/MAJOR/MINOR |

### 2. 医学编码检查（CodingChecker）

| 检查项 | 说明 | 严重级别 |
|--------|------|---------|
| CODING_MEDDRA | MedDRA LLT→PT→SOC 层级关系验证 | MINOR |
| CODING_ICD10 | ICD-10 诊断编码格式与有效性验证 | MINOR |
| CODING_ATC | ATC 药物编码格式与有效性验证 | MINOR |
| CODING_LOINC | LOINC 实验室检验项目编码验证 | MINOR |

### 3. 安全性检查（SafetyChecker）

| 检查项 | 说明 | 严重级别 |
|--------|------|---------|
| LAB_ABNORMALITY | 实验室异常值检查（CTCAE Grade 3-5） | MEDIUM/HIGH/CRITICAL |
| VITAL_SIGN_ALERT | 生命体征异常（血压、心率、体温等） | HIGH/CRITICAL |
| SAE_CRITERIA | SAE 标准验证（死亡/危及生命/住院等） | HIGH/CRITICAL |
| SAE_CANDIDATE | SAE 候选列表生成（ICH E2A / CTCAE≥3 / 时间可疑 / 未标记） | HIGH/MEDIUM |
| LAB_DETERIORATION | 实验室值快速恶化检测（>50% 变化） | MEDIUM |
| LAB_TREND_L1 | 通用趋势检查：按检验项目+访视分组，检测分布偏移 | MEDIUM |
| LAB_TREND_L2 | 肝毒性检查：Hy's Law + R-ratio 分类 | HIGH/CRITICAL |
| LAB_TREND_L3 | 统计异常值检测：IQR 法 | LOW |
| DRUG_AE_RELATION | 药物-AE 时间关系检查 | LOW |
| MISSING_SAFETY_DATA | 关键安全性数据缺失检查 | MEDIUM |

### 4. PK/PD 检查（PKPDChecker）

| 检查项 | 说明 | 严重级别 |
|--------|------|---------|
| PK_AUC_RANGE | AUC 范围检查（0.1–10000 ng·h/mL） | MAJOR |
| PK_CMAX_RANGE | Cmax 范围检查（0.1–10000 ng/mL） | MAJOR |
| PK_TMAX_RANGE | Tmax 范围检查（0–24 h） | MINOR |
| PK_THALF_RANGE | 半衰期范围检查（0.1–100 h） | MINOR |
| PD_EC50_RANGE | EC50 范围检查（0.01–1000 ng/mL） | MINOR |
| PD_EMAX_RANGE | Emax 范围检查（0–100%） | MINOR |
| PK_SAMPLING_TIME | 采样时间序列一致性 | MAJOR |
| PK_DOSE_CONCENTRATION | 剂量-浓度关系合理性 | MAJOR |

### 5. 基因检测检查（GeneticChecker）

| 检查项 | 说明 | 严重级别 |
|--------|------|---------|
| GENETIC_ANNOTATION | 基因变异注释完整性（必填字段） | MAJOR |
| GENETIC_GENOTYPE | 基因型格式检查（AA/AG/GG 或 A/G/G/G） | MINOR |
| GENETIC_AF | 等位基因频率合理性（0–1） | MAJOR |
| GENETIC_GENE_DRUG | 基因-药物关联检查 | MINOR |
| GENETIC_COVERAGE | 药物代谢基因覆盖度检查 | INFO |

### 6. 合规性检查（ComplianceManager）

| 检查项 | 说明 | 严重级别 |
|--------|------|---------|
| INFORMED_CONSENT | 知情同意完整性与时间检查 | HIGH/CRITICAL |
| PROTOCOL_DEVIATION | 方案偏离追踪 | MEDIUM/HIGH/CRITICAL |
| DATA_INTEGRITY | ALCOA+ 数据完整性原则验证 | MEDIUM |
| E_SIGNATURE | 电子签名合规性（FDA 21 CFR Part 11） | HIGH/MEDIUM |
| AUDIT_TRAIL | 审计追踪完整性 | MEDIUM |
| DATA_PRIVACY | 数据隐私检查（GDPR/HIPAA PII 检测） | HIGH |

## 快速开始

### 3 步上手

```python
# 步骤 1：导入并初始化
from medcage import MedCage
from core_data import CoreGageConfig, Severity

config = CoreGageConfig(
    project_id="my_trial",
    protocol_id="PROT-001",
    min_severity=Severity.LOW,
)

mc = MedCage(config=config)

# 步骤 2：加载数据
mc.load_data("data/edc.csv", source=DataSource.EDC)
mc.load_data("data/ae.csv", source=DataSource.AE)
mc.load_data("data/lab.csv", source=DataSource.LAB)
mc.load_data("data/vital.csv", source=DataSource.VITAL)

# 步骤 3：运行检查并保存结果
result = mc.run()
mc.save_results("output/report.json", format="json")
mc.print_summary()
```

### 一键运行

```python
from medcage import run_medical_review

result = run_medical_review(
    config_path="config.json",
    data_paths=["data/edc.csv", "data/ae.csv", "data/lab.csv"],
    output_path="output/report.json",
    output_format="json",
)
```

## 示例代码

### 示例 1：单独运行某个检查器

```python
from core_data import CoreGageConfig, CoreGageState, DataSource, Severity
from safety_checker import SafetyChecker

config = CoreGageConfig(min_severity=Severity.INFO)
state = CoreGageState(config=config)

# 加载实验室数据
lab_data = [
    {"subject_id": "S001", "test_code": "ALT", "test_value": 120.0,
     "test_date": "2024-01-15", "uln": 40.0},
    {"subject_id": "S001", "test_code": "TBIL", "test_value": 50.0,
     "test_date": "2024-01-15", "uln": 21.0},
]
state.set_data(DataSource.LAB, lab_data)

checker = SafetyChecker(config=config, state=state)
findings = checker.check()

for f in findings:
    print(f"[{f.severity.value}] {f.message}")
```

### 示例 2：自定义实验室异常规则

```python
from safety_checker import SafetyChecker, LabAbnormalityRule

checker = SafetyChecker(config=config, state=state)

# 添加自定义实验室异常规则
checker.add_lab_abnormality_rule(LabAbnormalityRule(
    test_code="CR",
    test_name="肌酐",
    unit="μmol/L",
    thresholds=(30.0, 50.0, 80.0, 150.0, 250.0, 400.0),  # (low_crit, low_sev, low_mod, high_mod, high_sev, high_crit)
    normal_low=53.0,
    normal_high=115.0,
))

findings = checker.check()
```

### 示例 3：时间序列检查

```python
from temporal_checker import TemporalChecker, TemporalCheckConfig

config = TemporalCheckConfig(
    concomitant_window_hours=24.0,
    allow_ae_before_dosing=False,
    missing_tolerance_days=30,
)

subject_data = {
    "VIS": [
        {"VISIT": "SCREENING", "VISITDT": "2024-01-01"},
        {"VISIT": "BASELINE", "VISITDT": "2024-01-05"},
        {"VISIT": "DOSING", "VISITDT": "2024-01-10"},
        {"VISIT": "FOLLOWUP", "VISITDT": "2024-01-20"},
    ],
    "AE": [
        {"AESTDTC": "2024-01-08", "AETERM": "头痛"},  # 早于给药 → 触发 TIME_ANCHOR
    ],
    "EX": [
        {"EXSTDTC": "2024-01-10"},
    ],
}

checker = TemporalChecker(subject_data, config, subject_id="001-001")
findings = checker.collect_findings()
```

## 输出格式

### CoreGageFinding 结构

每条检查结果都是一个 `CoreGageFinding` 对象，包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `finding_id` | `str` | 唯一标识符（UUID） |
| `category` | `CheckCategory` | 检查类别（temporal/coding/safety/compliance/consistency/integrity） |
| `severity` | `Severity` | 严重级别（info/low/medium/high/critical） |
| `source` | `str` | 数据来源（lab/vital/ae/ae_sae/edc/consent 等） |
| `subject_id` | `str` | 受试者 ID |
| `visit_id` | `str` | 访视 ID |
| `form_id` | `str` | 表单 ID |
| `field_name` | `str` | 字段名称 |
| `message` | `str` | 人类可读的描述信息 |
| `details` | `Dict` | 详细数据（JSON 可序列化） |
| `timestamp` | `str` | ISO 8601 时间戳 |
| `status` | `CheckStatus` | 检查状态（pending/running/passed/failed/error/skipped） |

### CoreGageResult 结构

运行完成后返回的聚合结果：

| 字段 | 类型 | 说明 |
|------|------|------|
| `run_id` | `str` | 运行唯一标识符 |
| `config` | `CoreGageConfig` | 使用的配置 |
| `started_at` / `completed_at` | `str` | 开始/完成时间 |
| `total_findings` | `int` | 总发现数 |
| `findings_by_severity` | `Dict[str, int]` | 按严重级别统计 |
| `findings_by_category` | `Dict[str, int]` | 按类别统计 |
| `temporal_findings` | `List[CoreGageFinding]` | 时间序列检查结果 |
| `coding_findings` | `List[CoreGageFinding]` | 编码检查结果 |
| `safety_findings` | `List[CoreGageFinding]` | 安全性检查结果 |
| `compliance_findings` | `List[CoreGageFinding]` | 合规性检查结果 |

### 输出格式支持

| 格式 | 方法 | 说明 |
|------|------|------|
| JSON | `save_results(path, format="json")` | 默认格式，完整保留所有字段 |
| CSV | `save_results(path, format="csv")` | 需要 pandas，UTF-8-BOM 编码 |
| Excel | `save_results(path, format="xlsx")` | 需要 pandas + openpyxl，含 Summary/By Severity/By Category 工作表 |

## 项目结构

```
pyCoreGage-医学插件/
├── core_data.py          # 核心数据结构（CoreGageConfig/State/Finding/Result）
├── medcage.py            # 主入口（MedCage 类）
├── temporal_checker.py   # 时间序列检查模块
├── coding_checker.py     # 医学编码检查模块
├── safety_checker.py     # 安全性检查模块（含 L1-L3 趋势检查）
├── pkpd_checker.py       # PK/PD 检查模块
├── genetic_checker.py    # 基因检测检查模块
├── compliance_manager.py # 合规性检查模块
├── 实战案例/              # 实战案例数据与测试脚本
│   ├── DM.csv            # 受试者基本信息（100 条）
│   ├── AE.csv            # 不良事件（170 条）
│   ├── CM.csv            # 合并用药（104 条）
│   ├── VS.csv            # 生命体征（400 条）
│   ├── LB.csv            # 实验室检查（500 条）
│   ├── rules/            # 规则配置文件
│   │   └── hepatic_rules.yaml  # 肝毒性检测规则
│   ├── run_demo.py       # 演示运行脚本
│   └── test_lab_trends.py # 实验室趋势检查测试脚本
├── dictionaries/         # 医学词典（MedDRA/ICD-10/ATC/LOINC/SNOMED）
├── README.md             # 本文件
├── CONFIG_GUIDE.md       # 配置指南
└── TROUBLESHOOTING.md    # 故障排除
```

## 依赖

- **Python 3.8+**
- **PyYAML**（可选，用于加载 YAML 规则配置；无 PyYAML 时自动使用内置解析器）
- **pandas + openpyxl**（可选，仅用于 CSV/Excel 输出格式）

## 许可证

pyCoreGage 医学插件 — 仅供学习和研究使用。

---

*最后更新：2026-06-25*