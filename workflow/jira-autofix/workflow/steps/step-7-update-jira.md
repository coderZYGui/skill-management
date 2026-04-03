# Step 7 — 更新 Jira

> **目标**：在 Jira Issue 上添加修复评论、更新状态。

---

## 输入

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| `issueKey` | string | ✅ | Issue Key |
| `fixRecord` | object | ✅ | Step 5 输出的修复记录 |
| `commitInfo` | object | ✅ | Step 6 输出的提交信息 |

---

## 执行流程

### 7.1 生成评论内容

调用 `jira_comment_generate.generate_jira_comment()`，支持三种模板：
- `detailed`：根因 + 解决方案 + 分支信息 + 修改文件 + 自测清单
- `standard`：根因 + 分支链接
- `minimal`：一句话 + 链接

### 7.2 发布评论

```python
POST /rest/api/2/issue/{issueKey}/comment
body: "{comment_content}"
```

### 7.3 更新状态

根据 `projectConfig.jira.defaultStatusTransition` 执行状态转换（如 `In Progress → Done`）。

### 7.4 飞书通知（可选）

如果配置了 `FEISHU_WEBHOOK_URL`，发送修复完成通知。

---

## 输出

```json
{
  "issueKey": "ANDROID-123",
  "comment": {
    "id": "123456",
    "url": "https://your-org.atlassian.net/browse/ANDROID-123?focusedCommentId=123456",
    "template": "detailed"
  },
  "statusUpdate": {
    "updated": true,
    "fromStatus": "In Progress",
    "toStatus": "Done"
  }
}
```

---

## 产物

| 文件 | 路径 |
|:---|:---|
| 评论草稿 | `{issueKey}/steps/step7/comment-draft.md` |
| 更新结果 | `{issueKey}/steps/step7/update-result.json` |

---

## 工作流完成

Step 7 完成后，工作流执行完毕。输出完整执行摘要：
- 各步骤执行状态和耗时
- Commit hash 和分支 URL
- Jira 评论链接
