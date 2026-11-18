import pytest

from acta import legibility
from acta.cli import main as cli_main
from acta.diagrams import KINDS, render_diagram


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
