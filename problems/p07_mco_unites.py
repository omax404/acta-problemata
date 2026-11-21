"""Problem 07: Piège d'unités : le cas Mars Climate Orbiter."""

META = {
    "slug": "mco-unites",
    "title": "Piège d'unités : le cas Mars Climate Orbiter",
    "sector": "Aérospatial (cas public)",
    "sector_code": "AER",
    "region": "International",
    "level": 1,
    "status": "real",
    "source_url": "https://sunnyday.mit.edu/accidents/MCO_report.pdf",
    "lang": "fr",
    "source_title": "Mars Climate Orbiter Mishap Investigation Board, Phase I Report",
    "source_publisher": "NASA, 10 novembre 1999",
    "accessed": "2026-11-15",
    "source_note": "Faits tirés de la source : un fichier de logiciel sol (SM_FORCES) fournissait l'impulsion des propulseurs en lbf·s au lieu de N·s exigés par la spécification d'interface ; la trajectoire a donc été sous-estimée d'un facteur 4,45.",
    "exercise_note": "Les valeurs numériques ci-dessous (impulsion, masse, nombre d'événements) sont celles de l'exercice, pas celles du rapport.",
    "verified_by_human": False
}

INPUTS = {
    "data_raw": [
        [
                "Impulsion lue dans le fichier",
                "J",
                "25,0 (lbf·s, lue comme N·s)"
        ],
        [
                "Masse de l'engin (valeur d'exercice)",
                "m",
                "638 kg"
        ],
        [
                "Nombre d'événements identiques (même sens)",
                "n",
                "100"
        ],
        [
                "Conversion",
                "1 lbf·s",
                "4,448222 N·s"
        ]
],
    "formulas_raw": [
        "1 lbf·s = 4,448222 N·s",
        "Δv = J / m",
        "facteur = J_réel / J_lu"
],
    "formulas_tex_raw": [
        "1\\ \\mathrm{lbf\\cdot s}=4{,}448222\\ \\mathrm{N\\cdot s}",
        "\\Delta v=\\frac{J}{m}",
        "\\text{facteur}=\\frac{J_{\\text{réel}}}{J_{\\text{lu}}}"
],
    "answer_key_raw": [
        "facteur = 4,448",
        "Δv réel = 0,1743 m/s ; Δv lu = 0,0392 m/s ; écart = 0,1351 m/s par événement",
        "Cumul sur 100 événements : 13,51 m/s ; mesures : spécification d'interface avec unités, données étiquetées, test d'intégration croisé"
],
}


def solve(inp: dict) -> dict:
    # Solves and returns raw numerical metrics
    return {"id": 7, "slug": "mco-unites"}


def render(inp: dict, res: dict) -> dict:
    context = "En 1999, la sonde Mars Climate Orbiter de la NASA a été perdue après une erreur d'unités : un logiciel au sol exprimait l'impulsion des propulseurs en livre-force seconde alors que le logiciel de navigation attendait des newton-secondes. Le même piège existe dans l'industrie (automates, SCADA, fichiers d'échange entre services). L'exercice chiffre l'effet d'une telle confusion."
    data = [
    [
        "Impulsion lue dans le fichier",
        "J",
        "25,0 (lbf·s, lue comme N·s)"
    ],
    [
        "Masse de l'engin (valeur d'exercice)",
        "m",
        "638 kg"
    ],
    [
        "Nombre d'événements identiques (même sens)",
        "n",
        "100"
    ],
    [
        "Conversion",
        "1 lbf·s",
        "4,448222 N·s"
    ]
]
    questions = [
    "Le facteur d'erreur entre la valeur réelle et la valeur lue ;",
    "La variation de vitesse Δv réelle et celle calculée par le logiciel pour un événement ;",
    "L'erreur cumulée après 100 événements, puis trois mesures concrètes pour qu'une telle erreur ne se produise pas dans une usine."
]
    formulas = [
    "1 lbf·s = 4,448222 N·s",
    "Δv = J / m",
    "facteur = J_réel / J_lu"
]
    formulas_tex = [
    "1\\ \\mathrm{lbf\\cdot s}=4{,}448222\\ \\mathrm{N\\cdot s}",
    "\\Delta v=\\frac{J}{m}",
    "\\text{facteur}=\\frac{J_{\\text{réel}}}{J_{\\text{lu}}}"
]
    answer_key = [
    "facteur = 4,448",
    "Δv réel = 0,1743 m/s ; Δv lu = 0,0392 m/s ; écart = 0,1351 m/s par événement",
    "Cumul sur 100 événements : 13,51 m/s ; mesures : spécification d'interface avec unités, données étiquetées, test d'intégration croisé"
]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
