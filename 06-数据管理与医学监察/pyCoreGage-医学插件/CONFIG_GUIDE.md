# pyCoreGage 配置指南

> 详细说明如何配置 pyCoreGage 医学插件的各项参数。

## 配置文件结构

pyCoreGage 使用 `CoreGageConfig` 数据类作为配置容器。配置可通过 Python 代码直接创建，也可从 JSON 文件加载。

### JSON 配置文件示例

```json
{
  "project_id": "my_trial",
  "protocol_id": "PROT-001",
  "version": "1.0.0",

  "enable_temporal": true,
  "enable_coding": true,
  "enable_safety": true,
  "enable_compliance": true,

  "min_severity": "low",

  "dict_dir": "dictionaries",
  "meddra_version": "26.0",
  "icd10_version": "2024",
  "loinc_version": "2.74",

  "output_dir": "output",
  "output_format": "json",
  "log_level": "INFO",

  "temporal_max_gap_days": 365,
  "temporal_tolerance_days": 1,

  "safety_lab_grades": ["3", "4", "5"],
  "safety_vital_alerts": {},

  "compliance_regions": ["US", "EU", "CN"],
  "compliance_standards": ["ICH-GCP", "FDA-21CFR11"],

  "parallel_workers": 4,
  "cache_enabled": true,
  "cache_ttl_seconds": 3600
}
```

### Python 代码配置

```python
from core_data import CoreGageConfig, Severity

config = CoreGageConfig(
    project_id="my_trial",
    protocol_id="PROT-001",
    min_severity=Severity.LOW,
    enable_temporal=True,
    enable_coding=True,
    enable_safety=True,
    enable_compliance=True,
    output_format="json",
    log_level="DEBUG",
)
```

## 核心配置参数

### 身份与版本

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `project_id` | `str` | `""` | 项目唯一标识符 |
| `protocol_id` | `str` | `""` | 方案编号 |
| `version` | `str` | `"1.0.0"` | 插件版本 |

### 模块开关

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enable_temporal` | `bool` | `True` | 是否启用时间序列检查 |
| `enable_coding` | `bool` | `True` | 是否启用医学编码检查 |
| `enable_safety` | `bool` | `True` | 是否启用安全性检查 |
| `enable_compliance` | `bool` | `True` | 是否启用合规性检查 |

### 严重性阈值

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `min_severity` | `Severity` | `Severity.LOW` | 最低接收严重级别 |

严重级别从低到高：`INFO` → `LOW` → `MEDIUM` → `HIGH` → `CRITICAL`

### 词典路径

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `dict_dir` | `str` | `"dictionaries"` | 医学词典目录 |
| `meddra_version` | `str` | `""` | MedDRA 词典版本 |
| `icd10_version` | `str` | `""` | ICD-10 词典版本 |
| `loinc_version` | `str` | `""` | LOINC 词典版本 |

### 输出配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `output_dir` | `str` | `"output"` | 输出目录 |
| `output_format` | `str` | `"json"` | 输出格式：`json` / `csv` / `xlsx` |
| `log_level` | `str` | `"INFO"` | 日志级别：`DEBUG` / `INFO` / `WARNING` / `ERROR` |

### 时间序列配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `temporal_max_gap_days` | `int` | `365` | 访视间最大间隔天数 |
| `temporal_tolerance_days` | `int` | `1` | 访视时间容差天数 |

### 安全性配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `safety_lab_grades` | `List[str]` | `["3", "4", "5"]` | 关键实验室异常等级 |
| `safety_vital_alerts` | `Dict` | `{}` | 生命体征告警阈值 |

### 合规性配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `compliance_regions` | `List[str]` | `["US", "EU", "CN"]` | 适用监管区域 |
| `compliance_standards` | `List[str]` | `["ICH-GCP", "FDA-21CFR11"]` | 适用合规标准 |

### 高级配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `parallel_workers` | `int` | `4` | 并行工作线程数 |
| `cache_enabled` | `bool` | `True` | 是否启用缓存 |
| `cache_ttl_seconds` | `int` | `3600` | 缓存 TTL（秒） |

## 规则配置

### 时间序列检查规则

通过 `TemporalCheckConfig` 配置：

```python
from temporal_checker import TemporalCheckConfig

