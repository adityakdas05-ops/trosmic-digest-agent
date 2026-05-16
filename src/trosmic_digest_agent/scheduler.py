from __future__ import annotations

import argparse
from datetime import datetime
import time

from trosmic_digest_agent.main import main as run_digest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Trosmic digest once per day.")
    parser.add_argument("--time", default="08:00", help="Local run time in HH:MM format")
    parser.add_argument("--config", help="Path to agent_config.yaml")
    args = parser.parse_args(argv)

    hour, minute = _parse_time(args.time)
    last_run_date: str | None = None
    print(f"Scheduler active. Daily run time: {hour:02d}:{minute:02d}")

    while True:
        now = datetime.now()
        today = now.date().isoformat()
        if now.hour == hour and now.minute == minute and last_run_date != today:
            command = ["--date", today]
            if args.config:
                command.extend(["--config", args.config])
            run_digest(command)
            last_run_date = today
        time.sleep(30)


def _parse_time(value: str) -> tuple[int, int]:
    try:
        hour_text, minute_text = value.split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("time must be HH:MM") from exc
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise argparse.ArgumentTypeError("time must be HH:MM")
    return hour, minute


if __name__ == "__main__":
    raise SystemExit(main())
