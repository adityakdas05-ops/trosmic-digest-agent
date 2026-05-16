from __future__ import annotations

import unittest

from trosmic_digest_agent.config import load_source_catalog
from trosmic_digest_agent.models import AgentConfig, Article, DigestDebug
from trosmic_digest_agent.pipeline.fetch import update_fetched_story_debug
from trosmic_digest_agent.source_policy import (
    is_hard_blocked_generic_ai_source,
    normalize_domain,
)


class SourcePolicyTests(unittest.TestCase):
    def test_source_catalog_is_sports_query_only(self) -> None:
        sources = load_source_catalog()

        self.assertGreaterEqual(len(sources), 8)
        self.assertTrue(all(source.type == "google_news_search" for source in sources))
        self.assertTrue(all(source.queries for source in sources))

    def test_openai_domain_is_blocked_without_sports_relevance(self) -> None:
        article = Article(
            title="OpenAI launches enterprise AI coding workflow",
            url="https://openai.com/blog/product",
            source="OpenAI",
            source_domain="openai.com",
        )

        self.assertTrue(is_hard_blocked_generic_ai_source(article))

    def test_openai_domain_can_pass_only_with_explicit_sports_relevance(self) -> None:
        article = Article(
            title="OpenAI supports sports broadcast production analytics",
            url="https://openai.com/blog/sports",
            source="OpenAI",
            source_domain="openai.com",
            summary="The deployment covers fan analytics for a sports league.",
        )

        self.assertFalse(is_hard_blocked_generic_ai_source(article))

    def test_debug_story_rows_include_source_fields(self) -> None:
        debug = DigestDebug()
        article = Article(
            title="NBA media rights deal resets valuation",
            url="https://sportsbusinessjournal.com/story",
            source="Sports Business Journal",
            source_domain=normalize_domain("https://www.sportsbusinessjournal.com/story"),
            connector="google_news_search",
            query_group="media_rights",
            query_used="latest sports media rights deal",
        )

        update_fetched_story_debug(debug, [article], selected=[article])

        self.assertEqual(debug.fetched_stories[0]["source_domain"], "sportsbusinessjournal.com")
        self.assertEqual(debug.fetched_stories[0]["connector"], "google_news_search")
        self.assertEqual(debug.fetched_stories[0]["query_group"], "media_rights")
        self.assertEqual(debug.fetched_stories[0]["selected_or_rejected"], "selected")

    def test_default_config_loads_sports_source_catalog(self) -> None:
        config = AgentConfig(sources=load_source_catalog())

        self.assertTrue(any(source.query_group == "india_sports" for source in config.sources))


if __name__ == "__main__":
    unittest.main()
