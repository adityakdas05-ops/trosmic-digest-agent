from __future__ import annotations

import unittest

from trosmic_digest_agent.models import Article
from trosmic_digest_agent.pipeline.eligibility import (
    PIPELINE_VERSION,
    is_eligible_for_trosmic_digest,
)


class EligibilityTests(unittest.TestCase):
    def test_pipeline_version_is_v3(self) -> None:
        self.assertEqual(PIPELINE_VERSION, "SPORTS_BUSINESS_FIRST_V3")

    def test_generic_ai_model_launch_is_rejected(self) -> None:
        story = Article(
            title="AI model launch promises faster enterprise workflows",
            url="https://example.com/ai-model",
            source="Tech News",
            summary="A foundation model for enterprise AI customers was released.",
        )

        self.assertFalse(is_eligible_for_trosmic_digest(story))

    def test_generic_ai_partnership_is_rejected(self) -> None:
        story = Article(
            title="AI partnership expands cloud AI assistant rollout",
            url="https://example.com/ai-partnership",
            source="Tech News",
            summary="The enterprise AI partnership targets general business workflows.",
        )

        self.assertFalse(is_eligible_for_trosmic_digest(story))

    def test_ai_sports_broadcast_production_story_passes(self) -> None:
        story = Article(
            title="Sports AI broadcast production platform signs league deal",
            url="https://example.com/sports-ai",
            source="SportsBusiness",
            summary=(
                "The sports league will use fan analytics, broadcast production, "
                "sponsorship analytics, and venue operations data."
            ),
        )

        self.assertTrue(is_eligible_for_trosmic_digest(story))

    def test_nba_media_rights_story_passes(self) -> None:
        story = Article(
            title="NBA media rights deal resets franchise valuation expectations",
            url="https://example.com/nba-rights",
            source="Sports Business Journal",
            summary="The league's broadcast and streaming rights package affects team valuation.",
        )

        self.assertTrue(is_eligible_for_trosmic_digest(story))

    def test_stadium_naming_rights_story_passes(self) -> None:
        story = Article(
            title="New stadium naming rights deal expands sponsor inventory",
            url="https://example.com/stadium",
            source="Front Office Sports",
            summary="The venue agreement covers live entertainment, ticketing, and hospitality.",
        )

        self.assertTrue(is_eligible_for_trosmic_digest(story))

    def test_pkl_sponsorship_story_passes(self) -> None:
        story = Article(
            title="PKL sponsorship deal strengthens Pro Kabaddi media package",
            url="https://example.com/pkl",
            source="Sportstar",
            summary="The kabaddi league deal includes brand partnership and viewership rights.",
        )

        self.assertTrue(is_eligible_for_trosmic_digest(story))

    def test_generic_saas_funding_is_rejected(self) -> None:
        story = Article(
            title="SaaS startup funding round backs cloud workflow software",
            url="https://example.com/saas",
            source="Tech News",
            summary="The company raised funding for general enterprise software.",
        )

        self.assertFalse(is_eligible_for_trosmic_digest(story))

    def test_sports_pe_investment_passes(self) -> None:
        story = Article(
            title="Sports private equity investment values club platform",
            url="https://example.com/sports-pe",
            source="Reuters Sports",
            summary="The private equity deal targets franchise economics and league revenue.",
        )

        self.assertTrue(is_eligible_for_trosmic_digest(story))

    def test_gcc_sports_venue_investment_passes(self) -> None:
        story = Article(
            title="Saudi sports venue investment expands live entertainment district",
            url="https://example.com/gcc-venue",
            source="PIF",
            summary="The GCC project includes arena financing, events, and sports tourism.",
        )

        self.assertTrue(is_eligible_for_trosmic_digest(story))


if __name__ == "__main__":
    unittest.main()
