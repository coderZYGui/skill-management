# Embedded 平台修复规范

> **适用平台**：嵌入式 / Firmware（C / C++ / 汇编）
> **触发条件**：Step 5 平台判断结果为 `embedded`

---

## 源码目录扫描

- C：`src/`、`app/`、`drivers/`
- 头文件：`include/`、`inc/`
- 链接脚本：`.ld`、`.lds`

## 堆栈解析（GDB 格式）

```
#0 in function_name() at file.c:123
HardFault_Handler → SCB->CFSR
```

CFSR 故障码：IACCVIOL（指令违规）、DACCVIOL（数据违规）、STKERR（栈错误）、DIVBYZERO（除零）。

常见崩溃类型：栈溢出、空指针、野指针、除零、中断阻塞。

## 根因定位

1. 解析崩溃日志 → 提取 fault 类型、寄存器值、崩溃地址
2. 使用 `addr2line` 映射到源文件和行号
3. 检查 SCB->CFSR 确定 fault 类型
4. 追溯调用栈

## 修复模板

### 栈溢出修复

```c
// ❌ 错误：栈上分配大数组
void func(void) {
    uint8_t buffer[4096];  // 可能栈溢出
}

// ✅ 修复：静态分配
static uint8_t buffer[4096];
```

### 空指针检查修复

```c
// ✅ 修复
void configure(sensor_config_t *config) {
    if (config == NULL) { return; }
    config->enable = true;
}
```

### 中断处理修复

```c
// ❌ 错误：中断中阻塞
void TIM2_IRQHandler(void) {
    delay_ms(100);  // ❌ 禁止
}

// ✅ 修复：设置标志位
volatile uint8_t data_ready = 0;
void TIM2_IRQHandler(void) { data_ready = 1; }
// 主循环处理
while (1) { if (data_ready) { data_ready = 0; process(); } }
```

## 格式检查

```bash
clang-format -i src/**/*.c
cppcheck --enable=all src/
```

## 验证

```bash
make clean && make
make test
```
