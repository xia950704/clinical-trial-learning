# 🎓 临床试验数据分析教程（中文）

> A practical, hands-on tutorial for clinical trial data analysis in Chinese.
> 面向中文读者的临床试验数据分析实战教程，从方案设计到统计输出。

<p align="center">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Language" src="https://img.shields.io/badge/language-R-276DC3?logo=R">
  <img alt="Last Updated" src="https://img.shields.io/badge/last%20update-2026--07--02-brightgreen">
  <img alt="Stars" src="https://img.shields.io/github/stars/xia950704/clinical-trial-learning?style=social">
</p>

---

## 📖 仓库结构

本仓库按**临床试验全流程**组织，覆盖从标准到实战的完整链路：

```
clinical-trial-learning/
├── 01-CDISC标准/          # CDISC 标准体系解读（SDTM / ADaM / Define.xml）
├── 02-试验设计/           # 试验设计方法学（随机化 / 样本量 / 中期分析）
├── 03-TLF规范/            # Table, Listings, Figures 模板
├── 04-与现有内容打通/      # 知识体系连接索引
├── 05-资源清单/            # 工具、书籍、文献清单
├── 06-数据管理与医学监察/  # 数据管理 + 医学编码 + 安全性信号（含 pyCoreGage 插件）
├── 07-IIT实战教程/        # 🔥 从零搭建 IIT 数据分析流水线（持续更新中）
├── 00-索引.md             # 内容导航
├── setup.R                # 一键安装依赖
└── LICENSE
```

---

## 🚀 快速开始

```r
# 1. 克隆仓库
# git clone https://github.com/xia950704/clinical-trial-learning.git

# 2. 一键安装依赖
source("setup.R")

# 3. 直接跑实战案例
source("06-数据管理与医学监察/pyCoreGage-医学插件/实战案例/run_case.R")
```

---

## 🔥 新：从零搭建 IIT 数据分析流水线

本教程参考 [build-your-own-x](https://github.com/codecrafters-io/build-your-own-x) 模式，
用真实案例带你从 CRF 数据走到统计报告。

| 步骤 | 标题 | 内容 | 状态 |
|------|------|------|------|
| Step 1 | 从 CRF 到数据框 | CRF 表格 → 干净 data.frame | 📝 规划中 |
| Step 2 | 清洗流水线 | 去重 → 日期标准化 → 逻辑核查 → 缺失值 | 📝 规划中 |
| Step 3 | 描述统计 + Table 1 | 基线特征表自动生成 | 📝 规划中 |
| Step 4 | 疗效分析 | t检验 / KM 曲线 / 混合效应模型 | 📝 规划中 |
| Step 5 | 安全性分析 | AE/SAE 汇总 + 瀑布图 | 📝 规划中 |
| Step 6 | 报告自动生成 | R Markdown / Quarto 一键输出 | 📝 规划中 |

> 📍 教程位于 `07-IIT实战教程/`，每个 Step 一个独立目录。

---

## 📊 核心能力

| 能力 | 覆盖内容 | 位置 |
|------|---------|------|
| CDISC 标准 | SDTM / ADaM / Define.xml 解读 | `01-CDISC标准/` |
| 试验设计 | 随机化、样本量计算、中期分析 | `02-试验设计/` |
| TLF 输出 | Table 1、安全性表、图表模板 | `03-TLF规范/` |
| 知识连接 | 与 Obsidian vault 的内容打通 | `04-与现有内容打通/` |
| 资源清单 | 工具、书籍、文献推荐 | `05-资源清单/` |
| 数据监测 | 医学编码、安全性信号、PK/PD 插件 | `06-数据管理与医学监察/` |

---

## 🎯 适用人群

- **研究生/博士生**：做动物实验或 IIT，需要统计分析
- **临床医生**：想自己分析数据，不依赖统计师
- **CRO 从业者**：需要快速上手 R 语言
- **自学 R 语言**：没有项目练手，用真实案例学习

---

## 📝 学习路径

```
第1周：环境搭建 + 跑实战案例（06-数据管理与医学监察）
第2周：熟悉 CDISC 标准体系（01-CDISC标准）
第3周：试验设计方法学（02-试验设计）
第4周：TLF 规范 + 输出（03-TLF规范）
第5周：IIT 实战教程跑通（07-IIT实战教程）
```

---

## 🤝 贡献

欢迎 PR、Issue、Star。

如果你想出一份力：
- 提交 Issue 指出错误或遗漏
- PR 添加新的分析模板或案例
- 在 Issue 区讨论 IIT 教程的改进方向

---

## ⚠️ 免责声明

本教程仅供学习和参考，不构成医疗或统计建议。
实际临床试验数据分析请咨询专业统计师。

---

*最后更新：2026-07-02*
*维护者：xia950704*