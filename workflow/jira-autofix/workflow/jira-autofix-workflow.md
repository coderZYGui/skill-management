# Jira Autofix Workflow — 工作流总览

> **本文件**：工作流总览 + 索引入口
>
> - **AGENT.md**：AI 行为规则（规则层）—— AI 执行每一步的详细行为规范
> - **local-analysis-mode.md**：本地快速分析模式（模式层）—— Jira 不可用时的离线工作方式
> - **workflow-appendix.md**：附录——FAQ、术语表、变更记录
> - **本文件**：索引层——步骤索引、环境配置、工作区约定

---

## 索引层

### 步骤索引

| 步骤 | 文件 | 名称 | 核心输入 | 核心输出 |
| :--- | :--- | :--- | :--- | :--- |
| Step 1 | `steps/step-1-fetch-jira.md` | 获取 Jira Issue | `issueKey` | Issue 上下文对象 |
| Step 2 | `steps/step-2-fetch-config.md` | 获取项目配置 | `projectKey` | 项目配置对象 |
| Step 3 | `steps/step-3-classify.md` | 问题分类 | Issue 上下文 | 问题分类结果 |
| Step 4 | `steps/step-4-download-code.md` | 下载并准备代码 | 项目配置 | 本地代码路径 + 修复分支 |
| Step 5 | `steps/step-5-fix-issue.md` | 定位并修复 | Issue + 代码 + 分类结果 | 修复文件列表 + 修复说明 |
| Step 5a | `steps/step-5-fix-issue/android.md` | Android 平台修复 | - | - |
| Step 5b | `steps/step-5-fix-issue/embedded.md` | Embedded 平台修复 | - | - |
| Step 6 | `steps/step-6-commit-code.md` | 提交代码 | 修复文件列表 + 提交规范 | commit hash + remote branch |
| Step 7 | `steps/step-7-update-jira.md` | 更新 Jira | 修复说明 + commit 信息 | Jira 评论链接 + Issue 已更新 |

### 文件索引

```
workflow/
├── jira-autofix-workflow.md      # 本文件 — 工作流总览 + 索引
├── AGENT.md                      # 规则层 — AI 行为完整规则
├── local-analysis-mode.md        # 模式层 — 本地快速分析模式
├── workflow-appendix.md          # 附录 — FAQ、术语表、变更记录
└── steps/
    ├── step-1-fetch-jira.md      # Step 1 详细规范
    ├── step-2-fetch-config.md    # Step 2 详细规范
    ├── step-3-classify.md        # Step 3 详细规范
    ├── step-4-download-code.md   # Step 4 详细规范
    ├── step-5-fix-issue.md       # Step 5 通用修复规范
    │   ├── android.md            # Android 平台修复补充
    │   └── embedded.md           # Embedded 平台修复补充
    ├── step-6-commit-code.md      # Step 6 详细规范
    └── step-7-update-jira.md     # Step 7 详细规范

scripts/
├── jira_comment_generate.py      # Jira 评论内容生成工具
├── feishu_fetch_util.py          # 飞书消息获取工具
├── feishu_upload_util.py         # 飞书通知上传工具
├── git_clone_util.py             # Git 仓库克隆工具
└── git_commit_util.py            # Git 提交辅助工具

ai-program-tool/
├── .claude/commands/jira-autofix.md      # Claude Code 命令
├── .cursor/commands/jira-autofix.md      # Cursor 命令
├── .cursor/rules/jira-autofix-agent.mdc   # Cursor Rules
├── .codex/prompts/jira-autofix.md         # Codex Prompt
└── .micode/commands/jira-autofix.toml    # Microcode 配置

readme/
├── README.md                     # 项目说明
└── CONTRIBUTING.md               # 贡献指南
```

### 快速启动

```bash
# 方式 1：通过 AI 编程工具命令触发
/jira-autofix <ISSUE_KEY>

# 方式 2：本地模式（离线）
/jira-autofix <ISSUE_KEY> --local

# 方式 3：断点续传（恢复 Jira 连接后）
/jira-autofix --resume <ISSUE_KEY>
```

---

## 环境配置

### 环境变量

| 变量名 | 必填 | 说明 | 示例 |
| :--- | :--- | :--- | :--- |
| `JIRA_BASE_URL` | 是 | Jira 实例地址 | `https://your-org.atlassian.net` |
| `JIRA_EMAIL` | 是 | Jira 账号邮箱 | `dev@your-org.com` |
| `JIRA_API_TOKEN` | 是 | Jira API Token | `abcdef123456` |
| `JIRA_AUTOFIX_LOCAL_MODE` | 否 | 强制本地模式 | `true` / `false` |
| `JIRA_DEFAULT_PROJECT` | 否 | 默认项目 Key | `ANDROID` |
| `GIT_DEFAULT_REMOTE` | 否 | Git 远程仓库名 | `origin` |
| `GIT_DEFAULT_BRANCH` | 否 | 默认分支名 | `main` |
| `FEISHU_WEBHOOK_URL` | 否 | 飞书 Webhook 地址 | `https://open.feishu.cn/open-apis/bot/v2/hook/xxx` |
| `REPO_CACHE_DIR` | 否 | 代码仓库本地缓存目录 | `~/.jira-autofix/repos` |
| `CONFIG_CACHE_DIR` | 否 | 配置文件缓存目录 | `~/.jira-autofix/configs` |
| `REPORT_OUTPUT_DIR` | 否 | 修复报告输出目录 | `~/.jira-autofix/reports` |

