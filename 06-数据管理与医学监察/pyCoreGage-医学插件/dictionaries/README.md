# 医学词典

本目录包含临床试验常用的医学编码词典，用于医学编码检查模块。

## 词典列表

| 词典 | 文件 | 说明 |
|------|------|------|
| **MedDRA** | meddra/meddra_codes.json | 不良事件编码词典（LLT→PT→SOC） |
| **ICD-10** | icd10/icd10_codes.json | 诊断编码词典 |
| **ATC** | atc/atc_codes.json | 药物编码词典 |
| **LOINC** | loinc/loinc_codes.json | 实验室检验项目编码词典 |
| **SNOMED CT** | snomed/snomed_codes.json | 临床术语编码词典 |

## 使用说明

1. **内置词典**：每个词典文件包含示例编码，用于测试和演示
2. **外部词典**：可下载完整版词典替换示例文件
3. **自定义词典**：可在 custom/ 目录添加项目自定义编码

## 词典来源

| 词典 | 官方来源 | 许可 |
|------|---------|------|
| **MedDRA** | [MedDRA Maintenance and Support Services Organization](https://www.meddra.org/) | 需注册 |
| **ICD-10** | [WHO International Classification of Diseases](https://icd.who.int/) | 公开 |
| **ATC** | [WHO Collaborating Centre for Drug Statistics Methodology](https://www.whocc.no/atc_ddd_index/) | 公开 |
| **LOINC** | [Regenstrief Institute](https://loinc.org/) | 公开 |
| **SNOMED CT** | [SNOMED International](https://www.snomed.org/) | 需许可 |

## 注意事项

- 本示例词典仅用于测试和演示，生产环境需使用完整版词典
- 词典版本需与项目要求一致
- 词典更新时需同步更新编码检查模块
