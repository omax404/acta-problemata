"""Problem 14: Productible d'une centrale solaire photovoltaïque en toiture."""

META = {
    "slug": "solaire-toiture",
    "title": "Productible d'une centrale solaire photovoltaïque en toiture",
    "sector": "Chimie & Plasturgie",
    "sector_code": "CHM",
    "region": "Marrakech-Safi",
    "level": 2,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Surface disponible en toiture",
                "S",
                "1 200 m²"
        ],
        [
                "Puissance surfacique des modules",
                "p",
                "200 Wc/m² (0,20 kWc/m²)"
        ],
        [
                "Gisement solaire annuel incliné",
                "H",
                "1 850 kWh/m²/an"
        ],
        [
                "Facteur de performance de l'installation",
                "PR",
                "0,78 (78 %)"
        ],
        [
                "Tarif électricité réseau",
                "c",
                "1,15 MAD/kWh"
        ]
],
    "formulas_raw": [
        "P_c = S \\cdot p",
        "E_{\\text{an}} = P_c \\cdot H_{\\text{site}} \\cdot \\text{PR} / 1\\text{ kW/m}^2",
        "\\text{Gain} = E_{\\text{an}} \\cdot c"
],
    "formulas_tex_raw": [
        "P_c = S \\cdot p",
        "E_{\\text{an}} = P_c \\cdot H_{\\text{site}} \\cdot \\text{PR} / 1\\text{ kW/m}^2",
        "\\text{Gain} = E_{\\text{an}} \\cdot c"
],
    "answer_key_raw": [
        "Puissance crête = 240 kWc",
        "Production annuelle = 346 320 kWh/an",
        "Économie annuelle = 398 268 MAD/an"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 14, "slug": "solaire-toiture"}


def render(inp: dict, res: dict) -> dict:
    context = "Une usine d'injection plastique dispose d'une toiture bien orientée et souhaite installer des panneaux solaires en autoconsommation sans injection réseau pour écrêter sa facture électrique ONEE."
    data = [
    [
        "Surface disponible en toiture",
        "S",
        "1 200 m²"
    ],
    [
        "Puissance surfacique des modules",
        "p",
        "200 Wc/m² (0,20 kWc/m²)"
    ],
    [
        "Gisement solaire annuel incliné",
        "H",
        "1 850 kWh/m²/an"
    ],
    [
        "Facteur de performance de l'installation",
        "PR",
        "0,78 (78 %)"
    ],
    [
        "Tarif électricité réseau",
        "c",
        "1,15 MAD/kWh"
    ]
]
    questions = [
    "La puissance crête totale installable ;",
    "La production annuelle d'électricité estimée ;",
    "L'économie annuelle réalisée sur la facture d'électricité."
]
    formulas = [
    "P_c = S \\cdot p",
    "E_{\\text{an}} = P_c \\cdot H_{\\text{site}} \\cdot \\text{PR} / 1\\text{ kW/m}^2",
    "\\text{Gain} = E_{\\text{an}} \\cdot c"
]
    formulas_tex = [
    "P_c = S \\cdot p",
    "E_{\\text{an}} = P_c \\cdot H_{\\text{site}} \\cdot \\text{PR} / 1\\text{ kW/m}^2",
    "\\text{Gain} = E_{\\text{an}} \\cdot c"
]
    answer_key = [
    "Puissance crête = 240 kWc",
    "Production annuelle = 346 320 kWh/an",
    "Économie annuelle = 398 268 MAD/an"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
