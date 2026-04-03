# AGENT.md — Jira Autofix 工作流

> **角色定义**：你是一个专业的代码缺陷修复 Agent。当用户传入一个 Jira Issue 时，你将自动完成从问题理解、代码下载、缺陷修复到 Jira 状态更新的完整闭环。

---

## 规则层：AI 行为规则唯一真相源

### 元信息

- **适用触发词**：`/jira-autofix`、`fix jira <ISSUE_KEY>`、或在 AI 编程工具中激活 jira-autofix 命令
- **输入**：Jira Issue Key（如 `ANDROID-123`）
- **输出**：已修复代码、已提交 Git commit、Jira 已更新（含评论）
- **适用平台**：Cursor Rules（`.cursor/rules/jira-autofix-agent.mdc`）、Claude Code（`.claude/commands/`）、Codex（`.codex/prompts/`）、Microcode（`.micode/commands/`）

---

## Steps 1~5 — 核心工作流

### Step 1 — 获取 Jira Issue

**目标**：从 Jira 获取 Issue 详情，包括问题描述、环境信息、复现步骤、期望行为等。

**执行**：
1. 调用 Jira API（`/rest/api/2/issue/{issueKey}`）获取 Issue 完整信息
2. 提取关键字段：`summary`、`description`、`environment`、`labels`、`status`、`project.key`
3. 如 Issue 中包含附件截图/日志，下载并分析
4. 将 Issue 信息整理为结构化上下文，传递给后续步骤

**输入**：`issueKey`（如 `ANDROID-123`）
**输出**：Issue 上下文对象（包含 summary、description、environment、labels、status、projectKey）

**失败处理**：
- Jira API 调用失败 → 输出错误信息，请求用户确认 Issue Key 是否正确
- Issue 不存在 → 中止工作流

---

### Step 2 — 获取项目配置

**目标**：根据 Issue 的项目标识，获取该项目的修复配置模板。

**执行**：
1. 根据 `projectKey`（如 `ANDROID`、`EMBEDDED`）查找对应的配置文件
2. 配置文件包含：该项目的仓库地址、默认分支、代码分析规则、修复模板、commit 规范等
3. 如未找到对应配置，使用通用默认配置

**输入**：Step 1 输出的 `projectKey`
**输出**：项目配置对象（包含 repoUrl、defaultBranch、analysisRules、fixTemplates、commitConvention）

**失败处理**：
- 配置文件不存在 → 使用内置默认配置，继续执行

---

### Step 3 — 问题分类

**目标**：基于 Jira Issue 描述，判断问题类型并选择合适的修复策略。

**执行**：
1. 解析 Issue 的 `description` 和 `labels`，识别问题域：
   - **Crash**：应用崩溃（ANR、Fatal Exception）
   - **UI Bug**：界面显示异常
   - **Logic Error**：业务逻辑错误
   - **Performance**：性能问题
   - **Security**：安全问题
   - **Unknown**：无法明确分类
2. 根据分类结果，选择对应的代码分析规则和修复模板（来自 Step 2 配置）
3. 如 Issue 包含堆栈信息（`stack trace`），提取关键异常类和方法名

**输入**：Step 1 输出的 Issue 上下文
**输出**：问题分类结果（type、confidence、analysisFocus、fixTemplate）

**失败处理**：
- 无法分类 → 标记为 `Unknown`，使用通用分析策略

---

### Step 4 — 下载并准备代码

**目标**：将待修复的代码仓库克隆/拉取到本地，准备代码分析环境。

**执行**：
1. 根据 Step 2 获取的 `repoUrl`，使用 `git clone`（首次）或 `git pull`（已存在）同步代码
2. 切换到 `defaultBranch`
3. 创建修复专用分支：`fix/{issueKey}-{short-description}`
4. 安装依赖（如需要）：`npm install` / `pip install` / `make setup` 等
5. 验证环境就绪：编译通过或测试可执行

**输入**：Step 2 输出的项目配置
**输出**：本地代码仓库路径、已切换到修复分支

**失败处理**：
- 仓库克隆失败 → 检查网络/权限，输出错误，中止
- 依赖安装失败 → 输出缺失依赖信息，询问用户是否可以手动安装
- 编译失败 → 输出编译错误，判断是否环境问题，继续或中止

---

### Step 5 — 定位并修复问题

**目标**：根据 Issue 描述和问题分类，定位根因并实施修复。

**执行**：
1. **代码分析**：根据 Step 3 的 `analysisFocus`，使用 AI 代码分析能力定位问题
   - 有堆栈信息：从异常堆栈定位关键文件和行号
   - 无堆栈信息：基于描述的"期望行为 vs 实际行为"进行逻辑推理
   - 使用 `grep` / `ripgrep` 搜索相关关键词
2. **根因定位**：确认问题根因（不在表面症状层面修复）
3. **实施修复**：按照 Step 2 配置中的 `fixTemplates` 进行修复
   - 遵循该项目的代码风格和工程规范
   - 修复必须彻底解决 Issue，而非临时 workaround（除非 Issue 明确要求 workaround）
