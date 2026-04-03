# 本地 Jira Issue 配置

> 在无法连接 Jira 时，模拟 Jira API 返回的 Issue 数据。
>
> **用途**：本地分析模式、测试、CI 验证
>
> **格式**：每条 Issue 为独立 JSON 块，放在 `<!-- ISSUE_START: {KEY} -->` 和 `<!-- ISSUE_END: {KEY} -->` 之间

---

## 使用方式

Step 1 检测到以下任一条件时，从本文件读取：
- 环境变量 `JIRA_AUTOFIX_LOCAL_MODE=true`
- 用户传入 `--local` 标志
- Jira API 不可达
- 本文件中包含目标 Issue Key

---

## 数据字段说明

| 字段路径 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| `key` | string | ✅ | Issue Key |
| `fields.summary` | string | ✅ | 标题 |
| `fields.description` | string | | 描述正文 |
| `fields.issuetype.name` | string | ✅ | Bug / Task / Story |
| `fields.status.name` | string | ✅ | To Do / In Progress / Done |
| `fields.priority.name` | string | | High / Medium / Low |
| `fields.project.key` | string | ✅ | 项目 Key |
| `fields.project.name` | string | | 项目名称 |
| `fields.labels` | array | | 标签列表 |
| `fields.environment` | string | | 环境信息 |
| `fields.created` | string | | 创建时间 ISO 8601 |
| `fields.updated` | string | | 更新时间 |
| `fields.assignee.name` | string | | 负责人 |
| `fields.reporter.name` | string | | 报告人 |
| `fields.attachment` | array | | 附件列表 |
| `fields.comment.comments` | array | | 评论列表 |

---

## 示例 Issue

<!-- ISSUE_START: ANDROID-110 -->

```json
{
  "key": "ANDROID-110",
  "id": "1001110",
  "fields": {
    "summary": "【Android】用户反馈：首页列表滑动时偶现空指针崩溃",
    "description": "*【问题描述】*\n用户反馈在首页列表快速滑动时，App 偶现崩溃。\n\n*【复现步骤】*\n1. 打开 App 进入首页\n2. 快速向上滑动列表\n3. 约 5~10 秒后崩溃\n\n*【期望行为】*\n列表正常滚动不崩溃。\n\n*【实际行为】*\n偶现 ANR 后崩溃，弹出 \"App 已停止\"。\n\n*【堆栈信息】*\n{noformat}\njava.lang.NullPointerException\n    at com.example.app.adapter.ListAdapter.onBindViewHolder(ListAdapter.java:87)\n    at androidx.recyclerview.widget.RecyclerView.dispatchLayoutStep2(RecyclerView.java:4154)\n{noformat}",
    "issuetype": {"name": "Bug"},
    "status": {"name": "In Progress"},
    "priority": {"name": "High"},
    "project": {"key": "ANDROID", "name": "Android App"},
    "labels": ["type/crash", "crash/android"],
    "environment": "Android 12, SDK 31",
    "created": "2026-03-15T09:30:00.000+0800",
    "updated": "2026-04-01T14:22:00.000+0800",
    "assignee": {"name": "张三", "displayName": "张三"},
    "reporter": {"name": "李四", "displayName": "李四"},
    "attachment": [],
    "comment": {
      "total": 3,
      "comments": [
        {
          "author": {"name": "张三", "displayName": "张三"},
          "created": "2026-03-18T09:15:00.000+0800",
          "body": "根因确认：ListAdapter 在 onBindViewHolder 中直接访问 dataList.get(position)，当用户快速滑动时，异步数据更新在 Layout 过程中触发 notifyDataSetChanged，导致 position 对应的数据已被清空或替换，getItem(position) 返回 null，item.title 直接调用导致 NullPointerException。"
        }
      ]
    }
  }
}
```

<!-- ISSUE_END: ANDROID-110 -->

---

## 添加新 Issue

```markdown
<!-- ISSUE_START: {ISSUE_KEY} -->

```json
{
  "key": "{ISSUE_KEY}",
  "fields": {
    "summary": "...",
    "description": "...",
    "issuetype": {"name": "Bug"},
    "status": {"name": "To Do"},
    "priority": {"name": "Medium"},
    "project": {"key": "ANDROID", "name": "Android App"},
    "labels": [],
    "environment": "...",
    "created": "...",
    "updated": "...",
    "assignee": null,
    "reporter": {"name": "...", "displayName": "..."},
    "attachment": [],
    "comment": {"total": 0, "comments": []}
  }
}
```

<!-- ISSUE_END: {ISSUE_KEY} -->
```

---

## Python 加载

```python
import re, json
from pathlib import Path

def load_local_issue(issue_key: str) -> dict:
    content = Path(__file__).parent.read_text()
    s = f"<!-- ISSUE_START: {issue_key} -->"
    e = f"<!-- ISSUE_END: {issue_key} -->"
    i = content.find(s) + len(s)
    j = content.find(e, i)
    return json.loads(content[i:j].strip())

def list_available() -> list:
    content = Path(__file__).parent.read_text()
    return re.findall(r"<!-- ISSUE_START: (\S+) -->", content)
```
