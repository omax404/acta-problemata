"""Solver submissions: schema check + numeric verification against the bank's computed answer key.

The stamp "VERIFIED by math_guard" is earned only when every number the solver declares in `answers`
matches a value computed by gen_bank.py (within a relative tolerance). Nothing here trusts the solver's prose.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .math_guard import within_tolerance

REQUIRED = ("name", "steps", "result")      # `answers` optional: without it the sheet is unverified
DEFAULT_TOL = 0.01          # 1 % relative: tolerates rounding, not method errors

_NUM = re.compile(r"-?\d{1,3}(?:[   ]\d{3})+(?:[.,]\d+)?|-?\d+(?:[.,]\d+)?")


class SolutionError(ValueError):
    """Raised when a solution JSON is unusable (bad JSON, missing or malformed fields)."""


def parse_number(text: str) -> float:
    """'134 198' -> 134198 ; '0,0194' -> 0.0194 ; '22.4' -> 22.4."""
    return float(re.sub(r"[   ]", "", text).replace(",", "."))


def expected_numbers(problem: dict) -> list[float]:
    """Numbers computed by gen_bank, read from answer_key lines (after '=' when the line has one)."""
    out: list[float] = []
    for line in problem.get("answer_key", []):
        segs = [seg.split("=", 1)[1] for seg in line.split(";") if "=" in seg]
        if segs:                                  # first number after each "=" only
            out += [parse_number(m[0]) for m in map(_NUM.findall, segs) if m]
        else:
            out += [parse_number(m) for m in _NUM.findall(line)]
    return out


def load_solution(path: Path) -> dict:
    try:
        sol = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SolutionError(f"cannot read solution JSON: {exc}") from exc
    return validate(sol)


def validate(sol: dict) -> dict:
    if not isinstance(sol, dict):
        raise SolutionError("solution JSON must be an object")
    missing = [k for k in REQUIRED if k not in sol or sol[k] in ("", [], None)]
    if missing:
        raise SolutionError(f"missing required field(s): {', '.join(missing)}")
    if not isinstance(sol["steps"], list) or not all(isinstance(x, str) for x in sol["steps"]):
        raise SolutionError("`steps` must be a list of strings")
    ans = sol.get("answers") or []
    ans = [ans] if isinstance(ans, (int, float, str)) and not isinstance(ans, bool) else ans
    try:
        sol["answers"] = [parse_number(a) if isinstance(a, str) else float(a) for a in ans]
    except (TypeError, ValueError) as exc:
        raise SolutionError("`answers` must be numbers (or numeric strings)") from exc
    return sol


@dataclass
class Verdict:
    status: str                                   # verified | mismatch | unchecked
    matched: list[float] = field(default_factory=list)
    unmatched: list[float] = field(default_factory=list)
    tol: float = DEFAULT_TOL

    @property
    def verified(self) -> bool:
        return self.status == "verified"

    @property
    def detail(self) -> str:
        n, total = len(self.matched), len(self.matched) + len(self.unmatched)
        if not total:
            return "no numeric answers declared"
        return f"{n}/{total} answers within {self.tol:.0%}"


def verify(problem: dict, sol: dict, tol: float = DEFAULT_TOL) -> Verdict:
    """Every declared answer must match some computed value; any miss means no stamp."""
    if not sol["answers"]:
        return Verdict("unchecked", tol=tol)
    exp = expected_numbers(problem)
    matched, unmatched = [], []
    for a in sol["answers"]:
        (matched if any(within_tolerance(a, e, tol) for e in exp) else unmatched).append(a)
    return Verdict("verified" if matched and not unmatched else "mismatch", matched, unmatched, tol)
