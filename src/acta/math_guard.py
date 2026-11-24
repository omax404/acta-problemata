"""Deterministic math guardrail (FR-03). The LLM never gets to do arithmetic.

Every formula is parsed with a whitelisted, injection-safe SymPy parser,
evaluated at high precision, and rounded to 3 significant figures. Any
LLM-supplied numeric answer is discarded and overwritten (FR-03.3).
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

import sympy as sp
from sympy.parsing.sympy_parser import convert_xor, parse_expr, standard_transformations

ALLOWED_FUNCS = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan, "atan2": sp.atan2,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "sqrt": sp.sqrt, "exp": sp.exp, "log": sp.log, "ln": sp.log,
    "Abs": sp.Abs, "sign": sp.sign, "floor": sp.floor, "ceiling": sp.ceiling,
    "Min": sp.Min, "Max": sp.Max,
}
CONSTANTS = {"pi": sp.pi, "E": sp.E}

_NUMBER = r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
_NUM_GUARD = r"(?<![A-Za-z_0-9])"          # don't eat the '1' inside 'R1'
_NUM_RE = re.compile(_NUM_GUARD + _NUMBER)
_IDENT = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")
_TOKEN_RE = re.compile(f"({_NUMBER})|([A-Za-z_][A-Za-z_0-9]*)")
# No dunders, attribute access, subscripts, statements, or strings.
_FORBIDDEN = re.compile(r"__|\.[A-Za-z_]|[\[\]{};='\"\\@]|\blambda\b|\bimport\b")
VAR_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,15}$")


class MathGuardError(ValueError):
    """Raised when a formula cannot be safely parsed or evaluated."""


@dataclass
class VerifiedFormula:
    symbolic: str
    variables: dict[str, float]
    computed_result: float          # 3 s.f. — the ONLY published answer
    full_precision: float           # for the solution page / CLI tolerance
    unit: str
    substituted: str = ""
    sympy_snippet: str = ""


def round_sig(x: float, sig: int = 3) -> float:
    if x == 0 or not math.isfinite(x):
        return 0.0 if x == 0 else x
    return float(f"{x:.{sig}g}")


def within_tolerance(user: float, exact: float, rel_tol: float = 0.01) -> bool:
    """True if `user` is within `rel_tol` (relative) of `exact`; exact 0 needs |user| < 1e-12."""
    if isinstance(user, bool) or not math.isfinite(user) or not math.isfinite(exact):
        return False
    if exact == 0:
        return abs(user) < 1e-12
    return abs(user - exact) <= rel_tol * abs(exact)


def _check_expression(expr: str, var_names: set[str]) -> None:
    if not isinstance(expr, str) or not (1 <= len(expr) <= 400):
        raise MathGuardError("symbolic expression must be a string of 1..400 chars")
    if not expr.isascii():
        raise MathGuardError("expression must be ASCII (use pi, sqrt(), **)")
    if _FORBIDDEN.search(expr):
        raise MathGuardError("expression contains forbidden tokens")
    for ident in _IDENT.findall(_NUM_RE.sub(" ", expr)):
        if ident not in var_names and ident not in ALLOWED_FUNCS and ident not in CONSTANTS:
            raise MathGuardError(f"unknown or undeclared identifier: {ident!r}")


def _substitute_display(expr: str, variables: dict[str, float]) -> str:
    def repl(m: re.Match) -> str:
        if m.group(1) is not None:
            return m.group(1)
        name = m.group(2)
        return f"({variables[name]:g})" if name in variables else name
    return _TOKEN_RE.sub(repl, expr)


def verify_formula(symbolic: str, variables: dict[str, float], unit: str) -> VerifiedFormula:
    """Parse safely, evaluate independently, round to 3 s.f. Raises MathGuardError."""
    for name, value in variables.items():
        if not VAR_NAME.match(name):
            raise MathGuardError(f"illegal variable name: {name!r}")
        if name in ALLOWED_FUNCS:
            raise MathGuardError(f"variable {name!r} collides with a function name")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise MathGuardError(f"variable {name!r} must be a finite number")
    if not variables:
        raise MathGuardError("equation_variables must not be empty")

    _check_expression(symbolic, set(variables))

    # Declared variables SHADOW SymPy defaults: E (Young's modulus), I (moment
    # of inertia), beta, gamma... must be plain real symbols, not Euler's e,
    # the imaginary unit, or special functions.
    local = dict(CONSTANTS)
    local.update(ALLOWED_FUNCS)
    local.update({name: sp.Symbol(name, real=True) for name in variables})

    try:
        expr = parse_expr(
            symbolic, local_dict=local,
            global_dict={"__builtins__": {}, "Integer": sp.Integer, "Float": sp.Float,
                         "Rational": sp.Rational, "Symbol": sp.Symbol},
            transformations=standard_transformations + (convert_xor,),
            evaluate=True,
        )
    except MathGuardError:
        raise
    except Exception as exc:
        raise MathGuardError(f"parse failure: {exc}") from exc

    if isinstance(expr, sp.logic.boolalg.Boolean) or expr.is_Relational:
        raise MathGuardError("expression must be numeric, not boolean/relational")
    free = {s.name for s in expr.free_symbols}
    if free != set(variables):
        missing, unused = free - set(variables), set(variables) - free
        raise MathGuardError(f"variable mismatch (missing={sorted(missing)}, unused={sorted(unused)})")

    try:
        exact = expr.subs({local[n]: sp.Float(v, 25) for n, v in variables.items()}).evalf(30)
    except Exception as exc:
        raise MathGuardError(f"evaluation failure: {exc}") from exc

    if not exact.is_number or exact.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
        raise MathGuardError("result is undefined (division by zero / overflow?)")
    re_c, im_c = sp.re(exact), sp.im(exact)
    if not re_c.is_finite or abs(complex(im_c)) > 1e-20 * max(1.0, abs(complex(re_c))):
        raise MathGuardError("result is not a finite real number")

    full = float(re_c)
    rounded = round_sig(full, 3)
    snippet = (
        "import sympy as sp\n"
        + "".join(f"{n} = {v!r}\n" for n, v in variables.items())
        + f"expr = sp.sympify({symbolic!r})\n"
        + f"result = expr.evalf(30)   # -> {full:.10g} {unit}\n"
        + f"answer = float(f'{{result:.3g}}')  # {rounded:g} {unit} (3 s.f.)"
    )
    return VerifiedFormula(
        symbolic=symbolic, variables=dict(variables), computed_result=rounded,
        full_precision=full, unit=unit,
        substituted=_substitute_display(symbolic, variables), sympy_snippet=snippet,
    )
