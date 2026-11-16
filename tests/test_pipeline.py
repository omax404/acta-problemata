import json
import shutil
import time
from datetime import date
from pathlib import Path

import pytest
from pypdf import PdfReader

from acta import ingest, pipeline, synthesize
from acta.cli import main as cli_main
from acta.cli import parse_number
from acta.diagrams import render_diagram
from acta.render import render_edition
from acta.schemas import LLMCase

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo(tmp_path):
    for name in ("templates", "data"):
        shutil.copytree(ROOT / name, tmp_path / name)
    shutil.copy(ROOT / "config.json", tmp_path / "config.json")
    (tmp_path / "data" / "ledger.json").unlink(missing_ok=True)
    return tmp_path


def _edition(**over):
    e = {"edition_number": 7, "date": "2026-11-15", "date_display": "15 November 2026",
         "domain": "Mechanical", "difficulty": "Intermediate", "headline": "Short title here",
         "narrative": "Word " * 140, "boundary_conditions": {f"Quantity {i}": f"{i}.5 m" for i in range(4)},
         "formula": {"symbolic": "P*L/E", "variables": {"P": 1.0}, "computed_result": 1.0,
                     "result_display": "1.00", "unit": "m"},
         "challenge_question": "Compute the result in metres to three significant figures.",
         "diagram_caption": "Fig. 1 - test", "source_line": "Source: test.",
         "repo_slug": "me/acta", "solution_url": "https://example.org/s/7", "reveal_answer": False}
    e.update(over)
    return e


@pytest.mark.parametrize("label,over", [
    ("minimal", {"narrative": "Word " * 120, "boundary_conditions": {f"q{i}": "1 m" for i in range(3)}}),
    ("maximal", {"headline": "A very long engineering headline exceeding all sane widths ok",
                 "narrative": ("Extraordinarily " * 100).strip() + " " + "x " * 50,
                 "boundary_conditions": {f"A rather long boundary condition name {i}": "123456.789 N·m/s²" for i in range(8)},
                 "challenge_question": "Q " * 140,
                 "diagram_caption": "A long caption " * 6}),
    ("reveal", {"reveal_answer": True}),
])
def test_layout_always_one_page(repo, label, over):
    svg = render_diagram("cantilever_point_load", {}, repo / "build" / "d.svg")
    pdf = repo / "out.pdf"
    fit = render_edition(_edition(**over), svg, "https://example.org/s/7", repo, pdf)
    assert fit["pages"] == 1 == len(PdfReader(str(pdf)).pages)


def _vault_llmcase(repo):
    e = json.loads((repo / "data" / "case_vault.json").read_text(encoding="utf-8"))[0]
    return LLMCase.model_validate(e["case"])


def test_math_guard_rejection_falls_back_to_vault(repo, monkeypatch):
    bad = _vault_llmcase(repo)
    bad.formula.symbolic = "undeclared_thing * 2"           # passes pydantic, fails the guard
    monkeypatch.setattr(ingest, "fetch_source", lambda *a, **k: ingest.SourceDoc("ntrs:1", "t", "x" * 400, "ntrs"))
    monkeypatch.setattr(synthesize, "synthesize", lambda *a, **k: bad)
    s = pipeline.run(repo, dry_run=True)
    assert s["origin"] == "vault" and s["pages"] == 1


def test_synthesis_deadline_is_enforced(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    with pytest.raises(synthesize.SynthesisError):
        synthesize.synthesize("src", "Mechanical", "Intermediate", {}, deadline=time.monotonic() - 1)


def test_parse_number():
    assert parse_number("1,350") == 1350 and parse_number("3,84") == 3.84
    assert parse_number("8.10e-4") == 8.10e-4 and parse_number("1 350.5") == 1350.5


def test_preview_then_check_roundtrip(repo, capsys):
    assert cli_main(["--root", str(repo), "preview"]) == 0
    capsys.readouterr()
    assert cli_main(["--root", str(repo), "check", "8.10e-4"]) == 0
    assert cli_main(["--root", str(repo), "check", "9e-4"]) == 1


def test_market_source_prefers_domain_and_is_offline(repo):
    led = {"seen": {}}
    src = ingest.fetch_source("Fluids", led, date(2026, 11, 15), repo, ["market"])
    assert src and src.origin == "market" and "Tuyauterie" in src.title


def test_delivery_failure_never_loses_the_edition(repo, monkeypatch):
    """A configured-but-broken SMTP/printer must not cost us the edition or the streak."""
    from acta import deliver

    def boom(*a, **k):
        raise OSError("smtp down")

    monkeypatch.setattr(deliver, "send_email", boom)
    monkeypatch.setattr(deliver, "send_printer", boom)
    s = pipeline.run(repo, force_vault=True)
    led = json.loads((repo / "data" / "ledger.json").read_text(encoding="utf-8"))
    assert led["streak"] == 1 and led["edition_number"] == 1      # published + recorded
    assert (repo / "docs" / "gazette" / "archive" / "acta-0001.pdf").exists()
    assert len(s["delivery_errors"]) == 2                         # but never silent


def test_compile_error_message_is_surfaced(repo):
    (repo / "templates" / "broadside.typ").write_text('#let d = json("edition.json")\n#d.nope.nope')
    svg = render_diagram("cantilever_point_load", {}, repo / "build" / "d.svg")
    with pytest.raises(RuntimeError, match="nope"):
        render_edition(_edition(), svg, "https://example.org/s/7", repo, repo / "o.pdf")


def test_pdf_has_metadata(repo):
    svg = render_diagram("cantilever_point_load", {}, repo / "build" / "d.svg")
    pdf = repo / "o.pdf"
    render_edition(_edition(), svg, "https://example.org/s/7", repo, pdf)
    meta = PdfReader(str(pdf)).metadata
    assert "Acta Problemata" in (meta.title or "") and "7" in (meta.title or "")


def test_tall_figure_cannot_starve_body_text(repo):
    """Regression: the civil-column diagram (tall) used to force 7.2 pt text and kill the worksheet."""
    import json as _json
    e = [x for x in _json.loads((repo / "data" / "case_vault.json").read_text(encoding="utf-8")) if x["id"] == "vault-civ-001"][0]
    svg = render_diagram(e["case"]["diagram"]["kind"], {}, repo / "build" / "d.svg")
    pdf = repo / "o.pdf"
    render_edition(_edition(), svg, "https://example.org/s/7", repo, pdf)
    text = PdfReader(str(pdf)).pages[0].extract_text()
    assert "WORKINGS" in text.replace(" ", "")                       # the worksheet survived
