from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class SourceConfig:
    name: str
    type: str
    url: str | None = None
    urls: list[str] = field(default_factory=list)
    queries: list[str] = field(default_factory=list)
    query_group: str = ""
    query_used: str = ""
    enabled: bool = True
    weight: float = 1.0


@dataclass(slots=True)
class AgentConfig:
    name: str = "Trosmic Digest Agent"
    timezone: str = "UTC"
    digest_title: str = "Trosmic Daily Digest"
    output_dir: str = "digests"
    max_items: int = 12
    summary_sentences: int = 3
    interests: list[str] = field(default_factory=list)
    queries: list[str] = field(default_factory=list)
    sources: list[SourceConfig] = field(default_factory=list)


@dataclass(slots=True)
class Article:
    title: str
    url: str
    source: str
    published_at: datetime | str | None = None
    summary: str = ""
    content: str = ""
    author: str | None = None
    source_domain: str = ""
    connector: str = ""
    query_group: str = ""
    query_used: str = ""
    score: float = 0.0
    matched_interests: list[str] = field(default_factory=list)
    relevance_score: int = 0
    relevance_breakdown: dict[str, int] = field(default_factory=dict)
    source_status: str = "inference"
    affected_pillar: str = ""
    why_it_matters: str = ""
    trosmic_implication: str = ""
    action_item: str = ""
    confidence_level: str = "Low"
    rejection_reason: str = ""
    is_ai_led: bool = False
    primary_topics: list[str] = field(default_factory=list)
    quota_category: str = ""

    def normalized_published_at(self) -> datetime | None:
        if isinstance(self.published_at, datetime):
            return self.published_at
        if isinstance(self.published_at, str):
            value = self.published_at.strip()
            if not value:
                return None
            if value.endswith("Z"):
                value = f"{value[:-1]}+00:00"
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return None
        return None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        published = self.normalized_published_at()
        data["published_at"] = published.isoformat() if published else None
        return data


@dataclass(slots=True)
class Digest:
    title: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    date: str | None = None
    articles: list[Article] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    debug: DigestDebug = field(default_factory=lambda: DigestDebug())

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "generated_at": self.generated_at.isoformat(),
            "date": self.date,
            "articles": [article.to_dict() for article in self.articles],
            "warnings": self.warnings,
            "debug": self.debug.to_dict(),
        }


@dataclass(slots=True)
class DigestDebug:
    pipeline_version: str = ""
    total_stories_fetched: int = 0
    top_30_fetched_titles: list[str] = field(default_factory=list)
    top_fetched_domains: list[dict[str, Any]] = field(default_factory=list)
    fetched_stories: list[dict[str, Any]] = field(default_factory=list)
    generic_ai_vendor_source_count: int = 0
    generic_ai_vendor_source_ratio: float = 0.0
    source_pool_contaminated_with_generic_ai: bool = False
    empty_digest_reason: str = ""
    rejected_generic_ai_or_tech_titles: list[str] = field(default_factory=list)
    rejected_generic_ai_count: int = 0
    rejected_generic_tech_count: int = 0
    rejected_no_trosmic_pillar_count: int = 0
    passing_eligibility_count: int = 0
    final_selected_titles: list[str] = field(default_factory=list)
    selected_scores_and_pillars: list[dict[str, Any]] = field(default_factory=list)
    ai_led_items_selected: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
