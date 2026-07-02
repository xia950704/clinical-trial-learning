# Step 5 — 安全性分析

## 目标

对 AE/SAE 数据进行系统性汇总和可视化，识别安全性信号。

## 你会学到

- AE 汇总表（SOC / PT 维度）
- 瀑布图展示个体最大 AE 等级
- 实验室检查异常值标记
- 安全性信号识别

## 输入

`Step-02-清洗流水线/derived/clean_data.rds`

## 输出

- `output/ae_summary.csv`
- `output/waterfall_plot.png`

## 代码骨架

```r
library(tidyverse)

data <- readRDS("../Step-02-清洗流水线/derived/clean_data.rds")

# AE 汇总
# ae_table <- data %>%
#   group_by(soc, pt, treatment) %>%
#   summarise(n_ae = n(), n_subj = n_distinct(subject_id)) %>%
#   mutate(pct = n_subj / total_subj * 100)

# 瀑布图
# data %>%
#   group_by(subject_id) %>%
#   slice_max(ae_grade) %>%
#   ggplot(aes(x = reorder(subject_id, ae_grade), y = ae_grade, fill = treatment)) +
#   geom_col() +
#   coord_flip()

message("Step 5 完成！")
```

## 验证标准

- [ ] AE 按 SOC/PT/组别三维汇总
- [ ] 瀑布图展示安全性分布
- [ ] 组间 AE 率对比

## 下一步

转到 [Step 6 — 报告自动生成](../Step-06-报告自动生成/README.md)
