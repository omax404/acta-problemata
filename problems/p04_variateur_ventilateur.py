"""Problem 04: Gain d'un variateur sur un ventilateur de process."""

META = {
    "slug": "variateur-ventilateur",
    "title": "Gain d'un variateur sur un ventilateur de process",
    "sector": "Matériaux de construction",
    "sector_code": "MAT",
    "region": "Marrakech-Safi",
    "level": 2,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Puissance nominale",
                "Pn",
                "55 kW"
        ],
        [
                "Puissance avec volet à 70 % de débit",
                "Pv",
                "85 % de Pn"
        ],
        [
                "Débit moyen",
                "Q/Qn",
                "0,70"
        ],
        [
                "Rendement du variateur",
                "ηv",
                "0,97"
        ],
        [
                "Fonctionnement",
                "h",
                "7 000 h/an"
        ],
        [
                "Tarif électricité",
                "c",
                "1,1 MAD/kWh"
        ]
],
    "formulas_raw": [
        "P ∝ n³  et  Q ∝ n  ⇒  P = Pn·(Q/Qn)³",
        "P_variateur = Pn·(Q/Qn)³ / ηv"
],
    "formulas_tex_raw": [
        "P\\propto n^{3},\\quad Q\\propto n\\;\\Rightarrow\\;P=P_n\\left(\\frac{Q}{Q_n}\\right)^{3}",
        "P_{var}=\\frac{P_n\\,(Q/Q_n)^{3}}{\\eta_v}"
],
    "answer_key_raw": [
        "Volet : 46,75 kW ; variateur : 19,45 kW",
        "Économie = 191 111 kWh/an = 210 222 MAD/an",
        "Retour = prix installé / économie annuelle (prix fournisseur à renseigner)"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 4, "slug": "variateur-ventilateur"}


def render(inp: dict, res: dict) -> dict:
    context = "Un ventilateur de dépoussiérage de 55 kW est régulé par un volet d'étranglement et tourne en moyenne à 70 % du débit nominal. L'équipe maintenance envisage un variateur de fréquence et veut savoir s'il se rembourse vite. Hypothèse : pas de pression statique ; la loi cubique surestime le gain si le circuit a une hauteur statique."
    data = [
    [
        "Puissance nominale",
        "Pn",
        "55 kW"
    ],
    [
        "Puissance avec volet à 70 % de débit",
        "Pv",
        "85 % de Pn"
    ],
    [
        "Débit moyen",
        "Q/Qn",
        "0,70"
    ],
    [
        "Rendement du variateur",
        "ηv",
        "0,97"
    ],
    [
        "Fonctionnement",
        "h",
        "7 000 h/an"
    ],
    [
        "Tarif électricité",
        "c",
        "1,1 MAD/kWh"
    ]
]
    questions = [
    "La puissance absorbée avec volet et avec variateur (lois de similitude) ;",
    "L'économie annuelle en kWh et en MAD ;",
    "Le temps de retour sur investissement pour un variateur dont le prix est à demander à un fournisseur."
]
    formulas = [
    "P ∝ n³  et  Q ∝ n  ⇒  P = Pn·(Q/Qn)³",
    "P_variateur = Pn·(Q/Qn)³ / ηv"
]
    formulas_tex = [
    "P\\propto n^{3},\\quad Q\\propto n\\;\\Rightarrow\\;P=P_n\\left(\\frac{Q}{Q_n}\\right)^{3}",
    "P_{var}=\\frac{P_n\\,(Q/Q_n)^{3}}{\\eta_v}"
]
    answer_key = [
    "Volet : 46,75 kW ; variateur : 19,45 kW",
    "Économie = 191 111 kWh/an = 210 222 MAD/an",
    "Retour = prix installé / économie annuelle (prix fournisseur à renseigner)"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
