# Workflow Appendix — 附录

> 本附录包含：错误排查指南、改进日志模板、报告模板（附录E）。

---

## 附录A：错误排查指南

### 按步骤分类的排查路径

#### Step 1 — Jira Issue 获取失败

| 症状 | 排查步骤 | 解决方案 |
| :--- | :--- | :--- |
| API 返回 401 Unauthorized | 1. 检查 `JIRA_EMAIL` 是否正确<br>2. 检查 `JIRA_API_TOKEN` 是否过期/正确<br>3. 确认 Token 未被 Atlassian 撤销 | 重新生成 API Token 并更新环境变量 |
| API 返回 404 Not Found | 1. 确认 `issueKey` 格式正确（如 ANDROID-123）<br>2. 确认 Jira URL 正确 | 核对 Issue Key |
| API 返回 403 Forbidden | 1. 确认账号有该项目访问权限<br>2. 确认 JIRA_EMAIL 对应账号在项目中 | 联系 Jira 管理员授予权限 |
| 网络超时 | 1. 检查网络连接<br>2. 检查 `JIRA_BASE_URL` 是否可访问<br>3. 尝试 ping Jira 域名 | 切换到本地分析模式 `--local` |
| Issue 描述为空 | 1. 查看 Jira Issue 是否为草稿状态<br>2. 确认 Issue 有 summary 和 description | 要求 Issue 创建者完善描述 |

#### Step 2 — 项目配置加载失败

| 症状 | 排查步骤 | 解决方案 |
| :--- | :--- | :--- |
| 配置文件不存在 | 1. 确认 `~/.jira-autofix/configs/{projectKey}.yaml` 存在<br>2. 确认项目根目录有 `.jira-autofix.yaml` | 创建配置文件或使用默认配置继续 |
| YAML 解析错误 | 1. 检查 YAML 语法（缩进、引号）<br>2. 确认无不可见字符 | 使用 YAML linter 修复语法 |
| 配置字段缺失 | 1. 对比 `workflow/jira-autofix-workflow.md` 中的必填字段<br>2. 确认 `repo.url` 和 `jira.project_key` 已填写 | 补全必填字段 |

#### Step 3 — 问题分类失败

| 症状 | 排查步骤 | 解决方案 |
| :--- | :--- | :--- |
| 分类置信度过低（< 0.5） | 1. 确认 Issue 描述足够详细<br>2. 确认堆栈信息格式正确 | 标记为 `Unknown`，使用通用分析策略 |
| 堆栈信息无法解析 | 1. 确认堆栈格式为标准格式（Java/Python/JS 等）<br>2. 确认堆栈未加密/混淆 | 手动提取关键类名和方法名 |
| 标签与描述矛盾 | 1. 以 Issue 描述为准<br>2. 忽略误导性标签 | 以描述为主进行分类 |

#### Step 4 — 代码下载失败

| 症状 | 排查步骤 | 解决方案 |
| :--- | :--- | :--- |
| Git 克隆超时 | 1. 检查网络到 Git 服务器<br>2. 尝试 shallow clone：`depth=1` | 修改配置 `clone_strategy: shallow` |
| SSH 认证失败 | 1. 确认 SSH 公钥已添加到 Git 服务器<br>2. 确认 `~/.ssh/config` 配置正确<br>3. 测试：`ssh -T git@github.com` | 配置 SSH 密钥 |
| HTTPS 认证失败 | 1. 确认凭证缓存（`git credential.helper`）<br>2. 尝试 Personal Access Token 方式 | 配置 Git 凭证 |
| 仓库已存在但非空 | 1. 确认本地仓库与配置的 repo_url 一致<br>2. 使用 `git pull` 同步 | AI 自动处理：pull 而非 clone |
| 分支创建失败 | 1. 确认没有同名分支<br>2. 确认分支保护规则允许创建 | 删除旧分支或使用新名称 |
| 依赖安装失败 | 1. 检查 Python/Node 环境<br>2. 检查镜像源<br>3. 检查系统权限 | 手动安装：`pip install -r requirements.txt` |

