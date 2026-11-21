"""Problem 26: Bilan thermique frigorifique d'une chambre froide de conservation."""

META = {
    "slug": "bilan-chambre-froide",
    "title": "Bilan thermique frigorifique d'une chambre froide de conservation",
    "sector": "Agroalimentaire",
    "sector_code": "AGR",
    "region": "Souss-Massa",
    "level": 2,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Surface totale de l'enveloppe isolée",
                "S",
                "340 m²"
        ],
        [
                "Coefficient de transmission thermique parois",
                "U",
                "0,22 W/(m²·K)"
        ],
        [
                "Température extérieure maximale été",
                "Text",
                "38 °C"
        ],
        [
                "Température de consigne chambre",
                "Tint",
                "2 °C"
        ],
        [
                "Entrée journalière de fruits",
                "m",
                "5 000 kg/jour"
        ],
        [
                "Chaleur massique des fruits",
                "cp",
                "3,8 kJ/(kg·K)"
        ],
        [
                "Refroidissement du produit",
                "T_fruit",
                "25 °C → 2 °C en 18 h"
        ],
        [
                "Charges internes annexes (ventilateurs, éclairage)",
                "Q_int",
                "1,8 kW"
        ]
],
    "formulas_raw": [
        "\\Phi_{\\text{paroi}} = U \\cdot S \\cdot (T_{\\text{ext}} - T_{\\text{int}})",
        "\\Phi_{\\text{prod}} = \\frac{m \\cdot c_p \\cdot \\Delta T}{\\Delta t}",
        "\\Phi_{\\text{tot}} = (\\Phi_{\\text{paroi}} + \\Phi_{\\text{prod}} + Q_{\\text{int}}) \\cdot 1{,}15"
],
    "formulas_tex_raw": [
        "\\Phi_{\\text{paroi}} = U \\cdot S \\cdot (T_{\\text{ext}} - T_{\\text{int}})",
        "\\Phi_{\\text{prod}} = \\frac{m \\cdot c_p \\cdot \\Delta T}{\\Delta t}",
        "\\Phi_{\\text{tot}} = (\\Phi_{\\text{paroi}} + \\Phi_{\\text{prod}} + Q_{\\text{int}}) \\cdot 1{,}15"
],
    "answer_key_raw": [
        "Transmission parois = 2,69 kW",
        "Puissance refroidissement produit = 6,74 kW",
        "Puissance frigorifique à installer = 12,92 kW (marge 15 %)"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 26, "slug": "bilan-chambre-froide"}


def render(inp: dict, res: dict) -> dict:
    context = "Une station d'emballage d'agrumes installe une chambre froide positive pour le stockage temporaire avant expédition frigorifique. L'ingénieur utilités doit calculer le bilan frigorifique pour dimensionner le groupe compresseur."
    data = [
    [
        "Surface totale de l'enveloppe isolée",
        "S",
        "340 m²"
    ],
    [
        "Coefficient de transmission thermique parois",
        "U",
        "0,22 W/(m²·K)"
    ],
    [
        "Température extérieure maximale été",
        "Text",
        "38 °C"
    ],
    [
        "Température de consigne chambre",
        "Tint",
        "2 °C"
    ],
    [
        "Entrée journalière de fruits",
        "m",
        "5 000 kg/jour"
    ],
    [
        "Chaleur massique des fruits",
        "cp",
        "3,8 kJ/(kg·K)"
    ],
    [
        "Refroidissement du produit",
        "T_fruit",
        "25 °C → 2 °C en 18 h"
    ],
    [
        "Charges internes annexes (ventilateurs, éclairage)",
        "Q_int",
        "1,8 kW"
    ]
]
    questions = [
    "La charge thermique transmise par conduction à travers les parois ;",
    "La puissance frigorifique requise pour le refroidissement des fruits en 18 h ;",
    "La puissance frigorifique nominale de l'évaporateur avec 15 % de marge de sécurité."
]
    formulas = [
    "\\Phi_{\\text{paroi}} = U \\cdot S \\cdot (T_{\\text{ext}} - T_{\\text{int}})",
    "\\Phi_{\\text{prod}} = \\frac{m \\cdot c_p \\cdot \\Delta T}{\\Delta t}",
    "\\Phi_{\\text{tot}} = (\\Phi_{\\text{paroi}} + \\Phi_{\\text{prod}} + Q_{\\text{int}}) \\cdot 1{,}15"
]
    formulas_tex = [
    "\\Phi_{\\text{paroi}} = U \\cdot S \\cdot (T_{\\text{ext}} - T_{\\text{int}})",
    "\\Phi_{\\text{prod}} = \\frac{m \\cdot c_p \\cdot \\Delta T}{\\Delta t}",
    "\\Phi_{\\text{tot}} = (\\Phi_{\\text{paroi}} + \\Phi_{\\text{prod}} + Q_{\\text{int}}) \\cdot 1{,}15"
]
    answer_key = [
    "Transmission parois = 2,69 kW",
    "Puissance refroidissement produit = 6,74 kW",
    "Puissance frigorifique à installer = 12,92 kW (marge 15 %)"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
