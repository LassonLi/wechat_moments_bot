# Copyright (c) 2026 LassonLi
# Licensed under the Apache License, Version 2.0
# See LICENSE in the project root for details.
# SPDX-License-Identifier: Apache-2.0

# ================================================================
#  writer.py — 调用 AI 生成朋友圈文案 & 评估文章质量
# ================================================================

import anthropic
import json
import os
import requests
from typing import Optional
import trafilatura
from config import (
    ANTHROPIC_API_KEY,
    COPYWRITING_PROMPT,
    MODEL_PROVIDER,
    QWEN_API_KEY,
    QWEN_BASE_URL,
    QWEN_MODEL,
)


def fetch_article_content(url: str) -> str | None:
    """用 trafilatura 抓取并提取文章正文"""
    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; WechatMomentsBot/1.0)"
        })
        resp.raise_for_status()
        text = trafilatura.extract(resp.text, include_comments=False, include_tables=False)
        return text.strip() if text else None
    except Exception as e:
        print(f"  [WARN] 抓取正文失败: {e}")
        return None


def call_ai_chat(system_msg: str, user_msg: str, model: Optional[str] = None, max_tokens: int = 200) -> tuple[str, dict]:
    """统一的聊天调用：根据 `MODEL_PROVIDER` 选择 anthropic 或 qwen(openai兼容)

    返回 (文本, meta)；meta 包含 provider 与实际使用的 model 名称。
    """
    provider = (MODEL_PROVIDER or "qwen").lower()

    if provider == "anthropic":
        used_model = model or "claude-sonnet-4-5"
        client = anthropic.Anthropic(base_url="https://vip.yyds168.net", api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=used_model,
            max_tokens=max_tokens,
            system=system_msg.strip(),
            messages=[{"role": "user", "content": user_msg}],
        )
        try:
            text = message.content[0].text.strip()
        except Exception:
            cont = getattr(message, "content", None)
            if isinstance(cont, list) and len(cont) > 0:
                text = str(getattr(cont[0], "text", cont[0])).strip()
            else:
                text = str(message).strip()

        return text, {"provider": "anthropic", "model": used_model}

    # 默认走 qwen / openai 兼容层
    try:
        from openai import OpenAI
    except Exception as e:
        raise RuntimeError("OpenAI-compatible SDK not installed (required for qwen provider)") from e

    used_model = model or QWEN_MODEL
    client = OpenAI(api_key=QWEN_API_KEY or os.getenv("DASHSCOPE_API_KEY"), base_url=QWEN_BASE_URL)
    msgs = [{"role": "system", "content": system_msg.strip()}, {"role": "user", "content": user_msg}]
    completion = client.chat.completions.create(model=used_model, messages=msgs, max_tokens=max_tokens)

    text: Optional[str] = None
    try:
        if hasattr(completion, "choices"):
            first = completion.choices[0]
            if isinstance(first, dict):
                text = first.get("message", {}).get("content") or first.get("text")
            else:
                msg = getattr(first, "message", None)
                if msg:
                    text = getattr(msg, "content", None)
                else:
                    text = getattr(first, "text", None)
    except Exception:
        text = None

    if not text:
        cont = getattr(completion, "content", None)
        if cont:
            if isinstance(cont, list) and len(cont) > 0:
                first = cont[0]
                text = getattr(first, "text", None) or (first.get("text") if isinstance(first, dict) else None)
            elif isinstance(cont, str):
                text = cont

    if not text:
        try:
            text = completion.model_dump_json()
        except Exception:
            text = str(completion)

    return str(text).strip(), {"provider": "qwen", "model": used_model}

def generate_copywriting(article: dict) -> str:
    cat = article.get("category", "ai")
    system_msg = COPYWRITING_PROMPT.get(cat, COPYWRITING_PROMPT["ai"])
    user_msg = f"标题：{article['title']}\n来源：{article['source']}\n摘要：{article['summary']}\n直接输出最终配文。"

    try:
        result_text, meta = call_ai_chat(system_msg=system_msg, user_msg=user_msg, model=None, max_tokens=300)
        # 将使用的模型信息写回文章对象（方便后续保存）
        try:
            article["copywriting_model"] = meta
        except Exception:
            pass
        if not result_text:
            raise RuntimeError("empty response")
        return result_text.strip()
    except Exception as e:
        print(f"  [WARN] 文案生成失败: {e}")
        return f"推荐阅读：{article['title']}"

def enrich_with_copywriting(articles: list[dict]) -> list[dict]:
    """批量生成朋友圈文案并存入 moments_text 字段"""
    for art in articles:
        print(f"  -> 生成朋友圈文案: {art['title'][:20]}...")
        art["copywriting"] = generate_copywriting(art)
    return articles


