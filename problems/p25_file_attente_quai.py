"""Problem 25: Modélisation de file d'attente M/M/1 à un quai d'expédition."""

META = {
    "slug": "file-attente-quai",
    "title": "Modélisation de file d'attente M/M/1 à un quai d'expédition",
    "sector": "Logistique & Distribution",
    "sector_code": "LOG",
    "region": "Casablanca-Settat",
    "level": 3,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Taux moyen d'arrivée des camions",
                "λ",
                "3,2 camions/h (loi de Poisson)"
        ],
        [
                "Capacité moyenne de traitement du quai",
                "μ",
                "4,0 camions/h (loi exponentielle)"
        ]
],
    "formulas_raw": [
        "\\rho = \\frac{\\lambda}{\\mu}",
        "L_q = \\frac{\\rho^2}{1 - \\rho}",
        "W_q = \\frac{L_q}{\\lambda} = \\frac{\\rho}{\\mu - \\lambda}"
],
    "formulas_tex_raw": [
        "\\rho = \\frac{\\lambda}{\\mu}",
        "L_q = \\frac{\\rho^2}{1 - \\rho}",
        "W_q = \\frac{\\rho}{\\mu - \\lambda}"
],
    "answer_key_raw": [
        "Intensité de trafic ρ = 80,0 %",
        "Longueur moyenne de file Lq = 3,2 camions",
        "Temps d'attente moyen Wq = 60 min (1,00 h)"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 25, "slug": "file-attente-quai"}


def render(inp: dict, res: dict) -> dict:
    context = "Le quai de pesée et de chargement d'un silo portuaire connaît des congestions répétées de camions aux heures de pointe. Le responsable d'exploitation utilise le modèle de file d'attente markovien M/M/1 pour évaluer l'opportunité d'ouvrir une seconde balance."
    data = [
    [
        "Taux moyen d'arrivée des camions",
        "λ",
        "3,2 camions/h (loi de Poisson)"
    ],
    [
        "Capacité moyenne de traitement du quai",
        "μ",
        "4,0 camions/h (loi exponentielle)"
    ]
]
    questions = [
    "Le taux d'utilisation du quai (intensité de trafic ρ) ;",
    "Le nombre moyen de camions qui patientent dans la file d'attente (Lq) ;",
    "Le temps moyen d'attente d'un transporteur avant le début du chargement (Wq en minutes)."
]
    formulas = [
    "\\rho = \\frac{\\lambda}{\\mu}",
    "L_q = \\frac{\\rho^2}{1 - \\rho}",
    "W_q = \\frac{L_q}{\\lambda} = \\frac{\\rho}{\\mu - \\lambda}"
]
    formulas_tex = [
    "\\rho = \\frac{\\lambda}{\\mu}",
    "L_q = \\frac{\\rho^2}{1 - \\rho}",
    "W_q = \\frac{\\rho}{\\mu - \\lambda}"
]
    answer_key = [
    "Intensité de trafic ρ = 80,0 %",
    "Longueur moyenne de file Lq = 3,2 camions",
    "Temps d'attente moyen Wq = 60 min (1,00 h)"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