### Jira API Token 获取

1. 登录 [Atlassian Account](https://id.atlassian.com/manage-profile/security/api-tokens)
2. 点击 **Create API token**
3. 输入标签（如 `jira-autofix`）并创建
4. 复制 Token 并配置到环境变量

### Python 环境依赖

```bash
pip install jira requests PyYAML
pip install feishu-sdk  # 可选：飞书通知
```

### 平台环境要求

| 平台 | 必要工具 | 版本要求 |
| :--- | :--- | :--- |
| macOS | git, python3 | git >= 2.x, python3 >= 3.8 |
| Linux | git, python3 | git >= 2.x, python3 >= 3.8 |
| Windows | git (WSL2), python3 | git >= 2.x, python3 >= 3.8 |

---

## 工作区约定

### 目录结构约定

```
~/.jira-autofix/
├── configs/              # 项目配置文件
│   ├── ANDROID.yaml
│   ├── EMBEDDED.yaml
│   └── default.yaml
├── repos/                # 代码仓库缓存
├── reports/              # 修复规划报告（本地模式）
├── logs/                 # 执行日志
│   └── jira-autofix-{date}.log
└── cache/                # 临时缓存
```

### 分支命名约定

```
fix/{projectKey}-{issueKey}-{short-description}

# 示例
fix/ANDROID-123-null-pointer-crash
fix/EMBEDDED-456-sensor-timeout
```

### Commit Message 约定

```
fix({projectKey}-{issueKey}): {简短描述}

# 示例
fix(ANDROID-123): 修复列表滚动时空指针崩溃

根因：RecyclerView 适配器在数据更新时未处理空视图引用。
修复：在 onBindViewHolder 中添加空值检查。

Ref: ANDROID-123
```

### Jira 评论格式约定

```markdown
## 修复说明

**根因**：
{detailed_root_cause}

**解决方案**：
{how_it_was_fixed}

**修复分支**：
`{branch_name}` — {commit_hash}

**自测结果**：
- [ ] 单元测试通过
- [ ] 场景测试通过
- [ ] 回归测试通过
```

### Issue 分类标签

| 分类 | 标签前缀 | 说明 |
| :--- | :--- | :--- |
| Crash | `type/crash` | 应用崩溃、ANR |
| UI Bug | `type/ui` | 界面显示异常 |
| Logic Error | `type/logic` | 业务逻辑错误 |
| Performance | `type/perf` | 性能问题 |
| Security | `type/security` | 安全漏洞 |
| Unknown | `type/unknown` | 无法明确分类 |

### 错误代码约定

| 代码 | 含义 | 处理建议 |
| :--- | :--- | :--- |
| `E001` | Jira API 认证失败 | 检查 JIRA_EMAIL 和 JIRA_API_TOKEN |
| `E002` | Jira Issue 不存在 | 确认 issueKey 是否正确 |
| `E003` | Git 克隆失败 | 检查网络和 SSH 密钥 |
| `E004` | 依赖安装失败 | 手动安装后重试 |
| `E005` | 编译失败 | 检查代码环境和构建工具 |
| `E006` | 修复验证失败 | 查看详细日志，调整修复方案 |
| `E007` | Git 提交失败 | 检查 git 状态和分支保护规则 |
| `E008` | Jira 更新失败 | 检查网络，保存 commit 后手动更新 |
| `E009` | 飞书通知失败 | 检查 FEISHU_WEBHOOK_URL |
| `E010` | 配置文件缺失 | 使用默认配置或创建配置文件 |

### ���志约定

```
[{timestamp}] [{level}] [{step}] {message}

[2026-04-02 10:30:15] [INFO]  [Step-1] Fetching Jira issue ANDROID-123
[2026-04-02 10:30:20] [INFO]  [Step-5] Root cause identified: null reference
[2026-04-02 10:30:45] [ERROR] [Step-7] Jira update failed: network timeout
```

### 缓存策略

| 缓存项 | TTL | 说明 |
| :--- | :--- | :--- |
| Jira Issue 响应 | 5 分钟 | 避免重复请求 |
| 项目配置 | 1 小时 | 配置变更不频繁 |
| Git 仓库（full clone） | 无过期 | 按需手动清理 |
| Git 仓库（shallow clone） | 7 天 | 超过后需重新 fetch |
| 修复规划报告 | 永久 | 用户需手动删除 |

---

## 执行流程图

```
用户触发 (/jira-autofix)
        │
        ▼
┌─────────────────────┐     否      ┌─────────────────────────┐
│ Jira 可连接？         │ ──────────► │ 本地分析模式              │
└─────────────────────┘             │ (local-analysis-mode.md) │
        │ 是                        └─────────────────────────┘
        ▼
┌─────────────────────┐
│ Step 1: 获取 Jira Issue │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Step 2: 获取项目配置    │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Step 3: 问题分类        │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Step 4: 下载代码        │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Step 5: 定位并修复       │
│ (Android / Embedded) │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Step 6: 提交代码        │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Step 7: 更新 Jira       │
│ (评论 + 状态)           │
└─────────────────────┘
        │
        ▼
    工作流完成
```
