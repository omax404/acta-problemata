import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from acta.cli import check_answer
from acta.ledger import is_seen, load, next_edition, record_success
from acta.math_guard import MathGuardError, verify_formula
from acta.render import display_result
from acta.schemas import LLMCase, gemini_response_schema

ROOT = Path(__file__).resolve().parents[1]


def test_cantilever_with_E_and_I_shadowing():
    vf = verify_formula("P*L**3/(3*E*I)", {"P": 1200.0, "L": 1.5, "E": 200e9, "I": 8.33e-6}, "m")
    assert vf.computed_result == 0.000810
    assert vf.full_precision == pytest.approx(8.10324e-4, rel=1e-4)


@pytest.mark.parametrize("expr,vars_", [
    ("__import__('os').system('id')", {"x": 1.0}),
    ("open('/etc/passwd').read()", {"x": 1.0}),
    ("x.__class__", {"x": 1.0}),
    ("x; import os", {"x": 1.0}),
    ("lambda: 1", {"x": 1.0}),
    ("[i for i in (1,)]", {"x": 1.0}),
    ("foo*2", {"x": 1.0}),
    ("x**2", {"x": 1.0, "y": 2.0}),
    ("sqrt(-P)", {"P": 4.0}),
    ("P/z", {"P": 1.0, "z": 0.0}),
])
def test_injection_blocked(expr, vars_):
    with pytest.raises(MathGuardError):
        verify_formula(expr, vars_, "u")


def test_vault_cases_all_valid():
    for e in json.loads((ROOT / "data" / "case_vault.json").read_text()):
        case = LLMCase.model_validate(e["case"])
        vf = verify_formula(case.formula.symbolic,
                            {v.symbol: v.value for v in case.formula.variables},
                            case.formula.unit)
        assert vf.computed_result != 0


def test_ledger_streak_idempotency_and_window(tmp_path):
    led = load(tmp_path / "ledger.json")
    d1, d2 = date(2026, 11, 14), date(2026, 11, 15)
    record_success(led, d1, "a", {"edition": 1, "date": d1.isoformat()})
    record_success(led, d2, "b", {"edition": 2, "date": d2.isoformat()})
    assert led["streak"] == 2 and next_edition(led, d2) == 2
    record_success(led, d2, "c", {"edition": 2, "date": d2.isoformat()})
    assert led["streak"] == 2 and len(led["history"]) == 1 + 1
    assert is_seen(led, "a", d2) and not is_seen(led, "a", d1 + timedelta(days=180))
    record_success(led, d2 + timedelta(days=2), "d", {"edition": 3, "date": "2026-11-17"})
    assert led["streak"] == 1


def test_answer_tolerance():
    assert check_answer(8.10e-4, 8.103241297e-4)
    assert not check_answer(8.2e-4, 8.103241297e-4)
    assert check_answer(22.6e6, 22.599e6)


def test_display_and_schema():
    assert display_result(22600000.0) == "2.26 × 10⁷"
    assert display_result(1350.0) == "1,350"
    s = json.dumps(gemini_response_schema(LLMCase))
    assert "$ref" not in s and "additionalProperties" not in s
