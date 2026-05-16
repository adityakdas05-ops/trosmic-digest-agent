from __future__ import annotations

import argparse

from trosmic_digest_agent.config import load_config
from trosmic_digest_agent.digest import build_digest
from trosmic_digest_agent.renderers import render_markdown, write_digest_files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a Trosmic digest.")
    parser.add_argument("--config", help="Path to agent_config.yaml")
    parser.add_argument("--date", help="Digest date label, e.g. 2026-05-16")
    parser.add_argument("--output-dir", help="Directory for generated digest files")
    parser.add_argument("--print", action="store_true", dest="print_digest", help="Print Markdown digest")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    if args.output_dir:
        config.output_dir = args.output_dir

    digest = build_digest(config, date=args.date)
    markdown_path, json_path = write_digest_files(digest, config.output_dir, config.summary_sentences)

    if args.print_digest:
        print(render_markdown(digest, config.summary_sentences))
    else:
        print(f"Wrote {markdown_path}")
        print(f"Wrote {json_path}")
        if digest.warnings:
            print("Warnings:")
            for warning in digest.warnings:
                print(f"- {warning}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
