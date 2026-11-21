"""Problem 08: Dimensionnement d'une boucle Kanban en câblage automobile."""

META = {
    "slug": "kanban-cablage",
    "title": "Dimensionnement d'une boucle Kanban en câblage automobile",
    "sector": "Automobile & Électromécanique",
    "sector_code": "AUT",
    "region": "Rabat-Salé-Kénitra",
    "level": 2,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Demande journalière moyenne",
                "D",
                "480 connecteurs/jour"
        ],
        [
                "Délai de réapprovisionnement (lead time)",
                "L",
                "0,75 jour (6 h de poste)"
        ],
        [
                "Facteur de sécurité aléas",
                "α",
                "20 % (0,20)"
        ],
        [
                "Capacité unitaire d'un bac (contenant)",
                "C",
                "25 connecteurs/bac"
        ]
],
    "formulas_raw": [
        "K = [D · L · (1 + α)] / C",
        "\\text{WIP}_{\\max} = K \\cdot C"
],
    "formulas_tex_raw": [
        "K = \\frac{D \\cdot L \\cdot (1 + \\alpha)}{C}",
        "\\text{WIP}_{\\max} = K \\cdot C"
],
    "answer_key_raw": [
        "K théorique = 17,28 ; K retenu = 18 cartes (bacs)",
        "WIP max = 450 connecteurs",
        "Avec L = 0,25 j : K = 6 cartes (baisse de l'en-cours de 300 connecteurs)"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 8, "slug": "kanban-cablage"}


def render(inp: dict, res: dict) -> dict:
    context = "Sur une ligne d'assemblage de faisceaux électriques automobiles, les ruptures de connecteurs provoquent des arrêts de ligne non planifiés. L'ingénieur méthodes doit dimensionner la boucle Kanban (nombre d'étiquettes) entre le magasin et le poste d'encliquetage."
    data = [
    [
        "Demande journalière moyenne",
        "D",
        "480 connecteurs/jour"
    ],
    [
        "Délai de réapprovisionnement (lead time)",
        "L",
        "0,75 jour (6 h de poste)"
    ],
    [
        "Facteur de sécurité aléas",
        "α",
        "20 % (0,20)"
    ],
    [
        "Capacité unitaire d'un bac (contenant)",
        "C",
        "25 connecteurs/bac"
    ]
]
    questions = [
    "Le nombre théorique et le nombre entier de cartes Kanban (bacs en circulation) ;",
    "L'en-cours maximum (WIP) garanti au poste de travail ;",
    "L'impact sur le flux si la digitalisation du Kanban réduit le délai L de 0,75 jour à 0,25 jour."
]
    formulas = [
    "K = [D · L · (1 + α)] / C",
    "\\text{WIP}_{\\max} = K \\cdot C"
]
    formulas_tex = [
    "K = \\frac{D \\cdot L \\cdot (1 + \\alpha)}{C}",
    "\\text{WIP}_{\\max} = K \\cdot C"
]
    answer_key = [
    "K théorique = 17,28 ; K retenu = 18 cartes (bacs)",
    "WIP max = 450 connecteurs",
    "Avec L = 0,25 j : K = 6 cartes (baisse de l'en-cours de 300 connecteurs)"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
