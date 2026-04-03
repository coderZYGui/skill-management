# Local Analysis Mode — 本地快速分析模式

> **适用场景**：当无法连接 Jira（如内网环境、网络故障、Jira API 不可用）时的离线修复模式。AI 基于本地代码和用户提供的 Issue 信息完成分析和修复规划，修复执行和 Jira 更新需用户在恢复连接后手动完成或分阶段完成。

---

## 模式层：本地快速分析模式完整规则

### 激活条件

满足以下任一条件时，自动进入本地分析模式：

1. Jira API 调用超时（> 10s）或返回网络错误
2. 用户传入 `--local` 或 `--offline` 标志
3. 用户直接提供 Issue 信息（跳过 Step 1，直接进入分析）
4. 环境变量 `JIRA_AUTOFIX_LOCAL_MODE=true`

---

## 模式切换规则

### 进入本地模式

1. 检测到 Jira 连接失败后，立即输出：

   ```
   [LOCAL MODE] 无法连接 Jira，进入本地快速分析模式。
   请提供 Issue 信息（可直接粘贴 Jira Issue 的标题和描述）。
   ```

2. 等待用户提供 Issue 信息（标题、描述、环境信息等）
3. 进入**增强版本地分析流程**

### 退出本地模式

满足以下任一条件，退出本地模式恢复正常流程：

1. Jira 连接恢复（`/health` 检查通过）
2. 用户传入 `--resume` 并提供了有效的 `issueKey`
3. 用户确认手动执行后续步骤

---

## 增强版本地分析流程

### L-Step 1 — 接收并解析 Issue 信息

**用户输入格式**（支持以下任一）：

- 纯文本粘贴（Jira Issue 的标题 + 描述 + 评论）
- 导出 JSON：`{"key": "ANDROID-123", "summary": "...", "description": "..."}`
- Markdown 格式的 Issue 摘要

**执行**：
1. 解析输入，提取：`summary`、`description`、`environment`、`labels`、`status`
2. 识别 `projectKey`（从 summary 前缀或用户明确指定，如 `ANDROID-xxx` -> `ANDROID`）
3. 生成 Issue 上下文对象（与 Step 1 输出格式一致）

**输出**：Issue 上下文（summary、description、environment、labels、status、projectKey）

---

### L-Step 2 — 获取项目配置（本地缓存）

**执行**：
1. 查找本地缓存的配置文件（`~/.jira-autofix/configs/{projectKey}.yaml` 或 `.jira-autofix.yaml`）
2. 如存在，加载配置（仓库地址、分支、修复模板）
3. 如不存在，读取当前工作目录的 `.jira-autofix.yaml`（如存在）
4. 仍不存在 -> 使用内置默认配置

**本地配置文件格式**（参考）：

```yaml
project: ANDROID
repo_url: git@github.com:your-org/android-app.git
default_branch: main
fix_branch_prefix: fix/
commit_convention:
  format: "fix({projectKey}): {short_description}"
  include_root_cause: true
analysis_rules:
  max_file_search_depth: 10
  timeout_minutes: 30
```

**输出**：项目配置对象

---

### L-Step 3 — 问题分类（离线）

**执行**：与 AGENT.md Step 3 完全一致
- 基于 Issue 描述中的关键词和堆栈信息进行分类
- 输出问题类型和对应的分析策略

**输出**：问题分类结果

---

### L-Step 4 — 本地代码准备

**执行**：
1. 检查当前目录是否为指定的 Git 仓库
2. 如是：确认分支是否为修复分支；使用 `git pull` 同步最新代码
3. 如否：提示用户指定代码路径或 clone 仓库
4. 验证代码完整性：检查关键文件是否存在

**用户交互**：
```
[LOCAL MODE] 请确认代码仓库路径：
  1. 使用当前目录: /path/to/current
  2. 指定其他路径
  3. 克隆新仓库（需要 repo_url）
```

**输出**：本地代码路径、当前分支

---

### L-Step 5 — 根因分析（本地）

**执行**：
1. **深度代码分析**：AI 基于 Issue 描述在本地代码库中搜索相关代码
   - 使用 `grep` / `ripgrep` 搜索关键词（类名、方法名、错误信息）
   - 分析代码逻辑：数据流、控制流、边界条件
   - 如有堆栈信息：定位到具体文件和行号
2. **根因定位**：输出问题根因（不是表面现象）
3. **修复方案**：生成修复代码片段或具体修改建议
4. **自测建议**：提供验证修复的测试用例

**输出**：
- `root_cause`：根因说明
- `fix_location`：需修改的文件 + 行号范围
- `fix_diff`：修复代码差异（以 Markdown 格式输出）
- `test_plan`：验证测试计划