#### Step 5 — 修复失败

| 症状 | 排查步骤 | 解决方案 |
| :--- | :--- | :--- |
| 找不到问题代码 | 1. 扩大搜索范围（增加 `max_file_search_depth`）<br>2. 使用更精确的关键词<br>3. 确认代码仓库是否最新 | 更新仓库 + 扩大搜索 |
| 修复引入新 Bug | 1. 查看 git diff<br>2. 撤销修复并重新分析 | 最多重试 3 次 |
| 编译失败 | 1. 检查语法错误<br>2. 确认修改符合项目代码规范<br>3. 查看完整编译器输出 | 对照编译器错误信息修复 |
| 单元测试不通过 | 1. 分析测试失败原因<br>2. 确认修复逻辑正确性<br>3. 确认测试用例覆盖场景 | 如修复正确但测试失败，标注为已知问题 |

#### Step 6 — Git 提交失败

| 症状 | 排查步骤 | 解决方案 |
| :--- | :--- | :--- |
| 没有可提交的文件 | 1. 运行 `git status` 查看状态<br>2. 确认 Step 5 修复已保存 | 检查文件是否被意外忽略 |
| Commit hook 拒绝 | 1. 查看 hook 输出<br>2. 修复 lint 错误 | 按照 hook 提示修复 |
| Push 被分支保护规则拒绝 | 1. 确认是否为受保护分支<br>2. 确认是否需要 PR | 创建 PR 而非直接 push |
| 无网络 | 1. 检查网络连接<br>2. 确认 Git 远程可达 | 本地 commit，恢复网络后 push |

#### Step 7 — Jira 更新失败

| 症状 | 排查步骤 | 解决方案 |
| :--- | :--- | :--- |
| 评论添加失败 | 1. 确认 Jira API 权限<br>2. 确认 Issue 状态允许评论 | 保存评论内容，连接恢复后手动添加 |
| 状态更新失败 | 1. 确认状态转换是否在工作流允许范围内<br>2. 确认账号有状态更新权限 | 跳过状态更新，仅添加评论 |
| 评论内容过长 | 1. 确认 Jira 评论字符限制（通常 32KB）<br>2. 精简评论内容 | 分段评论或使用摘要 + 链接 |

---

### 网络相关问题

| 问题 | 检测命令 | 解决方案 |
| :--- | :--- | :--- |
| Jira API 不通 | `curl -I {JIRA_BASE_URL}` | 检查 VPN/代理设置 |
| Git 服务器不可达 | `ssh -T git@github.com` 或 `ssh -T git@{host}` | 检查 SSH 配置和网络 |
| 飞书 Webhook 失败 | `curl -X POST {FEISHU_WEBHOOK_URL} -d '{"msg_type":"text"}'` | 确认 Webhook 有效性 |
| DNS 解析失败 | `nslookup {JIRA_BASE_URL}` | 检查 DNS 配置 |

---

### 环境问题

| 问题 | 检测方法 | 解决方案 |
| :--- | :--- | :--- |
| Python 版本过低 | `python3 --version` | 升级到 >= 3.8 |
| Git 版本过低 | `git --version` | 升级到 >= 2.x |
| 磁盘空间不足 | `df -h` | 清理缓存和旧仓库 |
| 权限不足 | `ls -la ~/.jira-autofix/` | 修复目录权限 |

---

## 附录B：改进日志模板

### 改进日志（Changelog Entry）

每次对工作流规则、配置、脚本的修改，都应在 `workflow-appendix.md` 末尾添加一条改进日志。

```markdown
### YYYY-MM-DD — {版本号}

**修改类型**：[规则增强 / Bug修复 / 配置优化 / 新增功能 / 文档更新]

**修改范围**：
- `{文件路径}` — {具体修改内容}
- `{文件路径}` — {具体修改内容}

**修改原因**：
{简要说明为何进行此修改}

**影响范围**：
- {受影响的步骤或功能}
- {需要用户注意的变化}

**贡献者**：[姓名/账号]
```

