from __future__ import annotations

from abc import ABC, abstractmethod

from trosmic_digest_agent.models import Article, SourceConfig


class Connector(ABC):
    def __init__(self, source: SourceConfig, timeout: float = 15.0) -> None:
        self.source = source
        self.timeout = timeout

    @abstractmethod
    def fetch(self) -> list[Article]:
        """Fetch articles from the configured source."""
