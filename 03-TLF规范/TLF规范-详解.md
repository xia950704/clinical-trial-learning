---
tags: [CDISC, TLF, 临床试验, 表格, 图表, FDA提交]
status: active
created: 2026-06-25
updated: 2026-06-25
vault_link: 03-TLF规范/TLF规范-详解.md
---

# TLF 规范 — Tables, Listings, Figures

> FDA 提交级报告生成：从 ADaM 到最终报告

---

## 一、什么是 TLF？

**TLF（Tables, Listings, Figures）** 是临床试验报告的标准格式，用于：

| 类型 | 说明 | 示例 |
|------|------|------|
| **Tables（表格）** | 汇总统计表 | 基线表、安全性表、疗效表 |
| **Listings（清单）** | 逐条数据展示 | 受试者清单、异常值清单 |
| **Figures（图表）** | 可视化展示 | 生存曲线、森林图、瀑布图 |

---

## 二、Tables（表格）

### 2.1 基线表（Table 1）

**目的**：展示受试者人口学特征和基线疾病特征。

**标准结构**：

| 变量 | 全人群 (N=306) | 治疗组 A (n=153) | 治疗组 B (n=153) |
|------|---------------|-----------------|-----------------|
| **年龄（岁）** | | | |
| 均值 ± SD | 58.2 ± 12.3 | 57.8 ± 11.9 | 58.6 ± 12.7 |
| 中位数（范围） | 59（25-82） | 58（26-80） | 60（25-82） |
| **性别 n（%）** | | | |
| 男 | 153（50.0） | 77（50.3） | 76（49.7） |
| 女 | 153（50.0） | 76（49.7） | 77（50.3） |
| **种族 n（%）** | | | |
| 白人 | 280（91.5） | 140（91.5） | 140（91.5） |
| 黑人 | 18（5.9） | 9（5.9） | 9（5.9） |
| 其他 | 8（2.6） | 4（2.6） | 4（2.6） |
| **基线疾病 n（%）** | | | |
| 高血压 | 182（59.5） | 91（59.5） | 91（59.5） |
| 糖尿病 | 92（30.1） | 46（30.1） | 46（30.1） |

**R 代码模板**：

```r
# 使用 {tableone} 或 {gtsummary}
library(tableone)
library(dplyr)

# 创建基线表
vars <- c("AGE", "SEX", "RACE", "ETHNIC")
strata <- "TRT01P"

table1 <- CreateTableOne(
  vars = vars,
  strata = strata,
  data = adsl,
  factorVars = c("SEX", "RACE", "ETHNIC")
)

# 输出
print(table1, showAllLevels = TRUE, quote = FALSE)
```

### 2.2 安全性表（Safety Tables）

**目的**：展示不良事件、实验室异常、生命体征变化。

**AE 汇总表结构**：

| 不良事件 | 治疗组 A (n=153) | 治疗组 B (n=153) |
|---------|-----------------|-----------------|
| **任何不良事件** | | |
| 任何 AE | 145（94.8） | 142（92.8） |
| SAE | 12（7.8） | 15（9.8） |
| AE 导致停药 | 8（5.2） | 10（6.5） |
| **治疗相关 AE** | | |
| 任何相关 AE | 98（64.1） | 95（62.1） |
| 严重相关 AE | 5（3.3） | 7（4.6） |
| **按系统器官分类** | | |
| 胃肠道疾病 | 45（29.4） | 42（27.5） |
| 神经系统疾病 | 32（20.9） | 30（19.6） |
| 皮肤疾病 | 18（11.8） | 16（10.5） |

**R 代码模板**：

```r
# 使用 {tidyverse} 和 {janitor}
library(dplyr)
library(tidyr)
library(janitor)

ae_summary <- adae %>%
  filter(TRTEMFL == "Y") %>%
  mutate(
    AE_GRADE = case_when(
      AESEV == "1" ~ "Mild",
      AESEV == "2" ~ "Moderate",
      AESEV == "3" ~ "Severe",
      TRUE ~ "Unknown"
    )
  ) %>%
  group_by(TRT01P, AEDECOD, AE_GRADE) %>%
  summarise(n = n(), .groups = "drop") %>%
  mutate(pct = round(n / sum(n) * 100, 1)) %>%
  pivot_wider(
    names_from = TRT01P,
    values_from = c(n, pct),
    names_sep = "_"
  )
```

