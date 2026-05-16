from __future__ import annotations

import argparse
import asyncio
import os
from typing import Any

from trosmic_digest_agent.config import load_config, load_dotenv
from trosmic_digest_agent.digest import build_digest
from trosmic_digest_agent.renderers import render_markdown


def generate_digest_text(config_path: str | None = None, date: str | None = None) -> str:
    config = load_config(config_path)
    digest = build_digest(config, date=date)
    return render_markdown(digest, config.summary_sentences)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Trosmic Band agent.")
    parser.add_argument("--config", help="Path to agent_config.yaml")
    parser.add_argument("--date", help="Digest date label, e.g. 2026-05-16")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Generate one digest locally and exit without connecting to Band.",
    )
    args = parser.parse_args(argv)

    load_dotenv()
    _require_env("OPENAI_API_KEY")

    if args.once:
        print(generate_digest_text(args.config, args.date))
        return 0

    _require_env("BAND_API_KEY")
    _require_env("BAND_AGENT_ID")

    try:
        from thenvoi import Agent  # type: ignore[import-not-found]
        from thenvoi.core.protocols import AgentToolsProtocol  # type: ignore[import-not-found]
        from thenvoi.core.simple_adapter import SimpleAdapter  # type: ignore[import-not-found]
        from thenvoi.core.types import PlatformMessage  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SystemExit(
            "Band runtime dependencies are not installed. Run: "
            'uv pip install "thenvoi-sdk[langgraph]" openai pyyaml'
        ) from exc

    class DigestAdapter(SimpleAdapter[Any]):
        async def on_message(
            self,
            msg: PlatformMessage,
            tools: AgentToolsProtocol,
            history: Any,
            participants_msg: str | None,
            contacts_msg: str | None,
            *,
            is_session_bootstrap: bool,
            room_id: str,
        ) -> None:
            del msg, history, participants_msg, contacts_msg, is_session_bootstrap, room_id
            await tools.send_message(generate_digest_text(args.config, args.date))

    agent = Agent.create(
        adapter=DigestAdapter(),
        agent_id=os.environ["BAND_AGENT_ID"],
        api_key=os.environ["BAND_API_KEY"],
        ws_url=os.environ.get("BAND_WS_URL", "wss://app.thenvoi.com/api/v1/socket/websocket"),
        rest_url=os.environ.get("BAND_REST_URL", "https://app.thenvoi.com"),
    )
    asyncio.run(agent.run())
    return 0


def _require_env(name: str) -> None:
    if not os.environ.get(name):
        raise SystemExit(f"Missing required environment variable: {name}")


if __name__ == "__main__":
    raise SystemExit(main())
