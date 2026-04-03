# -*- coding: utf-8 -*-
"""
git_commit_util.py — Git 提交工具

提供修改文件扫描、commit message 生成、提交和推送等操作。
"""

import subprocess
from pathlib import Path
from typing import Optional, List, Dict


def run_git_command(cmd: list, cwd: str, timeout: int = 60) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def get_changed_files(repo_path: str, staged: bool = False) -> List[str]:
    """获取已修改的文件列表。"""
    if staged:
        cmd = ["git", "-C", repo_path, "diff", "--cached", "--name-only"]
    else:
        cmd = ["git", "-C", repo_path, "status", "--porcelain"]
    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    files = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if staged:
            files.append(line)
        else:
            parts = line.split(" ", 1)
            if len(parts) >= 2:
                files.append(parts[1])
    return files


def get_diff_stats(repo_path: str) -> Dict:
    """获取变更统计信息。"""
    result = subprocess.run(["git", "-C", repo_path, "diff", "--stat"],
                          cwd=repo_path, capture_output=True, text=True)
    return {"stat": result.stdout}


def parse_commit_convention(
    issue_key: str,
    description: str,
    project_key: str = "",
    root_cause: str = "",
    footer: str = ""
) -> Dict:
    """生成规范格式的 commit message。"""
    if project_key:
        subject = f"fix({project_key}-{issue_key}): {description}"
    else:
        subject = f"fix({issue_key}): {description}"

    if len(subject) > 72:
        subject = subject[:69] + "..."

    body_parts = []
    if root_cause:
        body_parts.append(f"根因：{root_cause}")
    if footer:
        body_parts.append(f"修复：{footer}")

    body = "\n".join(body_parts)
    footer_line = f"Ref: {issue_key}"

    if body:
        full = f"{subject}\n\n{body}\n\n{footer_line}"
    else:
        full = f"{subject}\n\n{footer_line}"

    return {"subject": subject, "body": body, "footer": footer_line, "full": full}


def stage_files(repo_path: str, file_paths: List[str]) -> None:
    """暂存指定文件。"""
    if not file_paths:
        return
    subprocess.run(["git", "-C", repo_path, "add", "--"] + file_paths,
                   cwd=repo_path, check=True, capture_output=True)


def stage_all(repo_path: str) -> None:
    """暂存所有变更。"""
    subprocess.run(["git", "-C", repo_path, "add", "-A"],
                   cwd=repo_path, check=True, capture_output=True)


def create_commit(repo_path: str, message: str, allow_empty: bool = False) -> str:
    """创建 Git commit。"""
    cmd = ["git", "-C", repo_path, "commit"]
    if allow_empty:
        cmd.append("--allow-empty")
    cmd.extend(["-m", message])
    subprocess.run(cmd, cwd=repo_path, check=True, capture_output=True)
    result = subprocess.run(["git", "-C", repo_path, "rev-parse", "--short", "HEAD"],
                           cwd=repo_path, capture_output=True, text=True)
    return result.stdout.strip()


def get_current_branch(repo_path: str) -> str:
    result = subprocess.run(["git", "-C", repo_path, "branch", "--show-current"],
                          cwd=repo_path, capture_output=True, text=True)
    return result.stdout.strip()


def push_to_remote(
    repo_path: str,
    remote: str = "origin",
    branch: Optional[str] = None,
    force: bool = False,
    upstream: bool = True
) -> Dict:
    """推送到远程仓库。推送是强制操作，不跳过。"""
    if branch is None:
        branch = get_current_branch(repo_path)

    cmd = ["git", "-C", repo_path, "push"]
    if force:
        cmd.append("--force")
    if upstream:
        cmd.extend(["-u", remote, branch])
    else:
        cmd.extend([remote, branch])

    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    success = result.returncode == 0
    output = result.stdout if success else result.stderr

    return {"success": success, "remote": remote, "branch": branch, "output": output}


def get_remote_branch_url(repo_path: str, remote: str = "origin",
                         branch: Optional[str] = None) -> str:
    """获取远程分支的完整 URL。"""
    import re
    if branch is None:
        branch = get_current_branch(repo_path)

    result = subprocess.run(["git", "-C", repo_path, "remote", "get-url", remote],
                          cwd=repo_path, capture_output=True, text=True)
    remote_url = result.stdout.strip()

    # SSH -> HTTPS 转换
    match = re.match(r"git@([^:]+):(.+?)(?:\.git)?$", remote_url)
    if match:
        host, path = match.groups()
        remote_url = f"https://{host}/{path}"

    remote_url = re.sub(r"\.git$", "", remote_url)
    return f"{remote_url}/tree/{branch}"
