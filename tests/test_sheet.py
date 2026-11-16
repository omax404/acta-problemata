"""Bank problems -> one-page art-directed sheets (problem + solution, FR + EN)."""
import json
import shutil
from pathlib import Path

import pytest
from pypdf import PdfReader

from acta import sheet

ROOT = Path(__file__).resolve().parents[1]
SLUGS = [json.loads(f.read_text(encoding="utf-8"))["slug"] for f in sorted((ROOT / "bank").glob("*.json"))]
SOL = {"name": "Prénom Nom", "email": "a@b.ma", "phone": "+212 6 00 00 00 00", "link": "linkedin.com/in/x",
       "assumptions": ["Écoulement permanent", "Eau à 20 °C"],
       "steps": ["v = 4Q/(pi D^2) = 1,28 m/s", "Re = vD/nu = 1,34e5", "H = 22,4 m"],
       "result": "H = 22,4 m ; P = 3,59 kW", "recommendation": "Pompe 4 kW avec variateur."}


@pytest.fixture(scope="module")
def repo(tmp_path_factory):
    r = tmp_path_factory.mktemp("sheet")
    for n in ("bank", "templates"):
        shutil.copytree(ROOT / n, r / n)
    return r


@pytest.mark.parametrize("slug", SLUGS)
@pytest.mark.parametrize("lang", ["fr", "en"])
def test_every_problem_is_exactly_one_page(repo, slug, lang):
    p = sheet.load_problem(repo, slug)
    p["lang"] = lang
    out = repo / "out" / f"{slug}-{lang}.pdf"
    sheet.render_sheet(sheet.build_data(p), repo, out)
    assert len(PdfReader(str(out)).pages) == 1


def test_problem_sheet_never_prints_the_answer(repo):
    p = sheet.load_problem(repo, "pompage")
    assert "answer_key" in p
    out = repo / "out" / "noanswer.pdf"
    sheet.render_sheet(sheet.build_data(p), repo, out)
    text = PdfReader(str(out)).pages[0].extract_text()
    assert "22,4" not in text and "3,59" not in text


def test_solution_sheet_carries_author_and_result(repo):
    p = sheet.load_problem(repo, "pompage")
    out = repo / "out" / "sol.pdf"
    sheet.render_sheet(sheet.build_data(p, "solution", SOL), repo, out)
    r = PdfReader(str(out))
    text = r.pages[0].extract_text().replace(" ", "")
    assert len(r.pages) == 1 and "PrénomNom" in text and "22,4" in text and "a@b.ma" in text


def test_unknown_problem_lists_choices(repo):
    with pytest.raises(KeyError, match="pompage"):
        sheet.load_problem(repo, "nope")

@pytest.mark.parametrize("slug", SLUGS)
def test_nothing_is_clipped(repo, slug):
    """The body block clips overflow, so the last question and last formula must still be on the page."""
    p = sheet.load_problem(repo, slug)
    out = repo / "out" / f"clip-{slug}.pdf"
    sheet.render_sheet(sheet.build_data(p), repo, out)
    text = PdfReader(str(out)).pages[0].extract_text().replace(" ", "").replace("\n", "")
    for s in (p["questions"][-1], p["formulas"][-1]):
        probe = s.replace(" ", "")[:10]
        assert probe in text, f"{slug}: {probe!r} missing -> content clipped"