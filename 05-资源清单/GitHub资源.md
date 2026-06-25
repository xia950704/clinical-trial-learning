---
tags: [GitHub, 资源清单, 临床试验, 学习资源]
status: active
created: 2026-06-25
updated: 2026-06-25
---

# GitHub 临床试验资源清单

> 精选 GitHub 仓库，覆盖 CDISC 标准、试验设计、统计分析、TLF 生成

---

## 🏆 精选资源（按优先级排序）

### P0 — 核心学习资源

| 资源 | ⭐ | 语言 | 学习重点 | 链接 |
|------|-----|------|---------|------|
| **LiamHobby/Admiral-Hackathon** | 3 | R | CDISC {admiral} 包实战，完整 SDTM → ADaM 流程 | [GitHub](https://github.com/LiamHobby/Admiral-Hackathon) |
| **rogerjdeangelis/utl-end-to-end-cdisc-SDTM-ADaM-processing** | 17 | SAS | 端到端 SDTM/ADaM 处理，含 define.xml 生成 | [GitHub](https://github.com/rogerjdeangelis/utl-end-to-end-cdisc-SDTM-ADaM-processing) |
| **BhavnaMalladi/SDTM-to-ADAM-clinical-pipeline** | 3 | R | R 自动化 SDTM → ADaM 管道 | [GitHub](https://github.com/BhavnaMalladi/SDTM-to-ADAM-clinical-pipeline) |

### P1 — 试验设计

| 资源 | ⭐ | 语言 | 学习重点 | 链接 |
|------|-----|------|---------|------|
| **christos-athanasakopoulos/clinical-trial-design-RCT** | - | R | Phase I-II、Simon 设计、随机化、中期分析 | [GitHub](https://github.com/christos-athanasakopoulos/clinical-trial-design-RCT) |
| **yumengccc/BS851-Clinical-Trials** | - | - | 随机化、非劣效、生存分析、中期分析、组序贯设计 | [GitHub](https://github.com/yumengccc/BS851-Clinical-Trials) |
| **niekvandermaas/Analysis-of-The-Added-Value-of-Bayesian-Interim-Analysis** | - | R | 贝叶斯中期分析 | [GitHub](https://github.com/niekvandermaas/Analysis-of-The-Added-Value-of-Bayesian-Interim-Analysis) |

### P2 — 统计分析

| 资源 | ⭐ | 语言 | 学习重点 | 链接 |
|------|-----|------|---------|------|
| **sebasquirarte/biostats** | 86 | R | 生物统计工具箱，Lausanne 团队开发 | [GitHub](https://github.com/sebasquirarte/biostats) |
| **asifamrahim/Cirrhosis_SAS** | 2 | SAS | 生存分析实战：原发性胆汁性肝硬化 | [GitHub](https://github.com/asifamrahim/Cirrhosis_SAS) |
| **sumit-biostat/SAS-Oncology-SDTM-ADaM-TLFs** | 2 | SAS | 肿瘤学临床试验完整流程：SDTM → ADaM → TLF | [GitHub](https://github.com/sumit-biostat/SAS-Oncology-SDTM-ADaM-TLFs) |
| **sgolchi/BACTSO** | 2 | C++ | 贝叶斯生存分析 | [GitHub](https://github.com/sgolchi/BACTSO) |

### P3 — TLF 生成

| 资源 | ⭐ | 语言 | 学习重点 | 链接 |
|------|-----|------|---------|------|
| **SejalKankriya/clinical-trials-survival-analysis** | - | R | Kaplan-Meier、log-rank 检验、生存曲线 | [GitHub](https://github.com/SejalKankriya/clinical-trials-survival-analysis) |
| **josephquigley01-cmd/Survival-Analysis-on-Clinical-Trial-Data** | - | Python | Cox 模型、生存分析管道 | [GitHub](https://github.com/josephquigley01-cmd/Survival-Analysis-on-Clinical-Trial-Data) |

### P4 — 数据爬取与分析

| 资源 | ⭐ | 语言 | 学习重点 | 链接 |
|------|-----|------|---------|------|
| **DataQUEEN99/Clinical-Trials-Web-Scraper-Analyzer** | - | Python | 从 ClinicalTrials.gov 爬取数据并分析 | [GitHub](https://github.com/DataQUEEN99/Clinical-Trials-Web-Scraper-Analyzer) |
| **ricyoung/ClinicalTrialLLM-Extractor** | - | Jupyter | LLM 框架自动提取临床试验数据 | [GitHub](https://github.com/ricyoung/ClinicalTrialLLM-Extractor) |

---

## 📁 资源详情

### LiamHobby/Admiral-Hackathon

**最推荐的实战资源**，包含完整 SDTM → ADaM 流程。

| 目录 | 内容 |
|------|------|
| `sdtm/` | SDTM 源数据（22 个域：dm.xpt, ae.xpt, vs.xpt, lb.xpt 等） |
| `adam/` | ADaM 输出（adsl.xpt, adadas.xpt） |
| `programs/` | R 脚本（adsl.R, adadas.R, advs_template.R） |
| `metadata/` | 元数据（specs.xlsx, sap.pdf, annotated_crf.pdf） |

**关键文件示例**：

| 文件 | 内容 |
|------|------|
| `programs/adsl.R` | ADSL 构建：从 DM、DS、EX 推导 TRTSDT、TRTEDT |
| `programs/adadas.R` | ADaDAS 构建：ADAS-Cog 评分分析 |
| `programs/advs_template.R` | ADVS 模板：生命体征参数映射 |
| `metadata/specs.xlsx` | ADaM 规格表（12 个工作表：Define, Datasets, Variables, Codelists 等） |

**运行步骤**：

```bash
git clone https://github.com/LiamHobby/Admiral-Hackathon.git
cd Admiral-Hackathon
Rscript -e "install.packages(c('admiral', 'dplyr', 'haven', 'lubridate'))"
Rscript programs/adsl.R
Rscript programs/adadas.R
```

---

### rogerjdeangelis/utl-end-to-end-cdisc-SDTM-ADaM-processing

**SAS 实现**，包含 define.xml 生成。

| 内容 | 说明 |
|------|------|
| `cln_000makefile.sas` | 主脚本，端到端处理 |
| `SDTMIG_v3.3_FINAL.pdf` | SDTM 实施指南 |
| `SDTM Terminology.xls` | 标准术语集 |
| `TDF_ADaM_v1.0.zip` | ADaM 示例数据 |
| `admiral.7z` | {admiral} 包离线安装 |

**关键特点**：
- 使用 SAS 9.4M6
- 生成 define.xml
- 包含 SDTM 和 ADaM 完整处理流程

---

### BhavnaMalladi/SDTM-to-ADAM-clinical-pipeline

**R 自动化管道**，使用 {admiral} 包。

| 目录 | 内容 |
|------|------|
| `R/` | R 函数 |
| `data-raw/` | 原始数据和处理脚本 |
| `data/` | 生成的 ADaM 数据集 |
| `output/` | CSV 格式输出 |
| `inst/extdata/` | ADaM 规格表（adams-specs.xlsx） |

**管道流程**：

```
SDTM (pharmaversesdtm) → 元数据配置 → admiral 衍生 → ADaM 输出
```

**生成数据集**：
- ADSL（306 受试者）
- ADAE（1,191 事件）
- ADVS（29,643 记录）
- ADLB（59,580 记录）

---

### christos-athanasakopoulos/clinical-trial-design-RCT

**试验设计方法**，R 实现。

| 主题 | 说明 |
|------|------|
| Phase I 设计 | 剂量递增（3+3、CRM） |
| Phase II 设计 | Simon 两阶段、最优/最小样本量 |
| 随机化 | 简单、区组、分层随机化 |
| 中期分析 | 组序贯设计、贝叶斯中期分析 |

---

## 🔗 相关资源

### CDISC 官方资源

| 资源 | 说明 | 链接 |
|------|------|------|
| **CDISC GitHub** | CDISC 官方仓库 | [github.com/cdisc-org](https://github.com/cdisc-org) |
| **CDISC Pilot Project** | SDTM/ADaM 示例项目 | [github.com/cdisc-org/sdtm-adam-pilot-project](https://github.com/cdisc-org/sdtm-adam-pilot-project) |
| **{admiral} 官方文档** | CDISC {admiral} R 包文档 | [pharmaverse.github.io/admiral](https://pharmaverse.github.io/admiral) |

### R 包

| 包 | 说明 | 链接 |
|------|------|------|
| **{admiral}** | CDISC 官方 ADaM 构建包 | [CRAN](https://cran.r-project.org/web/packages/admiral) |
| **{pharmaversesdtm}** | CDISC 示例 SDTM 数据 | [CRAN](https://cran.r-project.org/web/packages/pharmaversesdtm) |
| **{xportr}** | define.xml 生成 | [GitHub](https://github.com/rogerjdeangelis/utl-end-to-end-cdisc-SDTM-ADaM-processing) |
| **{tableone}** | 基线表生成 | [CRAN](https://cran.r-project.org/web/packages/tableone) |
| **{gtsummary}** | 基线表和结果表 | [CRAN](https://cran.r-project.org/web/packages/gtsummary) |
| **{survival}** | 生存分析 | [CRAN](https://cran.r-project.org/web/packages/survival) |
| **{survminer}** | 生存曲线可视化 | [CRAN](https://cran.r-project.org/web/packages/survminer) |

### SAS 宏

| 宏 | 说明 |
|------|------|
| **{admiral} SAS 版本** | CDISC 官方 SAS 宏 |
| **rogerjdeangelis 宏库** | 端到端处理宏 |

---

## 📊 资源对比

| 资源 | 语言 | 适合人群 | 学习难度 | 推荐度 |
|------|------|---------|---------|--------|
| **LiamHobby/Admiral-Hackathon** | R | R 用户，想学 {admiral} | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **rogerjdeangelis/...** | SAS | SAS 用户，工业界 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **BhavnaMalladi/...** | R | R 用户，想学自动化管道 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **christos-athanasakopoulos/...** | R | 想学试验设计 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **sebasquirarte/biostats** | R | 想学生物统计工具箱 | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 学习建议

### 如果你是 R 用户

```
1. 克隆 LiamHobby/Admiral-Hackathon
2. 运行 programs/adsl.R 理解 ADSL 构建
3. 运行 programs/adadas.R 理解 ADaM 衍生
4. 查看 metadata/specs.xlsx 理解 ADaM 规格
5. 尝试用自定义数据复现
```

### 如果你是 SAS 用户

```
1. 克隆 rogerjdeangelis/utl-end-to-end-cdisc-SDTM-ADaM-processing
2. 运行 cln_000makefile.sas 理解端到端流程
3. 查看 define.xml 生成逻辑
4. 尝试用自定义数据复现
```

### 如果你想学生物统计

```
1. 克隆 sebasquirarte/biostats
2. 学习生物统计工具箱函数
3. 克隆 christos-athanasakopoulos/clinical-trial-design-RCT
4. 学习试验设计方法
```

---

## 🔄 与现有 Vault 的关联

| 已有内容 | 推荐 GitHub 资源 | 打通方式 |
|---------|----------------|---------|
| **steroids-trial-emulation** | christos-athanasakopoulos/clinical-trial-design-RCT | 目标试验模拟 → 试验设计 |
| **diabetes-comparative-effectiveness-study** | sumit-biostat/SAS-Oncology-SDTM-ADaM-TLFs | 比较效果研究 → 非劣效试验 |
| **TargetTrial_ThresholdsForIMV** | LiamHobby/Admiral-Hackathon | MIMIC 数据 → SDTM 标准化 |

---

*最后更新：2026-06-25*
*来源：GitHub API 搜索结果*
