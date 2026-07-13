# Step 4 — 疗效分析

## 目标

对主要疗效终点进行完整的统计分析，包括假设检验和可视化。

## 你会学到

- 疗效终点的选择逻辑（连续/二分类/时间事件）
- t检验 / Wilcoxon 秩和检验
- Kaplan-Meier 生存曲线
- 混合效应模型（重复测量数据）
- 亚组分析

## 输入

`Step-02-清洗流水线/derived/clean_data.rds`

## 输出

- `output/efficacy_summary.md`（结果汇总）
- `output/km_curve.png`（生存曲线图）

## 代码骨架

```r
library(tidyverse)
library(survival)
library(survminer)
library(lme4)

data <- readRDS("../Step-02-清洗流水线/derived/clean_data.rds")

# t检验（连续终点）
# t.test(efficacy_score ~ treatment, data = data)

# KM 曲线（时间事件终点）
# fit <- survfit(Surv(time, status) ~ treatment, data = data)
# ggsurvplot(fit, data = data, pval = TRUE)

# 混合效应模型（重复测量）
# model <- lmer(outcome ~ treatment * time + (1 | subject_id), data = data)
# summary(model)

message("Step 4 完成！")
```

## 验证标准

- [ ] 主要终点分析结果包含效应量 + 置信区间 + p 值
- [ ] 模型假设检验已做
- [ ] 可视化符合出版标准

## 下一步

转到 [Step 5 — 安全性分析](../Step-05-安全性分析/README.md)
