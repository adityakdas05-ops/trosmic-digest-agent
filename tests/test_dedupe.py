from __future__ import annotations

import unittest

from trosmic_digest_agent.dedupe import dedupe_articles
from trosmic_digest_agent.models import Article


class DedupeTests(unittest.TestCase):
    def test_removes_near_duplicate_headlines_with_token_overlap(self) -> None:
        articles = [
            Article(
                title="OpenAI releases new agent developer tools",
                url="https://example.com/a",
                source="A",
            ),
            Article(
                title="New OpenAI developer tools for agents released",
                url="https://example.com/b",
                source="B",
            ),
        ]

        deduped = dedupe_articles(articles)

        self.assertEqual(len(deduped), 1)

    def test_keeps_distinct_urls_and_titles(self) -> None:
        articles = [
            Article(title="AI coding tool launches", url="https://example.com/a", source="A"),
            Article(
                title="Database release notes published",
                url="https://example.com/b",
                source="B",
            ),
        ]

        self.assertEqual(len(dedupe_articles(articles)), 2)


if __name__ == "__main__":
    unittest.main()
