from __future__ import annotations

import re
from html import unescape
from urllib.request import Request, urlopen

from trosmic_digest_agent.connectors.base import Connector
from trosmic_digest_agent.models import Article
from trosmic_digest_agent.source_policy import normalize_domain


class ManualURLConnector(Connector):
    def fetch(self) -> list[Article]:
        articles: list[Article] = []
        for url in self.source.urls:
            article = self.fetch_one(url)
            if article:
                articles.append(article)
        return articles

    def fetch_one(self, url: str) -> Article | None:
        request = Request(url, headers={"User-Agent": "trosmic-digest-agent/0.1"})
        with urlopen(request, timeout=self.timeout) as response:
            payload = response.read().decode("utf-8", errors="replace")
        title = extract_title(payload) or url
        summary = extract_description(payload)
        return Article(
            title=title,
            url=url,
            source=self.source.name,
            summary=summary,
            source_domain=normalize_domain(url),
            connector="manual",
            query_group=self.source.query_group,
            query_used=self.source.query_used,
        )


def extract_title(html: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return _clean(match.group(1))


def extract_description(html: str) -> str:
    patterns = [
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']',
        r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']',
        r'<meta\s+content=["\'](.*?)["\']\s+property=["\']og:description["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return _clean(match.group(1))
    return ""


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()
