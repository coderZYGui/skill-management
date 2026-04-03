# Step 2 — 获取项目配置

> **目标**：根据 Issue 的 `projectKey`，获取该项目的修复配置。

---

## 输入

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| `projectKey` | string | ✅ | 项目 Key，来自 Step 1 |

---

## 执行流程

### 2.0 优先级判定

配置加载按以下优先级（从高到低）：

```
1. local/local-git-config.xlsx（本地 Excel 配置，最高优先级）
2. 远端配置仓库（如配置仓库可用）
3. 内置默认配置（兜底）
```

### 2.1 本地配置（local-git-config.xlsx）

**文件路径**：`local/local-git-config.xlsx`

**读取逻辑**：

```python
import pandas as pd

def load_from_excel(project_key: str) -> dict | None:
    """从 local-git-config.xlsx 读取项目配置"""
    excel_path = Path("local/local-git-config.xlsx")
    if not excel_path.exists():
        return None

    try:
        # 读取 configs 工作表
        df = pd.read_excel(excel_path, sheet_name="configs")
        # 筛选匹配 projectKey 的行
        row = df[df["projectKey"] == project_key]
        if row.empty:
            return None

        config_data = row.iloc[0].to_dict()

        # 构建标准格式的项目配置
        return {
            "projectKey": config_data.get("projectKey"),
            "projectName": config_data.get("projectName", config_data.get("projectKey")),
            "source": "local-git-config.xlsx",
            "repo": {
                "url": config_data.get("repoUrl"),
                "defaultBranch": config_data.get("defaultBranch", "main"),
                "fixBranchPrefix": config_data.get("fixBranchPrefix", "fix/"),
                "cloneStrategy": config_data.get("cloneStrategy", "shallow")
            },
            "git": {
                "commitConvention": {
                    "format": config_data.get("commitFormat", "fix({projectKey}-{issueKey}): {description}"),
                    "includeRootCause": config_data.get("includeRootCause", True),
                    "maxSubjectLength": config_data.get("maxSubjectLength", 72)
                },
                "pushStrategy": config_data.get("pushStrategy", "default")
            },
            "jira": {
                "commentTemplate": config_data.get("commentTemplate", "detailed"),
                "statusTransition": {
                    "In Progress": config_data.get("statusTransitionInProgress", "Done")
                }
            },
            "analysis": {
                "maxFileSearchDepth": config_data.get("maxFileSearchDepth", 10),
                "timeoutMinutes": config_data.get("timeoutMinutes", 30)
            },
            "verify": {
                "autoVerify": config_data.get("autoVerify", True),
                "verifyCommands": config_data.get("verifyCommands", "").split(",") if config_data.get("verifyCommands") else [],
                "styleCheck": config_data.get("styleCheck", True),
                "styleTool": config_data.get("styleTool", "")
            },
            "platformSpecific": {
                config_data.get("platform", "android"): {
                    "sourceDirs": config_data.get("sourceDirs", "").split(",") if config_data.get("sourceDirs") else [],
                    "gradleFile": config_data.get("gradleFile", ""),
                    "testCommand": config_data.get("testCommand", "")
                }
            }
        }
    except Exception as e:
        print(f"[WARN] 读取 local-git-config.xlsx 失败: {e}")
        return None
```

### 2.2 远端配置仓库

从配置仓库加载对应 YAML 文件（当 Excel 配置不存在时）。

### 2.3 默认配置

当以上配置均不可用时，使用内置默认配置。

---

## 输出

成功时返回完整配置对象（含 `source` 字段标识来源）：

```json
{
  "projectKey": "ANDROID",
  "projectName": "Android App",
  "source": "local-git-config.xlsx",
  "repo": {
    "url": "https://github.com/dukangkang/TestApplication.git",
    "defaultBranch": "main",
    "fixBranchPrefix": "fix/",
    "cloneStrategy": "shallow"
  },
  "git": {
    "commitConvention": {
      "format": "fix({projectKey}-{issueKey}): {description}",
      "includeRootCause": true,
      "maxSubjectLength": 72
    },
    "pushStrategy": "default"
  },
  "jira": {
    "commentTemplate": "detailed",
    "statusTransition": {"In Progress": "Done"}
  },
  "analysis": {
    "maxFileSearchDepth": 10,
    "timeoutMinutes": 30
  },
  "verify": {
    "autoVerify": true,
    "verifyCommands": ["./gradlew test", "./gradlew assemble"],
    "styleCheck": true,
    "styleTool": "ktlint"
  },
  "platformSpecific": {
    "android": {
      "sourceDirs": ["app/src/main/kotlin", "app/src/main/java"],
      "gradleFile": "app/build.gradle",
      "testCommand": "./gradlew testDebugUnitTest"
    }
  }
}
```

---

## 产物

| 文件 | 路径 |
|:---|:---|
| 项目配置 | `{issueKey}/steps/step2/project-config.json` |
| 配置来源 | `{issueKey}/steps/step2/config-source.txt` |

---

## 与 Step 3 衔接

将 `project-config.json` 传递给 Step 3，用于确定分析规则和修复模板。
