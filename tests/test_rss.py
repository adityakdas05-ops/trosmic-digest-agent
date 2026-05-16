from __future__ import annotations

import unittest

from trosmic_digest_agent.connectors.rss import parse_rss


class RSSTests(unittest.TestCase):
    def test_parse_rss_items(self) -> None:
        payload = b"""
        <rss><channel>
          <item>
            <title>Example story</title>
            <link>https://example.com/story</link>
            <description>Short summary.</description>
            <pubDate>Sat, 16 May 2026 08:00:00 GMT</pubDate>
          </item>
        </channel></rss>
        """

        articles = parse_rss(payload, "Example Feed")

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, "Example story")
        self.assertEqual(articles[0].source, "Example Feed")
        self.assertIsNotNone(articles[0].normalized_published_at())


if __name__ == "__main__":
    unittest.main()
