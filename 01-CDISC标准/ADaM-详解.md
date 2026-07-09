---
tags: [CDISC, ADaM, 临床试验, 分析数据集, FDA提交]
status: active
created: 2026-06-25
updated: 2026-06-25
vault_link: 01-CDISC标准/ADaM-详解.md
---

# ADaM 详解 — Analysis Data Model

> CDISC 标准的分析层：从 SDTM 到分析就绪数据集

---

## 一、什么是 ADaM？

**ADaM（Analysis Data Model）** 是 CDISC 制定的临床试验分析数据集标准，用于：

| 用途 | 说明 |
|------|------|
| **统计分析** | 为统计分析提供分析就绪的数据 |
| **结果复现** | 确保分析结果可追溯、可复现 |
| **FDA 提交** | 与 SDTM 一起作为 FDA 提交的标准格式 |
| **变量衍生** | 包含 SDTM 中没有的分析衍生变量 |

---

## 二、ADaM 核心概念

### 2.1 数据集类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **BDS（Basic Data Structure）** | 基本数据结构，最常用 | ADLB, ADVS, ADAE |
| **TFL（Tabulation, Listing, Figure）** | 表格、清单、图表 | 由 BDS 生成 |
| **ADSL（Subject-Level）** | 受试者级数据集 | 每个受试者一行 |
| **ADPC（Pharmacokinetic）** | 药代动力学 | 单次测量多次 |
| **ADTTE（Time-to-Event）** | 生存分析 | 时间 - 事件数据 |

### 2.2 变量分类

| 类型 | 说明 | 示例 |
|------|------|------|
| **Identifier（标识符）** | 唯一标识 | STUDYID, USUBJID, PARAMCD |
| **Grouping（分组）** | 分组变量 | TRT01P, SEX, RACE |
| **Timing（时序）** | 时间变量 | ADT, ADY, AVISIT |
| **Result/Measurement（结果）** | 观测值 | AVAL, AVALC |
| **Qualifier（限定符）** | 补充信息 | ABLFL, BASETYPE |

---

## 三、ADaM 数据集类型详解

### 3.1 ADSL — Subject-Level Analysis Dataset

**每个受试者一行**，包含所有受试者级别的衍生变量。

| 变量 | 说明 | 示例 | 来源 |
|------|------|------|------|
| STUDYID | 研究标识 | TDF001 | DM |
| USUBJID | 受试者标识 | TDF001-1001 | DM |
| TRT01P | 首次治疗组 | Drug X | DM.ARM |
| TRTSDT | 首次给药日期 | 2024-01-15 | EX |
| TRTEDT | 末次给药日期 | 2024-06-20 | EX |
| AGE | 年龄 | 45 | DM |
| SEX | 性别 | M | DM |
| RACE | 种族 | WHITE | DM |
| DTHFL | 死亡标识 | N | DM |
| DTHDT | 死亡日期 | — | DM |
| RFSTDTC | 随机化日期 | 2024-01-15 | DS |
| RFENDTC | 末次评估日期 | 2024-06-20 | DS |
| EOSSTT | 研究结束状态 | COMPLETED | DS |

**ADSL 衍生变量示例**：

```r
# 从 LiamHobby/Admiral-Hackathon/programs/adsl.R
adsl <- dm %>%
  select(STUDYID, USUBJID, SUBJID, SITEID, ARM, AGE, AGEU, 
         RACE, SEX, ETHNIC, DTHFL, RFSTDTC, RFENDTC, ARMCD) %>%
  mutate(
    TRT01P = ARM,
    TRT01A = ARM,
    TRTSDT = derive_var_trtadt(),  # 首次给药日期
    TRTEDT = derive_var_trtedt()   # 末次给药日期
  )
```

### 3.2 ADAE — Adverse Events Analysis Dataset

**每个不良事件一行**，包含衍生变量。

| 变量 | 说明 | 示例 | 来源 |
|------|------|------|------|
| USUBJID | 受试者标识 | TDF001-1001 | AE |
| AETERM | 不良事件名称 | HEADACHE | AE |
| AESER | 严重不良事件 | N | AE |
| AEREL | 相关性 | POSSIBLE | AE |
| AESEV | 严重程度 | 1 - MILD | AE |
| ASTDT | 开始日期 | 2024-01-20 | AE.AESTDTC |
| AENDT | 结束日期 | 2024-01-25 | AE.AEENDTC |
| TRTSDT | 首次给药日期 | 2024-01-15 | ADSL |
| TRTEDT | 末次给药日期 | 2024-06-20 | ADSL |
| TRTEMFL | 治疗期间发生 | Y | 衍生 |
| AEOUT | 结局 | RESOLVED | AE |

