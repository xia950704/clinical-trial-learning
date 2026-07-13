# Step 1 — 从 CRF 到数据框

## 目标

将纸质 CRF（Case Report Form）或电子数据导出（Excel/CSV）转换成可分析的 R data.frame。

## 你会学到

- 读取不同格式的源数据（Excel / CSV / REDCap 导出）
- 列名标准化（统一为 snake_case）
- 变量类型推断（数字 vs 字符 vs 因子）
- 初步数据校验（范围检查、缺失率）

## 输入

`data/source/crf_data.xlsx`（样例数据）

## 输出

- `derived/raw_data.rds`（标准化后的 R 对象）
- 数据字典 `derived/data_dictionary.csv`

## 代码骨架

```r
# Step 1: CRF → data.frame
# TODO: 完善此脚本

library(tidyverse)
library(readxl)
library(janitor)

# 1. 读取源数据
raw <- read_excel("data/source/crf_data.xlsx")

# 2. 列名标准化
clean_data <- raw %>%
  clean_names()  # janitor 包：统一 snake_case

# 3. 类型推断
# str(clean_data)

# 4. 保存
# saveRDS(clean_data, "derived/raw_data.rds")
# write_csv(data_dictionary, "derived/data_dictionary.csv")

message("Step 1 完成！")
```

## 验证标准

- [ ] 所有列名统一为 `snake_case`
- [ ] 日期列为 `Date` 类型
- [ ] 数值列无隐式字符
- [ ] 生成数据字典

## 下一步

转到 [Step 2 — 清洗流水线](../Step-02-清洗流水线/README.md)