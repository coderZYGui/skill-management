# iOS 平台修复规范

> **适用平台**：iOS App（Swift / Objective-C）
> **触发条件**：Step 5 平台判断结果为 `ios`

---

## 源码目录扫描

- 优先：`Sources/**/*.swift`
- 其次：`ProjectName/Classes/**/*.swift`

## 堆栈解析

```swift
EXC_BAD_ACCESS    // 空解引用
unexpectedly found nil while unwrapping an Optional value  // 强制解包崩溃
```

常见崩溃类型：强制解包（`!`）、野指针、主线程 UI、内存泄漏。

## 根因定位

1. 解析崩溃日志 → 提取崩溃类名、方法名
2. 在 `Sources/` 目录中搜索 `.swift` 文件
3. 检查可选值是否正确解包

## 修复模板

### 强制解包修复

```swift
// ❌ 错误
let name = user!.name

// ✅ 修复
let name = user?.name ?? "未知用户"
guard let user = user else { return }
```

### 主线程 UI 修复

```swift
// ✅ 修复
DispatchQueue.global().async {
    let data = api.fetch()
    DispatchQueue.main.async {
        self.label.text = data
    }
}
```

## 格式检查

```bash
swiftlint lint
swiftlint autocorrect
```

## 验证

```bash
xcodebuild test -project ProjectName.xcodeproj -scheme ProjectName
```
