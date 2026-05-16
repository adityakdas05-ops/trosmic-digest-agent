from __future__ import annotations

import re

from trosmic_digest_agent.models import Article


def summarize_article(article: Article, max_sentences: int = 3) -> str:
    text = article.summary or article.content
    sentences = _split_sentences(text)
    if not sentences:
        return ""
    return " ".join(sentences[:max_sentences])


def _split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()
    if not cleaned:
        return []
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", cleaned)
        if sentence.strip()
    ]
