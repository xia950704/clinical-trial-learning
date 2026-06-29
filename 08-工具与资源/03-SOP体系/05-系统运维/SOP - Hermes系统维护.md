---
tags: [SOP, 系统运维]
title: SOP - Hermes系统维护
status: active
created: 2026-06-19
updated: 2026-06-19
---
# SOP - Hermes系统维护（V1.0）

> 版本：V1.0 | 编制日期：2026-06-02
> 适用场景：Hermes Agent系统的日常维护、Cron管理、技能管理、故障排查
> 来源：AI协作踩坑录 + 已验证流程模式 + 流程方法论管理规范
> 关联：[[04-方法学与工具/00-踩坑录.md]] [[04-方法学与工具/90-流程方法论/03-流程模式-已验证.md|已验证的流程模式]] [[04-方法学与工具/90-流程方法论/01-流程方法论管理规范.md]]

---

## 一、目标与交付物

**目标**：保持Hermes系统稳定运行，定期维护Cron任务、技能库、配置文件，快速定位并修复故障。

**交付物清单**：
- 系统健康检查报告
- Cron任务状态清单
- 技能库更新日志
- 故障排查记录

---

## 二、标准工序

### 2.1 系统健康检查

**检查内容**：

| 检查项 | 命令 | 正常状态 |
|--------|------|---------|
| Hermes版本 | `hermes --version` | 最新稳定版 |
| Cron任务 | `hermes cron list` | 所有任务enabled |
| 技能列表 | `hermes skill list` | 无缺失技能 |
| 配置文件 | `cat ~/.hermes/config.yaml` | YAML语法正确 |
| 日志文件 | `tail -100 ~/.hermes/logs/*.log` | 无ERROR级别错误 |

**踩过的坑**：
- ⚠️ Cron list显示bug：CLI显示"No scheduled jobs"但jobs.json intact。→ 用 `cat ~/.hermes/jobs.json` 直接检查，不依赖CLI。

---

### 2.2 Cron任务管理

**标准操作**：

| 操作 | 命令 | 说明 |
|------|------|------|
| 查看任务 | `hermes cron list` | 列出所有 scheduled jobs |
| 创建任务 | `hermes cron create --schedule "0 20 * * *" --prompt "..."` | 每日20:00执行 |
| 暂停任务 | `hermes cron pause <job_id>` | 临时禁用 |
| 恢复任务 | `hermes cron resume <job_id>` | 重新启用 |
| 更新任务 | `hermes cron update <job_id> --prompt "新prompt"` | 修改执行内容 |
| 删除任务 | `hermes cron remove <job_id>` | 永久删除 |

**批量更新流程**（已验证模式）：
1. 逐一确认每个修改的必要性
2. 列出所有待更新任务
3. 按依赖顺序执行更新（先更新被依赖的任务）
4. 验证更新后任务状态

**踩过的坑**：
- ⚠️ Cron任务依赖顺序错误导致执行失败。→ 更新前梳理任务依赖关系，按依赖顺序执行。

---

### 2.3 技能管理

**标准操作**：

| 操作 | 命令 | 说明 |
|------|------|------|
| 查看技能 | `hermes skill list` | 列出所有可用技能 |
| 创建技能 | `hermes skill create --name "技能名" --content "..."` | 创建新技能 |
| 更新技能 | `hermes skill patch --name "技能名" --old "旧内容" --new "新内容"` | 修补技能 |
| 删除技能 | `hermes skill delete --name "技能名"` | 删除技能 |

**YAML构建铁律**（已固化）：
1. **避免角括号**：SKILL.md frontmatter中 `<KEY>` → `$KEY`，`<BASE_URL>` → `$BASE_URL`
2. **优先使用 `|` literal block scalar**：`description: >` folded scalar 容易解析异常，改用 `|`
3. **验证后再使用**：`package_skill.py` 验证通过后才能部署

**踩过的坑**：
- ⚠️ Job-Hunter Skill打包失败，YAML角括号解析错误。→ `<KEY>` → `$KEY`。
- ⚠️ YAML folded scalar `>` 解析异常。→ 改用 `|` literal block scalar。

---

### 2.4 故障排查

**常见故障及修复**：

| 故障 | 原因 | 修复方案 |
|------|------|---------|
| pip未找到 | macOS上pip绑定Python 2 | 改用 `pip3` |
| brew install超时 | 网络波动/下载源问题 | `timeout 300 brew install ...` |
| GitHub raw域名被屏蔽 | 网络防火墙 | 改用GitHub API + base64解码 |
| MCP不可用 | 连接问题 | 降级到read_file + patch直接编辑 |
| Embedder模型故障 | 模型配置错误 | 检查config.yaml embedder配置 |

**排查流程**：
1. 复现故障（记录错误信息）
2. 搜索踩坑录（`02-踩坑记录-AI协作.md`）
3. 如踩坑录无记录 → 记录新踩坑条目
4. 修复后验证
5. 更新踩坑录（如为新故障）

---

## 三、质量控制检查点

| QC编号 | 检查点 | 阈值 |
|:------:|:------|:----:|
| QC-1 | Cron任务完整性 | 所有必要任务enabled |
| QC-2 | 技能库完整性 | 无缺失/损坏技能 |
| QC-3 | 配置文件语法 | YAML无语法错误 |
| QC-4 | 日志无ERROR | 最近24小时无ERROR级别日志 |
| QC-5 | 踩坑录更新 | 新故障24小时内记录 |

---

## 四、可复用Prompt速查表

| 步 | 场景 | Prompt |
|:--:|:-----|:-------|
| 1 | 健康检查 | `hermes --version; hermes cron list; hermes skill list; cat ~/.hermes/config.yaml; tail -100 ~/.hermes/logs/*.log` |
| 2 | Cron管理 | `hermes cron list/pause/resume/update/remove <job_id>` |
| 3 | 技能管理 | `hermes skill list/create/patch/delete --name "技能名"` |
| 4 | 故障排查 | `复现故障→搜索踩坑录→修复→验证→更新踩坑录（如新故障）` |

---

*本SOP基于AI协作踩坑录（YAML格式/网络工具/模型配置/Cron等7类错误）和已验证流程模式编制。核心铁律：YAML避免角括号、优先使用`|` literal block scalar、macOS用pip3。*
