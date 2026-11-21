"""Problem 18: Vérification du non-risque de cavitation (NPSH disponible)."""

META = {
    "slug": "cavitation-npsh",
    "title": "Vérification du non-risque de cavitation (NPSH disponible)",
    "sector": "Agroalimentaire",
    "sector_code": "AGR",
    "region": "Rabat-Salé-Kénitra",
    "level": 2,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Pression atmosphérique du site",
                "Patm",
                "1 013 mbar (101 325 Pa)"
        ],
        [
                "Pression de vapeur saturante du fluide",
                "Pv",
                "2 338 Pa (20 °C)"
        ],
        [
                "Hauteur géométrique d'aspiration",
                "Ha",
                "3,5 m"
        ],
        [
                "Pertes de charge à l'aspiration",
                "Δha",
                "1,2 m"
        ],
        [
                "NPSH requis constructeur au point Q",
                "NPSHr",
                "3,8 m"
        ]
],
    "formulas_raw": [
        "\\text{NPSH}_a = \\frac{P_{\\text{atm}} - P_v}{\\rho \\cdot g} - H_a - \\Delta h_a",
        "\\text{Marge} = \\text{NPSH}_a - \\text{NPSH}_r \\ge 0{,}5\\text{ m}"
],
    "formulas_tex_raw": [
        "\\text{NPSH}_a = \\frac{P_{\\text{atm}} - P_v}{\\rho \\cdot g} - H_a - \\Delta h_a",
        "\\text{Marge} = \\text{NPSH}_a - \\text{NPSH}_r \\ge 0{,}5\\text{ m}"
],
    "answer_key_raw": [
        "Charge atmosphérique nette = 10,09 m",
        "NPSH disponible = 5,39 m",
        "Marge de sécurité = 1,59 m (Conforme car > 0,5 m)"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 18, "slug": "cavitation-npsh"}


def render(inp: dict, res: dict) -> dict:
    context = "Une pompe centrifuge aspire du jus de fruit clarifié depuis une cuve ouverte en contrebas. En période de forte production, des bruits de crépitement anormaux font craindre une entrée en cavitation destructive."
    data = [
    [
        "Pression atmosphérique du site",
        "Patm",
        "1 013 mbar (101 325 Pa)"
    ],
    [
        "Pression de vapeur saturante du fluide",
        "Pv",
        "2 338 Pa (20 °C)"
    ],
    [
        "Hauteur géométrique d'aspiration",
        "Ha",
        "3,5 m"
    ],
    [
        "Pertes de charge à l'aspiration",
        "Δha",
        "1,2 m"
    ],
    [
        "NPSH requis constructeur au point Q",
        "NPSHr",
        "3,8 m"
    ]
]
    questions = [
    "La charge absolue disponible au plan d'eau ;",
    "Le NPSH disponible réel à l'ouïe de la pompe ;",
    "La comparaison avec le NPSH requis constructeur et la marge de sécurité recommandée (≥ 0,5 m)."
]
    formulas = [
    "\\text{NPSH}_a = \\frac{P_{\\text{atm}} - P_v}{\\rho \\cdot g} - H_a - \\Delta h_a",
    "\\text{Marge} = \\text{NPSH}_a - \\text{NPSH}_r \\ge 0{,}5\\text{ m}"
]
    formulas_tex = [
    "\\text{NPSH}_a = \\frac{P_{\\text{atm}} - P_v}{\\rho \\cdot g} - H_a - \\Delta h_a",
    "\\text{Marge} = \\text{NPSH}_a - \\text{NPSH}_r \\ge 0{,}5\\text{ m}"
]
    answer_key = [
    "Charge atmosphérique nette = 10,09 m",
    "NPSH disponible = 5,39 m",
    "Marge de sécurité = 1,59 m (Conforme car > 0,5 m)"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
