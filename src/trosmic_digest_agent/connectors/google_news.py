from __future__ import annotations

import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from trosmic_digest_agent.connectors.base import Connector
from trosmic_digest_agent.connectors.rss import parse_rss
from trosmic_digest_agent.models import Article

GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
MAX_RESULTS_PER_QUERY = 12


class GoogleNewsSearchConnector(Connector):
    def fetch(self) -> list[Article]:
        articles: list[Article] = []
        first_error: Exception | None = None
        workers = min(8, max(1, len(self.source.queries)))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self._fetch_query, query): query
                for query in self.source.queries
            }
            for future in as_completed(futures):
                try:
                    articles.extend(future.result())
                except Exception as exc:  # noqa: BLE001 - let other query groups continue.
                    first_error = first_error or exc
        if not articles and first_error:
            raise first_error
        return articles

    def _fetch_query(self, query: str) -> list[Article]:
        url = GOOGLE_NEWS_RSS_URL.format(query=quote_plus(query))
        payload = _read_url(url, timeout_seconds=min(self.timeout, 5.0))
        return parse_rss(
            payload,
            source_name=self.source.name,
            connector="google_news_search",
            query_group=self.source.query_group,
            query_used=query,
        )[:MAX_RESULTS_PER_QUERY]


def _read_url(url: str, timeout_seconds: float) -> bytes:
    try:
        completed = subprocess.run(
            [
                "curl",
                "-L",
                "--silent",
                "--show-error",
                "--max-time",
                str(int(timeout_seconds)),
                "-A",
                "trosmic-digest-agent/0.1",
                url,
            ],
            capture_output=True,
            check=True,
            timeout=timeout_seconds + 2,
        )
        return completed.stdout
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        request = Request(
            url,
            headers={"User-Agent": "trosmic-digest-agent/0.1"},
        )
        with urlopen(request, timeout=timeout_seconds) as response:
            return response.read()