def score_article_by_title(article: dict) -> tuple[float, dict]:
    """
    第一轮筛选：仅根据标题评估文章质量
    返回 (总分, 评分详情)
    """
    cat = article.get("category", "ai")

    if cat == "ai":
        system_msg = """你是一位资深的AI技术内容评审专家。请仅根据文章标题评估其吸引力和价值，并以JSON格式输出：

评估维度：
1. 话题热度（0-10分）：是否是当前热点话题
2. 技术价值（0-10分）：标题是否暗示有实质性技术内容
3. 吸引力（0-10分）：标题是否吸引人点击
4. 受众相关性（0-10分）：是否适合技术从业者

请严格按照以下JSON格式输出（不要其他内容）：
{
  "话题热度": 8.5,
  "技术价值": 9.0,
  "吸引力": 7.5,
  "受众相关性": 8.0,
  "总分": 8.25,
  "评语": "简短评价（20字以内）"
}"""
    else:
        system_msg = """你是一位资深的金融行业内容评审专家。请仅根据文章标题评估其价值，并以JSON格式输出：

评估维度：
1. 重要性（0-10分）：是否是重要的行业动态
2. 时效性（0-10分）：是否是当前热点
3. 吸引力（0-10分）：标题是否吸引人
4. 受众相关性（0-10分）：是否适合金融从业者

请严格按照以下JSON格式输出（不要其他内容）：
{
  "重要性": 8.5,
  "时效性": 9.0,
  "吸引力": 7.5,
  "受众相关性": 8.0,
  "总分": 8.25,
  "评语": "简短评价（20字以内）"
}"""

    user_msg = f"标题：{article['title']}\n来源：{article['source']}"

    try:
        result_text, meta = call_ai_chat(system_msg=system_msg, user_msg=user_msg, model=None, max_tokens=200)
        try:
            article["title_score_model"] = meta
        except Exception:
            pass
        if not result_text:
            print(f"  [WARN] API 返回空内容")
            return 5.0, {"dimensions": {}, "comment": "API返回空响应"}

        # 检查是否为空
        if not result_text:
            print(f"  [WARN] API 返回空字符串")
            return 5.0, {"dimensions": {}, "comment": "API返回空字符串"}

        # 清理 markdown 代码块标记
        if result_text.startswith("```json"):
            result_text = result_text[7:]  # 移除 ```json
        if result_text.startswith("```"):
            result_text = result_text[3:]  # 移除 ```
        if result_text.endswith("```"):
            result_text = result_text[:-3]  # 移除结尾的 ```
        result_text = result_text.strip()

        # 解析 JSON 结果
        result = json.loads(result_text)
        total_score = result.get("总分", 5.0)

        # 构建评分详情
        score_details = {
            "dimensions": {k: v for k, v in result.items() if k not in ("总分", "评语")},
            "comment": result.get("评语", "")
        }

        return max(0.0, min(10.0, total_score)), score_details
    except json.JSONDecodeError as e:
        print(f"  [WARN] JSON解析失败: {e}")
        print(f"  [DEBUG] 尝试解析的内容: {result_text if 'result_text' in locals() else 'N/A'}")
        return 5.0, {"dimensions": {}, "comment": "JSON解析失败"}
    except Exception as e:
        print(f"  [WARN] 标题评分失败: {e}")
        print(f"  [DEBUG] 错误类型: {type(e).__name__}")
        return 5.0, {"dimensions": {}, "comment": "评分失败"}


