"""On-demand request: link + email in, private PDF out."""
import json
import shutil
import socket
from pathlib import Path

import pytest

from acta import deliver, request, sources, synthesize
from acta.schemas import LLMCase

ROOT = Path(__file__).resolve().parents[1]
LONG = "Boiler feed pump header vibration and cavitation at high suction temperature. " * 12


@pytest.fixture
def repo(tmp_path):
    for name in ("data", "templates"):
        shutil.copytree(ROOT / name, tmp_path / name)
    shutil.copy(ROOT / "config.json", tmp_path / "config.json")
    (tmp_path / "docs").mkdir()
    return tmp_path


def _public(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("93.184.216.34", 443))])


@pytest.mark.parametrize("addr,ok", [("a@b.co", True), ("x.y+z@mail.example.org", True),
                                     ("no-at.example", False), ("a@b", False),
                                     ("a@b.co\nBcc: x@y.zz", False), ("", False)])
def test_email_validation(addr, ok):
    assert request.valid_email(addr) is ok


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://example.org/x", "http://localhost/x",
                                 "http://127.0.0.1/x", "http://10.0.0.5/x",
                                 "http://169.254.169.254/latest", "https://u:p@example.org/"])
def test_private_or_odd_urls_refused(url):
    assert request.public_http_url(url) is False


def test_public_url_accepted(monkeypatch):
    _public(monkeypatch)
    assert request.public_http_url("https://example.org/page") is True


def test_bad_email_refused_before_any_network(repo, monkeypatch):
    monkeypatch.setattr(sources, "polite_get", lambda *a, **k: pytest.fail("fetched"))
    with pytest.raises(request.RequestError, match="email"):
        request.build_request(repo, "https://example.org", "nope")


def test_short_page_refused(repo, monkeypatch):
    _public(monkeypatch)
    monkeypatch.setattr(sources, "polite_get",
                        lambda *a, **k: sources.Fetched(b"<p>tiny</p>", "text/html", "u"))
    with pytest.raises(request.RequestError, match="too little"):
        request.build_request(repo, "https://example.org", "a@b.co")


def test_end_to_end_pdf_emailed_and_ledger_untouched(repo, monkeypatch):
    _public(monkeypatch)
    monkeypatch.setattr(sources, "polite_get",
                        lambda *a, **k: sources.Fetched(LONG.encode(), "text/plain", "u"))
    vault = json.loads((repo / "data" / "case_vault.json").read_text(encoding="utf-8"))
    case = LLMCase.model_validate(next(e for e in vault if e["id"] == "vault-fluid-001")["case"])
    monkeypatch.setattr(synthesize, "synthesize", lambda *a, **k: case)
    sent = {}
    monkeypatch.setattr(deliver, "send_email",
                        lambda pdf, ed, to=None, **k: sent.update(to=to, size=Path(pdf).stat().st_size) or True)
    out = request.build_request(repo, "https://example.org/p", "reader@example.org", "Fluids")
    assert out["emailed"] and out["pages"] == 1
    assert sent["to"] == "reader@example.org" and sent["size"] > 5000
    assert not (repo / "data" / "ledger.json").exists() or \
        json.loads((repo / "data" / "ledger.json").read_text(encoding="utf-8")).get("history", []) == []