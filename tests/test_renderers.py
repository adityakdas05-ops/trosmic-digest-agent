from __future__ import annotations

import unittest

from trosmic_digest_agent.models import Article, Digest
from trosmic_digest_agent.renderers import render_markdown


class RendererTests(unittest.TestCase):
    def test_markdown_contains_articles(self) -> None:
        digest = Digest(
            title="Daily",
            date="2026-05-16",
            articles=[
                Article(
                    title="NBA media rights deal resets franchise valuation expectations",
                    url="https://example.com/story",
                    source="SportsBusiness",
                    summary=(
                        "The league's new streaming and broadcast package is expected to "
                        "support sponsorship, fan data, and franchise economics."
                    ),
                    score=17.5,
                    relevance_score=16,
                    source_status="reported",
                    affected_pillar=(
                        "Media rights and OTT distribution; Franchise economics and "
                        "league governance"
                    ),
                    why_it_matters="Sports rights anchor OTT retention.",
                    trosmic_implication="Use this as a comp for WKCL rights packaging.",
                    action_item=(
                        "Watch: capture rights fee, platform, territory, and ad-sales model."
                    ),
                    confidence_level="High",
                )
            ],
        )

        markdown = render_markdown(digest)

        self.assertIn("# Daily", markdown)
        self.assertIn("## 1. Executive Signal of the Day", markdown)
        self.assertIn("## 2. Top 10 Trosmic-Relevant Developments", markdown)
        self.assertIn(
            "[NBA media rights deal resets franchise valuation expectations]"
            "(https://example.com/story)",
            markdown,
        )
        self.assertIn(
            "Trosmic implication: Use this as a comp for WKCL rights packaging.",
            markdown,
        )
        self.assertIn("## 6. Strategic Op-Ed", markdown)


if __name__ == "__main__":
    unittest.main()
