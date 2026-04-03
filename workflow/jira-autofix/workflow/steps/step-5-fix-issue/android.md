# Android 平台修复规范

> **适用平台**：Android App（Kotlin / Java）
> **触发条件**：Step 5 平台判断结果为 `android`

---

## 源码目录扫描

- 优先：`app/src/main/kotlin/`
- 其次：`app/src/main/java/`
- 其他：`library/src/main/`、`feature/src/main/`

## 堆栈解析

```
at com.example.app.adapter.ListAdapter.onBindViewHolder(ListAdapter.java:87)
```

常见崩溃类型：空指针（NPE）、数组越界、主线程 UI 操作、ANR、OOM。

## 根因定位

1. 解析堆栈 → 提取 crashClass、crashMethod、crashFile、crashLine
2. 在源码目录中定位文件
3. 分析崩溃行上下文，确认根因

## 修复模板

### 空指针修复（常见）

```kotlin
// ❌ 错误
val item = getItem(position)
holder.binding.tvTitle.text = item.title

// ✅ 修复
val item = getItem(position) ?: return
holder.binding.tvTitle.text = item.title
```

### 主线程 UI 操作修复

```kotlin
// ❌ 错误
Thread {
    data = api.get()
    textView.text = data  // 子线程更新 UI
}.start()

// ✅ 修复
Thread {
    data = api.get()
    runOnUiThread { textView.text = data }
}
```

## 格式检查

```bash
./gradlew ktlintCheck
./gradlew ktlintFormat
```

## 验证

```bash
./gradlew assembleDebug
./gradlew :app:testDebugUnitTest
```
