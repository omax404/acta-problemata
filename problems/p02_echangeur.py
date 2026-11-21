"""Problem 02: Surface d'un échangeur de pasteurisation."""

META = {
    "slug": "echangeur",
    "title": "Surface d'un échangeur de pasteurisation",
    "sector": "Agroalimentaire",
    "sector_code": "AGR",
    "region": "Casablanca-Settat",
    "level": 2,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Débit de lait",
                "ṁ",
                "2,0 kg/s"
        ],
        [
                "Cp du lait",
                "cp",
                "3,93 kJ/(kg·K)"
        ],
        [
                "Lait : entrée → sortie",
                "T",
                "5 °C → 72 °C"
        ],
        [
                "Eau chaude : entrée → sortie",
                "T",
                "90 °C → 80 °C"
        ],
        [
                "Cp de l'eau",
                "cp",
                "4,18 kJ/(kg·K)"
        ],
        [
                "Coefficient global",
                "U",
                "1 500 W/(m²·K)"
        ]
],
    "formulas_raw": [
        "Φ = ṁ·cp·ΔT",
        "ΔTlm = (ΔT₂ − ΔT₁) / ln(ΔT₂/ΔT₁)",
        "A = Φ / (U·ΔTlm)"
],
    "formulas_tex_raw": [
        "\\Phi=\\dot m\\,c_p\\,\\Delta T",
        "\\Delta T_{lm}=\\frac{\\Delta T_2-\\Delta T_1}{\\ln\\left(\\Delta T_2/\\Delta T_1\\right)}",
        "A=\\frac{\\Phi}{U\\,\\Delta T_{lm}}"
],
    "answer_key_raw": [
        "Φ = 526,6 kW",
        "ṁ eau = 12,60 kg/s",
        "ΔTlm = 39,94 K ; A = 8,79 m² ; avec 15 % de marge : 10,11 m²"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 2, "slug": "echangeur"}


def render(inp: dict, res: dict) -> dict:
    context = "Une laiterie veut chauffer son lait avant pasteurisation avec de l'eau chaude de récupération, dans un échangeur à plaques à contre-courant. Il faut déterminer la puissance échangée, le débit d'eau chaude et la surface d'échange nécessaires."
    data = [
    [
        "Débit de lait",
        "ṁ",
        "2,0 kg/s"
    ],
    [
        "Cp du lait",
        "cp",
        "3,93 kJ/(kg·K)"
    ],
    [
        "Lait : entrée → sortie",
        "T",
        "5 °C → 72 °C"
    ],
    [
        "Eau chaude : entrée → sortie",
        "T",
        "90 °C → 80 °C"
    ],
    [
        "Cp de l'eau",
        "cp",
        "4,18 kJ/(kg·K)"
    ],
    [
        "Coefficient global",
        "U",
        "1 500 W/(m²·K)"
    ]
]
    questions = [
    "La puissance thermique à transférer ;",
    "Le débit d'eau chaude nécessaire ;",
    "La DTLM puis la surface d'échange, avec une marge de 15 % recommandée."
]
    formulas = [
    "Φ = ṁ·cp·ΔT",
    "ΔTlm = (ΔT₂ − ΔT₁) / ln(ΔT₂/ΔT₁)",
    "A = Φ / (U·ΔTlm)"
]
    formulas_tex = [
    "\\Phi=\\dot m\\,c_p\\,\\Delta T",
    "\\Delta T_{lm}=\\frac{\\Delta T_2-\\Delta T_1}{\\ln\\left(\\Delta T_2/\\Delta T_1\\right)}",
    "A=\\frac{\\Phi}{U\\,\\Delta T_{lm}}"
]
    answer_key = [
    "Φ = 526,6 kW",
    "ṁ eau = 12,60 kg/s",
    "ΔTlm = 39,94 K ; A = 8,79 m² ; avec 15 % de marge : 10,11 m²"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
