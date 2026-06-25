# 医学词典下载说明

本目录包含临床试验常用的医学编码词典。由于版权和许可限制，完整版词典需要从官方来源下载。

---

## 📚 词典列表

| 词典 | 官方来源 | 许可 | 下载方式 |
|------|---------|------|---------|
| **MedDRA** | [MedDRA MMSO](https://www.meddra.org/) | 商业许可 | 需注册 MedDRA MMSO 账户 |
| **ICD-10** | [WHO ICD](https://icd.who.int/) | 公开 | 可直接下载（需注册） |
| **ATC** | [WHO ATC](https://www.whocc.no/atc_ddd_index/) | 公开 | 可直接下载（需注册） |
| **LOINC** | [LOINC](https://loinc.org/) | 公开 | 可直接下载（需注册） |
| **SNOMED CT** | [SNOMED International](https://www.snomed.org/) | 需许可 | 需注册许可 |

---

## 📥 下载步骤

### 1. MedDRA

1. 访问 [MedDRA MMSO](https://www.meddra.org/)
2. 注册 MedDRA MMSO 账户
3. 申请 MedDRA 词典下载许可
4. 下载 CSV/Excel 格式词典

**注意**：MedDRA 是商业词典，需要付费许可。

### 2. ICD-10

1. 访问 [WHO ICD](https://icd.who.int/)
2. 注册 WHO ICD 账户
3. 下载 ICD-10 映射文件（CSV 格式）

**注意**：ICD-10 是公开的，但下载需要注册。

### 3. ATC

1. 访问 [WHO ATC](https://www.whocc.no/atc_ddd_index/)
2. 注册 WHO ATC 账户
3. 下载 ATC 索引文件（CSV 格式）

**注意**：ATC 是公开的，但下载需要注册。

### 4. LOINC

1. 访问 [LOINC](https://loinc.org/)
2. 注册 LOINC 账户
3. 下载 LOINC 词典（CSV 格式）

**注意**：LOINC 是公开的，但下载需要注册。

### 5. SNOMED CT

1. 访问 [SNOMED International](https://www.snomed.org/)
2. 注册 SNOMED CT 许可
3. 下载 SNOMED CT 词典（Rf2/CSV 格式）

**注意**：SNOMED CT 需要许可，部分国家/地区可免费使用。

---

## 📁 词典结构

下载后，将词典文件放入对应目录：

```
dictionaries/
├── meddra/
│   ├── meddra_codes.json      # 示例词典（已存在）
│   └── meddra_full.csv        # 完整版词典（需下载）
├── icd10/
│   ├── icd10_codes.json       # 示例词典（已存在）
│   └── icd10_full.csv         # 完整版词典（需下载）
├── atc/
│   ├── atc_codes.json         # 示例词典（已存在）
│   └── atc_full.csv           # 完整版词典（需下载）
├── loinc/
│   ├── loinc_codes.json       # 示例词典（已存在）
│   └── loinc_full.csv         # 完整版词典（需下载）
└── snomed/
    ├── snomed_codes.json      # 示例词典（已存在）
    └── snomed_full.csv        # 完整版词典（需下载）
```

---

## 🔧 使用示例词典

本目录已包含示例词典文件（JSON 格式），用于测试和演示：

- `meddra/meddra_codes.json` - MedDRA 不良事件编码（10 条示例）
- `icd10/icd10_codes.json` - ICD-10 诊断编码（10 条示例）
- `atc/atc_codes.json` - ATC 药物编码（10 条示例）
- `loinc/loinc_codes.json` - LOINC 实验室检验编码（10 条示例）
- `snomed/snomed_codes.json` - SNOMED CT 临床术语（10 条示例）

---

## ⚠️ 注意事项

1. **示例词典仅用于测试**：示例词典包含少量编码，仅用于测试和演示
2. **生产环境需完整版**：生产环境需要使用完整版词典
3. **词典版本需一致**：词典版本需与项目要求一致
4. **词典更新需同步**：词典更新时需同步更新编码检查模块
5. **许可合规**：使用词典需遵守官方许可协议

---

## 📞 联系

如需帮助，请联系：

- **MedDRA**: [MedDRA MMSO](https://www.meddra.org/)
- **ICD-10**: [WHO ICD](https://icd.who.int/)
- **ATC**: [WHO ATC](https://www.whocc.no/atc_ddd_index/)
- **LOINC**: [LOINC](https://loinc.org/)
- **SNOMED CT**: [SNOMED International](https://www.snomed.org/)

---

*最后更新：2026-06-25*
