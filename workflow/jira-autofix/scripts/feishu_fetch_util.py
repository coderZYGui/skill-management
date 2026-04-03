# -*- coding: utf-8 -*-
"""
feishu_fetch_util.py — 飞书消息获取工具

从飞书获取消息和上下文信息。
"""

import requests
from typing import Optional, Dict


def fetch_feishu_messages(
    webhook_url: str,
    message_id: Optional[str] = None,
    container_id: Optional[str] = None,
    container_type: str = "chat"
) -> Dict:
    """
    获取飞书消息详情。

    Args:
        webhook_url: 飞书 Webhook 地址（用于认证）
        message_id: 消息 ID
        container_id: 容器 ID（chat_id / open_id）
        container_type: 容器类型（chat / thread）

    Returns:
        消息详情 JSON
    """
    base_url = "https://open.feishu.cn/open-apis"

    token = get_tenant_access_token(webhook_url)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if message_id and container_id:
        url = f"{base_url}/im/v1/messages/{message_id}"
        params = {"container_id_type": container_type, "container_id": container_id}
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    return {}


def get_tenant_access_token(webhook_url: str) -> str:
    """
    获取飞书租户访问令牌。

    Args:
        webhook_url: 飞书 Webhook 地址

    Returns:
        访问令牌
    """
    import re
    match = re.search(r"hook/([a-zA-Z0-9-]+)", webhook_url)
    if not match:
        raise ValueError("无效的飞书 Webhook URL")

    app_id = ""
    app_secret = ""

    token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": app_id, "app_secret": app_secret}

    response = requests.post(token_url, json=payload, timeout=10)
    response.raise_for_status()
    result = response.json()

    if result.get("code") != 0:
        raise RuntimeError(f"获取飞书 Token 失败: {result}")

    return result.get("tenant_access_token", "")


def search_messages_by_keyword(
    webhook_url: str,
    keyword: str,
    chat_id: str
) -> list:
    """
    在指定会话中搜索包含关键词的消息。

    Args:
        webhook_url: 飞书 Webhook 地址
        keyword: 搜索关键词
        chat_id: 会话 ID

    Returns:
        匹配的消息列表
    """
    token = get_tenant_access_token(webhook_url)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {
        "container_id_type": "chat",
        "container_id": chat_id,
        "query": keyword,
        "page_size": 20
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    result = response.json()

    return result.get("data", {}).get("items", [])
