# ================================================================
#  test_two_round_scoring.py — 测试两轮打分逻辑
# ================================================================

import sys
import logging
from datetime import datetime

from fetcher import fetch_candidates, load_seen, save_seen
from writer import rank_and_select

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


def test_two_round_scoring():
    """
    测试两轮打分逻辑：
    1. 抓取20篇AI文章
    2. 第一轮：标题打分，选出6篇
    3. 第二轮：完整内容打分，选出2篇
    4. 保存所有20篇文章到 seen_articles.json
    """
    log.info("=" * 60)
    log.info("测试两轮打分逻辑")
    log.info("=" * 60)

    # 1. 抓取20篇AI候选文章（忽略配额限制）
    log.info("\n【第1步】抓取20篇AI候选文章...")
    candidates = fetch_candidates(ai_limit=2, hsbc_limit=0)

    ai_articles = candidates["ai"]
    log.info(f"  [OK] 实际抓取到 {len(ai_articles)} 篇AI文章")

    if len(ai_articles) == 0:
        log.warning("未找到任何AI文章，测试终止")
        return

    # 显示抓取到的文章标题
    log.info("\n抓取到的文章列表：")
    for i, art in enumerate(ai_articles, 1):
        log.info(f"  {i}. {art['title'][:50]}... ({art['source']})")

    # 2. 执行两轮打分（固定选出2篇）
    log.info(f"\n【第2步】执行两轮AI评分...")
    selected, all_scored = rank_and_select(ai_articles, target_count=2, category="ai")

    if not selected:
        log.warning("两轮打分后未选出文章")
        return

    # 3. 保存所有评分文章到 seen_articles.json
    log.info(f"\n【第3步】保存 {len(all_scored)} 篇文章到 seen_articles.json...")
    seen = load_seen()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 获取已推送文章的ID集合（测试中，我们假设选中的文章会被推送）
    published_ids = {art["id"] for art in selected}

    for art in all_scored:
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
            article_data["post_content"] = "[测试模式，未生成配文]"

        seen[art["id"]] = article_data

    save_seen(seen)
    log.info(f"  [OK] 已保存 {len(all_scored)} 篇文章")

    # 4. 显示最终结果统计
    log.info(f"\n【第4步】评分结果统计：")
    log.info(f"  总共评分: {len(all_scored)} 篇")
    log.info(f"  仅标题评分: {len([a for a in all_scored if 'title_score' in a and 'content_score' not in a])} 篇")
    log.info(f"  完整评分: {len([a for a in all_scored if 'content_score' in a])} 篇")
    log.info(f"  最终选中: {len(selected)} 篇")

    # 5. 显示最终选中的文章详情
    log.info(f"\n【第5步】最终选中的 {len(selected)} 篇文章：")
    for i, art in enumerate(selected, 1):
        log.info(f"\n文章 {i}:")
        log.info(f"  标题: {art['title']}")
        log.info(f"  来源: {art['source']}")
        log.info(f"  标题分数: {art.get('title_score', 0):.2f}/10")
        log.info(f"  标题评语: {art.get('title_score_details', {}).get('comment', 'N/A')}")
        log.info(f"  内容分数: {art.get('content_score', 0):.2f}/10")
        log.info(f"  内容评语: {art.get('content_score_details', {}).get('comment', 'N/A')}")
        log.info(f"  最终综合分数: {art.get('final_score', 0):.2f}/10")

    log.info("\n" + "=" * 60)
    log.info("测试完成！")
    log.info(f"提示：查看 data/seen_articles.json 可以看到所有 {len(all_scored)} 篇文章的详细评分")
    log.info("=" * 60)


if __name__ == "__main__":
    test_two_round_scoring()