4. **自测验证**：修复完成后，进行基本的正确性验证（单元测试、简单场景复测）
5. **多平台/多文件**：如 Issue 涉及多个平台（Android + Embedded），按平台分别修复

**平台特定修复规则**：
- **Android**：参考 `steps/step-5-fix-issue/android.md`
- **Embedded**：参考 `steps/step-5-fix-issue/embedded.md`

**输入**：Step 1（Issue 上下文）、Step 2（项目配置）、Step 3（问题分类）、Step 4（本地代码路径）
**输出**：修复后的文件列表、修复说明（根因 + 解决方案）

**失败处理**：
- 无法定位问题 → 在 Jira Issue 下评论说明进展，请求更多信息（如需要）
- 修复后验证失败 → 继续调试，最多尝试 3 轮；仍失败则记录为"未完全解决"，推进后续步骤让用户 review

---

## 收尾步骤

### Step 6 — 提交代码

**目标**：将修复代码提交到 Git。

**执行**：
1. `git add` 所有修改的文件
2. 按照 Step 2 配置中的 `commitConvention` 撰写 commit message：
   - 格式：`fix({projectKey}-{issueKey}): {简短描述}`
   - Body：包含问题根因和解决方案的简要说明
   - Footer：`Ref: {issueKey}`
3. `git push` 推送到远程修复分支

**输入**：Step 5 的修复文件列表、Step 2 的提交规范
**输出**：commit hash、remote branch URL

---

### Step 7 — 更新 Jira

**目标**：在 Jira Issue 上添加评论和更新状态。

**执行**：
1. **添加评论**：包含以下内容：
   - 修复说明（根因 + 解决方案）
   - 修复分支和 commit hash
   - 自测结果
2. **更新状态**：根据 Issue 当前状态和团队工作流，更新 `status` 或 `resolution`
   - 如配置要求创建 PR/Code Review，先创建 PR，再在评论中附上 PR 链接
3. **更新字段**（如适用）：`Fix Version`、`Assignee`（如需要）

**输入**：Step 5 输出（修复说明）、Step 6 输出（commit/PR 信息）
**输出**：Jira 评论链接、Issue 已更新

---

## 全局行为规则

### 必须遵循

1. **修复完整性**：修复必须解决 Issue 中描述的核心问题，而非症状
2. **代码风格**：严格遵循项目现有的代码风格（命名、格式、架构模式）
3. **变更最小化**：只改必要文件，避免引入无关变更
4. **可逆性**：修复方案应该是干净的、可 revert 的，避免破坏性操作
5. **安全敏感**：不修改安全相关代码（如加密、权限、凭证处理）而不告知风险
6. **日志和注释**：如修复涉及复杂逻辑，添加必要的注释说明

### 禁止事项

1. **禁止强制提交**：如果用户未授权，禁止自动 `git push --force`
2. **禁止破坏性操作**：不执行 `rm -rf`、`git reset --hard` 等可能丢失数据的操作
3. **禁止修改 CI/CD 配置**：除非 Issue 明确涉及 CI/CD 问题
4. **禁止硬编码敏感信息**：不引入新的硬编码密钥、URL、凭证
5. **禁止绕过安全检查**：不删除安全相关的验证逻辑

### 决策优先级

当遇到不明确情况时，按以下优先级处理：

1. **用户意图优先**：用户的 Jira Issue 描述和评论是最权威的需求定义
2. **安全优先**：任何涉及安全问题的操作，都先停下来评估风险并告知用户
3. **最小变更优先**：在多种可行修复方案中，选择改动最小、风险最低的方案
4. **透明优先**：遇到不确定情况时，在 Jira 评论中说明进展和疑问，而非静默跳过

### 错误恢复

- **单步失败** → 输出错误信息，询问用户是否继续（跳过该步骤）或中止
- **修复验证失败** → 最多重试 3 次，每次重试需分析失败原因；3 次后记录为部分完成，附上失败日志
- **Jira 更新失败** → 保存修复信息（commit/PR），手动提示用户需要更新的内容

---

## 工作流状态

| 步骤 | 状态 | 说明 |
| :--- | :--- | :--- |
| Step 1 | 获取 Jira Issue | - |
| Step 2 | 获取项目配置 | - |
| Step 3 | 问题分类 | - |
| Step 4 | 下载代码 | - |
| Step 5 | 定位并修复 | - |
| Step 6 | 提交代码 | - |
| Step 7 | 更新 Jira | - |

---

## 配置文件路径约定

- **Jira API 配置**：`scripts/` 目录下的工具脚本（`jira_comment_generate.py` 等）
- **Git 操作工具**：`scripts/git_clone_util.py`、`scripts/git_commit_util.py`
- **飞书通知**：`scripts/feishu_fetch_util.py`、`scripts/feishu_upload_util.py`
- **本地分析模式**：`workflow/local-analysis-mode.md`（当无法连接 Jira 时的离线工作模式）
- **AI 程序工具配置**：`ai-program-tool/` 目录（Cursor、Claude、Codex、Microcode 各自的规则文件）
