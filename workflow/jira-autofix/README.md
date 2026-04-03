# Jira Autofix — Jira Issue 自动修复工作流

通过 AI 编程工具自���分析 Jira Issue、定位代码问题并生成修复。

---

## 快速开始

### 1. 环境准备

```bash
# 安装 Python 依赖
pip install jira requests PyYAML

# 可选：飞书通知
pip install feishu-sdk
```

### 2. 配置环境变量

```bash
# 必填
export JIRA_BASE_URL="https://your-org.atlassian.net"
export JIRA_EMAIL="dev@your-org.com"
export JIRA_API_TOKEN="your-api-token"

# 可选
export JIRA_DEFAULT_PROJECT="ANDROID"
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```

> API Token 获取：登录 [Atlassian Account](https://id.atlassian.com/manage-profile/security/api-tokens) → Create API token

### 3. 配置项目信息

编辑 `local/local-git-config.xlsx`，在 `configs` 工作表中填入项目信息（示例数据已预填）：

| 必填字段 | 说明 | 示例 |
|:---|:---|:---|
| `projectKey` | 项目标识 | `ANDROID` |
| `repoUrl` | Git 仓库地址 | `https://github.com/your-org/android-app.git` |
| `jiraProjectKey` | Jira 项目 Key | `ANDROID` |
| `platform` | 平台类型 | `android` / `ios` / `harmony` / `embedded` |

### 4. 运行命令

在 AI 编程工具（Claude Code / Cursor / Codex）中执行：

```
/jira-autofix ANDROID-123
```

---

## 命令使用

### 模式 A：全流程修复

```
/jira-autofix <ISSUE_KEY>
```

自动执行完整 7 步流程：获取 Issue → 加载配置 → 问题分类 → 下载代码 → 定位修复 → 提交代码 → 更新 Jira

```
# 示例
/jira-autofix ANDROID-123
/jira-autofix EMBEDDED-456
```

### 模式 B：本地快速分析

```
/jira-autofix <ISSUE_KEY> /path/to/repo
```

跳过 clone / commit / push，仅分析并输出修复建议。适合：
- 无 Jira 连接时快速验证
- 只想看 AI 的修复建议
- 在本地已有代码上测试

```
# 示例
/jira-autofix ANDROID-123 /Users/dev/android-app
```

### 模式 C：自动拉取待处理 Issue

```
/jira-autofix auto
```

从 `local/local-jira-config.md` 查询待处理 Issue，自动执行全流程。

### 模式 D：断点恢复

```
/jira-autofix resume
```

从上次中断处继续执行。检查 `{issueKey}/steps/step{N}/` 产物，从第一个缺失步骤恢复。

---

## 其他参数

```
/jira-autofix ANDROID-123 --local          # 强制本地模式（不连接 Jira）
/jira-autofix ANDROID-123 --skip-step-4    # 跳过指定步骤
```

---

## 支持的 AI 编程工具

| 工具 | 命令文件位置 |
|:---|:---|
| Claude Code | `ai-program-tool/.claude/commands/jira-autofix.md` |
| Cursor | `ai-program-tool/.cursor/commands/jira-autofix.md` |
| Codex | `ai-program-tool/.codex/prompts/jira-autofix.md` |
| MiCode | `ai-program-tool/.micode/commands/jira-autofix.toml` |

---

## 本地模式（离线使用）

当无法连接 Jira 时，可在 `local/local-jira-config.md` 中手动添加 Issue 数据：

```markdown
<!-- ISSUE_START: ANDROID-123 -->

{json 数据}

<!-- ISSUE_END: ANDROID-123 -->
```

触发方式：
- 命令加 `--local` 参数
- 设置环境变量 `JIRA_AUTOFIX_LOCAL_MODE=true`
- 或直接在 `local-jira-config.md` 中包含目标 Issue

---

## 工作区结构

执行后生成的目录：

```
workflows/jira-autofix/{issueKey}/
├── code/              # 克隆的代码仓库
└── steps/
    ├── step1/         # 获取 Jira Issue 产物
    ├── step2/         # 项目配置产物
    ├── step3/         # 问题分类产物
    ├── step4/         # 代码下载产物
    ├── step5/         # 修复产物
    ├── step6/         # 提交产物
    └── step7/         # Jira 更新产物
```

---

## 环境变量一览

| 变量名 | 必填 | 说明 |
|:---|:---:|:---|
| `JIRA_BASE_URL` | 是 | Jira 实例地址 |
| `JIRA_EMAIL` | 是 | Jira 账号邮箱 |
| `JIRA_API_TOKEN` | 是 | Jira API Token |
| `JIRA_AUTOFIX_LOCAL_MODE` | 否 | 强制本地模式 (`true`/`false`) |
| `JIRA_DEFAULT_PROJECT` | 否 | 默认项目 Key |
| `GIT_DEFAULT_REMOTE` | 否 | Git 远程仓库名（默认 `origin`） |
| `GIT_DEFAULT_BRANCH` | 否 | 默认分支名（默认 `main`） |
| `FEISHU_WEBHOOK_URL` | 否 | 飞书通知 Webhook 地址 |
| `REPO_CACHE_DIR` | 否 | 代码仓库缓存目录 |
| `CONFIG_CACHE_DIR` | 否 | 配置文件缓存目录 |
| `REPORT_OUTPUT_DIR` | 否 | 修复报告输出目录 |

---

## 常见问题

**Q: API 返回 401？** → 检查 `JIRA_EMAIL` 和 `JIRA_API_TOKEN` 是否正确

**Q: Git 克隆超时？** → 检查网络，或在配置中设置 `cloneStrategy: shallow`

**Q: 修复后测试不通过？** → AI 最多重试 3 次，仍失败则需人工介入

**Q: 想回滚已提交的修复？**
```bash
git log fix/ANDROID-123-xxx          # 查看提交历史
git revert {commit_hash}             # 回滚
git push                             # 推送
```

**Q: Commit 格式不符合团队规范？** → 修改配置文件中的 `commitFormat` 字段

更多问题参见 `workflow/workflow-appendix.md` 中的 FAQ。

---

## 详细文档

| 文件 | 内容 |
|:---|:---|
| `workflow/jira-autofix-workflow.md` | 工作流总览 + 环境配置 + 约定 |
| `workflow/AGENT.md` | AI 行为详细规则 |
| `workflow/local-analysis-mode.md` | 本地快速分析模式说明 |
| `workflow/workflow-appendix.md` | FAQ + 错误排查 + 报告模板 |
| `local/local-git-config.md` | 项目配置字段说明 |
| `local/local-jira-config.md` | 本地 Issue 数据格式说明 |

---

## 安全约束

- 禁止 `git push --force`
- 禁止 `rm -rf`、`git reset --hard`
- 禁止修改 CI/CD 配置
- 禁止硬编码敏感信息
