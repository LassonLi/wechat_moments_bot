#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 AI 评分功能
"""

from writer import score_article, rank_and_select
from datetime import datetime

# 模拟测试文章
test_articles = [
    {
        "id": "test1",
        "title": "OpenAI 发布 GPT-5：性能提升 10 倍",
        "url": "https://example.com/1",
        "summary": "OpenAI 今日正式发布 GPT-5 模型，在多项基准测试中性能提升显著，特别是在代码生成和数学推理方面表现出色。",
        "source": "AI Weekly",
        "category": "ai",
        "pub_date": datetime.now()
    },
    {
        "id": "test2",
        "title": "某公司推出新产品，欢迎试用",
        "url": "https://example.com/2",
        "summary": "我们的新产品上线了，功能强大，欢迎大家试用。限时优惠中。",
        "source": "营销号",
        "category": "ai",
        "pub_date": datetime.now()
    },
    {
        "id": "test3",
        "title": "深度学习在医疗影像诊断中的最新进展",
        "url": "https://example.com/3",
        "summary": "研究团队开发了一种新的深度学习算法，能够在 CT 扫描中准确识别早期肺癌，准确率达到 95%。",
        "source": "Nature AI",
        "category": "ai",
        "pub_date": datetime.now()
    }
]

print("=" * 60)
print("测试 AI 评分功能")
print("=" * 60)
# 测试单篇文章评分
print("\n【测试1】单篇文章评分：")
for art in test_articles:
    score = score_article(art)
    print(f"  [{score:.1f}/10] {art['title']}")

# 测试批量筛选
print("\n【测试2】从 3 篇中选出最好的 2 篇：")
selected = rank_and_select(test_articles.copy(), 2)
print(f"\n最终选出的文章：")
for i, art in enumerate(selected, 1):
    print(f"  {i}. [{art.get('ai_score', 0):.1f}/10] {art['title']}")

print("\n" + "=" * 60)
print("测试完成！")
