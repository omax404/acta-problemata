#!/usr/bin/env python3
"""Build the public archive into docs/ (GitHub Pages: main /docs): index.html + one full-width page per problem."""
import json, glob, shutil, pathlib, html, sys
import validate_bank
R = pathlib.Path(__file__).parent; D = R / "docs"; (D / "e").mkdir(parents=True, exist_ok=True)
validate_bank.main(R)                       # refuses to build if a "real" case lacks its source
shutil.copytree(R / "assets", D / "assets", dirs_exist_ok=True); (D / ".nojekyll").write_text("")
e = html.escape; pad = lambda n: f"{n:02d}"
bank = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(str(R / "bank" / "*.json")))]
tpl = (R / "problem_template.html").read_text(encoding="utf-8"); items = []
NOTE = {"realistic": "Classe de problèmes typique d'un site industriel. Aucune entreprise n'est désignée et aucun besoin d'une entreprise précise n'est affirmé.",
        "real": "Cas public documenté. Les faits viennent de la source ci-dessous ; les valeurs numériques de l'exercice sont signalées comme telles."}
for i, b in enumerate(bank):
    b.pop("answer_key", None); n = b["id"]; real = b["status"] == "real"
    code = f"AP-BANK-{pad(n)}-MA-{b['sector_code']}-{b['level']}"
    src = ""
    if real:
        src = (f'<div class="src"><b class="mono">Source</b><br><a href="{e(b["source_url"])}" rel="noopener noreferrer" target="_blank">{e(b["source_title"])}</a> · {e(b["source_publisher"])} · '
               f'<span class="mono">consulté le {e(b["accessed"])}</span><br>{e(b["source_note"])}<br><i>{e(b["exercise_note"])}</i></div>')
    prev_, next_ = bank[i - 1], bank[(i + 1) % len(bank)]
    m = {"TITLE": e(b["title"]), "NN": pad(n), "SECTOR": e(b["sector"]), "REGION": e(b["region"]), "STARS": "★" * b["level"] + "☆" * (3 - b["level"]), "CODE": code,
         "STCLASS": "real" if real else "", "STATUS": "Cas public réel" if real else "Problème réaliste", "STATUS_NOTE": e(NOTE[b["status"]]), "SOURCE_BLOCK": src,
         "CONTEXT": e(b["context"]), "ID": str(n),
         "ROWS": "".join(f'<tr><td>{e(a)}</td><td class="s">{e(s)}</td><td class="v">{e(v)}</td></tr>' for a, s, v in b["data"]),
         "QUESTIONS": "".join(f"<li><span>{e(q)}</span></li>" for q in b["questions"]),
         "FORMULAS": "".join(f'<div>$$ {t} $$</div>' for t in b["formulas_tex"]) + '<noscript>' + "".join(f"<p class='mono'>{e(f)}</p>" for f in b["formulas"]) + '</noscript>',
         "PREV": f"{pad(prev_['id'])}.html", "PREV_N": pad(prev_["id"]), "NEXT": f"{pad(next_['id'])}.html", "NEXT_N": pad(next_["id"])}
    page = tpl
    for k, v in m.items(): page = page.replace("{{%s}}" % k, v)
    assert "{{" not in page, "unfilled placeholder"
    (D / "e" / f"{pad(n)}.html").write_text(page, encoding="utf-8")
    items.append(dict(id=n, title=b["title"], sector=b["sector"], region=b["region"], level=b["level"], status=b["status"], code=code))
(D / "index.html").write_text((R / "archive_template.html").read_text(encoding="utf-8").replace("__DATA__", json.dumps(items, ensure_ascii=False)), encoding="utf-8")
print("archive:", len(items), "pages ->", D)
