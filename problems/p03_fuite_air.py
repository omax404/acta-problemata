"""Problem 03: Coût d'une fuite d'air comprimé."""

META = {
    "slug": "fuite-air",
    "title": "Coût d'une fuite d'air comprimé",
    "sector": "Textile",
    "sector_code": "TEX",
    "region": "Tanger-Tétouan-Al Hoceïma",
    "level": 1,
    "status": "realistic",
    "source_url": "",
    "lang": "fr"
}

INPUTS = {
    "data_raw": [
        [
                "Diamètre de l'orifice",
                "d",
                "3 mm"
        ],
        [
                "Pression relative réseau",
                "pg",
                "7 bar"
        ],
        [
                "Température de l'air",
                "T",
                "20 °C"
        ],
        [
                "Conditions de référence",
                "ISO 1217",
                "1,013 bar, 20 °C"
        ],
        [
                "Coefficient de décharge",
                "Cd",
                "0,65"
        ],
        [
                "Énergie spécifique du compresseur",
                "e",
                "0,11 kWh/Nm³"
        ],
        [
                "Fonctionnement",
                "h",
                "8 000 h/an"
        ],
        [
                "Tarif électricité",
                "c",
                "1,2 MAD/kWh"
        ]
],
    "formulas_raw": [
        "ṁ = Cd·A·p·√(γ/(R·T)) · (2/(γ+1))^((γ+1)/(2(γ−1)))",
        "Qₙ = ṁ / ρₙ  avec ρₙ = p₀/(R·T₀)",
        "Coût = Qₙ · e · h · c"
],
    "formulas_tex_raw": [
        "\\dot m=C_d\\,A\\,p\\sqrt{\\frac{\\gamma}{R\\,T}}\\left(\\frac{2}{\\gamma+1}\\right)^{\\frac{\\gamma+1}{2(\\gamma-1)}}",
        "Q_n=\\frac{\\dot m}{\\rho_n},\\quad \\rho_n=\\frac{p_0}{R\\,T_0}",
        "\\text{Coût}=Q_n\\,e\\,h\\,c"
],
    "answer_key_raw": [
        "ṁ = 8,69 g/s",
        "Qn = 26,0 Nm³/h",
        "Puissance perdue = 2,9 kW ; coût annuel = 27 435 MAD"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 3, "slug": "fuite-air"}


def render(inp: dict, res: dict) -> dict:
    context = "Lors d'un audit énergétique d'un atelier de confection, une fuite de 3 mm est repérée sur un réseau d'air comprimé qui tourne en continu. Le responsable maintenance demande de chiffrer ce que coûte cette seule fuite par an."
    data = [
    [
        "Diamètre de l'orifice",
        "d",
        "3 mm"
    ],
    [
        "Pression relative réseau",
        "pg",
        "7 bar"
    ],
    [
        "Température de l'air",
        "T",
        "20 °C"
    ],
    [
        "Conditions de référence",
        "ISO 1217",
        "1,013 bar, 20 °C"
    ],
    [
        "Coefficient de décharge",
        "Cd",
        "0,65"
    ],
    [
        "Énergie spécifique du compresseur",
        "e",
        "0,11 kWh/Nm³"
    ],
    [
        "Fonctionnement",
        "h",
        "8 000 h/an"
    ],
    [
        "Tarif électricité",
        "c",
        "1,2 MAD/kWh"
    ]
]
    questions = [
    "Le débit massique de la fuite (écoulement supposé sonique) ;",
    "Le débit volumique en Nm³/h ;",
    "La puissance perdue et le coût annuel, puis le gain d'une campagne de réparation."
]
    formulas = [
    "ṁ = Cd·A·p·√(γ/(R·T)) · (2/(γ+1))^((γ+1)/(2(γ−1)))",
    "Qₙ = ṁ / ρₙ  avec ρₙ = p₀/(R·T₀)",
    "Coût = Qₙ · e · h · c"
]
    formulas_tex = [
    "\\dot m=C_d\\,A\\,p\\sqrt{\\frac{\\gamma}{R\\,T}}\\left(\\frac{2}{\\gamma+1}\\right)^{\\frac{\\gamma+1}{2(\\gamma-1)}}",
    "Q_n=\\frac{\\dot m}{\\rho_n},\\quad \\rho_n=\\frac{p_0}{R\\,T_0}",
    "\\text{Coût}=Q_n\\,e\\,h\\,c"
]
    answer_key = [
    "ṁ = 8,69 g/s",
    "Qn = 26,0 Nm³/h",
    "Puissance perdue = 2,9 kW ; coût annuel = 27 435 MAD"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
