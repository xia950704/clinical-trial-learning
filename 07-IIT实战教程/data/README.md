# 样例数据集

## 目录

```
data/
├── source/           ← 原始数据（模拟真实 CRF 导出）
│   └── crf_data.xlsx
├── derived/          ← 各步处理后的中间数据
│   ├── raw_data.rds
│   └── clean_data.rds
└── output/           ← 最终输出
    ├── table1.html
    ├── km_curve.png
    └── IIT_analysis_report.html
```

## 数据说明

样例数据集为模拟 IIT 数据，包含约 100-200 例受试者的人口学、基线、疗效、安全性字段。

## 生成方式

使用 `data/generate_sample_data.R` 生成。
