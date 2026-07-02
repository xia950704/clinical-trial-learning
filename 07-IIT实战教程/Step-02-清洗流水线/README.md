# Step 2 — 清洗流水线

## 目标

对原始数据进行系统化清洗：去重 → 日期标准化 → 分类变量编码统一 → 逻辑核查 → 缺失值处理。

## 你会学到

- 多步清洗管道（pipe 式代码）
- 日期格式自动检测与统一
- 分类变量的编码映射
- 逻辑一致性检查（年龄 vs 出生日期）
- 缺失值模式识别与处理策略

## 输入

`Step-01-CRF到数据框/derived/raw_data.rds`

## 输出

`derived/clean_data.rds`

## 代码骨架

```r
library(tidyverse)
library(lubridate)
library(janitor)

raw <- readRDS("../Step-01-CRF到数据框/derived/raw_data.rds")

# S1: 去重
clean <- raw %>% distinct(patient_id, .keep_all = TRUE)

# S2: 日期标准化
# clean <- clean %>% mutate(across(ends_with("_dt"), ymd))

# S3: 分类变量标准化
# sex_map <- c("1"="男", "2"="女", "M"="男", "F"="女")
# clean <- clean %>% mutate(sex = recode(sex, !!!sex_map))

# S4: 逻辑核查
# clean <- clean %>% filter(age >= 18, age <= 100)

# S5: 缺失值处理
# visdat::vis_miss(clean)
# clean <- clean %>% drop_na(subject_id, treatment)

message("Step 2 完成！")
```

## 验证标准

- [ ] 无完全重复行
- [ ] 所有日期格式一致
- [ ] 分类变量编码统一
- [ ] 逻辑值域无异常
- [ ] 缺失值有记录

## 下一步

转到 [Step 3 — 描述统计与 Table 1](../Step-03-描述统计与Table1/README.md)