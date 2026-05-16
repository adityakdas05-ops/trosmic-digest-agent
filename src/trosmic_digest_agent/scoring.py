from __future__ import annotations

from datetime import UTC, datetime

from trosmic_digest_agent.models import AgentConfig, Article, DigestDebug
from trosmic_digest_agent.pipeline.eligibility import (
    EligibilityResult,
    detect_primary_topics,
    detect_trosmic_pillars,
    evaluate_eligibility,
)
from trosmic_digest_agent.trosmic_policy import (
    AI_TOP_10_CAP,
    TROSMIC_RELEVANCE_THRESHOLD,
    action_item,
    confidence_level,
    source_status,
    trosmic_implication,
    why_it_matters,
)

QUOTA_TARGETS = {
    "media_rights": 2,
    "sponsorship": 2,
    "venues": 2,
    "capital": 1,
    "india_sports": 1,
    "global_leagues": 1,
    "fan_data": 1,
}

COMMERCIAL_TERMS = (
    "rights",
    "deal",
    "sponsorship",
    "sponsor",
    "naming rights",
    "valuation",
    "sale",
    "investment",
    "private equity",
    "sovereign",
    "m&a",
    "financing",
    "revenue",
    "viewership",
    "brand partnership",
)


def score_articles(
    articles: list[Article],
    config: AgentConfig,
    now: datetime | None = None,
    debug: DigestDebug | None = None,
) -> list[Article]:
    now = now or datetime.now(UTC)
    eligible_articles: list[Article] = []

    for article in articles:
        eligibility = evaluate_eligibility(article)
        article.is_ai_led = eligibility.is_ai_led
        article.primary_topics = eligibility.primary_topics or []

        if not eligibility.eligible:
            _record_rejection(article, eligibility, debug)
            continue

        if debug is not None:
            debug.passing_eligibility_count += 1

        relevance_score, breakdown = score_trosmic_relevance(article, eligibility)
        if relevance_score < TROSMIC_RELEVANCE_THRESHOLD:
            article.rejection_reason = f"below Trosmic Relevance Gate ({relevance_score}/21)"
            continue

        article.score = round(relevance_score + _recency_score(article, now), 3)
        article.relevance_score = relevance_score
        article.relevance_breakdown = breakdown
        article.matched_interests = _matched_interests(article, config.interests)
        article.affected_pillar = "; ".join(eligibility.pillars or detect_trosmic_pillars(article))
        article.source_status = source_status(article)
        article.why_it_matters = why_it_matters(article)
        article.trosmic_implication = trosmic_implication(article)
        article.action_item = action_item(article)
        article.confidence_level = confidence_level(article)
        article.quota_category = quota_category(article)
        eligible_articles.append(article)

    selected = select_top_articles(eligible_articles, config.max_items)
    if debug is not None:
        debug.final_selected_titles = [article.title for article in selected]
        debug.selected_scores_and_pillars = [
            {
                "title": article.title,
                "relevance_score": article.relevance_score,
                "pillar": article.affected_pillar,
                "quota_category": article.quota_category,
            }
            for article in selected
        ]
        debug.ai_led_items_selected = sum(1 for article in selected if article.is_ai_led)
    return selected


def score_trosmic_relevance(
    article: Article,
    eligibility: EligibilityResult | None = None,
) -> tuple[int, dict[str, int]]:
    eligibility = eligibility or evaluate_eligibility(article)
    text = _article_text(article)
    pillars = eligibility.pillars or []
    primary_topics = eligibility.primary_topics or []

    pillar_score = min(5, 2 + len(pillars)) if pillars else 0
    sports_specificity = min(5, 2 + len(primary_topics)) if primary_topics else 0
    commercial_materiality = _keyword_score(text, COMMERCIAL_TERMS, cap=5)
    actionability = _actionability_score(text, pillars, commercial_materiality)
    credibility = _source_credibility_score(article)

    total = (
        pillar_score
        + sports_specificity
        + commercial_materiality
        + actionability
        + credibility
    )
    return total, {
        "direct_trosmic_pillar_relevance": pillar_score,
        "sports_media_entertainment_specificity": sports_specificity,
        "commercial_materiality": commercial_materiality,
        "actionability_for_trosmic": actionability,
        "source_credibility": credibility,
    }


