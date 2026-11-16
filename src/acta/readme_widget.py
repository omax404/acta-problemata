"""Enhancement 5: streak badge + archive table + monthly domain pie in README."""
from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path

BEGIN, END = "<!-- ACTA:BEGIN -->", "<!-- ACTA:END -->"


def update_readme(repo_root: Path, ledger: dict, today: date, repo_slug: str) -> None:
    month = [h for h in ledger["history"] if h["date"][:7] == today.isoformat()[:7]]
    counts = Counter(h["domain"] for h in month)
    pie = "\n".join(f'  "{d}" : {n}' for d, n in counts.most_common()) or '  "pending" : 1'
    rows = "\n".join(
        f"| {h['date']} | {h['edition']} | {h['domain']} | {h['headline']} "
        f"| [PDF]({h['pdf']}) | [Solution](docs/gazette/{h['solution']}) |"
        for h in reversed(ledger["history"][-14:]))
    badge = (f"![streak](https://img.shields.io/endpoint?url="
             f"https://raw.githubusercontent.com/{repo_slug}/main/badges/streak.json)")
    block = f"""{BEGIN}
{badge} ![editions](https://img.shields.io/badge/editions-{ledger['edition_number']}-8a6d3b)

**Current streak: {ledger['streak']} day(s) · {ledger['edition_number']} editions issued.**

### Recent broadsides
| Date | № | Domain | Headline | Read | Verify |
|---|---|---|---|---|---|
{rows}

### {today.strftime('%B %Y')} — domain focus
```mermaid
pie showData title Editions by domain
{pie}
```
{END}"""
    readme = repo_root / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else "# Acta Problemata\n"
    if BEGIN in text and END in text:
        text = text[:text.index(BEGIN)] + block + text[text.index(END) + len(END):]
    else:
        text += "\n\n" + block + "\n"
    readme.write_text(text, encoding="utf-8")

    badges = repo_root / "badges"
    badges.mkdir(exist_ok=True)
    (badges / "streak.json").write_text(json.dumps(
        {"schemaVersion": 1, "label": "streak",
         "message": f"{ledger['streak']} days", "color": "8a6d3b"}), encoding="utf-8")
