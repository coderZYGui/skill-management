# Step 5 — 定位并修复问题

> **目标**：根据 Issue 信息，在代码仓库中定位根因并实施修复。

---

## 输入

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| `issueContext` | object | ✅ | Step 1 输出的 Issue 上下文 |
| `projectConfig` | object | ✅ | Step 2 输出的项目配置 |
| `classificationResult` | object | ✅ | Step 3 输出的分类结果 |
| `codeReadyInfo` | object | ✅ | Step 4 输出的代码就绪信息 |

---

## 执行流程

### 5.0 平台自动判断

判断优先级：配置指定 > projectKey 匹配 > 关键词匹配 > repo URL 推断。

支持的平台：`android`、`ios`、`harmony`、`embedded`。

### 5.1 代码搜索

1. 从堆栈信息提取文件名，在 `code/` 目录中定位
2. 从 `keyClasses` 搜索匹配的源文件
3. 关键词全文搜索，定位相关代码

### 5.2 根因分析

根据 `analysisFocus` 调用对应策略：
- `crash_analysis`：堆栈定位 → 空安全 → 异常处理
- `ui_analysis`：线程检查 → 生命周期 → View 层级
- `logic_analysis`：数据流 → 控制流 → 边界条件
- `performance_analysis`：主线程阻塞 → 内存泄漏
- `security_analysis`：权限检查 → 数据加密
- `general_analysis`：通用分析策略

### 5.3 实施修复

根据平台实现规范（见 `step-5-fix-issue/{platform}.md`）进行修复。

### 5.4 平台分发

| 平台 | 实现规范文件 | 关键文件类型 |
|:---|:---|:---|
| Android | `step-5-fix-issue/android.md` | `.kt` `.java` `.gradle` |
| iOS | `step-5-fix-issue/ios.md` | `.swift` `.m` `.h` |
| HarmonyOS | `step-5-fix-issue/harmony.md` | `.ets` `.ts` `.js` |
| Embedded | `step-5-fix-issue/embedded.md` | `.c` `.cpp` `.h` |

---

## 输出

```json
{
  "platform": "android",
  "rootCause": "onBindViewHolder 中 getItem(position) 返回 null，直接访问 item.title 导致 NPE",
  "solution": "添加空值检查：val item = getItem(position) ?: return",
  "fixFiles": [
    {
      "file": "module_home/src/main/java/com/example/module_home/ui/ProductAdapter.kt",
      "line": 28,
      "change": "val item = getItem(position) ?: return"
    }
  ]
}
```

---

## 产物

| 文件 | 路径 |
|:---|:---|
| 平台判定 | `{issueKey}/steps/step5/platform-detected.json` |
| 代码搜索 | `{issueKey}/steps/step5/search-results.json` |
| 根因分析 | `{issueKey}/steps/step5/root-cause-analysis.json` |
| 修复记录 | `{issueKey}/steps/step5/fix-record.json` |

---

## 与 Step 6 衔接

将 `fix-record.json` 传递给 Step 6 进行提交。
