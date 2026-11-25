"""Rotation policy: prefer FR/MA bank, CSB at most 1 day in 3 (configurable), ledger cap for live CSB."""
import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from acta import ingest, rotation

ROOT = Path(__file__).resolve().parents[1]
FR = [{"slug": f"p{i}", "lang": "fr"} for i in range(5)]
EN = {"slug": "en1", "lang": "en"}
US = {"slug": "us1", "lang": "fr", "region_code": "US"}
CSB = [{"slug": f"c{i}", "lang": "en", "source_url": "https://www.csb.gov/x"} for i in range(2)]
DAYS = [date(2026, 1, 1) + timedelta(days=i) for i in range(120)]


def test_without_csb_equals_legacy_day_of_year():
    for d in DAYS[:40]:
        assert rotation.pick(FR, d)["slug"] == FR[(d.timetuple().tm_yday - 1) % 5]["slug"]


def test_prefers_french_moroccan_problems():
    for d in DAYS:
        assert rotation.pick([EN, US, *FR], d)["slug"].startswith("p")


def test_falls_back_when_no_preferred_problem():
    assert rotation.pick([EN], DAYS[0])["slug"] == "en1"


def test_csb_at_most_one_day_in_three():
    flags = [rotation.is_csb(rotation.pick([*FR, *CSB], d)) for d in DAYS]
    assert any(flags)
    assert all(sum(flags[i:i + 3]) <= 1 for i in range(len(flags) - 2))
    assert 0.25 < sum(flags) / len(flags) < 0.4


@pytest.mark.parametrize(("mx", "win", "lo", "hi"), [(0, 3, 0, 0), (2, 4, 0.45, 0.55), (1, 7, 0.1, 0.18)])
def test_ratio_is_configurable(mx, win, lo, hi):
    cfg = rotation.load_cfg(cfg={"rotation": {"csb_max_per_window": mx, "csb_window_days": win}})
    share = sum(rotation.is_csb(rotation.pick([*FR, *CSB], d, cfg)) for d in DAYS) / len(DAYS)
    assert lo <= share <= hi


def test_bad_ratio_is_rejected():
    with pytest.raises(ValueError):
        rotation.load_cfg(cfg={"rotation": {"csb_max_per_window": 4, "csb_window_days": 3}})


def test_shipped_config_has_the_rotation_block():
    cfg = rotation.load_cfg(ROOT)
    assert cfg["prefer_lang"] == "fr" and (cfg["csb_max_per_window"], cfg["csb_window_days"]) == (1, 3)


def test_csb_allowed_from_ledger_history():
    today = date(2026, 11, 24)
    hist = [{"date": "2026-11-23", "id": "web:fail-csb:abc"}]
    assert not rotation.csb_allowed(hist, today)                       # yesterday used the quota
    assert rotation.csb_allowed([{"date": "2026-11-21", "id": "web:fail-csb:abc"}], today)
    assert rotation.csb_allowed([{"date": "2026-11-23", "id": "bank-pompage"}], today)


def test_fetch_source_skips_excluded_listing_sources(tmp_path, monkeypatch):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "sources.json").write_text(json.dumps([
        {"id": "fail-csb", "enabled": True, "mode": "listing", "listing_url": "https://x", "link_pattern": "y"}]))
    calls = []
    monkeypatch.setattr(ingest.S, "polite_get", lambda *a, **k: calls.append(a) or (_ for _ in ()).throw(OSError()))
    assert ingest.fetch_source("Chemical", {"seen": {}}, date(2026, 1, 1), tmp_path, ["listing"],
                               frozenset({"fail-csb"})) is None and not calls
