from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from trosmic_digest_agent.config import load_config
from trosmic_digest_agent.delivery.email import (
    MISSING_SMTP_SETTINGS_MESSAGE,
    MissingSMTPSettingsError,
    send_digest_email,
)
from trosmic_digest_agent.digest import build_digest
from trosmic_digest_agent.renderers import write_digest_files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate and email the Trosmic daily digest.")
    parser.add_argument("--config", help="Path to agent_config.yaml")
    parser.add_argument("--date", help="Digest date label, e.g. 2026-05-16")
    parser.add_argument("--output-dir", help="Directory for generated digest files")
    args = parser.parse_args(argv)

    digest_date = args.date or datetime.now().date().isoformat()
    print(f"Starting daily email digest for {digest_date}.")

    config = load_config(args.config)
    if args.output_dir:
        config.output_dir = args.output_dir

    digest = build_digest(config, date=digest_date)
    write_digest_files(digest, config.output_dir, config.summary_sentences)
    markdown_path, json_path, debug_path = find_digest_files(config.output_dir, digest_date)

    if not markdown_path:
        print(f"No Markdown digest found for {digest_date} in {config.output_dir}.")
        return 1

    print(f"Generated digest: {markdown_path}")
    if json_path:
        print(f"Found JSON digest: {json_path}")
    if debug_path:
        print(f"Found debug JSON: {debug_path}")

    try:
        send_digest_email(
            markdown_path,
            json_path,
            debug_path,
            digest_date=digest_date,
        )
    except MissingSMTPSettingsError as exc:
        print(str(exc) or MISSING_SMTP_SETTINGS_MESSAGE)
        return 1

    print(f"Sent Trosmic Daily Intelligence Digest for {digest_date}.")
    return 0


def find_digest_files(
    output_dir: str | Path,
    digest_date: str,
) -> tuple[Path | None, Path | None, Path | None]:
    directory = Path(output_dir)
    markdown_path = directory / f"{digest_date}.md"
    json_path = directory / f"{digest_date}.json"
    debug_path = directory / f"debug-{digest_date}.json"
    return (
        markdown_path if markdown_path.exists() else None,
        json_path if json_path.exists() else None,
        debug_path if debug_path.exists() else None,
    )


if __name__ == "__main__":
    raise SystemExit(main())