def select_top_articles(articles: list[Article], max_items: int) -> list[Article]:
    sorted_articles = sorted(articles, key=lambda item: item.score, reverse=True)
    target_count = min(max_items, 10)
    selected: list[Article] = []
    selected_ids: set[int] = set()
    ai_led_count = 0

    for category, quota in QUOTA_TARGETS.items():
        category_articles = [
            article for article in sorted_articles if article.quota_category == category
        ]
        for article in category_articles:
            if len([item for item in selected if item.quota_category == category]) >= quota:
                break
            if len(selected) >= target_count:
                break
            if article.is_ai_led and ai_led_count >= AI_TOP_10_CAP:
                article.rejection_reason = "AI-led item cap reached"
                continue
            selected.append(article)
            selected_ids.add(id(article))
            if article.is_ai_led:
                ai_led_count += 1

    for article in sorted_articles:
        if len(selected) >= target_count:
            break
        if id(article) in selected_ids:
            continue
        if article.is_ai_led and ai_led_count >= AI_TOP_10_CAP:
            article.rejection_reason = "AI-led item cap reached"
            continue
        selected.append(article)
        selected_ids.add(id(article))
        if article.is_ai_led:
            ai_led_count += 1

    return selected


def quota_category(article: Article) -> str:
    text = _article_text(article)
    topics = set(article.primary_topics or detect_primary_topics(article))
    if topics & {"media rights", "OTT / streaming sports", "broadcast"}:
        return "media_rights"
    if topics & {"sponsorship", "naming rights"}:
        return "sponsorship"
    if topics & {"stadium", "arena", "venue", "live entertainment"}:
        return "venues"
    if topics & {
        "franchise sale",
        "team valuation",
        "sports private equity",
        "sports M&A",
        "sovereign sports investment",
        "family office sports investment",
    }:
        return "capital"
    if topics & {"kabaddi", "PKL", "IPL", "WPL", "BCCI", "India sports regulation"}:
        return "india_sports"
    if topics & {"UFC", "TKO", "WWE", "Formula 1", "NBA", "NFL", "FIFA", "IOC", "EPL", "MLS"}:
        return "global_leagues"
    if topics & {
        "fan engagement",
        "fantasy sports",
        "sports gaming",
        "sports data",
        "sports analytics",
    }:
        return "fan_data"
    if "fan data" in text or "sports ai" in text:
        return "fan_data"
    return "general"


def _record_rejection(
    article: Article,
    eligibility: EligibilityResult,
    debug: DigestDebug | None,
) -> None:
    article.rejection_reason = eligibility.reason
    if debug is None:
        return
    if eligibility.reason == "generic_ai":
        debug.rejected_generic_ai_count += 1
        debug.rejected_generic_ai_or_tech_titles.append(article.title)
    elif eligibility.reason == "generic_tech":
        debug.rejected_generic_tech_count += 1
        debug.rejected_generic_ai_or_tech_titles.append(article.title)
    elif eligibility.reason == "no_trosmic_pillar":
        debug.rejected_no_trosmic_pillar_count += 1


def _matched_interests(article: Article, interests: list[str]) -> list[str]:
    haystack = _article_text(article)
    return [interest for interest in interests if _interest_matches(interest, haystack)]


def _interest_matches(interest: str, haystack: str) -> bool:
    needle = interest.lower()
    if needle in haystack:
        return True
    tokens = [token for token in needle.split() if token not in {"sports", "sport"}]
    return bool(tokens) and all(token in haystack for token in tokens)


def _article_text(article: Article) -> str:
    return f"{article.title} {article.summary} {article.content}".lower()


def _keyword_score(text: str, keywords: tuple[str, ...], cap: int) -> int:
    matches = sum(1 for keyword in keywords if keyword in text)
    if matches >= 5:
        return cap
    if matches >= 3:
        return min(cap, 4)
    if matches >= 2:
        return min(cap, 3)
    if matches == 1:
        return min(cap, 2)
    return 0


def _actionability_score(text: str, pillars: list[str], commercial_score: int) -> int:
    if not pillars:
        return 0
    score = 1
    if commercial_score >= 3:
        score += 1
    if any(
        term in text
        for term in (
            "media rights",
            "sponsorship",
            "venue",
            "franchise",
            "fan data",
            "india",
            "gcc",
            "saudi",
            "uae",
            "qatar",
            "kabaddi",
        )
    ):
        score += 1
    return min(score, 3)


def _source_credibility_score(article: Article) -> int:
    status = source_status(article)
    if status in {"official", "reported"}:
        return 3
    if status == "estimated":
        return 2
    return 2


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
