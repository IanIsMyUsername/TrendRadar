# coding=utf-8
"""
文章内容读取工具

通过 Jina AI Reader API 将 URL 转换为 Markdown 格式。
用于 AI 分析时读取新闻正文，提升分析深度。
"""

import time
from typing import Dict, List, Optional

import requests

JINA_READER_BASE = "https://r.jina.ai"
DEFAULT_TIMEOUT = 30
DEFAULT_INTERVAL = 5.0  # 请求间隔（秒），避免触发 Jina 速率限制


def read_article(url: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[str]:
    """
    读取单篇文章正文（Markdown 格式）

    Args:
        url: 文章链接
        timeout: 请求超时时间（秒）

    Returns:
        文章正文内容，失败返回 None
    """
    if not url or not url.startswith(("http://", "https://")):
        return None
    try:
        response = requests.get(
            f"{JINA_READER_BASE}/{url}",
            headers={
                "Accept": "text/markdown",
                "X-Return-Format": "markdown",
                "X-No-Cache": "true",
            },
            timeout=timeout,
        )
        if response.status_code == 200:
            return response.text
        return None
    except Exception:
        return None


def read_articles_batch(
    urls: List[str],
    max_count: int = 5,
    timeout: int = DEFAULT_TIMEOUT,
    interval: float = DEFAULT_INTERVAL,
) -> Dict[str, str]:
    """
    批量读取文章正文，带速率限制

    Args:
        urls: 文章链接列表
        max_count: 最多读取篇数
        timeout: 每篇超时时间
        interval: 请求间隔（秒）

    Returns:
        {url: content} 成功读取的内容，失败的不包含
    """
    results = {}
    urls = [u for u in urls if u and u.startswith(("http://", "https://"))][:max_count]

    for i, url in enumerate(urls):
        if i > 0:
            time.sleep(interval)
        content = read_article(url, timeout=timeout)
        if content:
            # 截断过长内容，避免 token 爆炸（约 3000 字）
            if len(content) > 6000:
                content = content[:6000] + "\n\n[... 内容已截断 ...]"
            results[url] = content
    return results