### 改进日志示例

```markdown
### 2026-04-02 — v0.2.0

**修改类型**：规则增强

**修改范围**：
- `AGENT.md` — 补充 Step 5 的平台特定修复规则引用
- `local-analysis-mode.md` — 新增手动修复模式的交互式引导流程
- `workflow-appendix.md` — 新增错误排查指南（附录A）

**修改原因**：
提升多平台场景下的修复准确性，避免 Agent 在 Android/Embedded 混合问题中丢失平台特定处理逻辑。

**影响范围**：
- Step 5 修复流程现已支持 Android 和 Embedded 平台子规则
- 本地模式用户可通过交互式引导完成修复

**贡献者**：Dev Team
```

### 版本号管理

| 版本号 | 含义 |
| :--- | :--- |
| `v0.x.x` | 初始开发阶段，规则不稳定 |
| `v1.0.x` | 正式发布，语义化版本 |
| `v1.x.0` | 次版本更新，新增功能 |
| `vx.x.x` | 主版本更新，不兼容变更 |

---

## 附录C：FAQ

### Q1: 如何跳过某个步骤手动执行？

在命令中传入 `--skip-step-{N}`，例如：
```bash
/jira-autofix ANDROID-123 --skip-step-4
```
这将跳过 Step 4（代码下载），假设你已经手动拉取了代码。

### Q2: 修复分支命名不符合团队规范怎么办？

修改 `~/.jira-autofix/configs/{projectKey}.yaml` 中的 `fix_branch_prefix` 字段。
例如团队要求 `hotfix/ANDROID-123-xxx`，配置为 `fix_branch_prefix: hotfix/`。

### Q3: 如何强制使用本地模式？

```bash
/jira-autofix ANDROID-123 --local
```
或设置环境变量：`export JIRA_AUTOFIX_LOCAL_MODE=true`

### Q4: 修复后发现问题未完全解决怎么办？

```bash
# 在修复分支上继续修复
git checkout fix/ANDROID-123-null-pointer-crash
# ... 进行额外修复 ...
git commit -m "fix(ANDROID): additional fix for edge case"
git push

# 再次触发 Jira 更新
/jira-autofix --resume ANDROID-123
```

### Q5: 如何添加新的 Issue 分类？

在 `AGENT.md` Step 3 和 `local-analysis-mode.md` L-Step 3 中添加新的分类标签和对应的分析策略。

### Q6: Commit message 格式不符合团队规范？

修改配置文件中的 `git.commit_convention`：
```yaml
git:
  commit_convention:
    format: "fix({project_key}) #{issue_number}: {description}"
    body_template: |
      Problem: {root_cause}
      Solution: {fix_description}
```

### Q7: 如何禁用飞书通知？

不设置 `FEISHU_WEBHOOK_URL` 环境变量，或在配置中设置：
```yaml
feishu:
  enabled: false
```

### Q8: 可以同时处理多个 Issue 吗？

不支持并发处理多个 Issue。每次只处理一个 Issue。如需批量处理，可通过脚本循环调用 `/jira-autofix` 命令。

### Q9: 本地模式生成的报告保存在哪里？

默认保存在 `~/.jira-autofix/reports/{issueKey}-{timestamp}.md`。可通过 `REPORT_OUTPUT_DIR` 环境变量自定义。

### Q10: 如何回滚已提交的修复？

```bash
# 查看提交历史
git log fix/ANDROID-123-xxx

# 回滚到上一个提交
git revert {commit_hash}

# 或回滚到特定提交
git revert {commit_hash_1}..{commit_hash_N}

# 推送到远程
git push
```

---

## 附录D：术语表

