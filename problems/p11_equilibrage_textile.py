"""Problem 11: Équilibrage de ligne d'assemblage textile sous contraintes d'opérateurs."""

META = {
    "slug": "equilibrage-textile",
    "title": "Équilibrage de ligne d'assemblage textile sous contraintes d'opérateurs",
    "sector": "Textile & Confection",
    "sector_code": "TEX",
    "region": "Tanger-Tétouan-Al Hoceïma",
    "level": 3,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Somme des temps opératoires d'une pièce",
                "Σt",
                "320 s (5 min 20 s)"
        ],
        [
                "Temps de cycle requis (takt time client)",
                "Tc",
                "45 s/pièce"
        ],
        [
                "Temps d'ouverture d'un poste",
                "T_ouv",
                "7,5 h/jour (27 000 s)"
        ],
        [
                "Objectif de production journalier",
                "Obj",
                "600 pièces/jour"
        ]
],
    "formulas_raw": [
        "N_{\\text{théo}} = \\frac{\\sum t_i}{T_c}",
        "\\text{Efficience} = \\frac{\\sum t_i}{N_{\\text{retenu}} \\cdot T_c}",
        "\\text{Perte d'équilibrage} = (N \\cdot T_c) - \\sum t_i"
],
    "formulas_tex_raw": [
        "N_{\\text{théo}} = \\frac{\\sum t_i}{T_c}",
        "\\text{Efficience} = \\frac{\\sum t_i}{N_{\\text{retenu}} \\cdot T_c}",
        "\\text{Perte} = (N \\cdot T_c) - \\sum t_i"
],
    "answer_key_raw": [
        "N théorique = 7,11 ; N retenu = 8 postes de travail",
        "Efficience = 88,9 %",
        "Perte d'équilibrage = 40 s par vêtement (soit 6,67 h d'inactivité cumulée par jour)"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 11, "slug": "equilibrage-textile"}


def render(inp: dict, res: dict) -> dict:
    context = "Un atelier de confection textile produit des blousons techniques. Face à des commandes instables et des temps de réglage machine, le chef d'atelier doit rééquilibrer la ligne de couture pour atteindre le temps de cycle client (takt time)."
    data = [
    [
        "Somme des temps opératoires d'une pièce",
        "Σt",
        "320 s (5 min 20 s)"
    ],
    [
        "Temps de cycle requis (takt time client)",
        "Tc",
        "45 s/pièce"
    ],
    [
        "Temps d'ouverture d'un poste",
        "T_ouv",
        "7,5 h/jour (27 000 s)"
    ],
    [
        "Objectif de production journalier",
        "Obj",
        "600 pièces/jour"
    ]
]
    questions = [
    "Le nombre théorique et le nombre entier minimum de postes opérateurs requis ;",
    "L'efficience d'équilibrage de la ligne théorique ;",
    "Le temps d'inactivité cumulé (perte d'équilibrage) par pièce produite."
]
    formulas = [
    "N_{\\text{théo}} = \\frac{\\sum t_i}{T_c}",
    "\\text{Efficience} = \\frac{\\sum t_i}{N_{\\text{retenu}} \\cdot T_c}",
    "\\text{Perte d'équilibrage} = (N \\cdot T_c) - \\sum t_i"
]
    formulas_tex = [
    "N_{\\text{théo}} = \\frac{\\sum t_i}{T_c}",
    "\\text{Efficience} = \\frac{\\sum t_i}{N_{\\text{retenu}} \\cdot T_c}",
    "\\text{Perte} = (N \\cdot T_c) - \\sum t_i"
]
    answer_key = [
    "N théorique = 7,11 ; N retenu = 8 postes de travail",
    "Efficience = 88,9 %",
    "Perte d'équilibrage = 40 s par vêtement (soit 6,67 h d'inactivité cumulée par jour)"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