config = TemporalCheckConfig(
    # 时间窗：给药前允许合并用药的时间阈值（小时），默认 24h
    concomitant_window_hours=24.0,

    # 是否允许 AE 时间早于给药时间（部分方案允许，默认 False）
    allow_ae_before_dosing=False,

    # 必须存在的访视阶段（默认全部）
    required_visits=("SCREENING", "BASELINE", "DOSING", "FOLLOWUP"),

    # 缺失时间容忍天数（超过该天数判定为缺失）
    missing_tolerance_days=30,

    # 时间字段名映射（支持不同数据集命名风格）
    field_visit_date="VISITDT",
    field_visit_name="VISIT",
    field_ae_start="AESTDTC",
    field_ae_end="AEENDTC",
    field_dosing_date="EXSTDTC",
    field_concom_start="COSTDTC",
    field_concom_end="COENDTC",

    # 数据集键名
    ds_visits="VIS",
    ds_ae="AE",
    ds_exposure="EX",
    ds_concom="CM",
)
```

### 肝毒性检测规则（YAML）

肝毒性检测规则通过 YAML 文件配置，位于 `实战案例/rules/hepatic_rules.yaml`：

```yaml
# 酶峰后胆红素窗口天数（Hy's Law 时间窗口）
hy_window_days: 28

# Hy's Law 候选者判定标准
hys_law:
  enzyme_xuln_gte: 3       # ALT/AST ≥ 3×ULN（酶学升高阈值）
  tbil_xuln_gt: 2          # TBIL > 2×ULN（胆红素升高阈值）
  alp_xuln_lt: 2           # ALP < 2×ULN（排除胆汁淤积型）

# R-ratio 分类阈值
# R-ratio = (ALT或AST / ULN) / (ALP / ULN)
r_ratio:
  hepatocellular_gte: 5    # R ≥ 5 → 肝细胞型损伤
  cholestatic_lte: 2       # R ≤ 2 → 胆汁淤积型损伤
  # 2 < R < 5 → 混合型损伤

# 筛查阈值（用于快速筛选潜在肝毒性信号）
screening:
  alt_xuln_gte: 5          # ALT ≥ 5×ULN（高优先级筛查）
  alp_xuln_gte: 2          # ALP ≥ 2×ULN（胆汁淤积筛查）
  alt_xuln_and_tbil_xuln:
    alt_xuln_gte: 3        # ALT ≥ 3×ULN 且
    tbil_xuln_gt: 2        # TBIL > 2×ULN（联合筛查）
```

规则由 `SafetyChecker._load_hepatic_rules()` 加载，支持 PyYAML 或内置简单解析器。

### 安全性检查规则

通过 `LabAbnormalityRule` 和 `VitalSignRule` 配置：

```python
from safety_checker import SafetyChecker, LabAbnormalityRule, VitalSignRule

checker = SafetyChecker(config=config, state=state)

# 添加实验室异常规则
checker.add_lab_abnormality_rule(LabAbnormalityRule(
    test_code="CR",
    test_name="肌酐",
    unit="μmol/L",
    # CTCAE 阈值: (low_critical, low_severe, low_moderate, high_moderate, high_severe, high_critical)
    thresholds=(30.0, 50.0, 80.0, 150.0, 250.0, 400.0),
    normal_low=53.0,
    normal_high=115.0,
))

# 添加生命体征规则
checker.add_vital_sign_rule(VitalSignRule(
    parameter="heart_rate",
    alert_low=50,
    alert_high=100,
    critical_low=40,
    critical_high=150,
    unit="bpm",
))
```

### 合规性检查规则

通过 `ComplianceRule` 配置：

```python
from compliance_manager import ComplianceManager, ComplianceRule, ComplianceStandard
from core_data import Severity

manager = ComplianceManager(config=config, state=state)

