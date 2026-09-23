# 🎓 临床试验数据分析教程（中文）

> A practical, hands-on tutorial for clinical trial data analysis in Chinese.
> 面向中文读者的临床试验数据分析实战教程——从方案设计、过程管理到统计输出的一站式知识库。

<p align="center">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Language" src="https://img.shields.io/badge/language-R%20%2B%20JS-276DC3?logo=R">
  <img alt="Assets" src="https://img.shields.io/badge/assets-80%20files-orange">
  <img alt="Last Updated" src="https://img.shields.io/badge/last%20update-2026--07--13-brightgreen">
  <img alt="Stars" src="https://img.shields.io/github/stars/xia950704/clinical-trial-learning?style=social">
</p>

---

## 📚 这个仓库是什么

它不只是一份 R 教程。它是一套覆盖**临床试验全生命周期**的中文知识工程系统：

| 模块 | 数量 | 内容 |
|------|------|------|
| 🧭 试验设计指南 | 15 篇 | 生物制剂 / ADC / 双抗 / 肿瘤免疫 / 器械 / IVD / 疫苗 / I 期剂量探索 / CNS / 罕见病 / 药物经济学 / 流行病学 / RWE / 预测模型 / MRCT |
| 📝 报告模板 | 11 套 | CSR、IMRAD 论文、器械报告、IVD 准确性、Meta 分析、药物经济学、预测模型、PRO、RWE 方案、单臂试验、疫苗报告 |
| 🔧 过程管理工具 | 34 份 | 医学监查、方案偏离 PD、风险与质量、中心全生命周期、数据管理 DMP、生物制剂安全监查、器械/IVD/疫苗/药经专项 |
| ⚙️ 自动化工作流 | 15 个 | 医学监查审核、文献综述、Meta 分析、预测模型开发、RWE、PD 审核、风险评估、论文写作……（JS DAG，可被 AI agent 调用） |
| 📖 参考库 | 5 份 | 毒性分级系统、领域终点速查、监管指导原则索引、报告规范索引、样本量公式 |

> 合计 **80 份资产**，全部中文，面向中国临床试验实操语境。

---

## 📁 仓库结构

```
clinical-trial-learning/
├── 01-CDISC标准/            # CDISC 标准体系（SDTM / ADaM / Define.xml）
├── 02-试验设计/             # 试验设计方法学（随机化 / 样本量 / 中期分析）
├── 03-TLF规范/              # Table, Listings, Figures 模板
├── 04-与现有内容打通/        # 知识体系连接索引
├── 05-资源清单/              # 工具、书籍、文献清单
├── 06-数据管理与医学监察/    # 数据管理 + 医学编码 + 安全性信号（含 pyCoreGage 插件）
├── 07-IIT实战教程/          # 🔥 从零搭建 IIT 数据分析流水线（骨架就绪，代码填充中）
├── 00-索引.md                # 内容导航
├── setup.R                   # 一键安装依赖
└── LICENSE
```

> 💡 设计指南、报告模板、过程管理工具、工作流、参考库这 5 大模块（共 80 份资产）目前托管在作者的 Claude Code 工作区内，作为 AI 辅助临床研究的知识底座。本仓库承载它们的**实战教程与数据管理落地部分**，后续会逐步迁移过来。

---

## 🚀 快速开始

```r
# 1. 克隆仓库
# git clone https://github.com/xia950704/clinical-trial-learning.git

# 2. 一键安装依赖
source("setup.R")

# 3. 直接跑实战案例
python3 "06-数据管理与医学监察/pyCoreGage-医学插件/实战案例/run_demo_simple.py"
```

---

## 🔥 IIT 实战教程：从零搭建数据分析流水线

本教程参考 [build-your-own-x](https://github.com/codecrafters-io/build-your-own-x) 模式，
用真实案例带你从 CRF 数据走到统计报告。**6 步骨架已就绪**（每步含目标 / 输入 / 输出 / 学习要点），R 代码正按步填充。

| Step | 标题 | 状态 |
|------|------|------|
| 1 | 从 CRF 到数据框 | 📝 骨架就绪 |
| 2 | 清洗流水线 | 📝 骨架就绪 |
| 3 | 描述统计 + Table 1 | 📝 骨架就绪 |
| 4 | 疗效分析 | 📝 骨架就绪 |
| 5 | 安全性分析 | 📝 骨架就绪 |
| 6 | 报告自动生成 | 📝 骨架就绪 |

> 📍 教程位于 `07-IIT实战教程/`，每个 Step 一个独立目录。欢迎在 Issue 区认领任意一步贡献代码。

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
| IIT 实战 | 6 步从 CRF 到报告 | `07-IIT实战教程/` |

---

## 🎯 适用人群

- **研究生/博士生**：做动物实验或 IIT，需要统计分析
- **临床医生**：想自己分析数据，不依赖统计师
- **CRO/MA 从业者**：需要现成的 SOP、checklist、报告模板
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

## 🔗 相关渠道

- **公众号**：临床试验与数据科学（中文实操内容首发渠道，持续更新中）
- **作者**：夏爽 · 临床研究 + 医药投研 · 武汉
- **Issue 区**：欢迎认领 IIT 教程的任意一步贡献代码，或提出方向建议

> 这个仓库是作者"AI 辅助临床研究"体系的一部分。如果你也在用 AI 工具做临床数据分析，欢迎来交流——我们可能正解决同一个问题。

---

## 🤝 贡献

欢迎 PR、Issue、Star。

如果你想出一份力：
- 提交 Issue 指出错误或遗漏
- PR 补全 IIT 实战教程的任一步代码
- PR 添加新的分析模板或案例
- 在 Issue 区讨论教程的改进方向

---

## ⚠️ 免责声明

本教程仅供学习和参考，不构成医疗或统计建议。
实际临床试验数据分析请咨询专业统计师。

---

*最后更新：2026-07-13*
*维护者：xia950704*
