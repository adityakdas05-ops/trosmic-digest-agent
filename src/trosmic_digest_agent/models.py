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
    score: float = 0.0
    matched_interests: list[str] = field(default_factory=list)

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

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "generated_at": self.generated_at.isoformat(),
            "date": self.date,
            "articles": [article.to_dict() for article in self.articles],
            "warnings": self.warnings,
        }
