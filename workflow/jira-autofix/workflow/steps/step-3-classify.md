# Step 3 — 问题分类

> **目标**：基于 Issue 上下文，判断问题类型和严重程度，选择对应的分析策略。

---

## 输入

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| `issueContext` | object | ✅ | Step 1 输出的 Issue 上下文 |
| `projectConfig` | object | | Step 2 输出的项目配置（用于模板匹配） |

---

## 执行流程

### 3.1 关键词评分

```python
CLASSIFICATION_RULES = {
    "crash":    {"keywords": ["崩溃", "crash", "npe", "空指针", "anr"], "weight": 1.5},
    "ui":       {"keywords": ["ui", "界面", "显示", "布局", "闪退"], "weight": 1.0},
    "logic":    {"keywords": ["逻辑", "logic", "错误", "不符", "计算"], "weight": 1.0},
    "performance": {"keywords": ["卡顿", "慢", "性能", "lag", "内存"], "weight": 1.0},
    "security":  {"keywords": ["安全", "漏洞", "注入", "越权"], "weight": 2.0},
    "network":   {"keywords": ["网络", "超时", "请求", "断开"], "weight": 1.0}
}
```

### 3.2 标签评分

解析 Jira 标签：`type/crash` → crash 类 +10 分，其他按匹配度加权。

### 3.3 综合决策

合并关键词评分 + 标签评分，取最高分类并计算置信度。堆栈存在时 crash 类额外加权。

### 3.4 堆栈信息解析

提取 `crash_class`、`crash_method`、`crash_file`、`crash_line`。

---

## 输出

```json
{
  "category": "crash",
  "confidence": 0.87,
  "analysisFocus": "crash_analysis",
  "scores": {"crash": 12.5, "ui": 1.2},
  "hasStacktrace": true,
  "keyClasses": ["com.example.app.adapter.ListAdapter"],
  "keyMethods": ["onBindViewHolder"],
  "stacktraceInfo": {
    "crashFile": "ListAdapter.java",
    "crashLine": 87,
    "crashClass": "ListAdapter",
    "crashMethod": "onBindViewHolder"
  },
  "fixTemplate": {"templateName": "空指针修复模板", "fixHint": "使用 ?. 安全调用链"},
  "reason": "crash 类得分最高（12.5），置信度 87%"
}
```

---

## 产物

| 文件 | 路径 |
|:---|:---|
| 分类结果 | `{issueKey}/steps/step3/classification-result.json` |
| 堆栈分析 | `{issueKey}/steps/step3/stacktrace-analysis.json` |

---

## 与 Step 4 衔接

根据 `category` 确定分支策略，将 `classificationResult` + `projectConfig` 传递给 Step 4。
