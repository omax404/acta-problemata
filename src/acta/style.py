"""Per-domain art direction for the broadside: one accent colour per domain.

The Typst template reads `accent` from edition.json (falling back to the house
signal orange), so a single JSON field re-themes the whole sheet — hero block,
info bar, worksheet stamp, footer — without touching the layout contract.
Colours are kept bright enough for the graphite display type that sits on them.
"""

DEFAULT_ACCENT = "#ff4d00"                      # signal orange: the Mechanical / house default

DOMAIN_ACCENTS: dict[str, str] = {
    "Mechanical": "#ff4d00",                    # signal orange
    "Aerospace":  "#6f7dff",                    # indigo
    "Electrical": "#ffd60a",                    # high-vis yellow
    "Chemical":   "#27c07d",                    # process green
    "Civil":      "#e07b39",                    # terracotta
    "Thermal":    "#ff2d55",                    # heat red
    "Materials":  "#b18cff",                    # violet
    "Fluids":     "#00b4d8",                    # cyan
}


def accent_for(domain: str) -> str:
    return DOMAIN_ACCENTS.get(domain, DEFAULT_ACCENT)
