# Step 3 — 描述统计与 Table 1

## 目标

自动生成出版级基线特征表（Table 1），含组间比较 p 值。

## 你会学到

- `gtsummary` 包的 Table 1 自动生成
- 连续变量描述（均值±SD / 中位数[IQR]）
- 分类变量描述（n / %）
- 组间比较（t检验 / 卡方 / Fisher / 秩和）
- 输出格式（Word / HTML / 控制台）

## 输入

`Step-02-清洗流水线/derived/clean_data.rds`

## 输出

- 控制台 Table 1
- `output/table1.html`（交互式表格）

## 代码骨架

```r
library(tidyverse)
library(gtsummary)

data <- readRDS("../Step-02-清洗流水线/derived/clean_data.rds")

tbl <- data %>%
  select(treatment, age, sex, bmi, visit) %>%
  tbl_summary(
    by = treatment,
    statistic = list(all_continuous() ~ "{mean} ({sd})",
                     all_categorical() ~ "{n} ({p}%)"),
    digits = all_continuous() ~ 1
  ) %>%
  add_p() %>%
  add_overall()

tbl
```

## 验证标准

- [ ] Table 1 包含组别、总体三列
- [ ] 连续变量格式正确
- [ ] 分类变量格式正确
- [ ] 组间比较有 p 值

## 下一步

转到 [Step 4 — 疗效分析](../Step-04-疗效分析/README.md)