| 术语 | 英文 | 定义 |
| :--- | :--- | :--- |
| Issue 上下文 | Issue Context | 从 Jira Issue 中提取的结构化信息（标题、描述、环境、标签等） |
| 根因 | Root Cause | 导致 Bug 发生的根本原因，而非表面症状 |
| 修复分支 | Fix Branch | 为修复特定 Issue 而创建的 Git 分支 |
| 平台特定修复 | Platform-Specific Fix | 针对特定平台（Android/Embedded）的专门修复逻辑 |
| 断点续传 | Resume from Breakpoint | 本地模式完成后，恢复 Jira 连接继续执行后续步骤 |
| Commit Convention | Commit Convention | Commit Message 的格式规范 |
| 问题分类 | Issue Classification | 根据 Issue 特征判断问题类型的过程 |
| Shallow Clone | Shallow Clone | 只克隆最近 N 次提交的 Git clone 方式 |
| 堆栈信息 | Stack Trace | 程序异常时的调用栈信息 |
| 修复规划报告 | Fix Planning Report | 本地模式生成的包含根因和修复方案的文档 |

---

## 附录E：报告模板

### 附录E-1：每日执行报告

```markdown
# Jira Autofix 每日执行报告

**日期**：`{YYYY-MM-DD}`
**执行者**：`{agent_id / user_name}`
**总处理数**：`{N}`

---

## 执行摘要

| 状态 | 数量 |
| :--- | :--- |
| 成功修复 | `{N}` |
| 部分完成 | `{N}` |
| 失败 | `{N}` |
| 跳过 | `{N}` |

---

## 详细记录

### 成功修复

| Issue Key | 项目 | 分类 | 修复分支 | Commit |
| :--- | :--- | :--- | :--- | :--- |
| `{ANDROID-123}` | ANDROID | Crash | `fix/ANDROID-123-xxx` | `{hash}` |
| `{EMBEDDED-456}` | EMBEDDED | Logic Error | `fix/EMBEDDED-456-xxx` | `{hash}` |

### 部分完成

| Issue Key | 状态 | 待处理 | 备注 |
| :--- | :--- | :--- | :--- |
| `{ANDROID-789}` | 代码已提交 | 等待 Code Review | PR: {link} |

### 失败记录

| Issue Key | 失败步骤 | 错误代码 | 错误信息 |
| :--- | :--- | :--- | :--- |
| `{ANDROID-000}` | Step-5 | E006 | 验证测试失败，需人工介入 |

---

## 性能统计

- **平均修复时间**：`{X} 分钟`
- **最快修复**：`{ANDROID-xxx}` — `{Y} 分钟`
- **最长修复**：`{EMBEDDED-xxx}` — `{Z} 分钟`

## 备注

{additional_notes}
```

---

### 附录E-2：修复总结报告（单 Issue）

```markdown
# 修复总结报告 — {issueKey}

> **生成时间**：`{YYYY-MM-DD HH:MM:SS}`
> **执行模式**：`{正常模式 / 本地模式}`
> **执行步骤**：`{Step-1 ~ Step-7}`

---

## Issue 信息

| 字段 | 内容 |
| :--- | :--- |
| 项目 | `{projectKey}` |
| 类型 | `{issueType}` |
| 分类 | `{category}` |
| 优先级 | `{priority}` |
| 状态 | `{status}` -> `{new_status}` |
| 负责人 | `{assignee}` |

**摘要**：
`{summary}`

---

## 执行过程

### Step 1 — Jira Issue 获取
- **结果**：成功
- **提取字段**：summary, description, environment, labels

### Step 2 — 项目配置加载
- **结果**：成功
- **配置文件**：`{config_path}`
- **仓库**：`{repo_url}`

### Step 3 — 问题分类
- **结果**：成功
- **分类**：`{category}`（置信度：{confidence}%）
- **分析重点**：`{analysis_focus}`

### Step 4 — 代码准备
- **结果**：成功
- **仓库路径**：`{repo_path}`
- **分支**：`{branch_name}`
- **依赖安装**：`{install_result}`

### Step 5 — 修复
- **结果**：成功
- **根因**：`{root_cause}`
- **修复文件**：
  1. `{file_1}` — 行 {N}~{M}
  2. `{file_2}` — 行 {N}~{M}
- **验证测试**：`{test_result}`

### Step 6 — 提交
- **结果**：成功
- **Commit**：`{hash}`
- **分支**：`{branch_name}`

### Step 7 — Jira 更新
- **结果**：成功
- **评论**：已添加
- **状态**：已更新为 `{new_status}`

---

## 代码变更

```diff
{完整 git diff}
```

---

## 自测结果

| 测试项 | 结果 | 说明 |
| :--- | :--- | :--- |
| 单元测试 | 通过 / 失败 | `{detail}` |
| 编译构建 | 通过 / 失败 | `{detail}` |
| 场景复测 | 通过 / 失败 | `{detail}` |
| 回归测试 | 通过 / 失败 | `{detail}` |

---

## 风险评估

- **引入新 Bug 风险**：低 / 中 / 高
- **影响范围**：局部 / 模块级 / 系统级
- **是否需要 Code Review**：是 / 否

---

## 附件

- Jira 评论链接：{link}
- PR 链接（如有）：{link}
- 飞书通知记录：{link}

---

**报告生成者**：Jira Autofix Agent
```