---

## 本地模式输出格式

完成 L-Step 5 后，生成**修复规划报告**，格式如下：

```markdown
# 修复规划报告 — {issueKey}

> **模式**：本地分析模式
> **生成时间**：{timestamp}
> **分析耗时**：{duration}

## Issue 摘要

| 字段 | 内容 |
| :--- | :--- |
| 项目 | {projectKey} |
| 类型 | {issueType} |
| 分类 | {category} |
| 状态 | 待修复 |

{summary}

## 环境

{environment}

## 根因分析

{root_cause}

## 修复方案

### 需修改的文件

1. `src/path/to/FileA.java` — 行 {N}~{M}
2. `src/path/to/FileB.kt` — 行 {N}~{M}

### 修复代码

```diff
- 错误代码行
+ 修复代码行
```

### 验证方法

1. 运行单元测试：`./gradlew test --tests "*.{TestClass}"`
2. 运行场景测试：{具体步骤}
3. 验证结果：{预期输出}

## 待执行操作

- [ ] 手动应用以上修复代码
- [ ] 运行验证测试
- [ ] 连接 Jira 后提交代码并更新 Issue

## 后续步骤（需 Jira 连接）

1. 创建分支：`git checkout -b fix/{issueKey}-{short-desc}`
2. 提交代码：`git commit -m "fix({projectKey}): {description}"`
3. 更新 Jira（连接恢复后执行）：
   - 添加评论：粘贴上方"修复方案"部分
   - 更新状态：In Progress -> Done
```

---

## 手动修复模式

如用户选择直接在本地 IDE 中修复，AI 提供以下辅助：

### 交互式修复引导

1. **逐文件修复**：按 `fix_location` 顺序逐个处理
2. **代码片段生成**：为每个文件生成精确的修复代码
3. **差异预览**：在应用前展示完整的 `git diff`
4. **语法检查**：修复后运行语言级 linter（`clang-format`、`prettier`、`rustfmt` 等）

### 修复后验证

1. **编译验证**：`make build` 或 `./gradlew assemble`
2. **单元测试**：`make test`
3. **回归测试**（如配置）：运行相关模块的测试用例
4. **如验证失败**：返回 L-Step 5，重新分析失败原因

---

## 模式间协作

### 本地模式 -> 正常模式（恢复连接）

当 Jira 连接恢复时，支持**断点续传**：

1. 本地模式生成的修复规划报告保存在：`~/.jira-autofix/reports/{issueKey}-{timestamp}.md`
2. 用户执行 `--resume {issueKey}` 时：
   - AI 读取本地报告
   - 跳过 L-Step 1~5（已缓存）
   - 直接进入 Step 6（提交代码）和 Step 7（更新 Jira）
   - 自动补全 Jira 评论（从报告中提取）

### 增量分析

- **已有报告**：对比本地代码当前状态与报告中的 `fix_diff`，判断是否已应用修复
- **未修复**：继续引导用户完成修复
- **已修复**：进入提交 + Jira 更新流程

---

## 行为约束

### 本地模式特有规则

1. **不自动修改代码**：默认只生成修复规划和代码片段，不执行 `git commit` / `git push`
   - 例外：用户明确传入 `--auto-commit`
2. **不操作 Jira**：禁止在离线状态下更新 Jira（避免状态不一致）
3. **报告即记录**：本地生成的修复规划报告作为 Jira 连接的备用记录
4. **数据隔离**：Issue 信息和修复规划默认保存在本地，不上传任何外部服务

### 限制说明

| 功能 | 正常模式 | 本地模式 |
| :--- | :--- | :--- |
| Jira API 调用 | 支持 | 不支持 |
| 自动 commit | 支持 | 需手动确认 |
| 自动 push | 支持 | 不支持 |
| Jira 评论 | 支持 | 不支持 |
| Jira 状态更新 | 支持 | 不支持 |
| 代码分析修复 | 支持 | 支持 |
| 修复规划生成 | 支持 | 支持 |

---

## 错误处理

| 场景 | 处理方式 |
| :--- | :--- |
| 用户未提供 Issue 信息 | 循环提示，直到收到有效输入 |
| 本地配置不存在 | 使用默认配置，继续执行 |
| 代码仓库路径无效 | 提示用户指定有效路径 |
| 修复代码生成失败 | 输出分析结果，说明无法生成修复代码的原因 |
| 恢复 Jira 连接失败 | 保持本地模式，提示用户检查网络/Jira 服务状态 |
| 修复验证失败 | 分析失败原因，提供新的修复方向 |
