# 本地配置文件说明

> 定义本地配置的元素清单和 Excel 格式规范。
>
> **配置存储位置**：`local/local-git-config.xlsx`
>
> **工作表**：
> - `configs` — 主配置表
> - `repo_rules` — 仓库规则（可选）
> - `fix_templates` — 修复模板（可选）
>
> **快速使用**：直接编辑 `local-git-config.xlsx`，示例数据已在各工作表中填好，修改对应字段即可。

---

## configs 工作表 — 配置元素清单

| 列名 | 类型 | 必填 | 说明 | 示例 |
|:---|:---|:---:|:---|:---|
| `projectKey` | string | ✅ | 项目唯一标识 | `ANDROID` |
| `projectName` | string | | 项目名称 | `Android App` |
| `repoUrl` | string | ✅ | Git 仓库地址 | `https://github.com/your-org/android-app.git` |
| `defaultBranch` | string | | 默认分支 | `main` |
| `fixBranchPrefix` | string | | 修复分支前缀 | `fix/` |
| `cloneStrategy` | string | | shallow / full | `shallow` |
| `jiraProjectKey` | string | ✅ | Jira 项目 Key | `ANDROID` |
| `statusTransitionInProgress` | string | | In Progress 目标状态 | `Done` |
| `commentTemplate` | string | | detailed / standard / minimal | `detailed` |
| `commitFormat` | string | | Commit 格式模板 | `fix({projectKey}): {description}` |
| `includeRootCause` | boolean | | Commit 是否包含根因 | `true` |
| `maxSubjectLength` | integer | | Subject 最大字符 | `72` |
| `pushStrategy` | string | | default / force-if-clean / manual | `default` |
| `maxFileSearchDepth` | integer | | 代码搜索最大深度 | `10` |
| `timeoutMinutes` | integer | | 分析超时（分钟） | `30` |
| `autoVerify` | boolean | | 是否自动验证 | `true` |
| `verifyCommands` | string | | 验证命令（逗号分隔） | `./gradlew test,./gradlew assemble` |
| `styleCheck` | boolean | | 是否格式检查 | `true` |
| `styleTool` | string | | 格式检查工具 | `ktlint` |
| `platform` | string | ✅ | android / ios / harmony / embedded | `android` |
| `gradleFile` | string | | Gradle 文件路径 | `app/build.gradle` |
| `testCommand` | string | | 测试命令 | `./gradlew testDebugUnitTest` |
| `sourceDirs` | string | | 源码目录（逗号分隔） | `app/src/main/kotlin,app/src/main/java` |

## repo_rules 工作表（可选）

| 列名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| `projectKey` | string | ✅ | 关联项目 |
| `ruleName` | string | ✅ | 规则名称 |
| `ruleType` | string | | lint / naming / security |
| `filePattern` | string | | glob 匹配模式 | `**/*.kt` |
| `severity` | string | | error / warn / info |

## fix_templates 工作表（可选）

| 列名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| `projectKey` | string | ✅ | 关联项目 |
| `issueType` | string | ✅ | Bug / Task |
| `category` | string | ✅ | crash / ui / logic |
| `templateName` | string | ✅ | 模板名称 |
| `rootCausePattern` | string | | 根因关键词（逗号分隔） |
| `analysisHint` | string | | 分析提示 |
| `fixHint` | string | | 修复提示 |

---

## 示例数据

示例数据已填写在 `local-git-config.xlsx` 的各工作表中，可直接打开编辑。

| projectKey | projectName | repoUrl | platform |
|:---|:---|:---|:---|
| ANDROID | Android App | https://github.com/dukangkang/TestApplication.git | android |
| EMBEDDED | Embedded Firmware | https://github.com/your-org/embedded-firmware.git | embedded |

---

## Python 加载

```python
import pandas as pd

def load_project_config(excel_path: str, project_key: str) -> dict:
    config_df = pd.read_excel(excel_path, sheet_name="configs")  # 读取 local-git-config.xlsx
    row = config_df[config_df["projectKey"] == project_key].iloc[0]
    return dict(row.dropna())
```
