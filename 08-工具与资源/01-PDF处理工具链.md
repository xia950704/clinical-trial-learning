---
tags: [pdf, 摄入流程, clinical-project, 笔记]
created: 2026-05-26
status: active
title: PDF 处理工具链
type: tool
updated: 2026-05-31
---
# PDF 处理工具链

> 用于临床项目知识库的 PDF 文件提取。安装日期：2026-05-26

---

## 工具概述

| 工具 | 用途 | 覆盖场景 |
|------|------|---------|
| pdftotext（poppler） | 快速提取文本型 PDF | 合同类、报告类、单据类 — 约 80% 的 PDF |
| PyMuPDF（fitz） | 备用提取，处理乱码/复杂格式 | 扫描件、表格混合、pdftotext 输出乱码时 |

---

## 安装方法

```sh
# pdftotext（来自 poppler-utils）
brew install poppler

# PyMuPDF
pip install pymupdf
```

---

## 使用方式

### pdftotext（首选）

快速提取文本内容。合同类 PDF 效果最好。

```sh
# 提取到 stdout
pdftotext -layout 合同.pdf -

# 保存到文件
pdftotext -layout input.pdf output.txt

# 只提取前 3 页（用于大文件预览）
pdftotext -layout -f 1 -l 3 合同.pdf -
```

**选项说明**：
- `-layout`：保持段落布局，适合合同/表格
- `-f N -l M`：从第 N 页到第 M 页
- 不传参数：默认提取全部页面到同名 .txt 文件

### PyMuPDF（备用）

当 pdftotext 输出乱码或空白时使用。

```python
import fitz
doc = fitz.open("path/to/file.pdf")
for i, page in enumerate(doc):
    text = page.get_text()
    if text.strip():
        print(f"--- 第 {i+1} 页 ---")
        print(text)
```

PyMuPDF 的 `page.get_text()` 在处理扫描件+文字混合的 PDF 时优于 pdftotext。

> 纯扫描件的 PDF（全页为图片）两个工具都无法提取文字，需要 OCR（tesseract）。

---

## 已知场景测试结果

| 文件类型 | pdftotext | PyMuPDF | 推荐策略 |
|---------|-----------|---------|---------|
| 合同 PDF（文字型） | ✅ 完美，8465 字符 | ✅ 完美 | 先 pdftotext |
| 增值税发票 | ✅ 可用，365 字符 | ✅ 完整 | 优先 pdftotext |
| 费用报销（扫描+文字混合） | ⚠️ 部分乱码，10755 字符 | ✅ 更干净 | 先用 pdftotext，乱码则换 PyMuPDF |
| 纯扫描件合同（图片型） | ❌ 0 字符 | ❌ 0 字符 | 需 OCR（tesseract）|
| 用款申请邮件 | ✅ 完整，1567 字符 | ✅ 完整 | 优先 pdftotext |

---

## 在 cron 中的使用

每天的 `project-knowledge-base-daily-ingest` cron（20:00）按以下流程处理 PDF：

1. 扫描目录，筛选出 PDF 文件
2. 按优先级排序（P0: 合同/AE-SAE → P1: protocol/伦理 → P2: 费用）
3. 对每个 PDF 执行 `pdftotext -layout` 提取
4. 若输出为空或含大量乱码，回退到 PyMuPDF
5. LLM 读取提取结果 → 写入结构化 Obsidian 笔记
6. 记录处理状态到进度追踪

---

## 待改进

> 下一步待处理

| 改进项 | 优先级 | 预计收益 |
|--------|--------|---------|
| 安装 tesseract-ocr | 低 | 再覆盖 20% 的纯扫描件 PDF |
| 批量处理脚本（自动 pdftotext → fallback PyMuPDF）| 中 | 避免手动逐文件试错
