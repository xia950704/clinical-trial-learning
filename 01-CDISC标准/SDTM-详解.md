---
tags: [CDISC, SDTM, 临床试验, 数据标准, FDA提交]
status: active
created: 2026-06-25
updated: 2026-06-25
vault_link: 01-CDISC标准/SDTM-详解.md
---

# SDTM 详解 — Study Data Tabulation Model

> CDISC 标准的核心：原始数据到标准化数据的映射

---

## 一、什么是 SDTM？

**SDTM（Study Data Tabulation Model）** 是 CDISC 制定的临床试验数据标准化模型，用于：

| 用途 | 说明 |
|------|------|
| **FDA/EMA 提交** | 2016 年起 FDA 要求新药提交必须使用 SDTM 格式 |
| **数据标准化** | 不同试验、不同系统的数据统一格式 |
| **数据审查** | 监管机构可标准化审查所有提交数据 |
| **数据复用** | 标准化后可用于荟萃分析、真实世界研究 |

---

## 二、SDTM 核心概念

### 2.1 数据结构

| 概念 | 说明 |
|------|------|
| **Domain（域）** | 数据类别，如 DM（人口学）、AE（不良事件）、VS（生命体征） |
| **Record（记录）** | 一行数据，代表一个观测 |
| **Variable（变量）** | 一列数据，代表一个特征 |
| **Dataset（数据集）** | 一个域的所有记录，如 `dm.xpt`、`ae.xpt` |

### 2.2 变量分类

| 类型 | 说明 | 示例 |
|------|------|------|
| **Identifier（标识符）** | 唯一标识 | STUDYID, USUBJID |
| **Topic（主题）** | 观测主题 | AETERM（不良事件名称） |
| **Timing（时序）** | 时间信息 | AESTDTC, AEENDTC |
| **Result/Measurement（结果）** | 观测值 | AEREL, AESEV |
| **Qualifier（限定符）** | 补充信息 | AEREL, AESER |

---

## 三、SDTM 域结构（核心域）

### 3.1 人口学域（DM）

| 变量 | 说明 | 示例 |
|------|------|------|
| STUDYID | 研究标识 | TDF001 |
| USUBJID | 唯一受试者标识 | TDF001-1001 |
| SITEID | 研究中心标识 | 001 |
| SUBJID | 受试者编号 | 1001 |
| ARM | 治疗组 | A: Drug X |
| ARMCD | 治疗组代码 | A |
| AGE | 年龄 | 45 |
| AGEU | 年龄单位 | YEARS |
| RACE | 种族 | WHITE |
| SEX | 性别 | M / F |
| ETHNIC | 族裔 | HISPNIC / NONHISP |
| DTHFL | 死亡标识 | Y / N |
| RFSTDTC | 首次给药日期 | 2024-01-15 |
| RFENDTC | 末次给药日期 | 2024-06-20 |

### 3.2 不良事件域（AE）

| 变量 | 说明 | 示例 |
|------|------|------|
| USUBJID | 受试者标识 | TDF001-1001 |
| AESEQ | 不良事件序号 | 1 |
| AETERM | 不良事件名称 | HEADACHE |
| AESEV | 严重程度 | 1 - MILD |
| AESER | 严重不良事件 | Y / N |
| AEREL | 与药物相关性 | POSSIBLE |
| AEACN | 处理措施 | DRUG WITHDRAWN |
| AESTDTC | 开始日期 | 2024-01-20 |
| AEENDTC | 结束日期 | 2024-01-25 |
| AESCAN | 是否恢复 | Y / N |

### 3.3 生命体征域（VS）

| 变量 | 说明 | 示例 |
|------|------|------|
| USUBJID | 受试者标识 | TDF001-1001 |
| VSTESTCD | 测试代码 | SYSBP |
| VSTEST | 测试名称 | Systolic Blood Pressure |
| VSORRES | 原始结果 | 120 |
| VSORRESU | 原始单位 | mmHg |
| VSTESTCAT | 测试类别 | VITAL SIGNS |
| VSBLFL | 基线标识 | Y |
| VSTPT | 测试时点 | PRE-TREATMENT |
| VSDTC | 测试日期 | 2024-01-15 |
| VSTPT | 测试时点 | SCREENING |

### 3.4 实验室域（LB）

| 变量 | 说明 | 示例 |
|------|------|------|
| USUBJID | 受试者标识 | TDF001-1001 |
| LBTESTCD | 测试代码 | ALT |
| LBTEST | 测试名称 | Alanine Aminotransferase |
| LBORRES | 原始结果 | 45 |
| LBORRESU | 原始单位 | U/L |
| LBNRIND | 参考范围 | 10-40 U/L |
| LBBLFL | 基线标识 | Y |
| LBDTC | 测试日期 | 2024-01-15 |
| LBSTRESC | 标准化结果 | 45 |
| LBSTRESN | 标准化数值 | 45 |
| LBSTRESU | 标准化单位 | U/L |

