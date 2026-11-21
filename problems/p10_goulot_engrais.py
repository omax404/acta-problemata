"""Problem 10: Loi de Little et engorgement d'une unité de broyage d'engrais."""

META = {
    "slug": "goulot-engrais",
    "title": "Loi de Little et engorgement d'une unité de broyage d'engrais",
    "sector": "Mines & Chimie lourde",
    "sector_code": "CHM",
    "region": "Casablanca-Settat",
    "level": 2,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Débit moyen d'alimentation matière",
                "λ",
                "45 t/h"
        ],
        [
                "Temps de séjour moyen dans le process",
                "W",
                "2,4 h"
        ],
        [
                "Augmentation de charge prévue",
                "ΔD",
                "+40 % (63 t/h)"
        ],
        [
                "Capacité du stockage tampon dans le système",
                "L_max",
                "120 tonnes"
        ]
],
    "formulas_raw": [
        "L = \\lambda \\cdot W \\quad (\\text{Loi de Little})",
        "W_{\\text{crit}} = \\frac{L_{\\max}}{\\lambda_{\\text{pic}}}"
],
    "formulas_tex_raw": [
        "L = \\lambda \\cdot W",
        "W_{\\text{crit}} = \\frac{L_{\\max}}{\\lambda_{\\text{pic}}}"
],
    "answer_key_raw": [
        "L nominal = 108,0 tonnes",
        "L à +40 % = 151,2 tonnes",
        "W critique à 63 t/h = 1,90 h (114 min) avant saturation du stockage tampon"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 10, "slug": "goulot-engrais"}


def render(inp: dict, res: dict) -> dict:
    context = "Une unité de traitement chimique de phosphate et engrais reçoit un flux continu de matière broyée. L est l'en-cours total matière du système et la cuve de 120 t en constitue le stockage tampon. Les ingénieurs observent qu'une augmentation de 40 % de la demande amène l'atelier à saturation."
    data = [
    [
        "Débit moyen d'alimentation matière",
        "λ",
        "45 t/h"
    ],
    [
        "Temps de séjour moyen dans le process",
        "W",
        "2,4 h"
    ],
    [
        "Augmentation de charge prévue",
        "ΔD",
        "+40 % (63 t/h)"
    ],
    [
        "Capacité du stockage tampon dans le système",
        "L_max",
        "120 tonnes"
    ]
]
    questions = [
    "L'en-cours moyen matière total L dans le système en régime nominal (loi de Little) ;",
    "L'en-cours total prévu sous une hausse de 40 % si le temps de séjour reste identique ;",
    "Le temps de séjour critique W_critique au-delà duquel la cuve tampon de 120 t sature sous le flux de 63 t/h."
]
    formulas = [
    "L = \\lambda \\cdot W \\quad (\\text{Loi de Little})",
    "W_{\\text{crit}} = \\frac{L_{\\max}}{\\lambda_{\\text{pic}}}"
]
    formulas_tex = [
    "L = \\lambda \\cdot W",
    "W_{\\text{crit}} = \\frac{L_{\\max}}{\\lambda_{\\text{pic}}}"
]
    answer_key = [
    "L nominal = 108,0 tonnes",
    "L à +40 % = 151,2 tonnes",
    "W critique à 63 t/h = 1,90 h (114 min) avant saturation du stockage tampon"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
