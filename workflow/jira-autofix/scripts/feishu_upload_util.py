# -*- coding: utf-8 -*-
"""
feishu_upload_util.py — 飞书通知上传工具

通过飞书 Webhook 发送修复完成通知。
"""

import requests
from typing import Optional, Dict


def notify_feishu(
    webhook_url: str,
    issue_key: str,
    fix_summary: str,
    commit_hash: str,
    branch_name: str,
    remote_url: str = "",
    status: str = "success"
) -> Dict:
    """
    通过飞书 Webhook 发送修复完成通知。

    Args:
        webhook_url: 飞书 Webhook 地址
        issue_key: Issue Key
        fix_summary: 修复摘要
        commit_hash: Commit Hash
        branch_name: 修复分支名
        remote_url: 分支链接
        status: success / failure

    Returns:
        发送结果
    """
    if not webhook_url:
        return {"notified": False, "reason": "no_webhook"}

    template = "green" if status == "success" else "red"
    status_text = "✅ 修复完成" if status == "success" else "❌ 修复失败"

    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"{status_text} — {issue_key}"},
                "template": template
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**修复摘要**：{fix_summary}"}},
                {"tag": "div", "text": {"tag": "lark_md",
                     "content": f"**分支**：`{branch_name}`\n**Commit**：`{commit_hash}`"}},
                {"tag": "hr"},
                {"tag": "action", "actions": [
                    {"tag": "link", "text": {"tag": "plain_text", "content": "查看分支"},
                     "url": remote_url or "#"}
                ]}
            ]
        }
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        result = response.json()
        return {"notified": result.get("code") == 0, "response": result}
    except Exception as e:
        return {"notified": False, "error": str(e)}


def notify_feishu_simple(
    webhook_url: str,
    title: str,
    content: str,
    status: str = "info"
) -> Dict:
    """
    发送简单的飞书文本通知。

    Args:
        webhook_url: 飞书 Webhook 地址
        title: 通知标题
        content: 通知内容
        status: info / warning / error

    Returns:
        发送结果
    """
    if not webhook_url:
        return {"notified": False, "reason": "no_webhook"}

    msg_type_map = {"info": "blue", "warning": "yellow", "error": "red"}

    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": msg_type_map.get(status, "blue")
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": content}}
            ]
        }
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        result = response.json()
        return {"notified": result.get("code") == 0, "response": result}
    except Exception as e:
        return {"notified": False, "error": str(e)}
