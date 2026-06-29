# pyCoreGage 故障排除指南

> 常见问题、错误代码、性能优化和调试技巧。

## 目录

1. [常见问题](#常见问题)
2. [错误代码](#错误代码)
3. [性能优化](#性能优化)
4. [调试技巧](#调试技巧)

---

## 常见问题

### 1. 数据格式错误

#### 问题：日期字段无法解析

**现象**：检查结果中大量出现"缺少有效时间"或"时间解析失败"的发现。

**原因**：日期字段格式不被 `_parse_datetime()` 支持。

**支持的格式**：
- `%Y-%m-%d %H:%M:%S`（如 `2024-01-15 14:30:00`）
- `%Y-%m-%dT%H:%M:%S`（如 `2024-01-15T14:30:00`）
- `%Y-%m-%d`（如 `2024-01-15`）
- `%m/%d/%Y`（如 `01/15/2024`）
- `%d-%b-%Y`（如 `15-Jan-2024`）
- `%Y/%m/%d`（如 `2024/01/15`）

**解决方案**：
```python
# 方案一：统一日期格式
# 在加载数据前预处理日期字段
for record in lab_data:
    record["test_date"] = record["test_date"].strftime("%Y-%m-%d")

# 方案二：自定义 TemporalCheckConfig 字段名映射
config = TemporalCheckConfig(
    field_visit_date="VISIT_DATE",  # 使用你的字段名
    field_ae_start="AE_START_DATE",
)
```

#### 问题：数值字段包含非数字字符

**现象**：实验室值或生命体征值被跳过，无发现输出。

**原因**：`_parse_numeric()` 无法解析包含逗号、空格或特殊字符的值。

**解决方案**：
```python
# 预处理数据，清理数值字段
for record in lab_data:
    record["test_value"] = float(str(record["test_value"]).replace(",", "").strip())
```

#### 问题：数据集键名不匹配

**现象**：检查器日志显示"数据集域不存在"，跳过检查。

**原因**：`state.domains` 中的键名与检查器期望的不一致。

**各检查器期望的域键名**：

| 检查器 | 期望的域键名 |
|--------|------------|
| TemporalChecker | `VIS`, `AE`, `EX`, `CM` |
| CodingChecker (MedDRA) | `AE` |
| CodingChecker (ICD-10) | `DI`, `CM` |
| CodingChecker (ATC) | `CM`, `EX` |
| CodingChecker (LOINC) | `LB` |
| SafetyChecker | `LAB`, `VITAL`, `AE`, `AE_SAE`, `MED` |
| PKPDChecker | `PK`, `PD`, `EX` |
| GeneticChecker | `GENETIC`, `CM` |
| ComplianceManager | `CONSENT`, `VISIT`, `EDC` |

**解决方案**：确保 `state.domains` 使用正确的键名，或通过 `TemporalCheckConfig` 的 `ds_*` 参数自定义。

### 2. 配置错误

#### 问题：`min_severity` 过滤掉了所有发现

**现象**：`result.total_findings == 0`，但数据明显有问题。

**原因**：`min_severity` 设置过高（如 `CRITICAL`），所有发现都被过滤。

**解决方案**：
```python
config = CoreGageConfig(min_severity=Severity.INFO)  # 接收所有级别
# 或
config = CoreGageConfig(min_severity=Severity.LOW)   # 接收 LOW 及以上
```

#### 问题：模块开关导致某些检查未运行

**现象**：期望的安全性检查未执行。

**原因**：`enable_safety = False`。

**解决方案**：
```python
config = CoreGageConfig(
    enable_temporal=True,
    enable_coding=True,
    enable_safety=True,
    enable_compliance=True,
)
```

#### 问题：YAML 配置文件解析失败

**现象**：肝毒性规则使用默认值而非配置文件中的值。

**原因**：缺少 PyYAML，且内置简单解析器无法处理复杂 YAML 语法。

**解决方案**：
```bash
# 安装 PyYAML
pip install pyyaml
```

或确保 YAML 文件只使用简单格式（键值对、缩进 2 空格、最多 3 层嵌套）：
```yaml
# ✅ 支持
hy_window_days: 28
hys_law:
  enzyme_xuln_gte: 3

# ❌ 不支持（列表、锚点等高级语法）
rules:
  - name: rule1
    params: &params
      threshold: 3
  - name: rule2
    params: *params
```

### 3. 依赖问题

#### 问题：`ModuleNotFoundError: No module named 'pyyaml'`

**解决方案**：
```bash
pip install pyyaml
```

#### 问题：`ImportError: pandas is required for xlsx output`

**现象**：调用 `save_results(path, format="xlsx")` 时报错。

**解决方案**：
```bash
pip install pandas openpyxl
```

或改用 JSON 格式输出：
```python
mc.save_results("output/report.json", format="json")
```

#### 问题：`ModuleNotFoundError: No module named 'core_data'`

**原因**：当前工作目录不在 pyCoreGage 根目录下。

**解决方案**：
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))  # 添加项目根目录
```

### 4. 医学词典问题

#### 问题：编码检查发现大量"不在参考字典中"

**原因**：内置词典仅包含示例数据，不包含完整 MedDRA/ICD-10/ATC/LOINC 词典。

**解决方案**：

**方式一：使用外部参考表**
```python
# 设置环境变量
import os
os.environ["PYCOREGAGE_CODING_REF_DIR"] = "/path/to/reference/data"

# 或在配置中指定
config = CoreGageConfig()
# coding_ref_dir 属性（coding_checker.py 中读取）
```

**方式二：提供外部 CSV 参考表**

期望的文件格式：
- `meddra_llt.csv`：列 `llt_code`, `pt_code`, `soc_code`
- `icd10_codes.csv`：列 `code`, `chapter`, `description`
- `atc_codes.csv`：列 `atc_code`, `level1`, `description`
- `loinc_codes.csv`：列 `loinc_code`, `short_name`, `long_name`

**方式三：使用内置词典目录**

词典位于 `dictionaries/` 目录：
```
dictionaries/
├── meddra/meddra_codes.json
├── icd10/icd10_codes.json
├── atc/atc_codes.json
├── loinc/loinc_codes.json
└── snomed/snomed_codes.json
```

### 5. 数据源问题

#### 问题：`state.get_data(DataSource.LAB)` 返回 None

**原因**：数据未正确加载到 `CoreGageState`。

**解决方案**：
```python
# 确认数据已加载
state.set_data(DataSource.LAB, lab_data_list)

# 验证
print(state.get_data(DataSource.LAB))  # 应输出数据列表
```

#### 问题：CSV 文件编码问题

**现象**：中文内容乱码或解析失败。

**解决方案**：
```python
# 确保 CSV 文件使用 UTF-8 编码
# 如果使用 Python csv 模块读取
with open("data.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    records = list(reader)
```

---

## 错误代码

### 常见错误码与解决方案

| 错误类型 | 错误信息/现象 | 解决方案 |
|---------|-------------|---------|
| `FileNotFoundError` | `Data file not found: xxx.csv` | 检查文件路径是否正确，确保文件存在 |
| `ValueError` | `Provide either config or config_path, not both` | `MedCage()` 构造函数不能同时传入 `config` 和 `config_path` |
| `ImportError` | `pandas is required for xlsx output` | 安装 pandas：`pip install pandas openpyxl` |
| `ImportError` | `No module named 'pyyaml'` | 安装 PyYAML：`pip install pyyaml` |
| `KeyError` | 在 `state.domains` 中找不到域 | 确认域键名正确，或检查数据是否已加载 |
| `TypeError` | `NoneType object is not iterable` | 检查 `state.get_data()` 返回值是否为 None |
| `ValueError` | `Invalid severity value` | 确认 `Severity` 枚举值正确：`info`/`low`/`medium`/`high`/`critical` |
| `ValueError` | `Invalid CheckCategory value` | 确认 `CheckCategory` 枚举值正确 |

### 错误处理最佳实践

```python
from medcage import MedCage
from core_data import CoreGageConfig

try:
    mc = MedCage(config_path="config.json")
    mc.load_data("data/edc.csv")
    result = mc.run()
    mc.save_results("output/report.json")
except FileNotFoundError as e:
    print(f"文件未找到: {e}")
except ValueError as e:
    print(f"配置错误: {e}")
except ImportError as e:
    print(f"缺少依赖: {e}")
except Exception as e:
    print(f"未知错误: {e}")
    raise
```

---

## 性能优化

### 大数据集处理建议

#### 1. 启用缓存

```python
config = CoreGageConfig(
    cache_enabled=True,
    cache_ttl_seconds=3600,  # 1 小时缓存
)
```

#### 2. 调整并行工作线程数

```python
config = CoreGageConfig(
    parallel_workers=8,  # 根据 CPU 核心数调整
)
```

#### 3. 分批处理

对于超大数据集（>10 万条记录），建议分批处理：

```python
# 按受试者分批
subjects = list(set(r["subject_id"] for r in all_data))
batch_size = 100

for i in range(0, len(subjects), batch_size):
    batch_subjects = subjects[i:i + batch_size]
    batch_data = [r for r in all_data if r["subject_id"] in batch_subjects]

    state = CoreGageState(config=config)
    state.set_data(DataSource.LAB, batch_data)
    checker = SafetyChecker(config=config, state=state)
    findings = checker.check()

    # 合并结果
    all_findings.extend(findings)
```

#### 4. 减少不必要的检查

```python
config = CoreGageConfig(
    enable_temporal=True,
    enable_coding=False,   # 如果编码已验证，可关闭
    enable_safety=True,
    enable_compliance=False,  # 如果合规性已确认，可关闭
)
```

#### 5. 使用 `min_severity` 过滤

```python
config = CoreGageConfig(min_severity=Severity.MEDIUM)  # 只关注 MEDIUM 及以上
```

### 内存优化

- 实验室数据：建议按受试者+检验项目分组，避免一次性加载全部数据
- 时间序列数据：使用生成器而非列表，减少内存占用
- 输出格式：JSON 格式比 Excel 格式内存占用更小

### 日志级别优化

生产环境中建议将日志级别设为 `WARNING` 或 `ERROR`，减少 I/O 开销：

```python
config = CoreGageConfig(log_level="WARNING")
```

---

## 调试技巧

### 启用调试日志

```python
import logging

# 全局调试日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# 或针对特定模块
logging.getLogger("pyCoreGage").setLevel(logging.DEBUG)
logging.getLogger("pyCoreGage.safety").setLevel(logging.DEBUG)
logging.getLogger("pyCoreGage.temporal").setLevel(logging.DEBUG)
```

### 逐步调试

```python
# 单独运行某个检查器
from safety_checker import SafetyChecker

checker = SafetyChecker(config=config, state=state)

# 逐步执行各检查方法
checker._check_lab_abnormalities()
print(f"Lab abnormalities: {len(checker._findings)}")

checker._check_vital_signs()
print(f"Vital signs: {len(checker._findings)}")

checker._check_sae_criteria()
print(f"SAE criteria: {len(checker._findings)}")

checker._check_lab_trends_general()
print(f"Lab trends L1: {len(checker._findings)}")

checker._check_lab_hepatic_toxicity()
print(f"Lab trends L2: {len(checker._findings)}")

checker._check_lab_statistical_outliers()
print(f"Lab trends L3: {len(checker._findings)}")
```

### 验证数据加载

```python
# 检查数据是否正确加载
for source, data in state.data.items():
    if isinstance(data, list):
        print(f"{source.value}: {len(data)} records")
    else:
        print(f"{source.value}: {type(data)}")

# 检查词典是否正确加载
for name, data in state.dictionaries.items():
    print(f"Dictionary '{name}': {type(data)}")
```

### 使用 test_lab_trends.py 验证功能

```bash
# 运行实验室趋势检查测试
cd pyCoreGage-医学插件/实战案例
python test_lab_trends.py
```

该脚本会：
1. 生成合成实验室数据（20 名受试者 × 5 个访视 × 8 个检验项目）
2. 运行 L1→L3 趋势检查
3. 输出详细结果到 `test_lab_trends_output.json`

### 使用 test_sae_candidates.py 验证 SAE 检查

```bash
cd pyCoreGage-医学插件
python test_sae_candidates.py
```

该脚本会：
1. 加载 `实战案例/AE.csv` 和 `实战案例/CM.csv`
2. 运行 SAE 候选列表生成
3. 验证 ICH E2A、CTCAE≥3、时间可疑、未标记等检查

### 查看检查结果摘要

```python
# 打印摘要
mc.print_summary()

# 查看按严重级别统计
print(result.findings_by_severity)
# 输出示例: {"info": 5, "low": 10, "medium": 20, "high": 5, "critical": 2}

# 查看按类别统计
print(result.findings_by_category)
# 输出示例: {"safety": 35, "temporal": 10, "coding": 5, "compliance": 2}
```

### 使用 `get_compliance_summary()` 查看合规性摘要

```python
manager = ComplianceManager(config=config, state=state)
findings = manager.check()
summary = manager.get_compliance_summary()
print(summary)
# 输出示例:
# {
#   "total_findings": 10,
#   "by_standard": {"ICH-GCP": 5, "FDA-21CFR11": 3, "GDPR": 2},
#   "by_severity": {"high": 5, "medium": 3, "critical": 2},
#   "deviations_tracked": 3,
#   "unresolved_deviations": 1
# }
```

---

## 获取帮助

- 查看源代码中的 docstring 获取 API 文档
- 运行 `test_lab_trends.py` 和 `test_sae_candidates.py` 验证功能
- 检查日志输出获取调试信息

---

*最后更新：2026-06-25*