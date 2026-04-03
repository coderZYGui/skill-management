# /jira-autofix — Jira Issue 自动修复命令

执行 Jira Issue 自动修复工作流。

---

## 命令格式

```
/jira-autofix <ISSUE_KEY>                    # 分析单条 Issue
/jira-autofix <ISSUE_KEY> /path/to/repo     # 本地快速分析
/jira-autofix auto                           # 自动拉取待处理 Issue
/jira-autofix resume                         # 断点恢复
```

---

## 模式 A：单条 Issue 全流程

```
/jira-autofix ANDROID-123
```

执行完整 7 步：

```
Step 1 → 获取 Jira Issue（优先 local/local-jira-config.md）
Step 2 → 获取项目配置（优先 local/local-git-config.xlsx）
Step 3 → 问题分类（crash/ui/logic/performance）
Step 4 → clone 到 {issueKey}/code/，创建 fix/ 分支
Step 5 → 定位修复（自动判断 android/ios/harmony/embedded）
Step 6 → 提交代码并 push 到远程
Step 7 → 更新 Jira 评论
```

---

## 模式 B：本地快速分析

```
/jira-autofix ANDROID-123 /path/to/repo
```

跳过 clone/commit/update，仅执行 Step 1~3 + Step 5，输出修复建议供手动应用。

---

## 模式 C：自动拉取

```
/jira-autofix auto
```

从 `local/local-jira-config.md` 查询待处理 Issue，执行全流程。

---

## 模式 D：断点恢复

```
/jira-autofix resume
```

检查 `{issueKey}/steps/step{N}/` 产物，从第一个缺失步骤继续。

---

## 工作区结构

```
workflows/jira-autofix/{issueKey}/
├── code/          # 代码仓库（真实 clone）
└── steps/
    ├── step1/ ~ step7/   # 各步骤产物
```

---

## 工作流文档

执行前阅读：
1. `workflows/jira-autofix/workflow/AGENT.md`
2. `workflows/jira-autofix/workflow/jira-autofix-workflow.md`
3. 对应 Step 文档

---

## 安全约束

- 禁止 `git push --force`
- 禁止 `rm -rf`、`git reset --hard`
- 禁止修改 CI/CD 配置
- 禁止硬编码敏感信息
