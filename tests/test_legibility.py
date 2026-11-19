import shutil

import pytest

from acta import legibility
from acta.cli import main as cli_main
from acta.diagrams import KINDS, generator, render_diagram

pytestmark = pytest.mark.skipif(not shutil.which("rsvg-convert"), reason="rsvg-convert not installed")


def _svg(tmp_path, name, body):
    p = tmp_path / f"{name}.svg"
    p.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="260" '
                 f'viewBox="0 0 600 260">{body}</svg>')
    return p


def codes(path):
    return {(f.level, f.code) for f in legibility.analyze(path)}


@pytest.mark.parametrize("kind", sorted(KINDS))
def test_every_shipped_diagram_is_legible(kind, tmp_path):
    assert legibility.analyze(render_diagram(kind, {}, tmp_path / "d.svg")) == []


def test_detects_clipping_contrast_and_blank(tmp_path):
    assert codes(_svg(tmp_path, "a", '<rect x="0" y="100" width="300" height="40" fill="#111"/>')) == {("warn", "clipped")}
    assert ("error", "contrast") in codes(_svg(tmp_path, "b", '<rect x="100" y="80" width="400" height="100" fill="#cfcfcf"/>'))
    assert codes(_svg(tmp_path, "c", "")) == {("error", "blank")}
    assert codes(_svg(tmp_path, "d", '<rect x="100" y="80" width="400" height="100" fill="#1c1a17"/>')) == set()


def test_cli_reports_and_sets_exit_code(tmp_path, capsys):
    good = _svg(tmp_path, "ok", '<rect x="100" y="80" width="400" height="100" fill="#1c1a17"/>')
    bad = _svg(tmp_path, "bad", "")
    assert cli_main(["--root", str(tmp_path), "legibility", str(good)]) == 0
    assert cli_main(["--root", str(tmp_path), "legibility", str(bad)]) == 1
    assert "blank" in capsys.readouterr().out


@pytest.mark.parametrize("kind", sorted(KINDS))
def test_no_text_overlaps_in_shipped_diagrams(kind, tmp_path):
    pairs: list = []
    render_diagram(kind, {}, tmp_path / "d.svg", audit=pairs)
    assert pairs == [], pairs


def test_overlapping_labels_are_detected(tmp_path, monkeypatch):
    def bad(ax, p):
        ax.text(0, 0, "Contrainte maximale", ha="center")
        ax.text(0.05, 0.02, "Charge P", ha="center")
        ax.text(5, 5, "Far away", ha="center")
        ax.set_xlim(-2, 6); ax.set_ylim(-2, 6)
    monkeypatch.setitem(generator.KINDS, "bad", bad)
    pairs: list = []
    render_diagram("bad", {}, tmp_path / "d.svg", audit=pairs)
    assert pairs == [("Contrainte maximale", "Charge P")]
    assert [f.code for f in legibility.overlap_findings(pairs)] == ["overlap"]
