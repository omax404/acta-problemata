#!/usr/bin/env python3
"""Generates data/bank/*.json by loading problem modules from problems/ package.
Every problem has a solve() and render() method ensuring outputs stay in sync."""
import glob
import importlib
import pathlib
import sys
from problems.common import save_problem

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "data" / "bank"
OUT.mkdir(parents=True, exist_ok=True)

# Discover and load all problem modules in problems/
module_files = sorted(glob.glob(str(ROOT / "problems" / "p[0-9][0-9]_*.py")))
if not module_files:
    print("Error: No problem modules found in problems/")
    sys.exit(1)

# Clean existing bank json files
for f in OUT.glob("*.json"):
    f.unlink()

print(f"Generating problem bank from {len(module_files)} modules...")
for idx, mod_file in enumerate(module_files, 1):
    mod_path = pathlib.Path(mod_file)
    mod_name = f"problems.{mod_path.stem}"
    mod = importlib.import_module(mod_name)

    meta = getattr(mod, "META")
    inputs = getattr(mod, "INPUTS")
    solve_fn = getattr(mod, "solve")
    render_fn = getattr(mod, "render")

    results = solve_fn(inputs)
    rendered = render_fn(inputs, results)

    problem_data = {
        "id": idx,
        "slug": meta["slug"],
        "title": meta["title"],
        "sector": meta["sector"],
        "sector_code": meta["sector_code"],
        "region": meta["region"],
        "level": meta["level"],
        "status": meta["status"],
        "source_url": meta.get("source_url", ""),
        "lang": meta.get("lang", "fr"),
        "context": rendered["context"],
        "data": rendered["data"],
        "questions": rendered["questions"],
        "formulas": rendered["formulas"],
        "formulas_tex": rendered["formulas_tex"],
        "answer_key": rendered["answer_key"],
        "results": results,
    }

    # Optional fields for real cases or notes
    for opt_k in [
        "source_title",
        "source_publisher",
        "accessed",
        "source_note",
        "exercise_note",
        "verified_by_human",
    ]:
        if opt_k in meta:
            problem_data[opt_k] = meta[opt_k]

    save_problem(problem_data, OUT)
    print(f"{idx:02d} {meta['slug']} | {' | '.join(rendered['answer_key'])}")

import validate_bank
validate_bank.main()
