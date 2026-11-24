"""Leaderboard: verified-only, privacy, counts, streaks, page, index link."""
import json
import shutil
from datetime import date
from pathlib import Path

import pytest

from acta import leaderboard as lb
from acta import sheet
from acta.cli import main

ROOT = Path(__file__).resolve().parents[1]
EX = json.loads((ROOT / "solution.example.json").read_text(encoding="utf-8"))


@pytest.fixture
def repo(tmp_path):
    for n in ("data/bank", "templates", "assets"):
        shutil.copytree(ROOT / n, tmp_path / n)
    return tmp_path


def test_clean_handle_drops_emails_and_urls():
    assert lb.clean_handle("youssef-demo") == "youssef-demo"
    assert lb.clean_handle("a@b.ma") == "" and lb.clean_handle("https://x.y") == "" and lb.clean_handle(None) == ""
    assert len(lb.clean_handle("x" * 80)) == 24


def test_streaks():
    d = lambda n: date(2026, 11, n)  # noqa: E731
    assert lb.streaks({d(20), d(21), d(22)}, d(22)) == (3, 3)
    assert lb.streaks({d(20), d(21), d(22)}, d(23)) == (3, 3)          # yesterday still counts
    assert lb.streaks({d(10), d(11), d(20)}, d(22)) == (0, 2)
    assert lb.streaks(set(), d(22)) == (0, 0)


def test_record_has_no_personal_data_and_dedupes_named(repo):
    p = sheet.load_problem(repo, "pompage")
    sol = {**EX, "handle": "youssef-demo"}
    lb.record(repo, p, sol, date(2026, 11, 20))
    lb.record(repo, p, sol, date(2026, 11, 21))                        # same handle+problem: once
    rows = lb.load(repo)
    assert len(rows) == 1 and set(rows[0]) == {"handle", "problem", "domain", "date"}
    blob = json.dumps(rows)
    assert "@" not in blob and EX["name"] not in blob and EX["email"] not in blob


def test_stats_and_page(repo):
    rows = [{"handle": "a", "problem": "pompage", "domain": "Agro", "date": "2026-11-23"},
            {"handle": "a", "problem": "echangeur", "domain": "Agro", "date": "2026-11-24"},
            {"handle": "", "problem": "pompage", "domain": "Agro", "date": "2026-11-24"}]
    s = lb.stats(rows, date(2026, 11, 24))
    assert s["total"] == 3 and s["solvers"] == 1 and s["board"][0]["current"] == 2
    assert s["by_problem"][0] == ("pompage", 2) and s["by_domain"] == [("Agro", 3)]
    page = lb.render_html([{**rows[0], "handle": "<b>x</b>"}], date(2026, 11, 24))
    assert "<b>x</b>" not in page and "&lt;b&gt;" in page


def test_cli_records_only_verified(repo, tmp_path, capsys):
    good = tmp_path / "g.json"
    good.write_text(json.dumps({**EX, "handle": "g"}), encoding="utf-8")
    bad = tmp_path / "b.json"
    bad.write_text(json.dumps({**EX, "handle": "b", "answers": [99.0]}), encoding="utf-8")
    for f in (good, bad):
        assert main(["--root", str(repo), "sheet", "pompage", "--solution", str(f), "--record",
                     "--out", str(tmp_path / "o.pdf")]) == 0
    assert [r["handle"] for r in lb.load(repo)] == ["g"]
    assert main(["--root", str(repo), "leaderboard"]) == 0
    assert "g" in (repo / "docs" / "leaderboard.html").read_text(encoding="utf-8")


def test_empty_state_and_index_links_to_it(repo):
    assert "Aucune solution" in lb.render_html([])
    assert "leaderboard.html" in (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    assert "leaderboard.html" in (ROOT / "landing_template.html").read_text(encoding="utf-8")
