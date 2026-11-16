import json
import shutil
from datetime import date
from pathlib import Path

import pytest

from acta import ingest, pipeline, sources, synthesize
from acta.schemas import LLMCase

ROOT = Path(__file__).resolve().parents[1]
TODAY = date(2026, 11, 15)
LONG = "The water header between the tank and the extruders loses head. " * 12


@pytest.fixture
def repo(tmp_path):
    for name in ("templates", "data"):
        shutil.copytree(ROOT / name, tmp_path / name)
    shutil.copy(ROOT / "config.json", tmp_path / "config.json")
    (tmp_path / "data" / "ledger.json").unlink(missing_ok=True)
    (tmp_path / "inbox").mkdir()
    return tmp_path


class FakeResp:
    def __init__(self, status=200, text="", content=b"", ctype="text/html"):
        self.status_code, self.text, self.headers = status, text, {"content-type": ctype}
        self.content = content or text.encode()

    def iter_content(self, n):
        yield self.content


@pytest.fixture(autouse=True)
def _reset():
    sources._robots.clear()
    sources._last_hit.clear()
    sources.MIN_DELAY = 0


def test_html_to_text_drops_chrome_and_prefers_article():
    html = ("<html><title>T</title><nav>MENU LINKS</nav><script>evil()</script>"
            "<article><h1>Pump failure</h1><p>Real problem text.</p></article><footer>COPYRIGHT</footer></html>")
    title, text = sources.extract_text(html.encode(), "text/html")
    assert "Real problem text." in text and "MENU" not in text and "evil" not in text and "COPYRIGHT" not in text
    assert title == "Pump failure" or title == "T"


def test_pdf_text_extraction(tmp_path):
    import typst
    (tmp_path / "a.typ").write_text("Cement plant kiln fan shaft keyway fatigue crack tolerance h6.")
    typst.compile(str(tmp_path / "a.typ"), output=str(tmp_path / "a.pdf"))
    _, text = sources.extract_text((tmp_path / "a.pdf").read_bytes(), "application/pdf")
    assert "keyway" in text


def test_robots_disallow_blocks_without_fetching_page(monkeypatch):
    calls = []

    def fake_get(url, **kw):
        calls.append(url)
        if url.endswith("/robots.txt"):
            return FakeResp(200, "User-agent: *\nDisallow: /private/")
        return FakeResp(200, "<p>hi</p>")

    monkeypatch.setattr(sources.requests, "get", fake_get)
    with pytest.raises(sources.FetchBlocked):
        sources.polite_get("https://example.org/private/x")
    assert all(c.endswith("/robots.txt") for c in calls)
    assert sources.polite_get("https://example.org/public/x").content


def test_unreachable_or_forbidden_robots_is_treated_as_blocked(monkeypatch):
    monkeypatch.setattr(sources.requests, "get", lambda url, **kw: FakeResp(403))
    with pytest.raises(sources.FetchBlocked):
        sources.polite_get("https://example.org/a")


def test_inbox_files_fifo_with_domain_prefix_and_seen_skip(repo):
    (repo / "inbox" / "Fluids__water-header.txt").write_text(LONG)
    (repo / "inbox" / "b-second.txt").write_text(LONG + " second")
    (repo / "inbox" / "README.md").write_text("ignore me")
    led = {"seen": {}}
    first = ingest.fetch_source("Mechanical", led, TODAY, repo, ["inbox"])
    assert first.case_id == "inbox:Fluids__water-header" and first.domain == "Fluids" and first.origin == "inbox"
    led["seen"]["inbox:Fluids__water-header"] = TODAY.isoformat()
    second = ingest.fetch_source("Mechanical", led, TODAY, repo, ["inbox"])
    assert second.case_id == "inbox:b-second" and second.domain is None


def test_inbox_urls_are_fetched_politely_and_failures_skipped(repo, monkeypatch):
    (repo / "inbox" / "urls.txt").write_text(
        "# comment\nhttps://bad.example/a\nhttps://ok.example/tender | Thermal\n")

    def fake_polite(url, **kw):
        if "bad" in url:
            raise sources.FetchBlocked("nope")
        return sources.Fetched(f"<article><p>{LONG}</p></article>".encode(), "text/html", url)

    monkeypatch.setattr(sources, "polite_get", fake_polite)
    src = ingest.fetch_source("Mechanical", {"seen": {}}, TODAY, repo, ["inbox"])
    assert src.url == "https://ok.example/tender" and src.domain == "Thermal" and src.case_id.startswith("inbox:url-")


