# =============================================================================
# 基线表生成脚本 (Template One)
# 依赖包: {gtsummary}, {tidyverse}, {tableone}
# 作者: [姓名] | 日期: [YYYY-MM-DD] | 版本: v1.0
# =============================================================================

library(gtsummary)
library(tidyverse)
library(tableone)
library(dplyr)
library(survey)  # 可选：用于复杂抽样设计

# 设置全局选项
options(gtsummary.default_pkg_style = list(
  style_number = list(digits = 1, big.mark = ",", decimal.mark = "."),
  style_percent = list(digits = 1)
))

# ---- 1. 数据加载与预处理 ----
# 读取数据文件
clinical_data <- read_csv("data/clinical_baseline.csv",
                          col_types = cols(
                            patient_id = col_character(),
                            treatment = col_factor(levels = c("Control", "Experimental")),
                            age = col_double(),
                            sex = col_factor(levels = c("Male", "Female")),
                            race = col_factor(levels = c("White", "Asian", "Black", "Other")),
                            ecog = col_factor(levels = c("0", "1", "2", "3", "4")),
                            stage = col_factor(levels = c("I", "II", "III", "IV")),
                            hemoglobin = col_double(),
                            wbc = col_double(),
                            platelet = col_double()
                          ))

# 数据清洗
clinical_data <- clinical_data %>%
  mutate(
    age_group = case_when(
      age < 65 ~ "< 65 岁",
      TRUE ~ "≥ 65 岁"
    ),
    age_group = factor(age_group, levels = c("< 65 岁", "≥ 65 岁"))
  )

# 检查缺失值
missing_summary <- clinical_data %>%
  summarise(across(everything(), ~ sum(is.na(.)))) %>%
  pivot_longer(everything(), names_to = "variable", values_to = "missing_count") %>%
  filter(missing_count > 0)

if (nrow(missing_summary) > 0) {
  message("⚠️  以下变量存在缺失值:")
  print(missing_summary)
}

# ---- 2. 描述性统计 ----
# 连续变量：均值±标准差 或 中位数(四分位距)
# 分类变量：n (%)

# 方法 1: 使用 tbl_summary (gtsummary 推荐)
baseline_table <- clinical_data %>%
  select(treatment, age, age_group, sex, race, ecog, stage,
         hemoglobin, wbc, platelet) %>%
  tbl_summary(
    by = treatment,
    missing = "no",
    statistic = list(all_continuous() ~ "{mean} ({sd})",
                     all_categorical() ~ "{n} ({p}%)"),
    digits = list(
      all_continuous() ~ c(1, 1),
      all_categorical() ~ c(0, 1)
    )
  ) %>%
  modify_header(
    all_stat_cols() ~ "**{level}**<br>N = {n}"
  ) %>%
  modify_footnote(
    all_stat_cols() ~ "Mean (SD)"
  )

# ---- 3. 统计检验 ----
# 连续变量：t 检验 (正态) 或 Wilcoxon 秩和检验 (非正态)
# 分类变量：卡方检验 或 Fisher 精确检验

# 添加 p 值
baseline_table_with_p <- baseline_table %>%
  add_p(
    test = list(
      all_continuous() ~ "t.test",  # 或 "wilcox.test"
      all_categorical() ~ "chisq.test"  # 或 "fisher.test"
    ),
    pvalue_fun = ~ style_pvalue(.x, digits = 3)
  )

# ---- 4. 表格输出 ----

# 4.1 控制台输出
print(baseline_table_with_p)

# 4.2 导出为 Word
baseline_table_with_p %>%
  as_flex_table() %>%
  flex_table_options(
    table.width = "100%",
    font.size = 9
  ) %>%
  flex_table_header(
    title = "Table 1. Baseline Characteristics",
    subtitle = "Demographics and disease characteristics of study population"
  ) %>%
  flex_table_footnote(
    footnote = "Data are presented as mean (SD) or n (%). Abbreviations: SD = standard deviation."
  ) %>%
  flex_table_body(
    bold_rows = "Variable"
  ) %>%
  save_as_docx(path = "output/Table1_baseline.docx")

# 4.3 导出为 PDF (LaTeX)
baseline_table_with_p %>%
  as_flex_table() %>%
  save_as_pdf(
    path = "output/Table1_baseline.pdf",
    title = "Table 1. Baseline Characteristics",
    caption = "Demographics and disease characteristics of study population"
  )

# 4.4 导出为 RTF (用于 SAS 风格报告)
baseline_table_with_p %>%
  as_flex_table() %>%
  save_as_rtf(path = "output/Table1_baseline.rtf")

# ---- 5. 替代方案：使用 tableone 包 ----
# 当需要更灵活的统计检验控制时

# 定义变量列表
vars <- c("age", "sex", "race", "ecog", "stage", "hemoglobin", "wbc", "platelet")
strata <- "treatment"

# 创建 TableOne 对象
tableone_obj <- CreateTableOne(
  vars = vars,
  strata = strata,
  data = clinical_data,
  factorVars = c("sex", "race", "ecog", "stage"),
  test = TRUE
)

# 打印结果
print(tableone_obj, showAllLevels = TRUE, quote = TRUE, noSpaces = TRUE)

# 导出为 CSV
tableone_df <- data.frame(
  Variable = rownames(tableone_obj),
  Overall = tableone_obj$overall,
  Control = tableone_obj$cells[, 1],
  Experimental = tableone_obj$cells[, 2],
  p = tableone_obj$pval
)
write_csv(tableone_df, "output/Table1_tableone.csv")

# ---- 6. 变量标签设置 ----
# 使用 sjlabelled 包为变量添加标签

library(sjlabelled)

clinical_data <- clinical_data %>%
  set_variable_labels(
    age = "Age (years)",
    sex = "Sex",
    race = "Race",
    ecog = "ECOG Performance Status",
    stage = "Disease Stage",
    hemoglobin = "Hemoglobin (g/L)",
    wbc = "White Blood Cell Count (×10⁹/L)",
    platelet = "Platelet Count (×10⁹/L)"
  )

# ---- 7. 质量检查 ----
# 检查组间基线可比性

baseline_check <- clinical_data %>%
  group_by(treatment) %>%
  summarise(
    n = n(),
    age_mean = mean(age, na.rm = TRUE),
    age_sd = sd(age, na.rm = TRUE),
    male_pct = mean(sex == "Male", na.rm = TRUE) * 100
  )

print(baseline_check)

# ---- 8. 运行日志 ----
run_log <- list(
  script_name = "template_one.R",
  execution_date = Sys.Date(),
  input_file = "data/clinical_baseline.csv",
  output_files = c(
    "output/Table1_baseline.docx",
    "output/Table1_baseline.pdf",
    "output/Table1_tableone.csv"
  ),
  packages_used = c("gtsummary", "tidyverse", "tableone", "sjlabelled"),
  notes = "Baseline characteristics table generated successfully."
)

saveRDS(run_log, "output/run_log_baseline.rds")

message("✅ 基线表生成完成！")
