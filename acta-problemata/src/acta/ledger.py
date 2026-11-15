"""Git-backed state: edition counter, streak, 180-day dedupe window (FR-01.3).
Same-day re-runs are idempotent: they reuse the edition number and replace
the day's history entry instead of double-counting the streak.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

DEDUP_WINDOW_DAYS = 180
DEFAULT = {"edition_number": 0, "streak": 0, "last_run_date": None, "history": [], "seen": {}}


def load(path: Path) -> dict:
    if path.exists():
        return {**DEFAULT, **json.loads(path.read_text())}
    return json.loads(json.dumps(DEFAULT))


def save(path: Path, ledger: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2) + "\n")


def is_seen(ledger: dict, case_id: str, today: date, window: int = DEDUP_WINDOW_DAYS) -> bool:
    stamp = ledger["seen"].get(case_id)
    return bool(stamp) and (today - date.fromisoformat(stamp)).days < window


def prune(ledger: dict, today: date, window: int = DEDUP_WINDOW_DAYS) -> None:
    ledger["seen"] = {k: v for k, v in ledger["seen"].items()
                      if (today - date.fromisoformat(v)).days < window}


def next_edition(ledger: dict, today: date) -> int:
    if ledger["last_run_date"] == today.isoformat():
        return ledger["edition_number"]
    return ledger["edition_number"] + 1


def record_success(ledger: dict, today: date, case_id: str, entry: dict) -> None:
    iso = today.isoformat()
    if ledger["last_run_date"] == iso:
        pass                                       # idempotent re-run
    elif ledger["last_run_date"] == (today - timedelta(days=1)).isoformat():
        ledger["streak"] += 1
    else:
        ledger["streak"] = 1
    ledger["last_run_date"] = iso
    ledger["edition_number"] = entry["edition"]
    ledger["seen"][case_id] = iso
    ledger["history"] = [h for h in ledger["history"] if h["date"] != iso] + [entry]
    prune(ledger, today)
