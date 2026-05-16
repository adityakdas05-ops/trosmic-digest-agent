from __future__ import annotations

from difflib import SequenceMatcher
import re

from trosmic_digest_agent.models import Article


def dedupe_articles(articles: list[Article], similarity_threshold: float = 0.86) -> list[Article]:
    seen_urls: set[str] = set()
    kept: list[Article] = []

    for article in articles:
        normalized_url = _normalize_url(article.url)
        if normalized_url in seen_urls:
            continue
        if any(_is_near_duplicate(article, existing, similarity_threshold) for existing in kept):
            continue
        seen_urls.add(normalized_url)
        kept.append(article)

    return kept


def _is_near_duplicate(left: Article, right: Article, threshold: float) -> bool:
    left_title = _normalize_text(left.title)
    right_title = _normalize_text(right.title)
    if not left_title or not right_title:
        return False

    sequence_score = SequenceMatcher(None, left_title, right_title).ratio()
    token_score = _token_overlap(left_title, right_title)
    return sequence_score >= threshold or token_score >= 0.66


def _token_overlap(left: str, right: str) -> float:
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / min(len(left_tokens), len(right_tokens))


def _normalize_url(url: str) -> str:
    return url.strip().lower().rstrip("/")


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", text.lower())).strip()
