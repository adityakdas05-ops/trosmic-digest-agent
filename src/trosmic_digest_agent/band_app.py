from __future__ import annotations

import os

from trosmic_digest_agent.config import load_config, load_dotenv
from trosmic_digest_agent.digest import build_digest
from trosmic_digest_agent.renderers import render_markdown


def generate_digest_text(config_path: str | None = None, date: str | None = None) -> str:
    config = load_config(config_path)
    digest = build_digest(config, date=date)
    return render_markdown(digest, config.summary_sentences)


def main() -> int:
    load_dotenv()
    _require_env("OPENAI_API_KEY")

    try:
        import thenvoi  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SystemExit(
            "Band runtime dependencies are not installed. Run: "
            "uv pip install thenvoi langchain-openai langgraph openai pyyaml"
        ) from exc

    # The exact Band deployment API can vary by installed thenvoi version, so keep
    # the callable digest function importable and fail clearly if no runner exists.
    if hasattr(thenvoi, "run"):
        thenvoi.run(generate_digest_text)
        return 0

    print(generate_digest_text(os.environ.get("TROSMIC_CONFIG")))
    return 0


def _require_env(name: str) -> None:
    if not os.environ.get(name):
        raise SystemExit(f"Missing required environment variable: {name}")


if __name__ == "__main__":
    raise SystemExit(main())
