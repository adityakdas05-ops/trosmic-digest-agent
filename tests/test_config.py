from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from trosmic_digest_agent.config import load_config


class ConfigTests(unittest.TestCase):
    def test_loads_example_shaped_yaml_without_pyyaml_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "agent_config.yaml"
            path.write_text(
                "\n".join(
                    [
                        "name: Test Agent",
                        "timezone: Asia/Calcutta",
                        "digest_title: Test Digest",
                        "output_dir: out",
                        "max_items: 5",
                        "summary_sentences: 2",
                        "interests:",
                        "  - sports media rights",
                        "sources:",
                        "  - name: Feed",
                        "    type: rss",
                        "    url: https://example.com/feed.xml",
                        "    enabled: true",
                    ]
                ),
                encoding="utf-8",
            )

            config = load_config(path)

        self.assertEqual(config.name, "Test Agent")
        self.assertEqual(config.max_items, 5)
        self.assertEqual(config.interests, ["sports media rights"])
        self.assertEqual(config.sources[0].name, "Feed")
        self.assertTrue(config.sources[0].enabled)


if __name__ == "__main__":
    unittest.main()
