# ================================================================
#  fetcher.py — 抓取 RSS，按标准筛选文章
# ================================================================

import feedparser
import json
import os
import hashlib
from datetime import datetime, timedelta

from config import RSS_SOURCES, AI_CRITERIA, HSBC_CRITERIA

DATA_DIR  = os.path.join(os.path.dirname(__file__), "data")
SEEN_FILE = os.path.join(DATA_DIR, "seen_articles.json")
STAT_FILE = os.path.join(DATA_DIR, "push_stats.json")   # 记录本周/本双周已推送数量


# ── 持久化工具 ────────────────────────────────────────────────────

def _load_json(path: str, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def _save_json(path: str, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_seen() -> dict: # 返回 dict
    return _load_json(SEEN_FILE, {})

def save_seen(seen: dict): # 直接保存 dict
    _save_json(SEEN_FILE, seen)

def article_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


# ── 发布节奏控制 ──────────────────────────────────────────────────

def load_stats() -> dict:
    """加载本周/本双周已推送统计"""
    stats = _load_json(STAT_FILE, {})
    now = datetime.now()
    week_key    = now.strftime("%Y-W%W")          # 例: 2026-W19
    biweek_key  = f"{now.year}-BW{now.isocalendar()[1] // 2}"

    # 如果是新的一周/双周，自动重置计数
    if stats.get("week_key") != week_key:
        stats = {"week_key": week_key, "biweek_key": biweek_key,
                 "ai_pushed": 0, "hsbc_pushed": 0}
    elif stats.get("biweek_key") != biweek_key:
        stats["biweek_key"] = biweek_key
        stats["hsbc_pushed"] = 0

    return stats

def save_stats(stats: dict):
    _save_json(STAT_FILE, stats)


# ── RSS 抓取 ──────────────────────────────────────────────────────

def _parse_date(entry) -> datetime:
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime(*val[:6])
            except Exception:
                pass
    return datetime.now()

def fetch_rss(source: dict) -> list[dict]:
    articles = []
    try:
        feed = feedparser.parse(source["url"])
        for entry in feed.entries[:40]:
            articles.append({
                "title"   : entry.get("title", "").strip(),
                "url"     : entry.get("link", "").strip(),
                "summary" : entry.get("summary", "")[:600].strip(),
                "pub_date": _parse_date(entry),
                "source"  : source["name"],
                "category": source["category"],
            })
    except Exception as e:
        print(f"  [WARN] {source['name']} 抓取失败: {e}")
    return articles


# ── 筛选逻辑 ──────────────────────────────────────────────────────

def passes_filter(article: dict) -> bool:
    cat      = article["category"]
    criteria = AI_CRITERIA if cat == "ai" else HSBC_CRITERIA
    text     = (article["title"] + " " + article["summary"]).lower()

    # 1. 时效性
    cutoff = datetime.now() - timedelta(days=criteria["max_age_days"])
    if article["pub_date"] < cutoff:
        return False

    # 2. 必含关键词
    if not any(kw.lower() in text for kw in criteria["keywords_must"]):
        return False

    # 3. 黑名单过滤
    if any(kw.lower() in text for kw in criteria["keywords_ban"]):
        return False

    return True


# ── 主入口 ────────────────────────────────────────────────────────

# 修改 fetch_candidates 函数中的判断逻辑
def fetch_candidates(ai_limit: int = 2, hsbc_limit: int = 1) -> dict:
    """
    抓取候选文章
    - AI文章：固定抓取20篇（用于两轮筛选：20->6->2）
    - HSBC文章：抓取 hsbc_limit * 3 篇（用于一轮筛选）
    """
    seen = load_seen()  # 现在 seen 是一个字典
    candidates = {"ai": [], "hsbc": []}

    # AI文章固定抓取20篇，HSBC按原逻辑
    ai_candidate_limit = 20
    hsbc_candidate_limit = hsbc_limit * 3

    for source in RSS_SOURCES:
        cat = source["category"]
        target_limit = ai_candidate_limit if cat == "ai" else hsbc_candidate_limit

        if len(candidates[cat]) >= target_limit:
            continue

        for art in fetch_rss(source):
            if len(candidates[cat]) >= target_limit:
                break
            aid = article_id(art["url"])

            # 修改这里：判断 key 是否在字典中
            if aid in seen:
                continue

            if passes_filter(art):
                art["id"] = aid
                candidates[cat].append(art)

    # 最新的排前面
    for cat in candidates:
        candidates[cat].sort(key=lambda x: x["pub_date"], reverse=True)

    ai_n    = len(candidates["ai"])
    hsbc_n  = len(candidates["hsbc"])
    print(f"  [OK] 筛选完成 — AI候选: {ai_n} 篇 | HSBC候选: {hsbc_n} 篇")
    return candidates
