# HarmonyOS 平台修复规范

> **适用平台**：HarmonyOS / OpenHarmony（ArkTS / ArkUI）
> **触发条件**：Step 5 平台判断结果为 `harmony`

---

## 源码目录扫描

- ArkTS：`entry/src/main/ets/`
- ArkUI 页面：`entry/src/main/ets/pages/`
- JS：`entry/src/main/js/`

## 堆栈解析

```
Error at module.Class.method(file:123)
TypeError: x is not of type y
Cannot read property of undefined
```

常见崩溃类型：空引用（`undefined`）、类型错误、生命周期异常。

## 根因定位

1. 解析错误日志 → 提取模块名、方法名、文件名、行号
2. 在 `entry/src/main/ets/` 中定位 `.ets` 文件
3. 检查 `@State`、`@Link`、`@Prop` 装饰器的使用

## 修复模板

### 空状态修复

```typescript
// ❌ 错误
@State message: string

// ✅ 修复
@State message: string = ""
// 或
@State message?: string
```

### @Link 双向绑定修复

```typescript
// ✅ 父组件传值
ChildComponent({ count: $count })

// ✅ 子组件声明
@Link count: number
```

### ForEach 键值修复

```typescript
// ✅ 必须提供唯一稳定的键值
ForEach(this.items, (item: Item) => {
    Text(item.name)
}, (item: Item) => item.id.toString())
```

## 验证

```bash
hvigor build
```
