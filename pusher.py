# Copyright (c) 2026 LassonLi
# Licensed under the Apache License, Version 2.0
# See LICENSE in the project root for details.
# SPDX-License-Identifier: Apache-2.0

# ================================================================
#  pusher.py — 通过 Server酱 推送微信通知
# ================================================================

import requests
from datetime import datetime
from config import SERVERCHAN_SENDKEY


SERVERCHAN_URL = f"https://sctapi.ftqq.com/{SERVERCHAN_SENDKEY}.send"


def _build_message(articles: list[dict]) -> tuple[str, str]:
    """
    构建推送消息的标题和正文（Markdown格式）
    返回 (title, content)
    """
    now   = datetime.now().strftime("%m月%d日")
    total = len(articles)

    # ── 标题 ──────────────────────────────────────────────
    ai_count   = sum(1 for a in articles if a["category"] == "ai")
    hsbc_count = sum(1 for a in articles if a["category"] == "hsbc")

    parts = []
    if ai_count:   parts.append(f"AI文章×{ai_count}")
    if hsbc_count: parts.append(f"HSBC×{hsbc_count}")
    title = f"📱 朋友圈推荐 {now} — {' + '.join(parts)}"

    # ── 正文（每篇文章一个卡片）──────────────────────────
    lines = [f"## 今日朋友圈推荐（共{total}篇）\n"]

    for i, art in enumerate(articles, 1):
        cat_label = "🤖 AI技术" if art["category"] == "ai" else "🏦 HSBC资讯"
        pub_str   = art["pub_date"].strftime("%Y-%m-%d")

        lines.append(f"---\n")
        lines.append(f"### {i}. [{art['title']}]({art['url']})\n")
        lines.append(f"> 来源：**{art['source']}** | 类型：{cat_label} | 发布：{pub_str}\n")
        lines.append(f"\n**📝 朋友圈配文：**\n")
        lines.append(f"┌{'─' * 50}┐\n")
        lines.append(f"{art['copywriting']}\n")
        lines.append(f"└{'─' * 50}┘\n")

    lines.append("---\n")
    lines.append("_由朋友圈助手自动生成 · 长按配文区域即可复制_")

    return title, "\n".join(lines)


def push_to_wechat(articles: list[dict]) -> bool:
    """
    推送所有文章到微信，返回是否成功
    """
    if not articles:
        print("  [INFO] 今天没有符合条件的文章，跳过推送")
        return True

    title, content = _build_message(articles)

    try:
        resp = requests.post(
            SERVERCHAN_URL,
            data={
                "title"  : title,
                "desp"   : content,
            },
            timeout=15,
        )
        data = resp.json()

        if data.get("code") == 0:
            print(f"  [OK] 微信推送成功！共 {len(articles)} 篇文章")
            return True
        else:
            print(f"  [ERROR] Server酱返回错误: {data}")
            return False

    except Exception as e:
        print(f"  [ERROR] 微信推送失败: {e}")
        return False


def push_test_message() -> bool:
    """发送一条测试消息，验证 Server酱 配置是否正确"""
    try:
        resp = requests.post(
            SERVERCHAN_URL,
            data={
                "title": "✅ 朋友圈助手配置成功",
                "desp" : "Server酱推送正常工作！\n\n你的每日文章推荐将在配置的时间自动发送到这里。",
            },
            timeout=15,
        )
        data = resp.json()
        if data.get("code") == 0:
            print("  [OK] 测试消息发送成功，请查看微信")
            return True
        else:
            print(f"  [ERROR] 推送失败: {data}")
            return False
    except Exception as e:
        print(f"  [ERROR] 推送异常: {e}")
        return False