---

### 附录E-3：月度统计报告

```markdown
# Jira Autofix 月度统计报告

**月份**：`{YYYY-MM}`
**执行者**：`{agent_id / user_name}`

---

## 总体统计

| 指标 | 数值 |
| :--- | :--- |
| 总处理 Issue 数 | `{N}` |
| 成功修复数 | `{N}` |
| 成功率 | `{X}%` |
| 总节省时间估算 | `{Y} 小时` |

---

## 按项目分布

| 项目 | 数量 | 占比 |
| :--- | :--- | :--- |
| ANDROID | `{N}` | `{X}%` |
| EMBEDDED | `{N}` | `{X}%` |
| 其他 | `{N}` | `{X}%` |

---

## 按问题类型分布

| 类型 | 数量 | 占比 |
| :--- | :--- | :--- |
| Crash | `{N}` | `{X}%` |
| UI Bug | `{N}` | `{X}%` |
| Logic Error | `{N}` | `{X}%` |
| Performance | `{N}` | `{X}%` |
| Security | `{N}` | `{X}%` |
| Unknown | `{N}` | `{X}%` |

---

## 平均修复时长

| 步骤 | 平均耗时 |
| :--- | :--- |
| Step 1 (Jira) | `{X} 分钟` |
| Step 2 (配置) | `{X} 分钟` |
| Step 3 (分类) | `{X} 分钟` |
| Step 4 (代码) | `{X} 分钟` |
| Step 5 (修复) | `{X} 分钟` |
| Step 6 (提交) | `{X} 分钟` |
| Step 7 (Jira 更新) | `{X} 分钟` |
| **总计** | **{X} 分钟** |

---

## 失败分析

### 失败原因分布

| 错误代码 | 描述 | 数量 |
| :--- | :--- | :--- |
| E003 | Git 克隆失败 | `{N}` |
| E005 | 编译失败 | `{N}` |
| E006 | 验证失败 | `{N}` |
| E008 | Jira 更新失败 | `{N}` |
| 其他 | - | `{N}` |

### 典型失败案例

1. **{ANDROID-xxx}** — {简要描述}
2. **{EMBEDDED-yyy}** — {简要描述}

---

## 改进建议

- {improvement_suggestion_1}
- {improvement_suggestion_2}
- {improvement_suggestion_3}

---

**报告生成时间**：`{YYYY-MM-DD HH:MM:SS}`
```

---

## 附录F：变更记录

### 2026-04-02 — v0.1.0

**初始版本**

- `AGENT.md` — 规则层：AI 行为规则唯一真相源（Steps 1~7 + 收尾步骤）
- `jira-autofix-workflow.md` — 索引层：步骤索引、环境配置、工作区约定
- `local-analysis-mode.md` — 模式层：本地快速分析模式完整规则
- `workflow-appendix.md` — 附录层：本文档（错误排查、改进日志模板、报告模板）

**贡献者**：Dev Team
