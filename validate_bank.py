#!/usr/bin/env python3
"""Refuses to build if a problem breaks the honesty rules. Run by gen_bank.py and build_archive.py."""
import json, glob, re, sys, pathlib
REQ = ["id","slug","title","sector","sector_code","region","level","status","context","data","questions","formulas","formulas_tex"]
REAL = ["source_url","source_title","source_publisher","accessed","source_note","exercise_note"]
def check(b, name):
    e = []
    for k in REQ:
        if not b.get(k): e.append(f"missing '{k}'")
    if b.get("level") not in (1, 2, 3): e.append("level must be 1, 2 or 3")
    st = b.get("status")
    if st not in ("real", "realistic"): e.append("status must be 'real' or 'realistic'")
    if st == "real":
        for k in REAL:
            if not str(b.get(k, "")).strip(): e.append(f"REAL case without '{k}'")
        if not str(b.get("source_url", "")).startswith("https://") and not str(b.get("source_url", "")).startswith("http://"):
            e.append("REAL case: source_url must be a http(s) link")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(b.get("accessed", ""))): e.append("REAL case: 'accessed' must be YYYY-MM-DD")
    if st == "realistic" and b.get("source_url"): e.append("a 'realistic' problem must not carry a source_url (use status 'real' and fill every source field)")
    return [f"{name}: {m}" for m in e]
def main(root=None):
    root = pathlib.Path(root or pathlib.Path(__file__).parent) / "data" / "bank"; errs = []
    files = sorted(glob.glob(str(root / "*.json")))
    for f in files: errs += check(json.load(open(f, encoding="utf-8")), pathlib.Path(f).name)
    if errs: print("VALIDATION FAILED:\n  " + "\n  ".join(errs)); sys.exit(1)
    print(f"validate_bank: {len(files)} problems OK")
if __name__ == "__main__": main()
