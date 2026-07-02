# Step 6 — 报告自动生成

## 目标

将前面 5 步的分析结果自动整合为一份完整的统计报告（HTML / PDF / Word）。

## 你会学到

- R Markdown 参数化报告
- Quarto 跨格式输出
- 动态图表嵌入
- 一键渲染脚本

## 输入

前 5 步的所有输出

## 输出

- `output/IIT_analysis_report.html`（最终报告）

## 代码骨架

```yaml
---
title: "IIT 数据分析报告"
author: "xia950704"
date: "`r Sys.Date()`"
output: 
  html_document:
    toc: true
    toc_float: true
    theme: flatly
params:
  data_path: "Step-02-清洗流水线/derived/clean_data.rds"
---
```

## 验证标准

- [ ] 报告包含全部 5 步结果
- [ ] 表格和图片自动嵌入
- [ ] 一键渲染可重复

## 🎉 恭喜完成！

你已经掌握了 IIT 数据分析的完整流水线。
欢迎在 Issue 区分享你的建议。