### 2.3 疗效表（Efficacy Tables）

**目的**：展示主要终点和次要终点的分析结果。

**主要终点汇总表结构**：

| 终点 | 治疗组 A (n=153) | 治疗组 B (n=153) | 差异（95% CI） | p 值 |
|------|-----------------|-----------------|---------------|------|
| **主要终点：ORR** | | | | |
| 响应 n（%） | 92（60.1） | 78（51.0） | 9.1（0.2, 18.0） | 0.045 |
| **次要终点：PFS** | | | | |
| 中位 PFS（月） | 12.3（10.1-14.5） | 10.1（8.2-12.0） | HR = 0.75（0.58-0.97） | 0.028 |
| **次要终点：OS** | | | | |
| 中位 OS（月） | 24.5（20.1-28.9） | 22.1（18.0-26.2） | HR = 0.85（0.65-1.11） | 0.23 |

**R 代码模板**：

```r
# 使用 {survival} 和 {survminer}
library(survival)
library(survminer)

# Kaplan-Meier 分析
pfs_km <- survfit(Surv(PFS_TIME, PFS_EVENT) ~ TRT01P, data = adsl)

# Cox 回归
pfs_cox <- coxph(Surv(PFS_TIME, PFS_EVENT) ~ TRT01P + AGE + SEX, data = adsl)

# 输出结果
summary(pfs_km)
summary(pfs_cox)
```

---

## 三、Listings（清单）

### 3.1 受试者清单

**目的**：展示每个受试者的详细数据，用于数据审查。

**标准结构**：

| USUBJID | TRT01P | AGE | SEX | RACE | DISEASE | STATUS |
|---------|--------|-----|-----|------|---------|--------|
| TDF001-1001 | Drug X | 58 | M | WHITE | CANCER | COMPLETED |
| TDF001-1002 | Drug X | 62 | F | WHITE | CANCER | DISCONTINUED |
| TDF001-1003 | Placebo | 55 | M | BLACK | CANCER | COMPLETED |

**R 代码模板**：

```r
# 使用 {gt} 或 {flextable}
library(gt)

listing <- adsl %>%
  select(USUBJID, TRT01P, AGE, SEX, RACE, EOSSTT) %>%
  arrange(USUBJID)

gt(listing) %>%
  tab_header(title = "Subject Listing") %>%
  cols_label(
    USUBJID = "Subject ID",
    TRT01P = "Treatment",
    AGE = "Age",
    SEX = "Sex",
    RACE = "Race",
    EOSSTT = "Status"
  )
```

### 3.2 异常值清单

**目的**：展示实验室异常值或临床显著异常。

**R 代码模板**：

```r
# 实验室异常值清单
abnormal_lb <- adlb %>%
  filter(ANRIND %in% c("HIGH", "LOW") & ABLFL != "Y") %>%
  select(USUBJID, PARAMCD, AVAL, BASE, CHG, ANRIND, ADT) %>%
  arrange(USUBJID, ADT)
```

---

## 四、Figures（图表）

### 4.1 生存曲线（Kaplan-Meier）

**目的**：展示时间 - 事件终点（PFS、OS）。

**标准结构**：

```
生存概率
1.0 ┤
    │ ╲
0.8 ┤   ╲ 治疗组 A
    │     ╲
0.6 ┤       ╲─────── 治疗组 B
    │
0.4 ┤
    │
0.2 ┤
    │
0.0 ┼───────────────────────────
    0    6    12   18   24   30   时间（月）
```

**R 代码模板**：

```r
# 使用 {survminer}
library(survival)
library(survminer)

km_fit <- survfit(Surv(PFS_TIME, PFS_EVENT) ~ TRT01P, data = adsl)

ggsurvplot(
  km_fit,
  data = adsl,
  pval = TRUE,
  conf.int = TRUE,
  risk.table = TRUE,
  legend.title = "Treatment",
  legend.labs = c("Drug X", "Placebo"),
  xlab = "Time (months)",
  ylab = "Progression-Free Survival Probability",
  break.time.by = 6,
  ggtheme = theme_bw()
)
```

