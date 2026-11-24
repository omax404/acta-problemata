"""LinkedIn carousel: 5 square slides, caption, fr/en, honesty label, never blocks."""
import json
import shutil
from pathlib import Path

import pytest
from PIL import Image

from acta import carousel
from acta.cli import main

ROOT = Path(__file__).resolve().parents[1]
NAMES = ["slide-1-hook.png", "slide-2-data.png", "slide-3-question.png", "slide-4-hint.png", "slide-5-cta.png"]
EDITION = {
    "edition_number": 7, "date": "2026-01-01", "domain": "Fluids", "accent": "#00b4d8",
    "headline": "Pumping Line Head Loss Exceeds Operating Margin",
    "boundary_conditions": {"Flow rate": "40 m3/h", "Length": "250 m", "Roughness": "0.045 mm"},
    "formula": {"symbolic": "rho * g * H", "unit": "kPa"},
    "challenge_question": "What is the pressure drop across the line? Give it in kPa.",
    "source_line": "Scenario class: original AI-composed industrial problem (x); figures illustrative.",
    "source_url": "", "solution_url": "https://example.github.io/acta/solutions/edition-0007.html",
}


@pytest.fixture(scope="module")
def repo(tmp_path_factory):
    r = tmp_path_factory.mktemp("carousel")
    for n in ("data/bank", "templates", "assets"):
        shutil.copytree(ROOT / n, r / n)
    return r


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_bank_problem_renders_five_square_slides_and_caption(repo, lang):
    out = repo / f"out-{lang}"
    deck = carousel.load_deck(repo, "pompage", lang)
    files = carousel.render_carousel(deck, repo, out)
    assert [f.name for f in files] == NAMES
    for f in files:
        assert Image.open(f).size == (1080, 1080)
    cap = (out / "caption.txt").read_text(encoding="utf-8")
    assert "#" in cap and deck.status_label in cap


def test_language_switches_labels(repo):
    fr = carousel.caption(carousel.load_deck(repo, "pompage", "fr"))
    en = carousel.caption(carousel.load_deck(repo, "pompage", "en"))
    assert "Problème du jour" in fr and "REALISTIC PROBLEM" in en


def test_edition_deck_is_realistic_without_public_source():
    d = carousel.deck_from_edition(EDITION, "en")
    assert d.status_label == "REALISTIC PROBLEM" and d.accent == "#00b4d8" and d.code == "№ 007"


def test_edition_with_public_source_is_labelled_real():
    ed = {**EDITION, "source_url": "https://ntrs.nasa.gov/x", "source_line": "Source: NASA NTRS x (public domain)."}
    assert carousel.deck_from_edition(ed, "en").status_label == "REAL PUBLIC CASE"


def test_hint_never_prints_the_answer(repo):
    d = carousel.load_deck(repo, "pompage", "fr")
    assert "22,4" not in d.hint and "3,59" not in d.hint


def test_today_prefers_the_built_edition(repo):
    import datetime
    (repo / "build").mkdir(exist_ok=True)
    ed = {**EDITION, "date": datetime.datetime.now(datetime.UTC).date().isoformat()}
    (repo / "build" / "edition.json").write_text(json.dumps(ed), encoding="utf-8")
    assert carousel.load_deck(repo, "today").title == EDITION["headline"]
    (repo / "build" / "edition.json").write_text(json.dumps({**ed, "date": "2000-01-01"}), encoding="utf-8")
    assert carousel.load_deck(repo, "today").code.startswith("P")        # stale -> bank rotation


def test_greek_and_long_text_are_fitted_not_clipped(repo):
    d = carousel.load_deck(repo, "pompage", "fr")
    d.question = "Δz ε ν η " + "mot " * 120
    out = repo / "long"
    carousel.render_carousel(d, repo, out)
    assert Image.open(out / "slide-3-question.png").size == (1080, 1080)


def test_cli_ok_and_failure_never_raises(repo, tmp_path, capsys):
    assert main(["--root", str(repo), "carousel", "pompage", "--out", str(tmp_path / "c")]) == 0
    assert (tmp_path / "c" / "caption.txt").exists()
    assert main(["--root", str(repo), "carousel", "nope", "--out", str(tmp_path / "d")]) == 3
    assert "carousel failed" in capsys.readouterr().err
