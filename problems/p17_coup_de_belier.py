"""Problem 17: Surpression de coup de bélier selon Joukowsky."""

META = {
    "slug": "coup-de-belier",
    "title": "Surpression de coup de bélier selon Joukowsky",
    "sector": "Hydraulique & Eau",
    "sector_code": "AGR",
    "region": "Gharb-Chrarda-Béni Hsen",
    "level": 3,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Vitesse nominale d'écoulement",
                "v",
                "2,4 m/s"
        ],
        [
                "Célérité de l'onde de pression",
                "c",
                "1 150 m/s"
        ],
        [
                "Masse volumique de l'eau",
                "ρ",
                "1 000 kg/m³"
        ],
        [
                "Accélération pesanteur",
                "g",
                "9,81 m/s²"
        ]
],
    "formulas_raw": [
        "\\Delta P = \\rho \\cdot c \\cdot \\Delta v",
        "\\Delta H = \\frac{c \\cdot \\Delta v}{g}",
        "T_{\\text{crit}} = \\frac{2 \\cdot L}{c}"
],
    "formulas_tex_raw": [
        "\\Delta P = \\rho \\cdot c \\cdot \\Delta v",
        "\\Delta H = \\frac{c \\cdot \\Delta v}{g}",
        "T_{\\text{crit}} = \\frac{2 \\cdot L}{c}"
],
    "answer_key_raw": [
        "Surpression = 27,60 bar (2,76 MPa)",
        "Surpression = 281,3 mCE",
        "Temps de manœuvre critique (L=450m) = 0,78 s"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 17, "slug": "coup-de-belier"}


def render(inp: dict, res: dict) -> dict:
    context = "Sur une conduite d'adduction d'eau brute agricole, une vanne papillon motorisée se ferme brutalement lors d'un déclenchement électrique d'urgence. L'ingénieur d'exploitation calcule la surpression maximale pour dimensionner la soupape de décharge."
    data = [
    [
        "Vitesse nominale d'écoulement",
        "v",
        "2,4 m/s"
    ],
    [
        "Célérité de l'onde de pression",
        "c",
        "1 150 m/s"
    ],
    [
        "Masse volumique de l'eau",
        "ρ",
        "1 000 kg/m³"
    ],
    [
        "Accélération pesanteur",
        "g",
        "9,81 m/s²"
    ]
]
    questions = [
    "La surpression théorique instantanée selon Joukowsky en Pascals et en bars ;",
    "La hauteur manométrique équivalente de surpression en mètres de colonne d'eau (mCE) ;",
    "Le temps de fermeture critique de la vanne pour éviter le coup de bélier franc sur une conduite de 450 m."
]
    formulas = [
    "\\Delta P = \\rho \\cdot c \\cdot \\Delta v",
    "\\Delta H = \\frac{c \\cdot \\Delta v}{g}",
    "T_{\\text{crit}} = \\frac{2 \\cdot L}{c}"
]
    formulas_tex = [
    "\\Delta P = \\rho \\cdot c \\cdot \\Delta v",
    "\\Delta H = \\frac{c \\cdot \\Delta v}{g}",
    "T_{\\text{crit}} = \\frac{2 \\cdot L}{c}"
]
    answer_key = [
    "Surpression = 27,60 bar (2,76 MPa)",
    "Surpression = 281,3 mCE",
    "Temps de manœuvre critique (L=450m) = 0,78 s"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