### 4.2 森林图（Forest Plot）

**目的**：展示亚组分析结果。

**标准结构**：

```
亚组              HR (95% CI)
─────────────────────────────────────
全人群            0.75 (0.58-0.97)
  < 65 岁         0.72 (0.52-0.99)
  ≥ 65 岁         0.79 (0.55-1.13)
  男性            0.73 (0.53-1.00)
  女性            0.77 (0.54-1.09)
  白人            0.76 (0.58-0.99)
  非白人          0.71 (0.45-1.12)
─────────────────────────────────────
                  0.5    1.0    2.0
```

**R 代码模板**：

```r
# 使用 {forestplot} 或 {ggplot2}
library(forestplot)

forestplot(
  labeltext = c(subgroup, hr, ci),
  mean = hr_values,
  lower = ci_lower,
  upper = ci_upper,
  xlog = TRUE,
  col = fpColors(box = "royalblue", line = "darkblue"),
  xticks = c(0.5, 1.0, 2.0)
)
```

### 4.3 瀑布图（Waterfall Plot）

**目的**：展示肿瘤大小变化（肿瘤学试验）。

**R 代码模板**：

```r
# 使用 {ggplot2}
library(ggplot2)

waterfall <- adsl %>%
  mutate(
    BEST_RESPONSE = case_when(
      PCT_CHANGE <= -30 ~ "PR",
      PCT_CHANGE >= 20 ~ "PD",
      TRUE ~ "SD"
    )
  ) %>%
  arrange(PCT_CHANGE)

ggplot(waterfall, aes(x = reorder(USUBJID, PCT_CHANGE), y = PCT_CHANGE, fill = BEST_RESPONSE)) +
  geom_bar(stat = "identity") +
  geom_hline(yintercept = -30, linetype = "dashed", color = "red") +
  geom_hline(yintercept = 20, linetype = "dashed", color = "orange") +
  coord_flip() +
  labs(x = "Subject", y = "Best % Change from Baseline", fill = "Response") +
  theme_minimal()
```

---

## 五、TLF 生成流程

### 5.1 完整流程

```
ADaM 数据集 (.xpt)
    ↓
统计分析程序 (SAS/R)
    ↓
输出文件 (.rtf/.pdf/.png)
    ↓
TFL 汇总
    ↓
CSR（临床研究报告）
    ↓
FDA 提交
```

### 5.2 工具对比

| 工具 | 语言 | 优点 | 缺点 |
|------|------|------|------|
| **SAS** | SAS | 工业界标准，FDA 认可度高 | 成本高，学习曲线陡 |
| **{gtsummary}** | R | 快速生成基线表，美观 | 自定义有限 |
| **{forestplot}** | R | 森林图专业 | 仅森林图 |
| **{survminer}** | R | 生存曲线美观 | 仅生存分析 |
| **{xportr}** | R | 生成 define.xml | 仅元数据 |

---

## 六、实战资源

### 6.1 GitHub 资源

| 资源 | 说明 | 链接 |
|------|------|------|
| **sumit-biostat/SAS-Oncology-SDTM-ADaM-TLFs** | SAS 实现完整 TLF | [GitHub](https://github.com/sumit-biostat/SAS-Oncology-SDTM-ADaM-TLFs) |
| **SejalKankriya/clinical-trials-survival-analysis** | R 生存分析 + 图表 | [GitHub](https://github.com/SejalKankriya/clinical-trials-survival-analysis) |

---

## 七、关键要点总结

| 要点 | 说明 |
|------|------|
| **TLF 是 FDA 提交必需** | 表格、清单、图表缺一不可 |
| **基线表是 Table 1** | 所有报告的第一张表 |
| **生存曲线是核心** | 肿瘤学试验必备 |
| **森林图展示亚组** | 敏感性分析必备 |
| **{gtsummary} 是 R 首选** | 快速生成基线表 |

---

*最后更新：2026-06-25*
*来源：GitHub 资源 + CDISC 官方文档*
*下一步：[02-试验设计/](../02-试验设计/)*