### 3.5 暴露域（EX）

| 变量 | 说明 | 示例 |
|------|------|------|
| USUBJID | 受试者标识 | TDF001-1001 |
| EXTRT | 药物名称 | Drug X |
| EXDOSE | 剂量 | 50 |
| EXDOSU | 剂量单位 | mg |
| EXDOSFRM | 剂型 | TABLET |
| EXDOSFRQ | 给药频率 | QD |
| EXROUTE | 给药途径 | ORAL |
| EXSTDTC | 开始日期 | 2024-01-15 |
| EXENDTC | 结束日期 | 2024-06-20 |
| EXDOSFRQ | 给药频率 | QD |

### 3.6 疾病史域（MH）

| 变量 | 说明 | 示例 |
|------|------|------|
| USUBJID | 受试者标识 | TDF001-1001 |
| MHTESTCD | 测试代码 | CANCER |
| MHTEST | 测试名称 | Cancer History |
| MHDECOD | 编码术语 | LUNG CANCER |
| MHBLFL | 基线标识 | Y |
| MHDTC | 诊断日期 | 2020-05-10 |
| MHENDTC | 结束日期 | 2023-01-15 |
| MHCAT | 类别 | HISTORY |

### 3.7 合并用药域（CM）

| 变量 | 说明 | 示例 |
|------|------|------|
| USUBJID | 受试者标识 | TDF001-1001 |
| CMTRT | 药物名称 | ASPIRIN |
| CMDOSE | 剂量 | 100 |
| CMDOSU | 剂量单位 | mg |
| CMROUTE | 给药途径 | ORAL |
| CMSTDTC | 开始日期 | 2024-01-15 |
| CMENDTC | 结束日期 | 2024-06-20 |

### 3.8 处置域（DS）

| 变量 | 说明 | 示例 |
|------|------|------|
| USUBJID | 受试者标识 | TDF001-1001 |
| DSSEQ | 处置序号 | 1 |
| DSTERM | 处置术语 | SCREENING |
| DSDECOD | 编码术语 | SCREENING |
| DSCAT | 类别 | DISPOSITION |
| DSSCAT | 子类别 | SCREENING |
| DSSTDTC | 开始日期 | 2024-01-10 |
| DSSTDTC | 日期 | 2024-01-10 |

### 3.9 检查域（SV）

| 变量 | 说明 | 示例 |
|------|------|------|
| USUBJID | 受试者标识 | TDF001-1001 |
| SVTESTCD | 测试代码 | VISIT |
| SVTEST | 测试名称 | Visit |
| SVBLFL | 基线标识 | Y |
| SVSTDTC | 日期 | 2024-01-15 |

---

## 四、SDTM 映射流程

### 4.1 原始数据 → SDTM

```
原始数据 (EDC/CSV/Excel)
    ↓
数据清洗
    ↓
变量映射 (Mapping)
    ↓
SDTM 数据集 (.xpt)
    ↓
define.xml (元数据)
    ↓
FDA 提交
```

### 4.2 映射规则

| 规则 | 说明 |
|------|------|
| **USUBJID 一致性** | 所有域使用相同的 USUBJID 格式 |
| **日期格式** | 使用 ISO 8601 格式（YYYY-MM-DD） |
| **代码化术语** | 使用 CDISC 标准术语集（CT） |
| **缺失值处理** | 空白字符转为 NA |
| **单位标准化** | 使用 UCUM 标准单位 |

---

## 五、SDTM IG（Implementation Guide）

### 5.1 版本

| 版本 | 发布时间 | 说明 |
|------|---------|------|
| SDTM IG 1.0 | 2005 | 初始版本 |
| SDTM IG 1.1 | 2007 | 增加新域 |
| SDTM IG 1.2 | 2011 | 重大更新 |
| SDTM IG 1.3 | 2016 | 当前主流版本 |
| SDTM IG 3.3 | 2022 | 最新版本 |

### 5.2 关键文档

| 文档 | 说明 |
|------|------|
| **SDTMIG_v3.3_FINAL.pdf** | SDTM 实施指南 |
| **SDTM Terminology.xls** | 标准术语集 |
| **define.xml** | 元数据定义文件 |

---

## 六、SDTM 与 ADaM 的关系

| 特性 | SDTM | ADaM |
|------|------|------|
| **目的** | 数据标准化 | 分析就绪 |
| **结构** | 原始数据映射 | 衍生变量 |
| **变量** | 原始变量 | 分析变量（ADaM 衍生） |
| **用途** | FDA 提交 | 统计分析 |
| **关系** | ADaM 源自 SDTM | SDTM 是 ADaM 的输入 |

