from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from trosmic_digest_agent.models import AgentConfig, SourceConfig
from trosmic_digest_agent.source_policy import is_generic_ai_source_config
from trosmic_digest_agent.trosmic_policy import DEFAULT_TROSMIC_INTERESTS, SPORTS_FIRST_QUERIES

DEFAULT_SOURCE_CATALOG = Path("config/sources.yaml")


def load_dotenv(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip().lstrip("\ufeff")
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_config(path: str | Path | None = None) -> AgentConfig:
    load_dotenv()
    config_path = Path(path or os.environ.get("TROSMIC_CONFIG", "agent_config.yaml"))
    if not config_path.exists():
        return AgentConfig(
            interests=list(DEFAULT_TROSMIC_INTERESTS),
            queries=list(SPORTS_FIRST_QUERIES),
            sources=load_source_catalog(),
        )

    data = _load_yaml(config_path)
    sources = _active_source_universe(_parse_sources(data.get("sources", [])))

    return AgentConfig(
        name=str(data.get("name", "Trosmic Digest Agent")),
        timezone=str(data.get("timezone", "UTC")),
        digest_title=str(data.get("digest_title", "Trosmic Daily Digest")),
        output_dir=str(data.get("output_dir", "digests")),
        max_items=int(data.get("max_items", 12)),
        summary_sentences=int(data.get("summary_sentences", 3)),
        interests=[str(item) for item in data.get("interests", DEFAULT_TROSMIC_INTERESTS)],
        queries=_sports_first_queries(data.get("queries", SPORTS_FIRST_QUERIES)),
        sources=sources,
    )


def load_source_catalog(path: str | Path = DEFAULT_SOURCE_CATALOG) -> list[SourceConfig]:
    catalog_path = Path(path)
    if not catalog_path.exists():
        return []
    return _parse_sources(_load_yaml(catalog_path).get("sources", []))


def _parse_sources(raw_sources: Any) -> list[SourceConfig]:
    return [
        SourceConfig(
            name=str(item.get("name", item.get("url", "Unnamed Source"))),
            type=str(item.get("type", "rss")).lower(),
            url=item.get("url"),
            urls=[str(url) for url in item.get("urls", [])],
            queries=[str(query) for query in item.get("queries", [])],
            query_group=str(item.get("query_group", "")),
            query_used=str(item.get("query_used", "")),
            enabled=_as_bool(item.get("enabled", True)),
            weight=float(item.get("weight", 1.0)),
        )
        for item in raw_sources
        if isinstance(item, dict)
    ]


def _active_source_universe(config_sources: list[SourceConfig]) -> list[SourceConfig]:
    sanitized = [
        source
        for source in config_sources
        if not is_generic_ai_source_config(source)
    ]
    catalog_sources = load_source_catalog()
    has_sports_query_connector = any(
        source.enabled and source.type in {"google_news_search", "news_search", "search"}
        for source in sanitized
    )
    if not sanitized or not has_sports_query_connector:
        sanitized.extend(catalog_sources)
    return sanitized


def _sports_first_queries(raw_queries: Any) -> list[str]:
    configured = [str(query) for query in raw_queries] if isinstance(raw_queries, list) else []
    sports_like = [
        query
        for query in configured
        if any(
            term in query.lower()
            for term in (
                "sport",
                "league",
                "stadium",
                "arena",
                "venue",
                "sponsorship",
                "rights",
                "franchise",
                "kabaddi",
                "ipl",
                "wpl",
                "bcci",
                "ufc",
                "wwe",
                "nba",
                "nfl",
                "fifa",
                "formula 1",
                "fan",
            )
        )
    ]
    merged = [*SPORTS_FIRST_QUERIES, *sports_like]
    return list(dict.fromkeys(merged))


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        return _load_simple_yaml(path)

    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return loaded if isinstance(loaded, dict) else {}


def _load_simple_yaml(path: Path) -> dict[str, Any]:
    """Tiny YAML subset parser for the example config shape.

    This is not a general YAML parser. It supports simple scalars, top-level lists,
    and lists of dictionaries so the agent remains usable without PyYAML.
    """

    root: dict[str, Any] = {}
    current_key: str | None = None
    current_item: dict[str, Any] | None = None
    nested_list_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0 and not line.startswith("-") and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            current_item = None
            nested_list_key = None
            root[current_key] = _parse_scalar(value.strip()) if value.strip() else []
            continue

        if current_key is None:
            continue

        if indent >= 2 and line.startswith("- "):
            value = line[2:].strip()
            if current_item is not None and nested_list_key and indent >= 4:
                current_item.setdefault(nested_list_key, []).append(_parse_scalar(value))
            elif current_key == "sources":
                if ":" in value:
                    key, item_value = value.split(":", 1)
                    current_item = {key.strip(): _parse_scalar(item_value.strip())}
                else:
                    current_item = {}
                root.setdefault(current_key, []).append(current_item)
                nested_list_key = None
            else:
                root.setdefault(current_key, []).append(_parse_scalar(value))
            continue

        if indent >= 4 and current_item is not None and ":" in line:
            key, value = line.split(":", 1)
            nested_list_key = key.strip() if not value.strip() else None
            current_item[key.strip()] = _parse_scalar(value.strip()) if value.strip() else []

    return root


def _parse_scalar(value: str) -> Any:
    if value == "":
        return ""
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value.strip('"').strip("'")


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)
