# Step 4 — 下载并准备代码

> **目标**：将代码仓库克隆到 `{issueKey}/code/`，创建修复专用分支。

---

## 输入

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| `issueKey` | string | ✅ | Issue Key |
| `projectConfig` | object | ✅ | 项目配置 |
| `classificationResult` | object | | 分类结果（用于分支策略） |

---

## 执行流程

### 4.1 克隆仓库

代码目录：`workflows/jira-autofix/{issueKey}/code/`

**约束条件：**
- **必须为真实目录，禁止软链接** — 确保代码完整性和操作安全
- **目录唯一性** — 每个 Issue 独立的代码工作区，避免冲突

```python
code_dir = Path("workflows/jira-autofix") / issue_key / "code"
code_dir.mkdir(parents=True, exist_ok=True)

# 安全检查：确保不是软链接
if code_dir.is_symlink():
    raise ValueError("代码目录不能是软链接")

git clone --depth 1 --single-branch -b {defaultBranch} {repoUrl} {code_dir}
```

克隆策略：
- `shallow`（默认）：`--depth 1 --single-branch`，节省带宽
- `full`：完整克隆，保留历史

### 4.2 创建修复分支

分支命名：`{prefix}{issueKey}-{short-description}`

示例：`fix/ANDROID-123-null-pointer-crash`

```python
branch_name = f"{prefix}{issue_key}-{short_desc}"
git fetch origin {base_branch}
git checkout -b {branch_name} origin/{base_branch}
```

### 4.3 验证环境

- 检查 `.git` 目录存在
- 检查工作区干净
- 执行平台特定验证命令（如 `./gradlew --version`）

---

## 输出

```json
{
  "repoPath": "workflows/jira-autofix/ANDROID-123/code/android-app",
  "repoUrl": "https://github.com/your-org/android-app.git",
  "branch": {
    "current": "fix/ANDROID-123-null-pointer-crash",
    "base": "main",
    "created": true
  },
  "cloneStrategy": "shallow",
  "environment": {"gitDir": true, "gitClean": true}
}
```

---

## 产物

| 文件 | 路径 |
|:---|:---|
| 仓库信息 | `{issueKey}/steps/step4/repo-info.json` |
| 环境验证 | `{issueKey}/steps/step4/env-verification.json` |

---

## 与 Step 5 衔接

将 `repoPath` + `branchName` + `classificationResult` 传递给 Step 5。
