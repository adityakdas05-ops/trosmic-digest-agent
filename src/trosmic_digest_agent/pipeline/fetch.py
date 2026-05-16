from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

from trosmic_digest_agent.connectors import (
    GoogleNewsSearchConnector,
    ManualURLConnector,
    RSSConnector,
)
from trosmic_digest_agent.models import AgentConfig, Article, DigestDebug, SourceConfig
from trosmic_digest_agent.source_policy import (
    article_source_domain,
    is_generic_ai_vendor_article,
    is_hard_blocked_generic_ai_source,
    normalize_domain,
)

CONTAMINATION_WARNING = "WARNING: SOURCE_POOL_CONTAMINATED_WITH_GENERIC_AI"


def fetch_articles(
    config: AgentConfig,
    debug: DigestDebug,
    warnings: list[str],
) -> tuple[list[Article], list[Article]]:
    fetched: list[Article] = []
    enabled_sources = [source for source in config.sources if source.enabled]
    workers = min(8, max(1, len(enabled_sources)))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(_fetch_source, source): source
            for source in enabled_sources
        }
        for future in as_completed(futures):
            source = futures[future]
            try:
                fetched.extend(future.result())
            except Exception as exc:  # noqa: BLE001 - keep batch digest resilient per source.
                warnings.append(f"{source.name}: {exc}")
                continue

    debug.total_stories_fetched = len(fetched)
    debug.top_30_fetched_titles = [article.title for article in fetched[:30]]
    _record_domain_stats(fetched, debug)

    filtered: list[Article] = []
    for article in fetched:
        if is_hard_blocked_generic_ai_source(article):
            article.rejection_reason = "blocked_generic_ai_vendor_source"
            continue
        filtered.append(article)

    update_fetched_story_debug(debug, fetched, selected=[])
    return filtered, fetched


def update_fetched_story_debug(
    debug: DigestDebug,
    fetched: list[Article],
    selected: list[Article],
) -> None:
    selected_urls = {article.url for article in selected}
    debug.fetched_stories = [
        {
            "title": article.title,
            "source_domain": article_source_domain(article),
            "url": article.url,
            "connector": article.connector,
            "query_group": article.query_group,
            "query_used": article.query_used,
            "rejection_reason": _debug_rejection_reason(article, selected_urls),
            "selected_or_rejected": "selected" if article.url in selected_urls else "rejected",
        }
        for article in fetched
    ]


def _record_domain_stats(articles: list[Article], debug: DigestDebug) -> None:
    counts = Counter(article_source_domain(article) or "unknown" for article in articles)
    debug.top_fetched_domains = [
        {"domain": domain, "count": count}
        for domain, count in counts.most_common(20)
    ]
    debug.generic_ai_vendor_source_count = sum(
        1 for article in articles if is_generic_ai_vendor_article(article)
    )
    debug.generic_ai_vendor_source_ratio = (
        round(debug.generic_ai_vendor_source_count / len(articles), 4)
        if articles
        else 0.0
    )
    debug.source_pool_contaminated_with_generic_ai = debug.generic_ai_vendor_source_ratio > 0.2


def _connector_for(source: SourceConfig):
    if source.type == "rss":
        return RSSConnector(source)
    if source.type in {"google_news_search", "news_search", "search"}:
        return GoogleNewsSearchConnector(source)
    if source.type in {"manual", "url", "urls"}:
        return ManualURLConnector(source)
    raise ValueError(f"Unsupported source type: {source.type}")


def _fetch_source(source: SourceConfig) -> list[Article]:
    source_articles = _connector_for(source).fetch()
    for article in source_articles:
        _enrich_article(article, source)
    return source_articles


def _enrich_article(article: Article, source: SourceConfig) -> None:
    if not article.source_domain:
        article.source_domain = normalize_domain(article.url)
    if not article.connector:
        article.connector = source.type
    if not article.query_group:
        article.query_group = source.query_group
    if not article.query_used:
        article.query_used = source.query_used


def _debug_rejection_reason(article: Article, selected_urls: set[str]) -> str:
    if article.url in selected_urls:
        return ""
    return article.rejection_reason or "deduped_or_not_selected"
