# Step 6 — 提交代码

> **目标**：将修复代码提交到 Git，**推送到远程修复分支**。

---

## 输入

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| `issueKey` | string | ✅ | Issue Key |
| `fixRecord` | object | ✅ | Step 5 输出的修复记录 |
| `projectConfig` | object | ✅ | 项目配置 |
| `codeReadyInfo` | object | ✅ | Step 4 输出的代码就绪信息 |

---

## 执行流程

### 6.1 获取变更文件

```python
changed_files = git diff --name-only
staged_files = git diff --cached --name-only
```

### 6.2 生成 Commit Message

规范格式：
```
fix({projectKey}-{issueKey}): {简短动词开头描述}

根因：{详细说明}

修复：{解决方案}

Ref: {issueKey}
```

### 6.3 暂存修改

```python
git add {changed_files}
```

### 6.4 创建 Commit

```python
git commit -m "{commit_message}"
```

### 6.5 推送到远程

**推送是强制步骤，不跳过。**

```python
git push -u origin {branch_name}
```

### 6.6 清理本地代码

**约束条件：**
- **推送完成后必须清理** — 避免产物代码长期占用磁盘空间
- **仅删除代码目录，保留 steps 产物** — 确保流程可追溯

推送成功后，删除本地克隆的代码目录以节省空间：

```python
import shutil
from pathlib import Path

def cleanup_local_code(repo_path: str, issue_key: str) -> dict:
    """
    清理本地代码目录。
    仅删除本次工作流克隆的代码，保留 steps 产物。
    """
    code_dir = Path(repo_path)

    # 安全检查：确保路径在 workflows/jira-autofix/{issue_key}/ 下
    expected_parent = Path(f"workflows/jira-autofix/{issue_key}")
    if not code_dir.is_relative_to(expected_parent):
        return {
            "cleaned": False,
            "reason": "路径安全检查失败，非工作流目录"
        }

    if code_dir.exists():
        shutil.rmtree(code_dir)
        return {
            "cleaned": True,
            "deletedPath": str(code_dir),
            "reason": "推送成功，清理本地代码"
        }

    return {
        "cleaned": False,
        "reason": "代码目录不存在"
    }
```

**清理范围**：
- ✅ 删除：`workflows/jira-autofix/{issue_key}/code/` 及其子目录
- ❌ 保留：`workflows/jira-autofix/{issue_key}/steps/` 所有产物文件

---

## 输出

```json
{
  "issueKey": "ANDROID-123",
  "commitHash": "a1b2c3d",
  "commitMessage": "fix(ANDROID-123): 修复 ProductAdapter.onBindViewHolder 空指针崩溃\n\n根因：...\n\nRef: ANDROID-123",
  "branch": {
    "name": "fix/ANDROID-123-null-pointer-crash",
    "remote": "origin",
    "remoteUrl": "https://github.com/your-org/android-app/tree/fix/ANDROID-123-null-pointer-crash"
  },
  "pushResult": {"success": true},
  "cleanup": {
    "cleaned": true,
    "deletedPath": "workflows/jira-autofix/ANDROID-123/code",
    "reason": "推送成功，清理本地代码"
  }
}
```

---

## 产物

| 文件 | 路径 |
|:---|:---|
| 变更扫描 | `{issueKey}/steps/step6/change-scan.json` |
| Commit 信息 | `{issueKey}/steps/step6/commit-info.json` |
| 推送结果 | `{issueKey}/steps/step6/push-result.json` |
| 清理记录 | `{issueKey}/steps/step6/cleanup-result.json` |

---

## 与 Step 7 衔接

将 `commitHash` + `branch` + `commitMessage` 传递给 Step 7 更新 Jira。
