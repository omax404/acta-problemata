"""Solution sheets: schema check, math_guard verification, VERIFIED stamp, QR target."""
import json
import shutil
from pathlib import Path

import pytest
from pypdf import PdfReader

from acta import sheet, solution
from acta.cli import main
from acta.math_guard import within_tolerance

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "solution.example.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def repo(tmp_path_factory):
    r = tmp_path_factory.mktemp("solution")
    for n in ("data/bank", "templates", "assets"):
        shutil.copytree(ROOT / n, r / n)
    return r


def _pdf_text(path: Path) -> str:
    return PdfReader(str(path)).pages[0].extract_text().replace(" ", "").replace("\n", "")


def _write(tmp_path: Path, sol: dict) -> Path:
    f = tmp_path / "sol.json"
    f.write_text(json.dumps(sol), encoding="utf-8")
    return f


def test_within_tolerance():
    assert within_tolerance(22.4, 22.43, 0.01)
    assert not within_tolerance(25.0, 22.43, 0.01)
    assert not within_tolerance(float("nan"), 1.0)
    assert within_tolerance(0.0, 0.0)


def test_expected_numbers_parse_french_formats():
    p = {"answer_key": ["v = 1,28 m/s ; Re = 134 198 ; f = 0,0194", "H = 22,4 m (frottement 3,87 m)"]}
    assert solution.expected_numbers(p) == [1.28, 134198.0, 0.0194, 22.4]


def test_match_is_verified(repo):
    p = sheet.load_problem(repo, "pompage")
    v = solution.verify(p, solution.validate(dict(EXAMPLE)))
    assert v.verified and v.detail == "5/5 answers within 1%"


def test_mismatch_is_not_verified(repo):
    p = sheet.load_problem(repo, "pompage")
    bad = solution.validate({**EXAMPLE, "answers": [1.28, 31.0]})
    v = solution.verify(p, bad)
    assert not v.verified and v.unmatched == [31.0]


def test_no_answers_is_unchecked(repo):
    p = sheet.load_problem(repo, "pompage")
    v = solution.verify(p, solution.validate({k: x for k, x in EXAMPLE.items() if k != "answers"}))
    assert v.status == "unchecked" and not v.verified


@pytest.mark.parametrize("field", ["name", "steps", "result"])
def test_missing_required_field_is_refused(field):
    with pytest.raises(solution.SolutionError, match=field):
        solution.validate({k: v for k, v in EXAMPLE.items() if k != field})


def test_bad_answers_type_is_refused():
    with pytest.raises(solution.SolutionError, match="answers"):
        solution.validate({**EXAMPLE, "answers": ["abc"]})


def test_stamp_only_on_match(repo, tmp_path):
    good, bad = repo / "out" / "good.pdf", repo / "out" / "bad.pdf"
    p = sheet.load_problem(repo, "pompage")
    for out, answers in ((good, EXAMPLE["answers"]), (bad, [1.28, 31.0])):
        sol = solution.validate({**EXAMPLE, "answers": answers})
        sheet.render_sheet(sheet.build_data(p, "solution", sol, verdict=solution.verify(p, sol)), repo, out)
    assert "VÉRIFIÉparmath_guard" in _pdf_text(good)
    assert "VÉRIFIÉparmath_guard" not in _pdf_text(bad) and "NONVÉRIFIÉ" in _pdf_text(bad)
    assert len(PdfReader(str(bad)).pages) == 1


def test_sheet_shows_solver_name(repo):
    p = sheet.load_problem(repo, "pompage")
    sol = solution.validate(dict(EXAMPLE))
    out = repo / "out" / "name.pdf"
    sheet.render_sheet(sheet.build_data(p, "solution", sol, verdict=solution.verify(p, sol)), repo, out)
    assert "YoussefElMansouri" in _pdf_text(out)


def test_qr_points_to_public_archive_page(repo):
    p = sheet.load_problem(repo, "pompage")
    assert sheet.build_data(p)["qr_url"] == "https://omax404.github.io/acta-problemata/e/01.html"


def test_cli_missing_field_exits_2(repo, tmp_path, capsys):
    f = _write(tmp_path, {k: v for k, v in EXAMPLE.items() if k != "steps"})
    assert main(["--root", str(repo), "sheet", "pompage", "--solution", str(f)]) == 2
    assert "steps" in capsys.readouterr().err


def test_cli_end_to_end(repo, tmp_path, capsys):
    out = tmp_path / "s.pdf"
    f = _write(tmp_path, EXAMPLE)
    assert main(["--root", str(repo), "sheet", "pompage", "--solution", str(f), "--out", str(out)]) == 0
    assert "VERIFIED" in capsys.readouterr().err and out.exists()
