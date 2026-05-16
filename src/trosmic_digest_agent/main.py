from __future__ import annotations

import argparse
import sys

from trosmic_digest_agent.config import load_config
from trosmic_digest_agent.digest import build_digest
from trosmic_digest_agent.models import Digest
from trosmic_digest_agent.pipeline.eligibility import PIPELINE_VERSION
from trosmic_digest_agent.renderers import render_markdown, write_digest_files


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Generate a Trosmic digest.")
    parser.add_argument("--config", help="Path to agent_config.yaml")
    parser.add_argument("--date", help="Digest date label, e.g. 2026-05-16")
    parser.add_argument("--output-dir", help="Directory for generated digest files")
    parser.add_argument(
        "--print",
        action="store_true",
        dest="print_digest",
        help="Print Markdown digest",
    )
    args = parser.parse_args(argv)

    print(f"PIPELINE_VERSION={PIPELINE_VERSION}")
    config = load_config(args.config)
    if args.output_dir:
        config.output_dir = args.output_dir

    digest = build_digest(config, date=args.date)
    markdown_path, json_path, debug_path = write_digest_files(
        digest,
        config.output_dir,
        config.summary_sentences,
    )

    if args.print_digest:
        print(render_markdown(digest, config.summary_sentences))
    else:
        print(f"Wrote {markdown_path}")
        print(f"Wrote {json_path}")
        print(f"Wrote {debug_path}")
        if digest.warnings:
            print("Warnings:")
            for warning in digest.warnings:
                print(f"- {warning}")
    print_debug_summary(digest)

    return 0


def print_debug_summary(digest: Digest) -> None:
    debug = digest.debug
    print("Debug:")
    print(f"PIPELINE_VERSION={debug.pipeline_version}")
    print(f"1. Total stories fetched: {debug.total_stories_fetched}")
    print("Top fetched domains:")
    if debug.top_fetched_domains:
        for item in debug.top_fetched_domains:
            print(f"{item['domain']}: {item['count']}")
    else:
        print("None")
    if debug.source_pool_contaminated_with_generic_ai:
        print("WARNING: SOURCE_POOL_CONTAMINATED_WITH_GENERIC_AI")
    print("2. Top 30 fetched story titles:")
    if debug.top_30_fetched_titles:
        for index, title in enumerate(debug.top_30_fetched_titles, start=1):
            print(f"   {index}. {title}")
    else:
        print("   None")
    print("3. Stories rejected for being generic AI/tech:")
    if debug.rejected_generic_ai_or_tech_titles:
        for title in debug.rejected_generic_ai_or_tech_titles:
            print(f"   - {title}")
    else:
        print("   None")
    print(f"   Rejected generic AI: {debug.rejected_generic_ai_count}")
    print(f"   Rejected generic tech: {debug.rejected_generic_tech_count}")
    print(f"   No Trosmic pillar rejected: {debug.rejected_no_trosmic_pillar_count}")
    print(f"   Eligible stories: {debug.passing_eligibility_count}")
    print("4. Final selected Top 10 titles:")
    if debug.final_selected_titles:
        for index, title in enumerate(debug.final_selected_titles, start=1):
            print(f"   {index}. {title}")
    else:
        print("   None")
    print("5. Relevance score and pillar for each selected item:")
    if debug.selected_scores_and_pillars:
        for item in debug.selected_scores_and_pillars:
            print(f"   - {item['relevance_score']}/21 | {item['pillar']} | {item['title']}")
    else:
        print("   None")
    print(f"6. AI-led items selected: {debug.ai_led_items_selected}")
    if debug.empty_digest_reason:
        print(f"7. Empty digest reason: {debug.empty_digest_reason}")


if __name__ == "__main__":
    raise SystemExit(main())
