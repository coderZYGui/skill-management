# -*- coding: utf-8 -*-
"""
jira_comment_generate.py — Jira 评论内容生成工具

生成符合 Jira 评论规范的修复说明内容，并提供 Jira API 调用封装。
"""

import base64
from datetime import datetime
from typing import Optional, List, Dict


def generate_jira_comment(
    fix_record: dict,
    commit_info: dict,
    project_config: dict,
    template: str = "detailed"
) -> str:
    """生成 Jira Issue 评论内容。"""
    templates = {
        "detailed": _generate_detailed_comment,
        "standard": _generate_standard_comment,
        "minimal": _generate_minimal_comment
    }
    generator = templates.get(template, _generate_detailed_comment)
    return generator(fix_record, commit_info, project_config)


def _generate_detailed_comment(fix_record: dict, commit_info: dict, project_config: dict) -> str:
    """详细评论模板。"""
    category_display = {
        "crash": "崩溃 (Crash)",
        "ui": "界面问题 (UI Bug)",
        "logic": "逻辑错误 (Logic Error)",
        "performance": "性能问题 (Performance)",
        "security": "安全问题 (Security)",
        "network": "网络问题 (Network)",
        "unknown": "未知 (Unknown)"
    }.get(fix_record.get("category", ""), fix_record.get("category", ""))

    lines = [
        "## 修复说明",
        "",
        f"**问题分类**：{category_display}",
        "",
        "---",
        "",
        "### 根因分析",
        "",
        fix_record.get("rootCause", "") or fix_record.get("fixSummary", ""),
        "",
        "### 解决方案",
        "",
        fix_record.get("solution", ""),
        "",
        "---",
        "",
        "### 修复分支",
        "",
        f"* **分支名**：`{commit_info.get('branch', {}).get('name', '')}`",
        f"* **Commit**：`{commit_info.get('commitHash', '')}`",
        "",
        "### 自测结果",
        "",
        "- [ ] 单元测试通过",
        "- [ ] 场景测试通过",
        "- [ ] 回归测试通过",
        "",
        "---",
        "",
        "*🤖 此评论由 Jira AutoFix 自动生成*",
    ]
    return "\n".join(lines)


def _generate_standard_comment(fix_record: dict, commit_info: dict, project_config: dict) -> str:
    """标准评论模板。"""
    lines = [
        f"## 修复说明 — {fix_record.get('issueKey', '')}",
        "",
        f"**根因**：{fix_record.get('rootCause', '')}",
        f"**修复**：`{commit_info.get('branch', {}).get('name', '')}` — `{commit_info.get('commitHash', '')}`",
        "",
        "请验证修复结果。",
        "*🤖 AutoFix*",
    ]
    return "\n".join(lines)


def _generate_minimal_comment(fix_record: dict, commit_info: dict, project_config: dict) -> str:
    """最小化评论模板。"""
    parts = [
        f"✅ 已修复：`{commit_info.get('branch', {}).get('name', '')}` (`{commit_info.get('commitHash', '')}`)"
    ]
    parts.append("\n*🤖 AutoFix*")
    return "".join(parts)


# ===== Jira API 调用封装 =====

def build_jira_api_headers(email: str, api_token: str) -> dict:
    """构建 Jira API 请求头。"""
    auth = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    return {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def call_jira_api(method: str, base_url: str, endpoint: str,
                  headers: dict, data: Optional[dict] = None) -> dict:
    """通用 Jira API 调用。"""
    import requests
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    methods = {
        "GET": lambda: requests.get(url, headers=headers, timeout=30),
        "POST": lambda: requests.post(url, headers=headers, json=data, timeout=30),
        "PUT": lambda: requests.put(url, headers=headers, json=data, timeout=30),
        "DELETE": lambda: requests.delete(url, headers=headers, timeout=30),
    }
    response = methods[method]()
    response.raise_for_status()
    return response.json()


def add_jira_comment(base_url: str, headers: dict,
                      issue_key: str, comment_body: str) -> dict:
    """在 Jira Issue 上添加评论。"""
    endpoint = f"/rest/api/2/issue/{issue_key}/comment"
    return call_jira_api("POST", base_url, endpoint, headers, {"body": comment_body})


def update_jira_status(base_url: str, headers: dict,
                       issue_key: str, transition_id: str) -> dict:
    """更新 Jira Issue 状态。"""
    endpoint = f"/rest/api/2/issue/{issue_key}/transitions"
    return call_jira_api("POST", base_url, endpoint, headers, {"transition": {"id": transition_id}})


def get_jira_transitions(base_url: str, headers: dict, issue_key: str) -> List[dict]:
    """获取 Issue 可用的状态转换。"""
    endpoint = f"/rest/api/2/issue/{issue_key}/transitions"
    result = call_jira_api("GET", base_url, endpoint, headers)
    return result.get("transitions", [])


def update_issue_field(base_url: str, headers: dict,
                      issue_key: str, field_name: str, field_value) -> dict:
    """更新 Issue 的单个字段。"""
    endpoint = f"/rest/api/2/issue/{issue_key}"
    return call_jira_api("PUT", base_url, endpoint, headers, {"fields": {field_name: field_value}})
