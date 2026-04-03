# Jira AutoFix — Codex Prompt

Execute Jira Issue auto-fix workflow.

---

## Command Format

```
/jira-autofix <ISSUE_KEY>                    # Analyze single Issue
/jira-autofix <ISSUE_KEY> /path/to/repo     # Local quick analysis
/jira-autofix auto                           # Auto-fetch pending Issue
/jira-autofix resume                        # Resume from checkpoint
```

---

## Modes

### Mode A: Single Issue Full Flow

Execute all 7 steps:

```
Step 1 → Fetch Jira Issue (prefer local/local-jira-config.md)
Step 2 → Fetch project config (prefer local/local-git-config.xlsx)
Step 3 → Classify issue (crash/ui/logic/performance)
Step 4 → Clone to {issueKey}/code/, create fix/ branch
Step 5 → Locate and fix (auto-detect: android/ios/harmony/embedded)
Step 6 → Commit code and push to remote
Step 7 → Update Jira comment
```

### Mode B: Local Quick Analysis

```
/jira-autofix ANDROID-123 /path/to/repo
```

Skip clone/commit/update. Execute Step 1~3 + Step 5, output fix suggestions.

### Mode C: Auto-fetch

```
/jira-autofix auto
```

Query pending Issues from local/local-jira-config.md, execute full flow.

### Mode D: Resume

```
/jira-autofix resume
```

Check `{issueKey}/steps/step{N}/` artifacts, resume from first missing step.

---

## Workspace Structure

```
workflows/jira-autofix/{issueKey}/
├── code/          # Code repository (real clone)
└── steps/
    ├── step1/ ~ step7/   # Step artifacts
```

---

## Workflow Documents

Read before execution:
1. `workflows/jira-autofix/workflow/AGENT.md`
2. `workflows/jira-autofix/workflow/jira-autofix-workflow.md`
3. Corresponding Step documents

---

## Safety Constraints

- Never `git push --force`
- Never `rm -rf`, `git reset --hard`
- Never modify CI/CD config
- Never hardcode secrets