manager.add_compliance_rule(ComplianceRule(
    rule_id="CUSTOM-001",
    name="Custom Check Rule",
    standard=ComplianceStandard.ICH_GCP,
    description="自定义检查规则描述",
    severity=Severity.HIGH,
    enabled=True,
))
```

## 阈值设置

### 实验室异常阈值

阈值采用 CTCAE 风格 6 参数元组：

```
(low_critical, low_severe, low_moderate, high_moderate, high_severe, high_critical)
```

分级逻辑：
- Grade 5: `value <= low_critical` 或 `value >= high_critical`
- Grade 4: `value <= low_severe` 或 `value >= high_severe`
- Grade 3: `value <= low_moderate` 或 `value >= high_moderate`
- Grade 2: `value < normal_low` 或 `value > normal_high`
- Grade 1: 正常范围内

### 生命体征阈值

| 参数 | 告警范围 | 危急范围 | 单位 |
|------|---------|---------|------|
| 心率 | 50–100 | 40–150 | bpm |
| 收缩压 | 90–180 | 80–200 | mmHg |
| 舒张压 | 60–110 | 50–120 | mmHg |
| 体温 | 36.0–38.0 | 35.0–39.5 | °C |
| 呼吸频率 | 12–20 | 8–30 | breaths/min |

### PK/PD 参数正常范围

| 参数 | 范围 | 单位 |
|------|------|------|
| AUC | 0.1 – 10000 | ng·h/mL |
| Cmax | 0.1 – 10000 | ng/mL |
| Tmax | 0 – 24 | h |
| 半衰期 | 0.1 – 100 | h |
| 清除率 | 0.1 – 1000 | L/h |
| 分布容积 | 0.1 – 10000 | L |
| EC50 | 0.01 – 1000 | ng/mL |
| Emax | 0 – 100 | % |
| Hill 系数 | 0.1 – 10 | 无量纲 |

## 数据源配置

### 支持的数据源

| 数据源 | DataSource 枚举 | 说明 |
|--------|----------------|------|
| EDC | `DataSource.EDC` | 电子数据采集系统 |
| 实验室 | `DataSource.LAB` | 实验室检查数据 |
| 不良事件 | `DataSource.AE` | 不良事件数据 |
| SAE | `DataSource.AE_SAE` | 严重不良事件数据 |
| 合并用药 | `DataSource.MED` | 合并用药/药物暴露数据 |
| 生命体征 | `DataSource.VITAL` | 生命体征数据 |
| 人口学 | `DataSource.DEMOGRAPHIC` | 受试者基本信息 |
| 知情同意 | `DataSource.CONSENT` | 知情同意数据 |
| 访视 | `DataSource.VISIT` | 访视记录 |

### 加载数据

```python
from core_data import DataSource

# 方式一：通过 MedCage 加载
mc.load_data("data/edc.csv", source=DataSource.EDC, format="csv")
mc.load_data("data/lab.xlsx", source=DataSource.LAB, format="xlsx")

# 方式二：直接通过 CoreGageState 加载
state.set_data(DataSource.LAB, lab_data_list)
state.set_data(DataSource.AE, ae_data_list)
```

### 数据格式要求

数据以字典列表形式传入，每个字典代表一条记录。字段名需与检查器期望的字段名匹配：

| 数据源 | 期望字段名 | 说明 |
|--------|-----------|------|
| LAB | `subject_id`, `test_code`, `test_value`, `test_date`, `uln`, `visit` | 实验室检查 |
| AE | `subject_id`, `ae_term`, `onset_date`, `severity`, `seriousness` | 不良事件 |
| VITAL | `subject_id`, `parameter`, `value`, `vital_date` | 生命体征 |
| VIS | `VISIT`, `VISITDT` | 访视记录 |
| EX | `EXSTDTC` | 给药记录 |
| CM | `COSTDTC`, `COENDTC`, `COSTERM` | 合并用药 |

## 输出配置

### 输出格式

| 格式 | 说明 | 依赖 |
|------|------|------|
| JSON | 完整保留所有字段，支持嵌套结构 | 无 |
| CSV | 扁平化输出，UTF-8-BOM 编码 | pandas |
| Excel | 多工作表（All Findings / Summary / By Severity / By Category） | pandas + openpyxl |

### 自定义输出

```python
# 保存为 JSON
mc.save_results("output/report.json", format="json")

# 保存为 CSV
mc.save_results("output/report.csv", format="csv")

# 保存为 Excel
mc.save_results("output/report.xlsx", format="xlsx")

# 直接访问结果对象
result = mc.result
print(result.total_findings)
print(result.findings_by_severity)
```

## 配置加载与保存

```python
from core_data import CoreGageConfig

# 从 JSON 文件加载
config = CoreGageConfig.load("config.json")

# 保存为 JSON 文件
config.save("config_backup.json")

# 从字典创建
config = CoreGageConfig.from_dict({
    "project_id": "my_trial",
    "min_severity": "low",
})

# 转为字典
d = config.to_dict()
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `PYCOREGAGE_CODING_REF_DIR` | 外部编码参考表目录（覆盖内置 MedDRA/ICD-10/ATC/LOINC 数据） |

## 参考

- 核心数据结构：`core_data.py`
- 时间序列配置：`TemporalCheckConfig` in `temporal_checker.py`
- 肝毒性规则：`实战案例/rules/hepatic_rules.yaml`
- 安全性规则：`LabAbnormalityRule` / `VitalSignRule` in `safety_checker.py`

---

*最后更新：2026-06-25*