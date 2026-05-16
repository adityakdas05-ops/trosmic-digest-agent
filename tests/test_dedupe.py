from __future__ import annotations

import unittest

from trosmic_digest_agent.dedupe import dedupe_articles
from trosmic_digest_agent.models import Article


class DedupeTests(unittest.TestCase):
    def test_removes_near_duplicate_headlines_with_token_overlap(self) -> None:
        articles = [
            Article(
                title="IPL media rights sponsorship package expands",
                url="https://example.com/a",
                source="A",
            ),
            Article(
                title="New IPL sponsorship package expands media rights",
                url="https://example.com/b",
                source="B",
            ),
        ]

        deduped = dedupe_articles(articles)

        self.assertEqual(len(deduped), 1)

    def test_keeps_distinct_urls_and_titles(self) -> None:
        articles = [
            Article(title="UFC media rights deal renewed", url="https://example.com/a", source="A"),
            Article(
                title="Dubai arena financing plan approved",
                url="https://example.com/b",
                source="B",
            ),
        ]

        self.assertEqual(len(dedupe_articles(articles)), 2)


if __name__ == "__main__":
    unittest.main()
