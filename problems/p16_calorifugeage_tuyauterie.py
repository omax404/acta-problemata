"""Problem 16: Rentabilité du calorifugeage d'une ligne vapeur nue."""

META = {
    "slug": "calorifugeage-tuyauterie",
    "title": "Rentabilité du calorifugeage d'une ligne vapeur nue",
    "sector": "Chimie lourde",
    "sector_code": "CHM",
    "region": "Souss-Massa",
    "level": 3,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Diamètre extérieur tube",
                "De",
                "89 mm (DN80)"
        ],
        [
                "Longueur de ligne nue",
                "L",
                "60 m"
        ],
        [
                "Température de surface du tube",
                "Tp",
                "160 °C"
        ],
        [
                "Température ambiante moyenne",
                "Ta",
                "20 °C"
        ],
        [
                "Coefficient d'échange global vers l'air",
                "h",
                "15 W/(m²·K)"
        ],
        [
                "Efficacité thermique isolant 50 mm",
                "η_iso",
                "88 %"
        ],
        [
                "Coût énergie thermique gaz",
                "c_th",
                "0,42 MAD/kWh"
        ],
        [
                "Coût des travaux de calorifugeage",
                "C_inv",
                "350 MAD/m"
        ],
        [
                "Fonctionnement annuel",
                "t",
                "6 000 h/an"
        ]
],
    "formulas_raw": [
        "q = \\pi \\cdot D_e \\cdot h \\cdot (T_p - T_a)",
        "\\Phi = q \\cdot L",
        "\\text{Gain} = \\Phi \\cdot \\eta_{\\text{iso}} \\cdot t \\cdot c_{\\text{th}}",
        "\\text{TRI} = \\frac{C_{\\text{inv}}}{\\text{Gain}}"
],
    "formulas_tex_raw": [
        "q = \\pi \\cdot D_e \\cdot h \\cdot (T_p - T_a)",
        "\\Phi = q \\cdot L",
        "\\text{Gain} = \\Phi \\cdot \\eta_{\\text{iso}} \\cdot t \\cdot c_{\\text{th}}",
        "\\text{TRI} = \\frac{C_{\\text{inv}}}{\\text{Gain}}"
],
    "answer_key_raw": [
        "Perte linéique = 587,2 W/m ; Puissance perdue totale = 35,2 kW",
        "Économie annuelle = 186 013 kWh/an",
        "Gain = 78 126 MAD/an ; TRI = 3,2 mois"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 16, "slug": "calorifugeage-tuyauterie"}


def render(inp: dict, res: dict) -> dict:
    context = "Une ligne de distribution de vapeur saturée de 60 mètres n'a jamais été calorifugée suite à des travaux de maintenance. L'ingénieur utilités doit justifier l'investissement de calorifugeage auprès de la direction financière."
    data = [
    [
        "Diamètre extérieur tube",
        "De",
        "89 mm (DN80)"
    ],
    [
        "Longueur de ligne nue",
        "L",
        "60 m"
    ],
    [
        "Température de surface du tube",
        "Tp",
        "160 °C"
    ],
    [
        "Température ambiante moyenne",
        "Ta",
        "20 °C"
    ],
    [
        "Coefficient d'échange global vers l'air",
        "h",
        "15 W/(m²·K)"
    ],
    [
        "Efficacité thermique isolant 50 mm",
        "η_iso",
        "88 %"
    ],
    [
        "Coût énergie thermique gaz",
        "c_th",
        "0,42 MAD/kWh"
    ],
    [
        "Coût des travaux de calorifugeage",
        "C_inv",
        "350 MAD/m"
    ],
    [
        "Fonctionnement annuel",
        "t",
        "6 000 h/an"
    ]
]
    questions = [
    "La déperdition thermique linéique et totale de la ligne nue ;",
    "L'économie thermique annuelle apportée par le calorifuge ;",
    "L'économie en MAD et le temps de retour sur investissement (TRI en mois)."
]
    formulas = [
    "q = \\pi \\cdot D_e \\cdot h \\cdot (T_p - T_a)",
    "\\Phi = q \\cdot L",
    "\\text{Gain} = \\Phi \\cdot \\eta_{\\text{iso}} \\cdot t \\cdot c_{\\text{th}}",
    "\\text{TRI} = \\frac{C_{\\text{inv}}}{\\text{Gain}}"
]
    formulas_tex = [
    "q = \\pi \\cdot D_e \\cdot h \\cdot (T_p - T_a)",
    "\\Phi = q \\cdot L",
    "\\text{Gain} = \\Phi \\cdot \\eta_{\\text{iso}} \\cdot t \\cdot c_{\\text{th}}",
    "\\text{TRI} = \\frac{C_{\\text{inv}}}{\\text{Gain}}"
]
    answer_key = [
    "Perte linéique = 587,2 W/m ; Puissance perdue totale = 35,2 kW",
    "Économie annuelle = 186 013 kWh/an",
    "Gain = 78 126 MAD/an ; TRI = 3,2 mois"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
