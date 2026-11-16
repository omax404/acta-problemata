"""Enhancement 2: static GitHub Pages solution gateway (QR target).
Zero JS dependencies; derivation is generated deterministically from SymPy.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

from .math_guard import VerifiedFormula

_CSS = """body{font-family:Georgia,'Times New Roman',serif;background:#f7f3ea;color:#1c1a17;
max-width:720px;margin:2rem auto;padding:0 1rem;line-height:1.55}
h1{font-size:1.5rem;border-bottom:3px double #1c1a17;padding-bottom:.4rem}
code,pre{font-family:'Courier New',monospace;background:#efe9db}
pre{padding:.8rem;overflow-x:auto;border:1px solid #c9c0ab}
table{border-collapse:collapse;width:100%}td,th{border:1px solid #c9c0ab;padding:.3rem .6rem;text-align:left}
.meta{font-style:italic;color:#5a5346}.ans{font-size:1.2rem;font-weight:bold}"""


def write_solution_pages(repo_root: Path, edition: dict, vf: VerifiedFormula, ledger: dict) -> None:
    sol = repo_root / "docs" / "gazette" / "solutions"
    sol.mkdir(parents=True, exist_ok=True)
    n = edition["edition_number"]
    slug = f"edition-{n:04d}"
    e = html.escape
    src = edition.get("source_url", "")
    source_html = (
        f'<p class="meta">Original public source: <a href="{e(src)}" rel="noopener nofollow">{e(src)}</a></p>'
        if src.startswith(("http://", "https://")) else "")

    rows = "".join(f"<tr><td>{e(k)}</td><td><code>{e(v)}</code></td></tr>"
                   for k, v in edition["boundary_conditions"].items())
    steps = "".join(f"<tr><td><code>{e(s)}</code></td><td><code>{v:g}</code></td></tr>"
                    for s, v in vf.variables.items())
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Acta Problemata №{n} — Solution</title><style>{_CSS}</style></head><body>
<h1>№{n} — {e(edition['headline'])}</h1>
<p class="meta">{e(edition['date_display'])} · {e(edition['domain'])} · verified by SymPy</p>
{source_html}
<h2>1 · Governing equation</h2><pre>{e(vf.symbolic)}</pre>
<h2>2 · Boundary conditions</h2><table><tr><th>Quantity</th><th>Value</th></tr>{rows}</table>
<h2>3 · Substitution</h2><table><tr><th>Symbol</th><th>SI value</th></tr>{steps}</table>
<pre>{e(vf.substituted)}</pre>
<h2>4 · Evaluation</h2>
<p>Full precision: <code>{vf.full_precision:.10g} {e(vf.unit)}</code></p>
<p class="ans">Answer (3 s.f.): {e(edition['formula']['result_display'])} {e(vf.unit)}</p>
<h2>5 · Reproduce it yourself</h2><pre id="snip">{e(vf.sympy_snippet)}</pre>
<button onclick="navigator.clipboard.writeText(
document.getElementById('snip').textContent)">Copy SymPy snippet</button>
<p><a href="../archive/acta-{n:04d}.pdf">⬇ Today's broadside (PDF)</a> ·
<a href="../index.html">Archive</a></p>
<p class="meta">Check your own answer in a terminal: <code>acta check &lt;value&gt; --edition {n}</code></p>
</body></html>"""
    (sol / f"{slug}.html").write_text(page, encoding="utf-8")

    payload = {"edition": n, "date": edition["date"], "unit": vf.unit,
               "result": vf.computed_result, "full_precision": vf.full_precision,
               "symbolic": vf.symbolic, "variables": vf.variables,
               "significant_figures": 3}
    (sol / f"{slug}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (sol / "latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    items = "".join(
        f"<li>{h['date']} — <a href='archive/{h['pdf'].split('/')[-1]}'>№{h['edition']}</a> "
        f"<b>{e(h['headline'])}</b> <i>({e(h['domain'])})</i> "
        f"· <a href='solutions/edition-{h['edition']:04d}.html'>solution</a></li>"
        for h in reversed(ledger["history"][-60:]))
    (repo_root / "docs" / "gazette" / "index.html").write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>Acta Problemata — Archive</title>"
        f"<style>{_CSS}</style></head><body><h1>Acta Problemata — Archive</h1>"
        f"<p class='meta'>{ledger['streak']}-day streak · {ledger['edition_number']} editions</p>"
        f"<ul>{items}</ul></body></html>", encoding="utf-8")
