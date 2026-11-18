import shutil
from datetime import date
from pathlib import Path

import pytest

from acta import ingest, originality, pipeline
from acta import ledger as L
from acta.pages import write_solution_pages
from acta.schemas import LLMCase

ROOT = Path(__file__).resolve().parents[1]


def _case(**over) -> LLMCase:
    import json
    vault = json.loads((ROOT / "data" / "case_vault.json").read_text(encoding="utf-8"))
    data = vault[0]["case"]
    data.update(over)
    return LLMCase.model_validate(data)


def test_paraphrase_passes_and_copy_fails():
    case = _case()
    src_ok = "A pump skid was commissioned last spring; operators reported vibration near the coupling housing."
    assert originality.check_original(src_ok, case) < originality.RUN
    copied = " ".join(case.narrative.split()[10:30])              # 20 verbatim words
    assert originality.longest_shared_run(copied, case.narrative) >= 20
    with pytest.raises(originality.NotOriginalError):
        originality.check_original("intro words. " + copied + " trailing text.", case)


def test_matching_ignores_case_and_punctuation():
    a = "The  shaft, once misaligned; fails FAST under cyclic bending loads in service."
    b = "the shaft once misaligned fails fast under cyclic bending loads"
    assert originality.longest_shared_run(a, b) >= 10


def test_short_shared_phrases_are_allowed():
    assert originality.longest_shared_run("under cyclic bending loads", "x under cyclic bending loads y") == 4
    assert originality.longest_shared_run("", "anything") == 0


@pytest.fixture
def repo(tmp_path):
    for name in ("templates", "data"):
        shutil.copytree(ROOT / name, tmp_path / name)
    shutil.copy(ROOT / "config.json", tmp_path / "config.json")
    (tmp_path / "data" / "ledger.json").unlink(missing_ok=True)
    return tmp_path


def test_pipeline_falls_back_when_the_source_is_copied(repo, monkeypatch):
    case = _case()
    src_text = "Lead in. " + case.narrative + " Tail."
    doc = ingest.SourceDoc("web:copy", "t", src_text, "web", None, "https://example.org/p")
    monkeypatch.setattr(pipeline.ingest, "fetch_source", lambda *a, **k: doc)
    monkeypatch.setattr(pipeline.synthesize, "synthesize", lambda *a, **k: case)
    import json
    cfg = json.loads((repo / "config.json").read_text(encoding="utf-8"))
    led = {"seen": {}, "history": [], "edition_number": 0}
    got = pipeline.acquire_content(repo, cfg, led, date(2026, 11, 18), force_vault=False)
    assert got.origin in ("bank", "vault")                  # the copied web case was NOT used


def test_pipeline_keeps_an_original_case(repo, monkeypatch):
    case = _case()
    doc = ingest.SourceDoc("web:ok", "t", "Completely different public text about a cooling tower fan. " * 20,
                           "web", None, "https://example.org/p")
    monkeypatch.setattr(pipeline.ingest, "fetch_source", lambda *a, **k: doc)
    monkeypatch.setattr(pipeline.synthesize, "synthesize", lambda *a, **k: case)
    import json
    cfg = json.loads((repo / "config.json").read_text(encoding="utf-8"))
    led = {"seen": {}, "history": [], "edition_number": 0}
    got = pipeline.acquire_content(repo, cfg, led, date(2026, 11, 18), force_vault=False)
    assert got.origin == "web" and got.source_url == "https://example.org/p"


def test_solution_page_links_source_and_legal_notice(repo):
    from acta.math_guard import verify_formula
    case = _case()
    vf = verify_formula(case.formula.symbolic, {v.symbol: v.value for v in case.formula.variables},
                        case.formula.unit)
    ed = {"edition_number": 3, "date": "2026-11-18", "date_display": "18 Nov", "domain": "Fluids",
          "headline": "H", "boundary_conditions": {"a": "1"}, "source_url": "https://example.org/p",
          "formula": {"result_display": "1.00"}}
    write_solution_pages(repo, ed, vf, L.load(repo / "data" / "ledger.json"))
    html = (repo / "docs" / "gazette" / "solutions" / "edition-0003.html").read_text(encoding="utf-8")
    assert 'href="https://example.org/p"' in html and "not affiliated" in html
    assert 'href="../../legal.html"' in html


def test_legal_page_and_takedown_template_exist_and_link_up():
    legal = (ROOT / "docs" / "legal.html").read_text(encoding="utf-8")
    for needle in ("robots.txt", "8 ", "takedown.yml", "non-affiliation", "NTRS"):
        assert needle in legal, needle
    assert (ROOT / ".github" / "ISSUE_TEMPLATE" / "takedown.yml").exists()
    for page in ("index.html", "archive.html"):
        assert 'href="legal.html"' in (ROOT / "docs" / page).read_text(encoding="utf-8")
