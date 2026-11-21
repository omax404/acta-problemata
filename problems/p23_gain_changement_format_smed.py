"""Problem 23: Gain de capacité par réduction de temps de changement (SMED)."""

META = {
    "slug": "gain-changement-format-smed",
    "title": "Gain de capacité par réduction de temps de changement (SMED)",
    "sector": "Agroalimentaire",
    "sector_code": "AGR",
    "region": "Fès-Meknès",
    "level": 2,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Temps initial de changement de format",
                "T₁",
                "75 min"
        ],
        [
                "Temps de changement atteint après SMED",
                "T₂",
                "22 min"
        ],
        [
                "Nombre de changements de série",
                "N",
                "14 changements/semaine"
        ],
        [
                "Semaines d'activité annuelle",
                "S",
                "48 semaines/an"
        ],
        [
                "Cadence nominale de la ligne",
                "C",
                "1 200 briques/h"
        ]
],
    "formulas_raw": [
        "\\Delta t = T_1 - T_2",
        "\\text{Heures gagnées} = \\frac{\\Delta t \\cdot N \\cdot S}{60}",
        "\\text{Gain production} = \\text{Heures} \\cdot C"
],
    "formulas_tex_raw": [
        "\\Delta t = T_1 - T_2",
        "\\text{Heures gagnées} = \\frac{\\Delta t \\cdot N \\cdot S}{60}",
        "\\text{Gain prod} = \\text{Heures} \\cdot C"
],
    "answer_key_raw": [
        "Gain par changement = 53 min (70,7 %)",
        "Temps de production dégagé = 594 heures/an",
        "Production additionnelle possible = 712 320 briques/an"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 23, "slug": "gain-changement-format-smed"}


def render(inp: dict, res: dict) -> dict:
    context = "Une ligne de conditionnement de jus d'agrumes subit de fréquents changements de formats de briques. Un chantier SMED a permis de convertir les réglages internes en tâches externes préparées à l'avance."
    data = [
    [
        "Temps initial de changement de format",
        "T₁",
        "75 min"
    ],
    [
        "Temps de changement atteint après SMED",
        "T₂",
        "22 min"
    ],
    [
        "Nombre de changements de série",
        "N",
        "14 changements/semaine"
    ],
    [
        "Semaines d'activité annuelle",
        "S",
        "48 semaines/an"
    ],
    [
        "Cadence nominale de la ligne",
        "C",
        "1 200 briques/h"
    ]
]
    questions = [
    "Le gain de temps de calage par changement et en pourcentage ;",
    "Le nombre d'heures de production libérées sur l'année ;",
    "Le supplément de production annuel permis par cette disponibilité recouvrée."
]
    formulas = [
    "\\Delta t = T_1 - T_2",
    "\\text{Heures gagnées} = \\frac{\\Delta t \\cdot N \\cdot S}{60}",
    "\\text{Gain production} = \\text{Heures} \\cdot C"
]
    formulas_tex = [
    "\\Delta t = T_1 - T_2",
    "\\text{Heures gagnées} = \\frac{\\Delta t \\cdot N \\cdot S}{60}",
    "\\text{Gain prod} = \\text{Heures} \\cdot C"
]
    answer_key = [
    "Gain par changement = 53 min (70,7 %)",
    "Temps de production dégagé = 594 heures/an",
    "Production additionnelle possible = 712 320 briques/an"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
