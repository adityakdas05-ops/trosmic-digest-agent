from __future__ import annotations

__all__ = ["main", "run_once"]


def main(argv: list[str] | None = None) -> int:
    from trosmic_digest_agent.scheduler.run_daily import main as run_daily_main

    return run_daily_main(argv)


def run_once(date: str | None = None, config_path: str | None = None) -> int:
    from trosmic_digest_agent.scheduler.run_daily import run_once as run_daily_once

    return run_daily_once(date=date, config_path=config_path)
