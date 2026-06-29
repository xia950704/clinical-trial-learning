# 实战案例：临床试验数据管理

> 使用 pyCoreGage 医学插件进行真实场景的临床试验数据检查。

## 案例概述

本案例演示如何使用 pyCoreGage 医学插件对合成临床试验数据进行多维度检查，包括时间序列、医学编码、安全性（含 L1→L3 趋势检查）、PK/PD 和基因检测。

### 研究背景

- **研究类型**：多中心、随机、双盲、安慰剂对照 III 期临床试验
- **适应症**：心脏术后新发房颤
- **干预措施**：尼非卡兰 vs 胺碘酮
- **主要终点**：4 小时内房颤转复率
- **样本量**：100 例受试者（1:1 随机分组）

### 数据集说明

| 数据域 | 文件 | 记录数 | 关键字段 |
|--------|------|--------|---------|
| **DM** | `DM.csv` | 100 | `SUBJID`, `SITEID`, `AGE`, `SEX`, `ARM`, `SCRNDTC` |
| **AE** | `AE.csv` | 170 | `SUBJID`, `AETERM`, `AESTDTC`, `AEENDTC`, `AETOXGR`, `AEREL`, `AESEV` |
| **CM** | `CM.csv` | 104 | `SUBJID`, `CMNAME`, `COSTDTC`, `COSTIME`, `CMDOSE` |
| **VS** | `VS.csv` | 400 | `SUBJID`, `VISIT`, `VSDTC`, `VSSBP`, `VSDBP`, `VSHR`, `VSTEMP` |
| **LB** | `LB.csv` | 500 | `SUBJID`, `LBTESTCD`, `LBDTC`, `LBORRES`, `LBORRESU`, `LBSTNRLO`, `LBSTNRHI` |

**注意**：本数据集为合成数据，仅用于演示和测试。

## 文件结构

```
实战案例/
├── DM.csv                  # 受试者基本信息（100 条）
├── AE.csv                  # 不良事件（170 条）
├── CM.csv                  # 合并用药（104 条）
├── VS.csv                  # 生命体征（400 条）
├── LB.csv                  # 实验室检查（500 条）
├── rules/                  # 规则配置文件
│   └── hepatic_rules.yaml  # 肝毒性检测规则（Hy's Law + R-ratio）
├── run_demo.py             # 演示运行脚本
├── test_lab_trends.py      # 实验室趋势检查测试脚本（L1→L3）
├── test_lab_trends_output.json  # 趋势检查结果输出
├── rule_registry_medical.json  # 规则注册表
└── README.md               # 本文件
```

## 运行指南

### 方式一：运行演示脚本

```bash
cd pyCoreGage-医学插件/实战案例
python run_demo.py
```

该脚本会：
1. 初始化 `MedCage` 并加载配置
2. 加载 `data/` 目录下的所有数据
3. 运行所有启用的检查器
4. 保存结果到 `outputs/report.json`
5. 打印检查摘要

### 方式二：运行实验室趋势检查测试

```bash
cd pyCoreGage-医学插件/实战案例
python test_lab_trends.py
```

该脚本会：
1. 生成合成实验室数据（20 名受试者 × 5 个访视 × 8 个检验项目）
2. 运行 L1→L3 趋势检查：
   - **L1**：通用趋势检查（按检验项目+访视分组，检测分布偏移）
   - **L2**：肝毒性检查（Hy's Law + R-ratio 分类）
   - **L3**：统计异常值检测（IQR 法）
3. 输出详细结果到 `test_lab_trends_output.json`
4. 运行单元测试（`_compute_stats`、`_merge_dict`、YAML 解析）

### 方式三：运行 SAE 候选列表生成测试

```bash
cd pyCoreGage-医学插件
python test_sae_candidates.py
```

该脚本会：
1. 加载 `实战案例/AE.csv` 和 `实战案例/CM.csv`
2. 运行 SAE 候选列表生成（ICH E2A / CTCAE≥3 / 时间可疑 / 未标记）
3. 验证检查结果

### 方式四：Python 代码直接调用

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core_data import CoreGageConfig, CoreGageState, DataSource, Severity
from safety_checker import SafetyChecker

# 加载数据
import csv

def load_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

ae_data = load_csv("实战案例/AE.csv")
cm_data = load_csv("实战案例/CM.csv")

# 初始化
config = CoreGageConfig(min_severity=Severity.INFO)
state = CoreGageState(config=config)
state.set_data(DataSource.AE, ae_data)
state.set_data(DataSource.MED, cm_data)

# 运行检查
checker = SafetyChecker(config=config, state=state)
findings = checker.check()

print(f"Total findings: {len(findings)}")
for f in findings[:5]:
    print(f"[{f.severity.value}] {f.message[:80]}")
