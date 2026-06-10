from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from app.generators.scenarios import generate_deterministic_events, generate_random_events
from app.schemas.events import BaseEvent


def event_to_json_line(event: BaseEvent) -> str:
    return event.model_dump_json()


def write_events(events: Iterable[BaseEvent], output: Path | None = None) -> None:
    lines = [event_to_json_line(event) for event in events]

    if output is None:
        for line in lines:
            print(line)
        return

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate simulated manufacturing quality events.")
    parser.add_argument("--mode", choices=["deterministic", "random"], required=True)
    parser.add_argument("--count", type=int, default=10, help="Number of events to generate in random mode.")
    parser.add_argument("--output", type=Path, help="Optional JSON Lines output file.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be greater than 0")

    if args.mode == "deterministic":
        events = generate_deterministic_events()
    else:
        events = generate_random_events(args.count)

    write_events(events, args.output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
