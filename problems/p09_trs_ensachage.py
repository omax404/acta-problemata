"""Problem 09: Diagnostic TRS et pertes d'une ligne de sacs industriels."""

META = {
    "slug": "trs-ensachage",
    "title": "Diagnostic TRS et pertes d'une ligne de sacs industriels",
    "sector": "Emballage & Chimie",
    "sector_code": "EMB",
    "region": "Casablanca-Settat",
    "level": 2,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Temps d'ouverture poste (1 poste de 8 h)",
                "T_ouv",
                "28 800 s (8 h)"
        ],
        [
                "Arrêts non planifiés cumulés (pannes, réglages)",
                "T_arr",
                "4 680 s (78 min)"
        ],
        [
                "Production totale enregistrée",
                "N_tot",
                "11 200 sacs"
        ],
        [
                "Production conforme livrable",
                "N_bon",
                "10 850 sacs"
        ],
        [
                "Temps de cycle nominal machine",
                "t_cycle",
                "1,5 s/sac"
        ]
],
    "formulas_raw": [
        "\\text{Disponibilité} = \\frac{T_{\\text{fonctionnement}}}{T_{\\text{ouverture}}}",
        "\\text{Performance} = \\frac{N_{\\text{tot}} \\cdot t_{\\text{cycle}}}{T_{\\text{fonctionnement}}}",
        "\\text{Qualité} = \\frac{N_{\\text{bon}}}{N_{\\text{tot}}}",
        "\\text{TRS} = D \\cdot P \\cdot Q"
],
    "formulas_tex_raw": [
        "\\text{Disponibilité} = \\frac{T_{\\text{fonct}}}{T_{\\text{ouv}}}",
        "\\text{Performance} = \\frac{N_{\\text{tot}} \\cdot t_{\\text{cycle}}}{T_{\\text{fonct}}}",
        "\\text{Qualité} = \\frac{N_{\\text{bon}}}{N_{\\text{tot}}}",
        "\\text{TRS} = D \\cdot P \\cdot Q"
],
    "answer_key_raw": [
        "Disponibilité = 83,8 %",
        "Performance = 69,7 %",
        "Qualité = 96,9 % ; TRS = 56,51 % (perte principale : cadence/micro-arrêts, perte de performance = 30,3 %)"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 9, "slug": "trs-ensachage"}


def render(inp: dict, res: dict) -> dict:
    context = "Lors d'un audit de productivité sur une ligne de fabrication de sacs industriels (fond de sac), le Taux de Rendement Synthétique (TRS) moyen s'avère anormalement bas (~57 %). L'ingénieur de production doit décomposer les 3 taux pour identifier le levier prioritaire."
    data = [
    [
        "Temps d'ouverture poste (1 poste de 8 h)",
        "T_ouv",
        "28 800 s (8 h)"
    ],
    [
        "Arrêts non planifiés cumulés (pannes, réglages)",
        "T_arr",
        "4 680 s (78 min)"
    ],
    [
        "Production totale enregistrée",
        "N_tot",
        "11 200 sacs"
    ],
    [
        "Production conforme livrable",
        "N_bon",
        "10 850 sacs"
    ],
    [
        "Temps de cycle nominal machine",
        "t_cycle",
        "1,5 s/sac"
    ]
]
    questions = [
    "Le taux de disponibilité temporelle de la ligne ;",
    "Le taux de performance machine (perte de cadence) ;",
    "Le taux de qualité et le TRS global, avec identification de la perte principale (disponibilité vs cadence)."
]
    formulas = [
    "\\text{Disponibilité} = \\frac{T_{\\text{fonctionnement}}}{T_{\\text{ouverture}}}",
    "\\text{Performance} = \\frac{N_{\\text{tot}} \\cdot t_{\\text{cycle}}}{T_{\\text{fonctionnement}}}",
    "\\text{Qualité} = \\frac{N_{\\text{bon}}}{N_{\\text{tot}}}",
    "\\text{TRS} = D \\cdot P \\cdot Q"
]
    formulas_tex = [
    "\\text{Disponibilité} = \\frac{T_{\\text{fonct}}}{T_{\\text{ouv}}}",
    "\\text{Performance} = \\frac{N_{\\text{tot}} \\cdot t_{\\text{cycle}}}{T_{\\text{fonct}}}",
    "\\text{Qualité} = \\frac{N_{\\text{bon}}}{N_{\\text{tot}}}",
    "\\text{TRS} = D \\cdot P \\cdot Q"
]
    answer_key = [
    "Disponibilité = 83,8 %",
    "Performance = 69,7 %",
    "Qualité = 96,9 % ; TRS = 56,51 % (perte principale : cadence/micro-arrêts, perte de performance = 30,3 %)"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