**TRTEMFL 衍生逻辑**：

```
TRTEMFL = Y  if AE 发生在 TRTSDT 到 TRTEDT 之间
TRTEMFL = N  otherwise
```

### 3.3 ADVS — Vital Signs Analysis Dataset

**每个生命体征测量一行**，包含衍生变量。

| 变量 | 说明 | 示例 | 来源 |
|------|------|------|------|
| USUBJID | 受试者标识 | TDF001-1001 | VS |
| PARAMCD | 参数代码 | SYSBP | 衍生 |
| PARAM | 参数名称 | Systolic BP | 衍生 |
| AVAL | 分析值 | 120 | VS.VSORRES |
| AVALC | 分析值（字符） | 120 | VS.VSORRES |
| BASE | 基线值 | 118 | 衍生 |
| CHG | 变化量 | 2 | AVAL - BASE |
| PCHG | 百分比变化 | 1.7% | (AVAL - BASE) / BASE * 100 |
| ADT | 分析日期 | 2024-01-15 | VS.VSDTC |
| ADY | 分析日 | 1 | 衍生 |
| AVISIT | 访视 | WEEK 1 | 衍生 |
| TRT01P | 治疗组 | Drug X | ADSL |

**参数映射示例**：

```r
# 从 LiamHobby/Admiral-Hackathon/programs/advs_template.R
param_lookup <- tibble::tribble(
  ~VSTESTCD, ~PARAMCD, ~PARAM, ~PARAMN,
  "SYSBP", "SYSBP", "Systolic Blood Pressure (mmHg)", 1,
  "DIABP", "DIABP", "Diastolic Blood Pressure (mmHg)", 2,
  "PULSE", "PULSE", "Pulse Rate (beats/min)", 3,
  "WEIGHT", "WEIGHT", "Weight (kg)", 4,
  "HEIGHT", "HEIGHT", "Height (cm)", 5,
  "TEMP", "TEMP", "Temperature (C)", 6,
  "MAP", "MAP", "Mean Arterial Pressure (mmHg)", 7,
  "BMI", "BMI", "Body Mass Index (kg/m^2)", 8,
  "BSA", "BSA", "Body Surface Area (m^2)", 9
)
```

### 3.4 ADLB — Laboratory Analysis Dataset

**每个实验室测量一行**，包含衍生变量。

| 变量 | 说明 | 示例 | 来源 |
|------|------|------|------|
| USUBJID | 受试者标识 | TDF001-1001 | LB |
| PARAMCD | 参数代码 | ALT | 衍生 |
| PARAM | 参数名称 | Alanine Aminotransferase | 衍生 |
| AVAL | 分析值 | 45 | LB.LBORRES |
| BASE | 基线值 | 35 | 衍生 |
| CHG | 变化量 | 10 | AVAL - BASE |
| ABLFL | 基线标识 | Y | 衍生 |
| ANRIND | 异常标识 | NORMAL / HIGH / LOW | 衍生 |
| ADT | 分析日期 | 2024-01-15 | LB.LBDTC |
| TRT01P | 治疗组 | Drug X | ADSL |

**异常标识衍生逻辑**：

```r
# 从 SDTM IG 和 ADaM IG
ANRIND <- case_when(
  LBORRES < LBLLOF ~ "LOW",
  LBORRES > LBLHIF ~ "HIGH",
  TRUE ~ "NORMAL"
)
```

### 3.5 ADTTE — Time-to-Event Analysis Dataset

**生存分析数据集**，每个受试者 - 事件组合一行。

| 变量 | 说明 | 示例 | 来源 |
|------|------|------|------|
| USUBJID | 受试者标识 | TDF001-1001 | 多个域 |
| PARAMCD | 参数代码 | PFS | 衍生 |
| AVAL | 时间值 | 180 | 衍生 |
| AVALC | 事件标识 | 1 | 衍生 |
| CNSR | 删失标识 | 0 = 事件, 1 = 删失 | 衍生 |
| TRT01P | 治疗组 | Drug X | ADSL |
| AGE | 年龄 | 45 | ADSL |
| SEX | 性别 | M | ADSL |