def test_listing_adapter_follows_pattern_links(repo, monkeypatch):
    reg = [{"id": "t", "name": "T", "url": "https://t.example", "mode": "listing", "enabled": True,
            "listing_url": "https://t.example/list", "link_pattern": r"/thread/\d+"}]
    (repo / "data" / "sources.json").write_text(json.dumps(reg))
    pages = {"https://t.example/list": '<a href="/thread/1">a</a><a href="/other">b</a>',
             "https://t.example/thread/1": f"<article><p>{LONG}</p></article>"}
    monkeypatch.setattr(sources, "polite_get",
                        lambda url, **kw: sources.Fetched(pages[url].encode(), "text/html", url))
    src = ingest.fetch_source("Fluids", {"seen": {}}, TODAY, repo, ["listing"])
    assert src.url == "https://t.example/thread/1" and src.origin == "web"


def test_disabled_registry_entries_are_never_fetched(repo, monkeypatch):
    monkeypatch.setattr(sources, "polite_get", lambda *a, **k: pytest.fail("must not fetch"))
    assert ingest.fetch_source("Fluids", {"seen": {}}, TODAY, repo, ["listing"]) is None


def test_registry_covers_every_listed_source():
    reg = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    hosts = " ".join(s["url"] for s in reg)
    for h in ("marchespublics.gov.ma", "maroc-business.com", "appeldoffres.ma", "marchespublic360.ma",
              "kerix.net", "telecontact.ma", "kompass.com", "grabcad.com/challenges", "wazokucrowd.com",
              "ninesigma.com", "cadcrowd.com/contests", "taskerplatform.com", "kolabtree.com", "upwork.com",
              "grabcad.com/library", "traceparts.com", "mcmaster.com", "eng-tips.com"):
        assert h in hosts, h
    assert all(s["mode"] in {"listing", "manual", "leads", "reference"} and "note" in s for s in reg)
    assert not any(s["enabled"] for s in reg)          # nothing is on until verified with sources-check


def test_anonymize_rule_in_prompt(monkeypatch):
    seen = {}
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    monkeypatch.setattr(synthesize, "_call_gemini", lambda p, c, t: seen.setdefault("p", p) and "{}")
    with pytest.raises(synthesize.SynthesisError):
        synthesize.synthesize("src", "Fluids", "Intermediate", {}, anonymize=True)
    assert "never name any company" in seen["p"].lower()


def test_end_to_end_inbox_to_edition(repo, monkeypatch):
    (repo / "inbox" / "Fluids__header.txt").write_text(LONG)
    vault = json.loads((repo / "data" / "case_vault.json").read_text(encoding="utf-8"))
    fluid = next(e for e in vault if e["id"] == "vault-fluid-001")
    monkeypatch.setattr(synthesize, "synthesize", lambda *a, **k: LLMCase.model_validate(fluid["case"]))
    cfg = json.loads((repo / "config.json").read_text(encoding="utf-8"))
    cfg["source_order"] = ["inbox"]
    (repo / "config.json").write_text(json.dumps(cfg))
    s = pipeline.run(repo)
    assert s["origin"] == "inbox" and s["pages"] == 1
    led = json.loads((repo / "data" / "ledger.json").read_text(encoding="utf-8"))
    assert "inbox:Fluids__header" in led["seen"]


def _solution_html(repo, url):
    from acta.math_guard import verify_formula
    from acta.pages import write_solution_pages
    vault = json.loads((repo / "data" / "case_vault.json").read_text(encoding="utf-8"))[0]
    case = LLMCase.model_validate(vault["case"])
    vf = verify_formula(case.formula.symbolic, {v.symbol: v.value for v in case.formula.variables},
                        case.formula.unit)
    cfg = json.loads((repo / "config.json").read_text(encoding="utf-8"))
    c = pipeline.Content(case, vault["id"], "inbox", url)
    ed = pipeline.build_edition(c, vf, cfg, edition_no=1, today=TODAY, repo_slug="o/r", solution_url="https://x/s")
    led = {"seen": {}, "history": [], "edition_number": 1, "streak": 1}
    write_solution_pages(repo, ed, vf, led)
    return (repo / "docs" / "gazette" / "solutions" / "edition-0001.html").read_text(encoding="utf-8")


def test_solution_page_links_public_source(repo):
    html = _solution_html(repo, "https://example.org/tender?id=7&x=<b>")
    assert 'href="https://example.org/tender?id=7&amp;x=&lt;b&gt;"' in html


def test_solution_page_refuses_non_http_source_urls(repo):
    assert "javascript:" not in _solution_html(repo, "javascript:alert(1)")
