---
tags: [SOP]
title: SOP - OCR批量处理
status: active
created: 2026-06-19
updated: 2026-06-19
---
# SOP - OCR批量处理（V1.0）

> 版本：V1.0 | 编制日期：2026-06-02
> 适用场景：临床研究项目中纯扫描件PDF的批量OCR处理
> 来源：PDF处理工具链 + 临床研究知识库摄入报告（OCR积压145+文件）
> 关联：[[02-百利/06-进度追踪/PDF处理工具链.md]] [[04-方法学与工具/90-SOP体系/01-临床研究/SOP - 临床研究项目知识库每日摄入.md]]

---

## 一、目标与交付物

**目标**：将纯扫描件PDF（文字提取字符数=0）批量转换为可搜索/可提取的PDF，纳入知识库摄入流程。

**交付物清单**：
- OCR处理后的PDF文件（`ocr_原文件名.pdf`）
- OCR处理日志（处理数量/失败文件/耗时统计）
- 纳入每日摄入流程的待处理队列

**质量标准**：
- OCR引擎：tesseract（chi_sim+eng 双语）
- 输出格式：可搜索PDF（文字层叠加在原始图像上）
- 失败文件必须记录原因并单独处理

---

## 二、环境准备

### 2.1 安装依赖

```bash
# 1. 安装 tesseract OCR 引擎（含中文语言包）
brew install tesseract
brew install tesseract-lang  # 包含chi_sim（简体中文）

# 2. 安装 ghostscript（ocrmypdf依赖）
brew install ghostscript

# 3. 安装 ocrmypdf
pip3 install ocrmypdf

# 4. 验证安装
tesseract --version
ocrmypdf --version
gs --version
```

**踩过的坑**：
- ⚠️ `pip install ocrmypdf` 失败，提示pip未找到。→ macOS上优先使用 `pip3` 而非 `pip`。
- ⚠️ `ocrmypdf` 报错缺少 `gs`（ghostscript）。→ 安装ocrmypdf前确保ghostscript已安装：`brew install ghostscript`。
- ⚠️ `brew install tesseract` 超时。→ 增加timeout到300s：`timeout 300 brew install tesseract`。

---

## 三、标准工序（3个阶段）

### 阶段1：扫描积压清单

**目标**：识别所有需要OCR处理的PDF文件

**动作顺序**：
1. 从每日摄入报告的"待OCR文件清单"中获取文件列表
2. 验证文件路径可访问
3. 按项目/中心/文件类型分类排序
4. 输出待处理队列

**输入**：摄入报告中的OCR积压清单
**输出**：排序后的OCR处理队列

---

### 阶段2：批量OCR处理

**目标**：批量执行OCR转换

**动作顺序**：

1. **创建输出目录**：
   ```bash
   mkdir -p ocr_output
   ```

2. **执行批量OCR**：
   ```bash
   for f in *.pdf; do
     echo "Processing: $f"
     ocrmypdf --lang chi_sim+eng \
              --output-type pdf \
              --force-ocr \
              "$f" "ocr_output/ocr_${f}"
     if [ $? -ne 0 ]; then
       echo "FAILED: $f" >> ocr_failed.log
     fi
   done
   ```

3. **验证OCR结果**：
   ```bash
   # 检查OCR后PDF的文字提取效果
   pdftotext -layout "ocr_output/ocr_测试文件.pdf" - | head -20
   ```

4. **记录处理日志**：
   - 成功处理数量
   - 失败文件列表及原因
   - 总耗时

**OCR参数说明**：

| 参数 | 说明 |
|------|------|
| `--lang chi_sim+eng` | 中英文双语识别 |
| `--output-type pdf` | 输出可搜索PDF（非纯文本） |
| `--force-ocr` | 强制OCR（即使PDF已有文字层） |

**踩过的坑**：
- ⚠️ 部分扫描件质量差（手写体/低分辨率/倾斜），OCR效果不佳。→ 预处理：`--rotate-pages` 自动校正页面旋转，`--deskew` 校正倾斜。
- ⚠️ 大文件（>100页）处理超时。→ 分批处理，每批≤20个文件。

---

### 阶段3：纳入摄入流程

**目标**：将OCR处理后的PDF重新纳入每日知识库摄入流程

**动作顺序**：
1. 将OCR输出目录链接到项目目录
2. 更新manifest，标记原文件为"已OCR处理"
3. 次日每日摄入流程自动处理OCR后的PDF
4. 验证提取效果（字符数≥50）

**输入**：OCR处理后的PDF
**输出**：纳入摄入流程的结构化笔记

---

## 四、质量控制检查点

| QC编号 | 检查点 | 阶段 | 阈值 |
|:------:|:------|:----:|:----:|
| QC-1 | 依赖安装完整性 | 阶段1 | tesseract/ghostscript/ocrmypdf全部可用 |
| QC-2 | OCR提取字符数 | 阶段2 | OCR后字符数≥50（可进入LLM提取） |
| QC-3 | 失败文件记录 | 阶段2 | 所有失败文件记录原因到ocr_failed.log |
| QC-4 | manifest更新 | 阶段3 | 原文件标记为"已OCR处理" |

---

## 五、紧急情况处理机制

| 场景 | 处理流程 | 回退级别 |
|:----|:---------|:--------:|
| A OCR质量差（字符数<50） | ①尝试 `--rotate-pages --deskew` 预处理 → ②手动调整语言包 → ③标记为"需人工转录" | 阶段2回退 |
| B 大文件超时 | ①分批处理（每批≤20文件） → ②增加 `--jobs 4` 并行处理 | 阶段2分批 |
| C 依赖安装失败 | ①检查brew/pip3环境 → ②换用镜像源 → ③手动编译安装 | 阶段1回退 |

---

## 六、可复用Prompt速查表

| 步 | 场景 | Prompt |
|:--:|:-----|:-------|
| 1 | 安装依赖 | `brew install tesseract tesseract-lang ghostscript; pip3 install ocrmypdf; 验证tesseract --version/ocrmypdf --version` |
| 2 | 批量OCR | `for f in *.pdf; do ocrmypdf --lang chi_sim+eng --output-type pdf --force-ocr "$f" "ocr_output/ocr_${f}"; done; 失败记录到ocr_failed.log` |
| 2 | OCR验证 | `pdftotext -layout ocr_output/ocr_测试文件.pdf - | head -20，检查字符数≥50` |
| 3 | 纳入流程 | `将ocr_output目录链接到项目目录。更新manifest标记"已OCR处理"。次日摄入流程自动处理` |

---

*本SOP基于274项目OCR积压145+文件的待改进项编制。当前扫描件占比32.7%，部署OCR后可再覆盖约20%的PDF文件。*
