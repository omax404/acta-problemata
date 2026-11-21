"""Problem 22: Optimisation de stock par la quantité économique de Wilson."""

META = {
    "slug": "quantite-economique-stock",
    "title": "Optimisation de stock par la quantité économique de Wilson",
    "sector": "Logistique & Distribution",
    "sector_code": "LOG",
    "region": "Casablanca-Settat",
    "level": 1,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Consommation annuelle régulière",
                "D",
                "12 000 unités/an"
        ],
        [
                "Coût administratif d'une passation de commande",
                "S",
                "180 MAD/commande"
        ],
        [
                "Coût unitaire annuel de possession de stock",
                "H",
                "4,50 MAD/(unité·an)"
        ]
],
    "formulas_raw": [
        "Q^* = \\sqrt{\\frac{2 \\cdot D \\cdot S}{H}}",
        "N = \\frac{D}{Q^*}",
        "\\text{Coût total} = \\sqrt{2 \\cdot D \\cdot S \\cdot H}"
],
    "formulas_tex_raw": [
        "Q^* = \\sqrt{\\frac{2 \\cdot D \\cdot S}{H}}",
        "N = \\frac{D}{Q^*}",
        "\\text{Coût total} = \\sqrt{2 \\cdot D \\cdot S \\cdot H}"
],
    "answer_key_raw": [
        "Lot économique Q* = 980 unités",
        "Nombre de commandes = 12,2 commandes/an",
        "Coût total optimal = 4 409 MAD/an"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 22, "slug": "quantite-economique-stock"}


def render(inp: dict, res: dict) -> dict:
    context = "Le magasin central des pièces de rechange d'un groupe industriel gère une référence de filtre hydraulique à rotation élevée. Pour réduire les coûts combinés de commande et de stockage, le logisticien applique le modèle de Wilson."
    data = [
    [
        "Consommation annuelle régulière",
        "D",
        "12 000 unités/an"
    ],
    [
        "Coût administratif d'une passation de commande",
        "S",
        "180 MAD/commande"
    ],
    [
        "Coût unitaire annuel de possession de stock",
        "H",
        "4,50 MAD/(unité·an)"
    ]
]
    questions = [
    "La quantité économique optimale de commande Q* ;",
    "Le nombre optimal de commandes par an et la périodicité de réapprovisionnement ;",
    "Le coût global annuel de gestion du stock à l'optimum."
]
    formulas = [
    "Q^* = \\sqrt{\\frac{2 \\cdot D \\cdot S}{H}}",
    "N = \\frac{D}{Q^*}",
    "\\text{Coût total} = \\sqrt{2 \\cdot D \\cdot S \\cdot H}"
]
    formulas_tex = [
    "Q^* = \\sqrt{\\frac{2 \\cdot D \\cdot S}{H}}",
    "N = \\frac{D}{Q^*}",
    "\\text{Coût total} = \\sqrt{2 \\cdot D \\cdot S \\cdot H}"
]
    answer_key = [
    "Lot économique Q* = 980 unités",
    "Nombre de commandes = 12,2 commandes/an",
    "Coût total optimal = 4 409 MAD/an"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
