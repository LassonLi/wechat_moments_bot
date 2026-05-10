# Copyright (c) 2026 LassonLi
# Licensed under the Apache License, Version 2.0
# See LICENSE in the project root for details.
# SPDX-License-Identifier: Apache-2.0

# ================================================================
#  main.py — 主程序，每天定时运行的入口
# ================================================================

import sys
import logging
import os
from datetime import datetime

from config   import SCHEDULE
from fetcher  import fetch_candidates, load_seen, save_seen, load_stats, save_stats
from writer   import enrich_with_copywriting, rank_and_select
from pusher   import push_to_wechat, push_test_message

# ── 日志设置 ──────────────────────────────────────────────────────
LOG_DIR  = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"run_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ── 节奏判断：今天该推几篇 ────────────────────────────────────────

def decide_today_quota() -> tuple[int, int]:
    """
    根据本周/本双周已推送数量决定今天推几篇
    返回 (ai_quota, hsbc_quota)
    """
    stats        = load_stats()
    ai_quota     = max(0, SCHEDULE["ai_per_week"]    - stats["ai_pushed"])
    hsbc_quota   = max(0, SCHEDULE["hsbc_per_biweek"] - stats["hsbc_pushed"])

    # 每天最多推2篇 AI，避免刷屏
    ai_quota   = min(ai_quota, 2)
    hsbc_quota = min(hsbc_quota, 1)

    log.info(f"本周AI已推: {stats['ai_pushed']}/{SCHEDULE['ai_per_week']}  "
             f"双周HSBC已推: {stats['hsbc_pushed']}/{SCHEDULE['hsbc_per_biweek']}  "
             f"→ 今日配额 AI:{ai_quota} HSBC:{hsbc_quota}")

    return ai_quota, hsbc_quota, stats


# ── 主流程 ────────────────────────────────────────────────────────

def run():
    log.info("=" * 60)
    log.info("朋友圈助手 启动")
    log.info("=" * 60)

    # 1. 判断今天要推几篇
    ai_quota, hsbc_quota, stats = decide_today_quota()

    if ai_quota == 0 and hsbc_quota == 0:
        log.info("本周/双周配额已满，今天跳过推送")
        return

    # 2. 抓取候选文章（数量为目标的3倍）
    log.info("\n【第1步】抓取候选文章...")
    candidates = fetch_candidates(ai_limit=ai_quota, hsbc_limit=hsbc_quota)

    all_candidates = candidates["ai"] + candidates["hsbc"]
    if not all_candidates:
        log.info("今天未找到符合标准的文章，明天再试")
        return

    # 3. AI选出最优文章
    log.info(f"\n【第2步】AI 评分筛选最优文章...")

    ai_selected = []
    ai_all_scored = []
    if candidates["ai"]:
        ai_selected, ai_all_scored = rank_and_select(candidates["ai"], ai_quota, category="ai")

    hsbc_selected = []
    hsbc_all_scored = []
    if candidates["hsbc"]:
        hsbc_selected, hsbc_all_scored = rank_and_select(candidates["hsbc"], hsbc_quota, category="hsbc")

    all_articles = ai_selected + hsbc_selected
    all_scored_articles = ai_all_scored + hsbc_all_scored

    if not all_articles:
        log.info("AI 评分后未选出合适文章，明天再试")
        return

    # 4. 生成朋友圈配文
    log.info(f"\n【第3步】为 {len(all_articles)} 篇精选文章生成配文...")
    all_articles = enrich_with_copywriting(all_articles)

    # 5. 推送到微信
    log.info("\n【第4步】推送到微信...")
    success = push_to_wechat(all_articles)

    # 6. 更新已推送记录
    if success:
        # 更新统计量
        stats["ai_pushed"] += len(ai_selected)
        stats["hsbc_pushed"] += len(hsbc_selected)
        save_stats(stats)

        # 更新已读历史（保存所有参与评分的文章）
        seen = load_seen()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 获取已推送文章的ID集合
        published_ids = {art["id"] for art in all_articles}

        # 保存所有参与评分的文章
        for art in all_scored_articles:
            is_published = art["id"] in published_ids

            # 基础信息
            article_data = {
                "title": art["title"],
                "url": art["url"],
                "source": art["source"],
                "category": art["category"],
                "is_published": is_published,
                "scored_at": now,
            }

            # 标题评分（所有文章都有）
            if "title_score" in art:
                article_data["title_score"] = art["title_score"]
                article_data["title_score_details"] = art.get("title_score_details", {})

            # 内容评分（只有进入第二轮的文章才有）
            if "content_score" in art:
                article_data["content_score"] = art["content_score"]
                article_data["content_score_details"] = art.get("content_score_details", {})
                article_data["final_score"] = art.get("final_score", 0)

            # 推送信息（只有已推送的文章才有）
            if is_published:
                article_data["pushed_at"] = now
                article_data["post_content"] = art.get("copywriting", "")

            seen[art["id"]] = article_data

        save_seen(seen)
        print(f"成功推送 {len(all_articles)} 篇文章，并保存 {len(all_scored_articles)} 篇评分记录。")
        log.info(f"\n[OK] 完成！已推送 {len(all_articles)} 篇文章到微信，保存 {len(all_scored_articles)} 篇评分记录")
    else:
        log.warning("\n[WARN] 推送失败，已推送记录未更新，明天会重试")

    log.info("=" * 60)


# ── 命令行入口 ────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # python main.py test — 发送测试消息验证配置
        print("\n发送测试消息到微信...")
        push_test_message()
    else:
        # python main.py — 正常执行
        run()
