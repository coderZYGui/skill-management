# -*- coding: utf-8 -*-
"""
git_clone_util.py — Git 仓库克隆工具

提供仓库克隆、拉取、修复分支创建等 Git 操作。
"""

import os
import subprocess
from pathlib import Path
from typing import Optional


# 工作区根目录
WORKSPACE_ROOT = Path("workflows/jira-autofix")


def get_issue_dir(issue_key: str) -> Path:
    """获取 Issue 工作目录。"""
    return WORKSPACE_ROOT / issue_key


def get_code_dir(issue_key: str) -> Path:
    """获取 Issue 的代码仓库目录。"""
    code_dir = get_issue_dir(issue_key) / "code"
    code_dir.mkdir(parents=True, exist_ok=True)
    return code_dir


def get_steps_dir(issue_key: str, step: int) -> Path:
    """获取 Issue 的步骤产物目录。"""
    step_dir = get_issue_dir(issue_key) / "steps" / f"step{step}"
    step_dir.mkdir(parents=True, exist_ok=True)
    return step_dir


def run_git_command(cmd: list, cwd: Optional[str] = None, timeout: int = 300) -> subprocess.CompletedProcess:
    """执行 Git 命令的封装。"""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def get_repo_name_from_url(repo_url: str) -> str:
    """从 Git URL 中提取仓库名。"""
    basename = os.path.basename(repo_url.rstrip("/"))
    if basename.endswith(".git"):
        basename = basename[:-4]
    return basename


def is_repo_cloned(repo_url: str, cache_dir: Path) -> bool:
    """检查仓库是否已在缓存目录中。"""
    repo_name = get_repo_name_from_url(repo_url)
    return (cache_dir / repo_name / ".git").exists()


def clone_or_update_repo(
    repo_url: str,
    cache_dir: str,
    branch: str = "main",
    strategy: str = "shallow",
    force_update: bool = False
) -> str:
    """
    克隆或更新仓库。

    Args:
        repo_url: 仓库地址（SSH 或 HTTPS）
        cache_dir: 缓存目录
        branch: 指定分支
        strategy: shallow（默认）/ full
        force_update: 强制重新拉取

    Returns:
        仓库本地路径
    """
    cache_path = Path(cache_dir)
    repo_name = get_repo_name_from_url(repo_url)
    repo_path = cache_path / repo_name

    if is_repo_cloned(repo_url, cache_path):
        if force_update or strategy == "full":
            run_git_command(["git", "-C", str(repo_path), "fetch", "--all", "--prune"], cwd=str(repo_path))
            run_git_command(["git", "-C", str(repo_path), "checkout", branch], cwd=str(repo_path))
            run_git_command(["git", "-C", str(repo_path), "pull", "origin", branch], cwd=str(repo_path))
        else:
            run_git_command(["git", "-C", str(repo_path), "fetch", "origin", branch], cwd=str(repo_path))
    else:
        cmd = ["git", "clone"]
        if strategy == "shallow":
            cmd += ["--depth", "1", "--single-branch", "-b", branch, repo_url, str(repo_path)]
        else:
            cmd += ["-b", branch, repo_url, str(repo_path)]
        run_git_command(cmd, cwd=str(cache_path))

    return str(repo_path)


def create_fix_branch(
    repo_path: str,
    issue_key: str,
    short_description: str,
    base_branch: str = "main",
    prefix: str = "fix/"
) -> str:
    """创建修复专用分支。"""
    safe_desc = "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in short_description.lower())
    while "--" in safe_desc:
        safe_desc = safe_desc.replace("--", "-")
    safe_desc = safe_desc.strip("-")[:30]
    branch_name = f"{prefix}{issue_key}-{safe_desc}"

    result = subprocess.run(["git", "-C", repo_path, "rev-parse", "--verify", branch_name],
                          capture_output=True, text=True)
    if result.returncode == 0:
        run_git_command(["git", "-C", repo_path, "checkout", branch_name], cwd=repo_path)
    else:
        run_git_command(["git", "-C", repo_path, "fetch", "origin", base_branch], cwd=repo_path)
        run_git_command(["git", "-C", repo_path, "checkout", "-b", branch_name, f"origin/{base_branch}"], cwd=repo_path)
    return branch_name


def verify_repo_ready(repo_path: str, verify_commands: Optional[list] = None) -> dict:
    """验证仓库环境就绪。"""
    checks = []
    errors = []

    git_dir = Path(repo_path) / ".git"
    checks.append({"name": "git_dir", "status": "pass" if git_dir.exists() else "fail"})

    result = subprocess.run(["git", "-C", repo_path, "status", "--porcelain"],
                          capture_output=True, text=True)
    if result.stdout.strip() == "":
        checks.append({"name": "git_clean", "status": "pass"})
    else:
        lines = result.stdout.strip().split("\n")
        checks.append({"name": "git_clean", "status": "warn", "detail": f"{len(lines)} 个文件变更"})

    return {"success": len(errors) == 0, "repo_path": repo_path, "checks": checks, "errors": errors}


def get_current_branch(repo_path: str) -> str:
    """获取当前分支名。"""
    result = subprocess.run(["git", "-C", repo_path, "branch", "--show-current"],
                          capture_output=True, text=True)
    return result.stdout.strip()
