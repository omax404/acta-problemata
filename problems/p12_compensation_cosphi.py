"""Problem 12: Compensation d'énergie réactive par batterie de condensateurs."""

META = {
    "slug": "compensation-cosphi",
    "title": "Compensation d'énergie réactive par batterie de condensateurs",
    "sector": "Agroalimentaire",
    "sector_code": "AGR",
    "region": "Fès-Meknès",
    "level": 1,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Puissance active moyenne",
                "P",
                "250 kW"
        ],
        [
                "Facteur de puissance initial",
                "cos φ₁",
                "0,72"
        ],
        [
                "Facteur de puissance visé",
                "cos φ₂",
                "0,93"
        ],
        [
                "Tension réseau",
                "U",
                "400 V triphasé"
        ]
],
    "formulas_raw": [
        "Q_c = P \\cdot (\\tan \\varphi_1 - \\tan \\varphi_2)",
        "S = \\sqrt{P^2 + Q^2}"
],
    "formulas_tex_raw": [
        "Q_c = P \\cdot (\\tan \\varphi_1 - \\tan \\varphi_2)",
        "S = \\sqrt{P^2 + Q^2}"
],
    "answer_key_raw": [
        "tan φ₁ = 0,964 ; tan φ₂ = 0,395",
        "Q_c nécessaire = 142,2 kVAr",
        "Batterie normalisée recommandée = 150 kVAr (gradins de 25 kVAr)"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 12, "slug": "compensation-cosphi"}


def render(inp: dict, res: dict) -> dict:
    context = "Une minoterie industrielle subit des pénalités pour dépassement de puissance réactive sur sa facture moyenne tension ONEE. Le responsable électrique doit dimensionner la batterie de condensateurs automatique pour remonter le facteur de puissance."
    data = [
    [
        "Puissance active moyenne",
        "P",
        "250 kW"
    ],
    [
        "Facteur de puissance initial",
        "cos φ₁",
        "0,72"
    ],
    [
        "Facteur de puissance visé",
        "cos φ₂",
        "0,93"
    ],
    [
        "Tension réseau",
        "U",
        "400 V triphasé"
    ]
]
    questions = [
    "La puissance réactive initiale et finale ;",
    "La puissance capacitive de la batterie à installer ;",
    "Le choix d'un gradinage standard et l'économie sur les pénalités réactives."
]
    formulas = [
    "Q_c = P \\cdot (\\tan \\varphi_1 - \\tan \\varphi_2)",
    "S = \\sqrt{P^2 + Q^2}"
]
    formulas_tex = [
    "Q_c = P \\cdot (\\tan \\varphi_1 - \\tan \\varphi_2)",
    "S = \\sqrt{P^2 + Q^2}"
]
    answer_key = [
    "tan φ₁ = 0,964 ; tan φ₂ = 0,395",
    "Q_c nécessaire = 142,2 kVAr",
    "Batterie normalisée recommandée = 150 kVAr (gradins de 25 kVAr)"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