---

## 四、SDTM → ADaM 映射流程

### 4.1 映射关系

```
SDTM                    ADaM
─────────────────────────────────────────
DM  (人口学)      →     ADSL (受试者级)
AE  (不良事件)    →     ADAE (不良事件分析)
VS  (生命体征)    →     ADVS (生命体征分析)
LB  (实验室)      →     ADLB (实验室分析)
EX  (暴露)        →     ADSL (TRTSDT, TRTEDT)
DS  (处置)        →     ADSL (EOSSTT, RFSTDTC)
```

### 4.2 衍生变量类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **日期衍生** | 从字符日期转为 Date | AESTDTC → ASTDT |
| **时间计算** | 计算时间差 | TRTSDT 到 ADT 的天数 |
| **基线衍生** | 识别基线值 | 首次访视的测量值 |
| **变化量** | 计算变化 | AVAL - BASE |
| **异常标识** | 基于参考范围 | ANRIND = HIGH/LOW/NORMAL |
| **治疗期间** | 判断是否在治疗期间 | TRTEMFL |

---

## 五、{admiral} R 包 — CDISC 官方工具

### 5.1 什么是 {admiral}？

**{admiral}** 是 CDISC 官方推荐的 R 包，用于构建 ADaM 数据集。

| 特性 | 说明 |
|------|------|
| **官方支持** | CDISC 和 Pharmaverse 项目 |
| **标准化函数** | 内置 ADaM 衍生函数 |
| **可追溯性** | 自动生成变量来源记录 |
| **FDA 兼容** | 符合 ADaM IG 标准 |

### 5.2 核心函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `derive_var_trtadt()` | 推导首次给药日期 | `derive_var_trtadt(dataset, date = EXSTDTC)` |
| `derive_var_trtedt()` | 推导末次给药日期 | `derive_var_trtedt(dataset, date = EXENDTC)` |
| `derive_param_ex()` | 推导暴露参数 | `derive_param_ex(dataset, ...)` |
| `derive_var_aeval()` | 推导分析值 | `derive_var_aeval(dataset, value = LBORRES)` |
| `derive_var_base()` | 推导基线值 | `derive_var_base(dataset, ...)` |
| `derive_var_chg()` | 推导变化量 | `derive_var_chg(dataset)` |
| `derive_var_pchg()` | 推导百分比变化 | `derive_var_pchg(dataset)` |

### 5.3 实战示例

```r
# 从 LiamHobby/Admiral-Hackathon/programs/adsl.R
library(admiral)
library(dplyr)
library(haven)

# 加载 SDTM 数据
dm <- read_xpt("./sdtm/dm.xpt")
ds <- read_xpt("./sdtm/ds.xpt")
ex <- read_xpt("./sdtm/ex.xpt")

# 转换为 NA（SAS 空白字符问题）
dm <- convert_blanks_to_na(dm)
ds <- convert_blanks_to_na(ds)
ex <- convert_blanks_to_na(ex)

# 构建 ADSL
adsl <- dm %>%
  select(STUDYID, USUBJID, SUBJID, SITEID, ARM, AGE, AGEU, 
         RACE, SEX, ETHNIC, DTHFL, RFSTDTC, RFENDTC, ARMCD) %>%
  mutate(
    TRT01P = ARM,
    TRT01A = ARM
  ) %>%
  derive_vars_trtadt(
    new_vars_prefix = "TRT01",
    dtc = RFSTDTC
  ) %>%
  derive_vars_trtedt(
    new_vars_prefix = "TRT01",
    dtc = RFENDTC
  )
```

---

## 六、define.xml — 元数据定义

### 6.1 什么是 define.xml？

**define.xml** 是描述 SDTM/ADaM 数据集元数据的 XML 文件，包含：

| 内容 | 说明 |
|------|------|
| **数据集描述** | 每个数据集的标签、类、结构 |
| **变量描述** | 每个变量的标签、类型、长度、格式 |
| **代码列表** | 每个代码化变量的允许值 |
| **变量来源** | 每个变量的 SDTM 来源 |
| **衍生规则** | 每个衍生变量的计算逻辑 |

### 6.2 define.xml 结构

