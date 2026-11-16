"""acta run | preview | check | verify-vault"""
from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from pathlib import Path

from . import pipeline
from .math_guard import verify_formula
from .schemas import LLMCase


def check_answer(user: float, exact: float, sig: int = 3) -> bool:
    """Accept anything correct to `sig` significant figures (half-unit in last place)."""
    if not math.isfinite(user):
        return False
    if exact == 0:
        return abs(user) < 1e-12
    exp = math.floor(math.log10(abs(exact)))
    tol = 0.5 * 10 ** (exp - sig + 1)
    return abs(user - exact) <= max(tol, 1e-12)


def parse_number(text: str) -> float:
    """'1,350' -> 1350 (thousands) but '3,84' -> 3.84 (decimal comma)."""
    v = text.strip().replace(" ", "")
    if v.count(",") == 1 and "." not in v and len(v.rsplit(",", 1)[-1]) == 3:
        v = v.replace(",", "")
    else:
        v = v.replace(",", ".")
    return float(v)


def cmd_sources_check(root: Path) -> int:
    from .sources import check_sources
    rows = check_sources(root)
    print(f"{'id':22} {'mode':10} {'on':3} {'robots':16} {'http':12} links")
    for r in rows:
        on = "yes" if r["enabled"] else "no"
        print(f"{r['id']:22} {r['mode']:10} {on:3} {r['robots']:16} {r['http']:12} {r['links']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser(prog="acta", description="Acta Problemata daily engineering broadside")
    p.add_argument("--root", type=Path, default=Path.cwd())
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="full daily pipeline")
    r.add_argument("--dry-run", action="store_true", help="no delivery, no ledger mutation")
    r.add_argument("--force-vault", action="store_true", help="skip APIs and LLM entirely")
    sub.add_parser("preview", help="compile a vault edition locally (offline)")
    c = sub.add_parser("check", help="verify your computed answer")
    c.add_argument("value")
    c.add_argument("--edition", type=int)
    sub.add_parser("mail-pull", help="save new mail from allowed senders into inbox/")
    sub.add_parser("sources-check", help="probe each registry source (robots, reachability)")
    q = sub.add_parser("request", help="build a PDF from a link and email it")
    q.add_argument("--url", required=True)
    q.add_argument("--email", required=True)
    q.add_argument("--domain")
    q.add_argument("--no-send", action="store_true")
    s = sub.add_parser("sheet", help="render a bank problem (or your solution) as a one-page PDF")
    s.add_argument("problem", help="bank slug or id")
    s.add_argument("--solution", type=Path, help="JSON with name, email, steps, result ... -> solution sheet")
    s.add_argument("--lang", choices=["fr", "en"])
    s.add_argument("--out", type=Path)
    sub.add_parser("verify-vault", help="validate every vault case through the math guard")
    a = p.parse_args(argv)
    root = a.root

    if a.cmd in ("run", "preview"):
        s = pipeline.run(root, dry_run=(a.cmd == "preview" or a.dry_run),
                         force_vault=(a.cmd == "preview" or a.force_vault))
        print(json.dumps(s, indent=2))
        return 0

    if a.cmd == "sheet":
        from . import sheet
        prob = sheet.load_problem(root, a.problem)
        sol = json.loads(a.solution.read_text(encoding="utf-8")) if a.solution else None
        if a.lang:
            prob["lang"] = a.lang
        mode = "solution" if sol else "problem"
        data = sheet.build_data(prob, mode, sol)
        out = a.out or root / "build" / f"{data['code']}.pdf"
        sheet.render_sheet(data, root, out)
        print(out)
        return 0
    if a.cmd == "request":
        from .request import RequestError, build_request
        try:
            print(json.dumps(build_request(root, a.url, a.email, a.domain, not a.no_send), indent=2))
        except RequestError as exc:
            print(f"refused: {exc}", file=sys.stderr)
            return 3
        return 0
    if a.cmd == "mail-pull":
        from .mailbox import pull
        print(f"saved {pull(root)} item(s) into inbox/")
        return 0
    if a.cmd == "sources-check":
        return cmd_sources_check(root)
    if a.cmd == "verify-vault":
        entries = json.loads((root / "data" / "case_vault.json").read_text(encoding="utf-8"))
        for e in entries:
            case = LLMCase.model_validate(e["case"])
            vf = verify_formula(case.formula.symbolic,
                                {v.symbol: v.value for v in case.formula.variables},
                                case.formula.unit)
            print(f"OK {e['id']}: {vf.computed_result:g} {vf.unit}")
        return 0

    # check
    sol_dir = root / "docs" / "gazette" / "solutions"
    f = sol_dir / (f"edition-{a.edition:04d}.json" if a.edition else "latest.json")
    if not f.exists() and not a.edition:
        f = root / "build" / "summary.json"          # preview / dry-run fallback
    if not f.exists():
        print("No solution found. Run `acta preview` or `acta run` first.", file=sys.stderr)
        return 2
    sol = json.loads(f.read_text(encoding="utf-8"))
    try:
        user = parse_number(a.value)
    except ValueError:
        print(f"Cannot parse {a.value!r} as a number.", file=sys.stderr)
        return 2
    if check_answer(user, sol["full_precision"], sol.get("significant_figures", 3)):
        print(f"✓ Correct. Edition №{sol['edition']}: {sol['result']:g} {sol['unit']} (3 s.f.)")
        return 0
    print(f"✗ Not quite. Expected {sol['result']:g} {sol['unit']} (3 s.f.). "
          f"See docs/gazette/solutions/edition-{sol['edition']:04d}.html for the derivation.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
