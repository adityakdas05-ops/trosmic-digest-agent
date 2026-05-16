from __future__ import annotations

from datetime import datetime, timezone
import unittest

from trosmic_digest_agent.models import AgentConfig, Article
from trosmic_digest_agent.scoring import score_articles


class ScoringTests(unittest.TestCase):
    def test_scores_string_timestamps_and_interests(self) -> None:
        article = Article(
            title="AI agents update",
            url="https://example.com",
            source="Example",
            published_at="2026-05-16T06:00:00+00:00",
            summary="Developer tools for AI agents.",
        )
        config = AgentConfig(interests=["AI agents", "developer tools"])

        scored = score_articles(
            [article],
            config,
            now=datetime(2026, 5, 16, 12, 0, tzinfo=timezone.utc),
        )

        self.assertGreater(scored[0].score, 5)
        self.assertEqual(scored[0].matched_interests, ["AI agents", "developer tools"])


if __name__ == "__main__":
    unittest.main()