```xml
<DefineXML>
  <Study id="TDF001">
    <Dataset name="ADSL">
      <Label>Subject Level Analysis Dataset</Label>
      <Variable name="USUBJID">
        <Label>Unique Subject Identifier</Label>
        <DataType>text</DataType>
        <Origin>DM.USUBJID</Origin>
      </Variable>
      <Variable name="TRT01P">
        <Label>Treatment Group</Label>
        <DataType>text</DataType>
        <Origin>DM.ARM</Origin>
      </Variable>
    </Dataset>
  </Study>
</DefineXML>
```

### 6.3 define.xml 生成工具

| 工具 | 语言 | 说明 |
|------|------|------|
| **xportr** | R | {admiral} 配套包，生成 define.xml |
| **SAS macros** | SAS | 工业界常用 |
| **Python** | Python | 新兴工具 |

---

## 七、实战资源

### 7.1 GitHub 资源

| 资源 | 说明 | 链接 |
|------|------|------|
| **LiamHobby/Admiral-Hackathon** | CDISC {admiral} R 包完整实战 | [GitHub](https://github.com/LiamHobby/Admiral-Hackathon) |
| **BhavnaMalladi/SDTM-to-ADAM-clinical-pipeline** | R 自动化 SDTM → ADaM 管道 | [GitHub](https://github.com/BhavnaMalladi/SDTM-to-ADAM-clinical-pipeline) |
| **rogerjdeangelis/utl-end-to-end-cdisc-SDTM-ADaM-processing** | 端到端 SDTM/ADaM 处理 | [GitHub](https://github.com/rogerjdeangelis/utl-end-to-end-cdisc-SDTM-ADaM-processing) |

### 7.2 LiamHobby/Admiral-Hackathon 结构

```
Admiral-Hackathon/
├── sdtm/                    # SDTM 源数据 (.xpt)
│   ├── dm.xpt               # 人口学
│   ├── ae.xpt               # 不良事件
│   ├── vs.xpt               # 生命体征
│   ├── lb.xpt               # 实验室
│   ├── ex.xpt               # 暴露
│   └── ...
├── adam/                    # ADaM 输出 (.xpt)
│   ├── adsl.xpt             # 受试者级
│   ├── adadas.xpt           # ADAS-Cog 分析
│   └── ...
├── programs/                # R 脚本
│   ├── adsl.R               # ADSL 构建
│   ├── adadas.R             # ADaDAS 构建
│   └── advs_template.R      # ADVS 模板
├── metadata/                # 元数据
│   ├── specs.xlsx           # ADaM 规格表
│   ├── sap.pdf              # 统计分析计划
│   └── annotated_crf.pdf    # 标注的 CRF
```

---

## 八、学习路径

### 8.1 入门（1-2 周）

| 步骤 | 内容 |
|------|------|
| 1 | 阅读 ADaM IG 1.1 文档 |
| 2 | 理解 ADSL、ADAE、ADVS、ADLB 结构 |
| 3 | 学习 {admiral} 包的核心函数 |

### 8.2 进阶（2-3 周）

| 步骤 | 内容 |
|------|------|
| 1 | 克隆 `LiamHobby/Admiral-Hackathon` 并运行 |
| 2 | 理解每个程序的衍生逻辑 |
| 3 | 尝试用自定义数据构建 ADaM |

### 8.3 实战（3-4 周）

| 步骤 | 内容 |
|------|------|
| 1 | 生成 define.xml |
| 2 | 验证 ADaM 数据集 |
| 3 | 与 SDTM 建立追溯链 |

---

## 九、与 SDTM 的关系

| 特性 | SDTM | ADaM |
|------|------|------|
| **目的** | 数据标准化 | 分析就绪 |
| **结构** | 原始数据映射 | 衍生变量 |
| **变量** | 原始变量 | 分析变量 |
| **用途** | FDA 提交 | 统计分析 |
| **关系** | ADaM 的输入 | SDTM 的输出 |

---

## 十、关键要点总结

| 要点 | 说明 |
|------|------|
| **ADaM 是分析就绪** | 包含 SDTM 中没有的衍生变量 |
| **ADSL 是基础** | 所有 ADaM 数据集都引用 ADSL |
| **{admiral} 是官方工具** | CDISC 推荐的 R 包 |
| **define.xml 是元数据** | 描述每个变量的来源和衍生规则 |
| **追溯性是关键** | 每个变量都可追溯到 SDTM 源 |

---

*最后更新：2026-06-25*
*来源：GitHub 资源 + CDISC 官方文档*
*下一步：[define.xml-模板.md](./define.xml-模板.md)*
