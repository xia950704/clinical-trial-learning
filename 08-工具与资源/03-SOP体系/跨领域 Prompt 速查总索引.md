---
tags: [SOP, 索引]
title: 跨领域 Prompt 速查总索引
status: active
created: 2026-06-19
updated: 2026-06-19
---
# 跨领域 Prompt 速查总索引

> 编制日期：2026-06-02
> 用途：所有SOP中Prompt的统一索引，按领域分类
> 关联：[[04-方法学与工具/90-SOP体系/SOP体系总览与规划.md]]

---

## 索引目录

| 编号 | 领域 | Prompt 数量 | 详细索引 |
|:----:|------|:----------:|---------|
| P-CR | 临床研究 | 26+14=40条 | [临床研究Prompt](#p-cr-临床研究) |
| P-IR | 投研 | 10条 | [投研Prompt](#p-ir-投研) |
| P-KM | 知识库管理 | 10条 | [知识库管理Prompt](#p-km-知识库管理) |
| P-TL | 工具链 | 4条 | [工具链Prompt](#p-tl-工具链) |
| P-SYS | 系统运维 | 4条 | [系统运维Prompt](#p-sys-系统运维) |
| P-GEN | 通用 | 3条 | [通用Prompt](#p-gen-通用) |

**总计：71条可复用Prompt**

---

## P-CR 临床研究（40条）

### IIT数据分析SOP（26条）— 详见 `08-临床研究/IIT 数据分析 Prompt 速查索引.md`

| 步 | 场景 | Prompt |
|:--:|:-----|:-------|
| P-CR-01 | 首次接触数据 | `列出所有Sheet及行数列数；对每Sheet输出字段清单、唯一值枚举、缺失率；识别SUB/DM/EXB/EVA/AE/CM/VS/EG/DS核心域` |
| P-CR-02 | 输出数据字典 | `遍历所有Sheet，提取每列：Sheet名,列号,中文标签,变量名,数据类型,示例值,缺失率→输出为variable_inventory.csv` |
| P-CR-03 | 识别EDC第1行/第2行 | `判断第1行是否为中文标签、第2行是否为变量名。对_TXT后缀的特殊处理` |
| P-CR-04 | 交叉验证总数 | `从SUB域提取SUBJID列表。从入组管理表提取SUBJID列表。比对→三种输出` |
| P-CR-05 | 去重 | `按SUBJID检查重复，保留第一条，输出删除的重复项到CSV。所有关联Sheet同步执行` |
| P-CR-06 | 日期标准化 | `扫描所有*DAT/*DT字段，统一为YYYY-MM-DD。处理多种格式。无法解析的输出到CSV` |
| P-CR-07 | 分类变量标准化 | `枚举所有分类变量的唯一值。将Y/N/1/0/是/否统一为Y/N。输出转换日志CSV` |
| P-CR-08 | 中心映射 | `建立中心名称→标准2位编码映射。验证数据库中心分布与管理表一致` |
| P-CR-09 | 逻辑核查 | `执行6项逻辑核查：跨域一致性/访视顺序/AE时间/CM时间/转复时间逻辑/中心归属` |
| P-CR-10 | 生成ADSL | `基于清洗数据生成：ADSL(受试者级,含ARM)、ADEFF(疗效)、ADAE(安全性)、ADVS(生命体征)` |
| P-CR-11 | 术语提取 | `从MH/AE/CM域提取所有诊断/药物/事件术语，去重` |
| P-CR-12 | MH清洗 | `合并Excel软换行断裂术语。使用诊断词锚点切分（心血管用104词库）` |
| P-CR-13 | CM清洗 | `执行五步清洗：①剥离剂量 ②商品名→通用名映射 ③复合配方拆分 ④括号对称修正 ⑤中药标记` |
| P-CR-14 | MH编码 | `清洗后的诊断逐条匹配ICD-10→MedDRA LLT→PT→SOC` |
| P-CR-15 | 待确认项输出 | `无法编码的术语按原因分类输出到pending_list.xlsx` |
| P-CR-16 | 编码回映射 | `将编码写回原始数据库，新增MH_ICD10/MH_MedDRA_LLT等字段` |
| P-CR-17 | 分组验证 | `从随机分配表提取随机号→组别映射。与ADSL的ARM交叉验证` |
| P-CR-18 | Table 1 | `ADSL+MH+手术数据。三栏表：年龄/性别/既往史(SOC)/手术类型` |
| P-CR-19 | 主要终点 | `从ADEFF提取转复状态（用visit_map精确映射！）。χ²检验(Yates校正)` |
| P-CR-20 | 转复时间KM | `EVACDAT+EVACTIM - EXBHRDAT+EXBHRTIM = time_to_conv(hours)。KM估计+Log-rank` |
| P-CR-21 | AE Listing | `从ADAE提取所有AETERM非空的记录。每个AE一行：SUBJID/组别/AETERM/CTCAE/SOC` |
| P-CR-22 | AE SOC汇总 | `按SOC分组，各组计数除以总例数。Fisher精确检验` |
| P-CR-23 | SOC手动映射 | `建立AETERM→SOC映射字典` |
| P-CR-24 | 中文Protocol | `语言规则：零连接词/零元话语/被动语态优先/无评价无解释/去口语化` |
| P-CR-25 | 英文Protocol | `从中文版翻译。替换中文文献为英文。引用改为AMA格式` |
| P-CR-26 | 文献格式转换 | `从GB/T 7714转为AMA：括号[]→上标编号` |

### 知识库每日摄入SOP（7条）

| 步 | 场景 | Prompt |
|:--:|:-----|:-------|
| P-CR-27 | 预检环境 | `检查pdftotext版本、硬盘挂载状态、读取manifest文件、扫描新增PDF` |
| P-CR-28 | 优先级排序 | `按P0(合同/SAE)→P1(protocol/伦理)→P2(费用/会议)→P3(文献/病例)排序` |
| P-CR-29 | PDF提取 | `pdftotext -layout input.pdf -，检查字符数≥50，<50标记SKIP_SCANNED` |
| P-CR-30 | LLM提取-合同 | `从合同文本提取：甲方/乙方/金额/日期/核心条款/签署状态` |
| P-CR-31 | LLM提取-病例 | `从病例文本提取：SUBJID/中心/诊断/用药/AE事件/转归状态` |
| P-CR-32 | 写入验证 | `写入笔记到vault指定目录，建立wikilink关联，更新manifest` |
| P-CR-33 | 报告输出 | `输出每日摄入报告：工具状态/挂载状态/可读性评估/各项目详情/diff分析` |

### 医学编码SOP（7条）

| 步 | 场景 | Prompt |
|:--:|:-----|:-------|
| P-CR-34 | 术语提取 | `从MH/AE/CM域提取所有诊断/药物/事件术语，去重` |
| P-CR-35 | MH清洗 | `合并Excel软换行断裂术语。使用诊断词锚点切分` |
| P-CR-36 | CM清洗 | `执行五步清洗：①剥离剂量 ②商品名→通用名 ③复合配方拆分 ④括号修正 ⑤中药标记` |
| P-CR-37 | MH编码 | `逐条匹配ICD-10→MedDRA LLT→PT→SOC` |
| P-CR-38 | AE编码 | `同MH流程+CTCAE v5.0分级` |
| P-CR-39 | 待确认项 | `无法编码的术语按原因分类输出到pending_list.xlsx` |
| P-CR-40 | 回映射 | `将编码写回原始数据库，新增编码字段` |

---

## P-IR 投研（10条）

### 医药股票周检SOP（4条）

| 步 | 场景 | Prompt |
|:--:|:-----|:-------|
| P-IR-01 | 锚股票检查 | `逐一打开港交所披露易/巨潮资讯，检查12只锚股票本周公告` |
| P-IR-02 | 信号判断 | `检查6项信号：BD大单/ADC销售/生物安全法案/百济盈利/CM310销售/销售费用问询` |
| P-IR-03 | 深度跟踪 | `读取最新财报/公告/研报。提取关键数据。对比上期变化` |
| P-IR-04 | 价格更新 | `调用stock-price-fetcher批量拉取行情。patch更新frontmatter价格` |

### 个股分析SOP（6条）

| 步 | 场景 | Prompt |
|:--:|:-----|:-------|
| P-IR-05 | 创建投资笔记 | `核心判断(一句话)+关键数据表+估值状态(🟢🟡⚠️🔴)+投资逻辑+操作区间` |
| P-IR-06 | 创建技术分析 | `现价+52周高/低+距高比例+MA5/20/60/250位置+支撑/阻力位` |
| P-IR-07 | 创建事件时间线 | `BD/临床/财报/政策事件按时间排序，含日期/类型/描述/影响评估/来源` |
| P-IR-08 | 创建估值追踪 | `PE(TTM)/PB+历史分位(近5年)+买入/卖出区间+估值变化日志` |
| P-IR-09 | 创建业务管线 | `核心产品(收入/占比)+在研管线(阶段/预计上市)+竞品对比+商业模式` |
| P-IR-10 | 批量创建 | `为{股票名}({CODE})批量创建5个标准文件，frontmatter含code/name/sector/status/tags` |

---

## P-KM 知识库管理（10条）

### Vault健康检查SOP（4条）

| 步 | 场景 | Prompt |
|:--:|:-----|:-------|
| P-KM-01 | 健康扫描 | `扫描vault：文件总数/broken links/stub笔记/重复文件/缺失frontmatter/编号冲突` |
| P-KM-02 | Broken links修复 | `逐一处理broken links：确认目标状态→选择修复方式→patch更新源文件` |
| P-KM-03 | Stub处理 | `评估每个stub笔记：重要→创建(用模板)；无意义→移除链接；暂时不需要→保留` |
| P-KM-04 | 结构整理 | `检查文件命名(编号规范)/目录结构/frontmatter/链接规范` |

### AI观察日志SOP（2条）

| 步 | 场景 | Prompt |
|:--:|:-----|:-------|
| P-KM-05 | 每日记录 | `在99-AI观察日志追加：新事实/新洞察(→归档位置)/待办(P0-P3)` |
| P-KM-06 | 每周归档 | `扫描99-AI观察日志最近7天。提取新洞察。按领域分类。更新归档索引` |

### 临床研究摄入SOP（4条）— 已在P-CR中

---

## P-TL 工具链（4条）

### OCR批量处理SOP（4条）

| 步 | 场景 | Prompt |
|:--:|:-----|:-------|
| P-TL-01 | 安装依赖 | `brew install tesseract tesseract-lang ghostscript; pip3 install ocrmypdf` |
| P-TL-02 | 批量OCR | `for f in *.pdf; do ocrmypdf --lang chi_sim+eng "$f" "ocr_output/ocr_${f}"; done` |
| P-TL-03 | OCR验证 | `pdftotext -layout ocr_output/ocr_测试文件.pdf - | head -20，检查字符数≥50` |
| P-TL-04 | 纳入流程 | `将ocr_output目录链接到项目目录。更新manifest标记"已OCR处理"` |

---

## P-SYS 系统运维（4条）

### Hermes系统维护SOP（4条）

| 步 | 场景 | Prompt |
|:--:|:-----|:-------|
| P-SYS-01 | 健康检查 | `hermes --version; hermes cron list; hermes skill list; cat ~/.hermes/config.yaml` |
| P-SYS-02 | Cron管理 | `hermes cron list/pause/resume/update/remove <job_id>` |
| P-SYS-03 | 技能管理 | `hermes skill list/create/patch/delete --name "技能名"` |
| P-SYS-04 | 故障排查 | `复现故障→搜索踩坑录→修复→验证→更新踩坑录（如新故障）` |

---

## P-GEN 通用（3条）

### 模板使用与创建SOP（3条）

| 步 | 场景 | Prompt |
|:--:|:-----|:-------|
| P-GEN-01 | 使用模板 | `在笔记frontmatter添加 `template: 模板名称`，根据模板结构填充内容` |
| P-GEN-02 | 创建新模板 | `确定模板类型→设计标准结构→命名`模板-描述.md`→存入07-模板/→验证→更新索引` |
| P-GEN-03 | 更新模板索引 | `在07-模板/00-模板索引.md中添加新模板条目` |

---

## 快速检索

- **按领域搜**：搜索 `P-CR` / `P-IR` / `P-KM` / `P-TL` / `P-SYS` / `P-GEN`
- **按编号搜**：搜索 `P-CR-01` ~ `P-CR-40` / `P-IR-01` ~ `P-IR-10` 等
- **按关键词搜**：搜索 `PDF提取` / `医学编码` / `Protocol` / `股票` / `OCR` / `Cron`

---

*本索引汇总所有SOP中的Prompt，共71条。详细Prompt见各SOP文件中的"可复用Prompt速查表"章节。*
