from __future__ import annotations

from datetime import UTC, datetime

from trosmic_digest_agent.connectors import ManualURLConnector, RSSConnector
from trosmic_digest_agent.dedupe import dedupe_articles
from trosmic_digest_agent.models import AgentConfig, Article, Digest, SourceConfig
from trosmic_digest_agent.scoring import score_articles


def build_digest(config: AgentConfig, date: str | None = None) -> Digest:
    warnings: list[str] = []
    articles: list[Article] = []

    for source in config.sources:
        if not source.enabled:
            continue
        try:
            articles.extend(_connector_for(source).fetch())
        except Exception as exc:  # noqa: BLE001 - keep batch digest resilient per source.
            warnings.append(f"{source.name}: {exc}")

    deduped = dedupe_articles(articles)
    scored = score_articles(deduped, config)
    limited = scored[: config.max_items]
    return Digest(
        title=config.digest_title,
        generated_at=datetime.now(UTC),
        date=date,
        articles=limited,
        warnings=warnings,
    )


def _connector_for(source: SourceConfig):
    if source.type == "rss":
        return RSSConnector(source)
    if source.type in {"manual", "url", "urls"}:
        return ManualURLConnector(source)
    raise ValueError(f"Unsupported source type: {source.type}")
