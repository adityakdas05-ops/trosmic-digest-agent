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
                    title="Story",
                    url="https://example.com/story",
                    source="Example",
                    summary="A useful summary.",
                    score=3.5,
                )
            ],
        )

        markdown = render_markdown(digest)

        self.assertIn("# Daily", markdown)
        self.assertIn("[Story](https://example.com/story)", markdown)
        self.assertIn("A useful summary.", markdown)


if __name__ == "__main__":
    unittest.main()