### 6.1 映射示例

```
SDTM DM (人口学)  →  ADaM ADSL (受试者级分析数据集)
SDTM AE (不良事件) →  ADaM ADAE (不良事件分析)
SDTM VS (生命体征) →  ADaM ADVS (生命体征分析)
SDTM LB (实验室)   →  ADaM ADLB (实验室分析)
```

---

## 七、实战资源

### 7.1 GitHub 资源

| 资源 | 说明 | 链接 |
|------|------|------|
| **rogerjdeangelis/utl-end-to-end-cdisc-SDTM-ADaM-processing** | 端到端 SDTM/ADaM 处理，含 define.xml 生成 | [GitHub](https://github.com/rogerjdeangelis/utl-end-to-end-cdisc-SDTM-ADaM-processing) |
| **LiamHobby/Admiral-Hackathon** | CDISC {admiral} R 包实战，含完整 SDTM → ADaM 流程 | [GitHub](https://github.com/LiamHobby/Admiral-Hackathon) |
| **BhavnaMalladi/SDTM-to-ADAM-clinical-pipeline** | R 自动化 SDTM → ADaM 管道 | [GitHub](https://github.com/BhavnaMalladi/SDTM-to-ADAM-clinical-pipeline) |
| **p-et/sdtm-adam-project** | SAS 实现 SDTM → ADaM | [GitHub](https://github.com/p-et/sdtm-adam-project) |

### 7.2 关键文件示例

从 `LiamHobby/Admiral-Hackathon` 获取的 SDTM 域：

| 域 | 文件 | 说明 |
|----|------|------|
| DM | `sdtm/dm.xpt` | 人口学 |
| DS | `sdtm/ds.xpt` | 处置 |
| EX | `sdtm/ex.xpt` | 暴露 |
| AE | `sdtm/ae.xpt` | 不良事件 |
| LB | `sdtm/lb.xpt` | 实验室 |
| VS | `sdtm/vs.xpt` | 生命体征 |
| MH | `sdtm/mh.xpt` | 疾病史 |
| CM | `sdtm/cm.xpt` | 合并用药 |

---

## 八、学习路径

### 8.1 入门（1-2 周）

| 步骤 | 内容 |
|------|------|
| 1 | 阅读 SDTM IG 3.3 文档（重点：DM、AE、VS、LB、EX 域） |
| 2 | 下载 `pharmaversesdtm` R 包，熟悉示例数据 |
| 3 | 理解 USUBJID 格式和变量命名规则 |

### 8.2 进阶（2-3 周）

| 步骤 | 内容 |
|------|------|
| 1 | 学习 `admiral` R 包（CDISC 官方推荐） |
| 2 | 实践 SDTM → ADaM 映射 |
| 3 | 学习 define.xml 生成 |

### 8.3 实战（3-4 周）

| 步骤 | 内容 |
|------|------|
| 1 | 克隆 `LiamHobby/Admiral-Hackathon` 并运行 |
| 2 | 尝试用自定义数据创建 SDTM 数据集 |
| 3 | 生成 define.xml 并验证 |

---

## 九、与现有内容打通

### 9.1 与你 vault 的关系

| 你已有 | SDTM/ADaM 对应 | 打通方式 |
|--------|--------------|---------|
| **steroids-trial-emulation** | 原始数据 → SDTM 映射 | 理解观察性数据如何标准化 |
| **diabetes-comparative-effectiveness-study** | 分析数据集 → ADaM | 理解分析就绪数据集构建 |
| **TargetTrial_ThresholdsForIMV** | MIMIC 数据标准化 | 理解 ICU 数据如何映射到 SDTM |

### 9.2 差异点

| 你已有 | SDTM/ADaM 不同 |
|--------|--------------|
| 观察性研究数据 | SDTM 专为 RCT 设计 |
| 自定义变量命名 | SDTM 有严格命名规则 |
| 非标准化格式 | SDTM 有标准域和变量 |

---

## 十、关键要点总结

| 要点 | 说明 |
|------|------|
| **SDTM 是标准** | FDA/EMA 提交必需，不是可选 |
| **USUBJID 是核心** | 所有域通过 USUBJID 关联 |
| **SDTM → ADaM** | SDTM 是输入，ADaM 是分析就绪输出 |
| **define.xml 是元数据** | 描述每个变量来源、标签、格式 |
| **{admiral} 是 R 包** | CDISC 官方推荐的 ADaM 构建工具 |
| **SAS 仍是主流** | 工业界 80%+ 仍用 SAS，但 R 在增长 |

---

*最后更新：2026-06-25*
*来源：GitHub 资源 + CDISC 官方文档*
*下一步：[ADaM-详解](./ADaM-详解.md)*
