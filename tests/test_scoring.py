from __future__ import annotations

import unittest
from datetime import UTC, datetime

from trosmic_digest_agent.models import AgentConfig, Article, DigestDebug
from trosmic_digest_agent.scoring import score_articles


class ScoringTests(unittest.TestCase):
    def test_scores_string_timestamps_and_trosmic_relevance(self) -> None:
        article = Article(
            title="IPL media rights renewal drives new OTT sponsorship packages",
            url="https://example.com",
            source="SportsBusiness",
            published_at="2026-05-16T06:00:00+00:00",
            summary=(
                "The league is exploring streaming rights, sponsor inventory, fan data, "
                "and franchise valuation upside in India."
            ),
        )
        config = AgentConfig(interests=["IPL", "sports media rights", "fan data"])

        scored = score_articles(
            [article],
            config,
            now=datetime(2026, 5, 16, 12, 0, tzinfo=UTC),
        )

        self.assertGreaterEqual(scored[0].relevance_score, 14)
        self.assertEqual(scored[0].matched_interests, ["IPL", "sports media rights", "fan data"])
        self.assertIn("media rights / OTT", scored[0].affected_pillar)

    def test_excludes_generic_ai_news(self) -> None:
        article = Article(
            title="AI coding startup launches new developer tool",
            url="https://example.com/ai",
            source="Example",
            summary="The startup released a generic product for software developers.",
        )
        scored = score_articles([article], AgentConfig(interests=["sports AI"]))

        self.assertEqual(scored, [])

    def test_caps_ai_led_items_at_one(self) -> None:
        articles = [
            Article(
                title="Sports AI broadcast production platform signs league deal",
                url="https://example.com/ai-sports-1",
                source="SportsBusiness",
                summary=(
                    "The deal covers fan analytics, sponsorship analytics, media rights "
                    "packaging, and venue operations for a sports league."
                ),
            ),
            Article(
                title="Sports AI fan analytics tool expands across stadium operations",
                url="https://example.com/ai-sports-2",
                source="SportsBusiness",
                summary=(
                    "The product supports broadcast production, fan data, sponsors, "
                    "and venue operations for professional sports teams."
                ),
            ),
            Article(
                title="UFC TKO media rights sponsorship deal expands live event revenue",
                url="https://example.com/tko",
                source="SportsBusiness",
                summary=(
                    "The combat sports company is packaging streaming rights, brand "
                    "partnerships, live entertainment, and franchise economics."
                ),
            ),
        ]
        debug = DigestDebug()

        scored = score_articles(articles, AgentConfig(), debug=debug)

        self.assertEqual(sum(article.is_ai_led for article in scored), 1)
        self.assertEqual(debug.ai_led_items_selected, 1)
        self.assertTrue(
            any("UFC TKO media rights sponsorship deal" in article.title for article in scored)
        )


if __name__ == "__main__":
    unittest.main()
