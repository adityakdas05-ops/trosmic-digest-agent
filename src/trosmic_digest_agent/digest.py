from __future__ import annotations

from datetime import UTC, datetime

from trosmic_digest_agent.dedupe import dedupe_articles
from trosmic_digest_agent.models import AgentConfig, Digest, DigestDebug
from trosmic_digest_agent.pipeline.eligibility import PIPELINE_VERSION
from trosmic_digest_agent.pipeline.fetch import (
    CONTAMINATION_WARNING,
    fetch_articles,
    update_fetched_story_debug,
)
from trosmic_digest_agent.scoring import score_articles


def build_digest(config: AgentConfig, date: str | None = None) -> Digest:
    warnings: list[str] = []
    debug = DigestDebug(pipeline_version=PIPELINE_VERSION)

    articles, all_fetched = fetch_articles(config, debug, warnings)
    if debug.source_pool_contaminated_with_generic_ai:
        warnings.append(CONTAMINATION_WARNING)

    deduped = dedupe_articles(articles)
    limited = score_articles(deduped, config, debug=debug)
    _set_empty_digest_reason(debug, limited)
    update_fetched_story_debug(debug, all_fetched, selected=limited)
    return Digest(
        title=config.digest_title,
        generated_at=datetime.now(UTC),
        date=date,
        articles=limited,
        warnings=warnings,
        debug=debug,
    )


def _set_empty_digest_reason(debug: DigestDebug, selected_count: list[object]) -> None:
    if selected_count:
        return
    if debug.source_pool_contaminated_with_generic_ai:
        debug.empty_digest_reason = "source pool was AI-contaminated"
    elif debug.total_stories_fetched == 0:
        debug.empty_digest_reason = "no sports-first connectors returned results"
    else:
        debug.empty_digest_reason = "eligibility too strict"
