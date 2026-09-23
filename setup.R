# ============================================================
# setup.R — 一键安装 clinical-trial-learning 所需依赖包
# 用法: source("setup.R")
# ============================================================

options(repos = c(CRAN = "https://cloud.r-project.org"))

required_pkgs <- c(
  # 数据处理
  "tidyverse",   # dplyr + tidyr + ggplot2 + readr + purrr
  "lubridate",   # 日期处理
  "stringr",     # 字符串标准化

  # 统计分析
  "lme4",        # 混合效应模型（动物实验重复测量）
  "lmerTest",    # 混合效应模型 p 值
  "emmeans",     # 事后检验
  "survival",    # KM 曲线 + Cox 回归
  "survminer",   # 出版级 KM 图
  "rstatix",     # 统计检验包装（t检验/卡方/秩和）

  # 可视化
  "ggplot2",     # 基础图形
  "ggpubr",      # 出版级图表（含统计比较）
  "showtext",    # 中文字体支持
  "RColorBrewer",# 配色

  # 报告
  "rmarkdown",   # R Markdown 报告
  "knitr",       # 动态报告
  "kableExtra",  # 表格美化

  # 实用工具
  "here",        # 路径管理
  "readxl",      # Excel 读取
  "writexl",     # Excel 输出
  "janitor"      # 数据清洗辅助
)

# 检查 + 安装缺失包
install_if_missing <- function(pkg) {
  if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
    message("安装: ", pkg)
    install.packages(pkg)
  } else {
    message("✓ ", pkg)
  }
}

invisible(lapply(required_pkgs, install_if_missing))

message("\n✓ 所有依赖包已就绪！")
message("运行 'source(\"01-...\")' 开始学习。")