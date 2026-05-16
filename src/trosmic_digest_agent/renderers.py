from __future__ import annotations

import json
from pathlib import Path

from trosmic_digest_agent.models import Digest
from trosmic_digest_agent.summarizer import summarize_article


def render_markdown(digest: Digest, summary_sentences: int = 3) -> str:
    lines = [
        f"# {digest.title}",
        "",
        f"Generated: {digest.generated_at.isoformat()}",
    ]
    if digest.date:
        lines.append(f"Digest date: {digest.date}")
    lines.append("")

    if digest.warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in digest.warnings)
        lines.append("")

    if not digest.articles:
        lines.extend(["No articles found.", ""])
        return "\n".join(lines)

    lines.extend(["## Top Items", ""])
    for index, article in enumerate(digest.articles, start=1):
        lines.append(f"### {index}. [{article.title}]({article.url})")
        metadata = [article.source, f"score {article.score:g}"]
        published = article.normalized_published_at()
        if published:
            metadata.append(published.isoformat())
        lines.append(f"_{' | '.join(metadata)}_")
        if article.matched_interests:
            lines.append(f"Interests: {', '.join(article.matched_interests)}")
        summary = summarize_article(article, summary_sentences)
        if summary:
            lines.extend(["", summary])
        lines.append("")

    return "\n".join(lines)


def write_digest_files(digest: Digest, output_dir: str | Path, summary_sentences: int = 3) -> tuple[Path, Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    stem = digest.date or digest.generated_at.date().isoformat()
    markdown_path = directory / f"{stem}.md"
    json_path = directory / f"{stem}.json"
    markdown_path.write_text(render_markdown(digest, summary_sentences), encoding="utf-8")
    json_path.write_text(json.dumps(digest.to_dict(), indent=2), encoding="utf-8")
    return markdown_path, json_path
