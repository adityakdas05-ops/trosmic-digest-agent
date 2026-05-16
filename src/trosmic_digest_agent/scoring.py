from __future__ import annotations

from datetime import UTC, datetime

from trosmic_digest_agent.models import AgentConfig, Article


def score_articles(
    articles: list[Article],
    config: AgentConfig,
    now: datetime | None = None,
) -> list[Article]:
    now = now or datetime.now(UTC)
    scored: list[Article] = []

    for article in articles:
        score = 1.0
        matched = _matched_interests(article, config.interests)
        score += len(matched) * 2.5
        score += _recency_score(article, now)
        article.score = round(score, 3)
        article.matched_interests = matched
        scored.append(article)

    return sorted(scored, key=lambda item: item.score, reverse=True)


def _matched_interests(article: Article, interests: list[str]) -> list[str]:
    haystack = f"{article.title} {article.summary} {article.content}".lower()
    return [interest for interest in interests if interest.lower() in haystack]


def _recency_score(article: Article, now: datetime) -> float:
    published = article.normalized_published_at()
    if not published:
        return 0.0
    if published.tzinfo is None:
        published = published.replace(tzinfo=UTC)
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)

    age_hours = max((now - published).total_seconds() / 3600, 0)
    if age_hours <= 24:
        return 2.0
    if age_hours <= 72:
        return 1.0
    if age_hours <= 168:
        return 0.4
    return 0.0
