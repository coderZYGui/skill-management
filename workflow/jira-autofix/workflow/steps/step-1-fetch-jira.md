# Step 1 — 获取 Jira Issue

> **目标**：从 Jira 获取 Issue 详情，构建完整的 Issue 上下文对象，传递给后续步骤。
>
> **支持两种模式**：
> - **远端模式（默认）**：通过 Jira REST API 获取 Issue 数据
> - **本地模式**：从 `local/local-jira-config.md` 读取模拟 Issue 数据

---

## 输入

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| `issueKey` | string | ✅ | Jira Issue Key，如 `ANDROID-123` |

---

## 前置条件

**远端模式**：Jira API 配置已就绪（`JIRA_BASE_URL`、`JIRA_EMAIL`、`JIRA_API_TOKEN`）

**本地模式**：`local/local-jira-config.md` 存在且包含对应 Issue Key 的数据

---

## 执行流程

### 1.0 模式检测

```python
def detect_fetch_mode(issue_key: str) -> str:
    # 1. 环境变量强制本地模式
    if os.getenv("JIRA_AUTOFIX_LOCAL_MODE") == "true":
        return "local"
    # 2. 检查 local-jira-config.md 中是否有该 Issue
    if f"<!-- ISSUE_START: {issue_key} -->" in Path("local/local-jira-config.md").read_text():
        return "local"
    # 3. 尝试 Jira API 连通性
    try:
        requests.head(os.getenv("JIRA_BASE_URL"), timeout=5)
        return "remote"
    except Exception:
        return "local"
```

### 模式A — 远端获取（Jira REST API）

调用 `GET /rest/api/2/issue/{issueKey}`，提取字段：key、summary、description、issueType、status、priority、projectKey、labels、environment、assignee、reporter、resolution。

解析 description：提取复现步骤、期望/实际行为、堆栈信息（`at com.example.Class.method(File:123)`）、错误日志。

### 模式B — 本地获取（local-jira-config.md）

从 `local/local-jira-config.md` 中通过 `<!-- ISSUE_START: {issueKey} -->` / `<!-- ISSUE_END: {issueKey} -->` 标记解析 JSON。字段提取逻辑与远端模式一致。

---

## 输出

```json
{
  "key": "ANDROID-123",
  "summary": "首页列表滑动时偶现空指针崩溃",
  "description": "...",
  "issueType": "Bug",
  "status": "In Progress",
  "priority": "High",
  "projectKey": "ANDROID",
  "projectName": "Android App",
  "labels": ["type/crash", "crash/android"],
  "environment": "Android 12, SDK 31",
  "assignee": "张三",
  "reporter": "李四",
  "parsed": {
    "steps_to_reproduce": ["1. 打开 App", "2. 快速滑动", "3. 崩溃"],
    "stack_traces": ["at ListAdapter.onBindViewHolder(ListAdapter.java:87)"]
  },
  "comments_summary": "根因已确认：异步数据更新在 Layout 过程中触发 notifyDataSetChanged"
}
```

---

## 产物

| 文件 | 路径 |
|:---|:---|
| Issue 上下文 | `{issueKey}/steps/step1/issue-context.json` |
| 评论摘要 | `{issueKey}/steps/step1/comments-summary.md` |
| 数据来源 | `{issueKey}/steps/step1/data-source.txt` |

---

## 与 Step 2 衔接

将 `issue-context.json` 中的 `projectKey` 传递给 Step 2 获取项目配置。
