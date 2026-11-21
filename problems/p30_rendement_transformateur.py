"""Problem 30: Bilan des pertes et rendement d'un transformateur de distribution."""

META = {
    "slug": "rendement-transformateur",
    "title": "Bilan des pertes et rendement d'un transformateur de distribution",
    "sector": "Matériaux de construction",
    "sector_code": "MAT",
    "region": "Béni Mellal-Khénifra",
    "level": 2,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Puissance apparente nominale transfo",
                "Sn",
                "630 kVA"
        ],
        [
                "Pertes fer à vide mesurées",
                "P0",
                "1,3 kW (1 300 W)"
        ],
        [
                "Pertes cuivre à charge nominale",
                "Pcc",
                "6,5 kW (6 500 W)"
        ],
        [
                "Taux de charge moyen de l'installation",
                "β",
                "0,65 (65 %)"
        ],
        [
                "Facteur de puissance moyen de l'atelier",
                "cos φ",
                "0,88"
        ],
        [
                "Tarif électricité moyen",
                "c",
                "1,05 MAD/kWh"
        ]
],
    "formulas_raw": [
        "P_{\\text{pertes}} = P_0 + \\beta^2 \\cdot P_{cc}",
        "P_{\\text{utile}} = \\beta \\cdot S_n \\cdot \\cos \\varphi",
        "\\eta = \\frac{P_{\\text{utile}}}{P_{\\text{utile}} + P_{\\text{pertes}}}"
],
    "formulas_tex_raw": [
        "P_{\\text{pertes}} = P_0 + \\beta^2 \\cdot P_{cc}",
        "P_{\\text{utile}} = \\beta \\cdot S_n \\cdot \\cos \\varphi",
        "\\eta = \\frac{P_{\\text{utile}}}{P_{\\text{utile}} + P_{\\text{pertes}}}"
],
    "answer_key_raw": [
        "Pertes cuivre = 2,75 kW ; Pertes totales = 4,05 kW",
        "Puissance utile = 360,4 kW ; Rendement = 98,89 %",
        "Pertes annuelles = 35 445 kWh/an ; Coût = 37 217 MAD/an"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 30, "slug": "rendement-transformateur"}


def render(inp: dict, res: dict) -> dict:
    context = "Une cimenterie alimente son atelier d'ensachage par un transformateur triphasé 630 kVA 22 kV / 400 V. Le service énergie analyse le taux de charge réel pour optimiser le rendement énergétique global de la sous-station."
    data = [
    [
        "Puissance apparente nominale transfo",
        "Sn",
        "630 kVA"
    ],
    [
        "Pertes fer à vide mesurées",
        "P0",
        "1,3 kW (1 300 W)"
    ],
    [
        "Pertes cuivre à charge nominale",
        "Pcc",
        "6,5 kW (6 500 W)"
    ],
    [
        "Taux de charge moyen de l'installation",
        "β",
        "0,65 (65 %)"
    ],
    [
        "Facteur de puissance moyen de l'atelier",
        "cos φ",
        "0,88"
    ],
    [
        "Tarif électricité moyen",
        "c",
        "1,05 MAD/kWh"
    ]
]
    questions = [
    "Les pertes totales du transformateur sous un taux de charge de 65 % ;",
    "La puissance active utile délivrée et le rendement instantané du transformateur ;",
    "L'énergie totale dissipée en pertes thermiques sur une année (8 760 h) et son coût en MAD."
]
    formulas = [
    "P_{\\text{pertes}} = P_0 + \\beta^2 \\cdot P_{cc}",
    "P_{\\text{utile}} = \\beta \\cdot S_n \\cdot \\cos \\varphi",
    "\\eta = \\frac{P_{\\text{utile}}}{P_{\\text{utile}} + P_{\\text{pertes}}}"
]
    formulas_tex = [
    "P_{\\text{pertes}} = P_0 + \\beta^2 \\cdot P_{cc}",
    "P_{\\text{utile}} = \\beta \\cdot S_n \\cdot \\cos \\varphi",
    "\\eta = \\frac{P_{\\text{utile}}}{P_{\\text{utile}} + P_{\\text{pertes}}}"
]
    answer_key = [
    "Pertes cuivre = 2,75 kW ; Pertes totales = 4,05 kW",
    "Puissance utile = 360,4 kW ; Rendement = 98,89 %",
    "Pertes annuelles = 35 445 kWh/an ; Coût = 37 217 MAD/an"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