def score_article_by_content(article: dict) -> tuple[float, dict]:
    """
    让 AI 评估单篇文章的质量，返回 (总分, 评分详情)
    评估维度：内容价值、时效性、可读性、受众相关性
    """
    cat = article.get("category", "ai")

    if cat == "ai":
        system_msg = """你是一位资深的AI技术内容评审专家。请从以下维度评估文章质量，并以JSON格式输出：

评估维度：
1. 技术深度与价值（0-10分）：是否有实质性技术内容，而非纯营销
2. 时效性与热度（0-10分）：是否是当前热点话题
3. 可读性（0-10分）：标题和摘要是否吸引人
4. 受众相关性（0-10分）：是否适合技术从业者阅读

请严格按照以下JSON格式输出（不要其他内容）：
{
  "技术深度": 8.5,
  "时效性": 9.0,
  "可读性": 7.5,
  "受众相关性": 8.0,
  "总分": 8.25,
  "评语": "简短评价（20字以内）"
}"""
    else:
        system_msg = """你是一位资深的金融行业内容评审专家。请从以下维度评估文章质量，并以JSON格式输出：

评估维度：
1. 内容价值（0-10分）：是否有实质性信息，而非纯宣传
2. 时效性与重要性（0-10分）：是否是重要的行业动态
3. 可读性（0-10分）：标题和摘要是否吸引人
4. 受众相关性（0-10分）：是否适合金融从业者阅读

请严格按照以下JSON格式输出（不要其他内容）：
{
  "内容价值": 8.5,
  "时效性": 9.0,
  "可读性": 7.5,
  "受众相关性": 8.0,
  "总分": 8.25,
  "评语": "简短评价（20字以内）"
}"""

    user_msg = f"标题：{article['title']}\n来源：{article['source']}\n摘要：{article['summary']}"

    # 抓取正文全文
    full_text = fetch_article_content(article["url"])
    if full_text:
        # 截断防止超长，保留前 4000 字
        if len(full_text) > 4000:
            full_text = full_text[:4000] + "\n\n[... 以下内容已截断]"
        user_msg += f"\n正文：\n{full_text}"

    try:
        result_text, meta = call_ai_chat(system_msg=system_msg, user_msg=user_msg, model=None, max_tokens=200)
        try:
            article["content_score_model"] = meta
        except Exception:
            pass
        if not result_text:
            print(f"  [WARN] API 返回空内容")
            return 5.0, {"dimensions": {}, "comment": "API返回空响应"}

        # 检查是否为空
        if not result_text:
            print(f"  [WARN] API 返回空字符串")
            return 5.0, {"dimensions": {}, "comment": "API返回空字符串"}

        # 清理 markdown 代码块标记
        if result_text.startswith("```json"):
            result_text = result_text[7:]  # 移除 ```json
        if result_text.startswith("```"):
            result_text = result_text[3:]  # 移除 ```
        if result_text.endswith("```"):
            result_text = result_text[:-3]  # 移除结尾的 ```
        result_text = result_text.strip()

        # 解析 JSON 结果
        result = json.loads(result_text)
        total_score = result.get("总分", 5.0)

        # 构建评分详情
        score_details = {
            "dimensions": {k: v for k, v in result.items() if k not in ("总分", "评语")},
            "comment": result.get("评语", "")
        }

        return max(0.0, min(10.0, total_score)), score_details
    except json.JSONDecodeError as e:
        print(f"  [WARN] JSON解析失败: {e}")
        print(f"  [DEBUG] 尝试解析的内容: {result_text if 'result_text' in locals() else 'N/A'}")
        return 5.0, {"dimensions": {}, "comment": "JSON解析失败"}
    except Exception as e:
        print(f"  [WARN] 文章评分失败: {e}")
        print(f"  [DEBUG] 错误类型: {type(e).__name__}")
        return 5.0, {"dimensions": {}, "comment": "评分失败"}


def rank_and_select(articles: list[dict], target_count: int, category: str = "ai") -> tuple[list[dict], list[dict]]:
    """
    两轮AI评分筛选文章：
    - AI类文章：第一轮用标题打分（仅标题评分），第二轮对标题评分最高的6篇进行完整内容打分，最终取最高分2篇
    - HSBC类文章：一轮完整内容打分

    返回: (selected_articles, all_scored_articles)
    - selected_articles: 最终选中的文章
    - all_scored_articles: 所有参与评分的文章（包括未入选的）
    """
    if len(articles) <= target_count:
        return articles, articles

    # AI类文章使用两轮筛选
    if category == "ai":
        print(f"  -> 【第一轮】对 {len(articles)} 篇文章进行标题打分...")

        # 第一轮：标题打分
        for art in articles:
            score, details = score_article_by_title(art)
            art["title_score"] = score
            art["title_score_details"] = details
            print(f"     [标题 {score:.1f}/10] {art['title'][:40]}... - {details.get('comment', '')}")

        # 按标题分数排序，选出标题得分最高的6篇用于第二轮内容打分
        articles.sort(key=lambda x: x.get("title_score", 0), reverse=True)
        round1_selected = articles[:6]
        round1_rejected = articles[6:]  # 未进入第二轮的文章

        print(f"  [OK] 第一轮完成，选出标题得分最高的 {len(round1_selected)} 篇用于第二轮内容评分")
        print(f"\n  -> 【第二轮】对 {len(round1_selected)} 篇文章进行完整内容打分...")

        # 第二轮：对标题最高的6篇进行完整内容打分
        for art in round1_selected:
            score, details = score_article_by_content(art)
            art["content_score"] = score
            art["content_score_details"] = details
            # 最终分数 = 标题分数 * 0.3 + 内容分数 * 0.7
            art["final_score"] = art["title_score"] * 0.3 + score * 0.7
            print(f"     [内容 {score:.1f}/10 | 综合 {art['final_score']:.1f}/10] {art['title'][:40]}... - {details.get('comment', '')}")

        # 按综合分数排序，选出最终的文章
        round1_selected.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        final_selected = round1_selected[:target_count]

        print(f"  [OK] 第二轮完成，最终选出 {len(final_selected)} 篇文章")

        # 返回: (最终选中的文章, 所有参与评分的文章)
        all_scored = round1_selected + round1_rejected
        return final_selected, all_scored

    else:
        # HSBC类文章：一轮完整内容打分
        print(f"  -> 开始对 {len(articles)} 篇文章进行完整内容打分...")

        for art in articles:
            score, details = score_article_by_content(art)
            art["content_score"] = score
            art["content_score_details"] = details
            art["final_score"] = score
            print(f"     [{score:.1f}/10] {art['title'][:40]}... - {details.get('comment', '')}")

        # 按分数排序，选出最高分的文章
        articles.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        selected = articles[:target_count]

        print(f"  [OK] 已选出得分最高的 {len(selected)} 篇文章")
        return selected, articles