```

## 结果解读

### 实验室趋势检查结果（test_lab_trends.py）

运行 `test_lab_trends.py` 后，结果输出到 `test_lab_trends_output.json`，包含：

#### L1 通用趋势检查

检测检验项目在不同访视之间的分布偏移。当某检验项目在后续访视的中位数相对于基线变化超过 20% 时，触发发现。

**示例发现**：
```
L1 Trend: 'CR' median increased from 65.0 (Baseline) to 135.0 (Week 8) (107.7% change)
```

#### L2 肝毒性检查（Hy's Law）

检测满足 Hy's Law 标准的肝毒性候选者：
1. ALT/AST ≥ 3×ULN
2. ALP < 2×ULN（排除胆汁淤积型）
3. TBIL > 2×ULN（在酶峰后 28 天内）

同时计算 R-ratio 进行分类：
- R ≥ 5：肝细胞型损伤
- R ≤ 2：胆汁淤积型损伤
- 2 < R < 5：混合型损伤

**示例发现**：
```
L2 Hy's Law candidate: S001 — ALT=120.0 (3.0×ULN), TBIL=50.0 (2.4×ULN),
ALP=60.0 (0.5×ULN), R-ratio=6.0 (hepatocellular)
```

#### L3 统计异常值检测（IQR）

使用四分位距（IQR）方法检测统计异常值。当某检验值超出 `[Q1 - 1.5×IQR, Q3 + 1.5×IQR]` 范围时，触发发现。

**示例发现**：
```
L3 Outlier: 'HGB' value 80.00 for subject S010 at Week 8 is below IQR range [110.00, 160.00]
```

### SAE 候选列表结果（test_sae_candidates.py）

SAE 候选列表包含四类发现：

| 类别 | 说明 | 严重级别 |
|------|------|---------|
| ICH E2A | 满足 ICH E2A 标准（死亡/危及生命/住院/残疾/先天异常） | HIGH/CRITICAL |
| CTCAE ≥ 3 | CTCAE 分级 ≥ 3 的 AE | HIGH |
| 时间可疑 | AE 起始时间在给药后 7 天内 | MEDIUM |
| 未标记 | CTCAE ≥ 3 但未标记为 SAE | MEDIUM |

### 综合检查结果解读

运行 `run_demo.py` 后，结果保存在 `outputs/report.json`，包含：

```json
{
  "run_id": "xxx-xxx-xxx",
  "total_findings": 150,
  "findings_by_severity": {
    "info": 10,
    "low": 20,
    "medium": 50,
    "high": 40,
    "critical": 30
  },
  "findings_by_category": {
    "safety": 80,
    "temporal": 40,
    "coding": 20,
    "compliance": 10
  }
}
```

**解读建议**：
1. **CRITICAL 级别**：立即处理，可能涉及受试者安全或严重合规问题
2. **HIGH 级别**：优先处理，可能影响试验结论
3. **MEDIUM 级别**：计划处理，常规数据清理
4. **LOW/INFO 级别**：参考信息，可在后续清理中处理

## 扩展指南

### 如何添加新的检查规则

#### 步骤 1：创建新的检查器模块

```python
# new_checker.py
from core_data import CoreGageConfig, CoreGageState, CoreGageFinding, CheckCategory, Severity

class NewChecker:
    def __init__(self, config: CoreGageConfig, state: CoreGageState):
        self.config = config
        self.state = state
        self._findings = []

    def check(self) -> list:
        self._findings = []
        self._check_something()
        return self._findings

    def _check_something(self):
        # 实现检查逻辑
        self._findings.append(CoreGageFinding(
            category=CheckCategory.CONSISTENCY,
            severity=Severity.MEDIUM,
            source="new",
            message="发现某个问题",
        ))
```

#### 步骤 2：在 MedCage 中注册

在 `medcage.py` 的 `_init_checkers()` 方法中添加：

```python
if self.config.enable_new:  # 需要在 CoreGageConfig 中添加此开关
    self._checkers["new"] = NewChecker(
        config=self.config, state=self.state
    )
```

#### 步骤 3：添加配置开关

在 `core_data.py` 的 `CoreGageConfig` 中添加：

```python
enable_new: bool = True
```

### 如何自定义阈值

#### 修改肝毒性阈值

编辑 `实战案例/rules/hepatic_rules.yaml`：

```yaml
hy_window_days: 14        # 缩短时间窗口
hys_law:
  enzyme_xuln_gte: 5      # 提高酶学阈值
  tbil_xuln_gt: 3         # 提高胆红素阈值
```

#### 修改实验室异常阈值

```python
from safety_checker import LabAbnormalityRule

checker.add_lab_abnormality_rule(LabAbnormalityRule(
    test_code="ALT",
    test_name="丙氨酸氨基转移酶",
    unit="U/L",
    thresholds=(5.0, 10.0, 20.0, 80.0, 200.0, 500.0),
    normal_low=9.0,
    normal_high=50.0,
))
```

#### 修改 PK/PD 参数范围

```python
from pkpd_checker import PKPDChecker

checker = PKPDChecker(state=state, config=config)
checker.pk_normal_ranges["AUC"]["max"] = 50000  # 扩大 AUC 上限
```

### 如何添加自定义数据源

```python
from core_data import DataSource

# 注册自定义数据源
state.set_data(DataSource.EDC, custom_data_list)

# 在检查器中访问
custom_data = self.state.get_data(DataSource.EDC)
```

### 如何自定义输出格式

```python
# 保存为 JSON（默认）
mc.save_results("output/report.json", format="json")

# 保存为 CSV
mc.save_results("output/report.csv", format="csv")

# 保存为 Excel（含多个工作表）
mc.save_results("output/report.xlsx", format="xlsx")

# 自定义输出处理
result = mc.result
for finding in result.all_findings:
    if finding.severity == Severity.CRITICAL:
        # 发送告警通知
        send_alert(finding)
```

## 注意事项

1. **示例数据**：本数据集为合成数据，仅用于演示和测试
2. **生产环境**：生产环境需使用真实临床试验数据
3. **数据隐私**：真实数据需进行去标识化处理
4. **许可合规**：使用医学词典需遵守官方许可协议
5. **依赖安装**：运行测试脚本前确保已安装所需依赖

---

*最后更新：2026-06-25*