"""Problem 01: Dimensionnement d'une ligne de pompage."""
import math

from problems.common import fr

META = {
    "slug": "pompage",
    "title": "Dimensionnement d'une ligne de pompage",
    "sector": "Agroalimentaire",
    "sector_code": "AGR",
    "region": "Fès-Meknès",
    "level": 2,
    "status": "realistic",
    "source_url": "",
    "lang": "fr",
}

INPUTS = {
    "Q_m3h": 40.0,       # Débit volumique en m³/h
    "D_m": 0.105,        # Diamètre intérieur en m (105 mm)
    "L_m": 250.0,        # Longueur de la conduite en m
    "dz_m": 18.0,        # Dénivelé géométrique en m
    "eps_m": 4.5e-5,     # Rugosité absolue en m (0.045 mm)
    "K_sing": 6.5,       # Somme des coefficients de pertes singulières
    "eta": 0.68,         # Rendement global de la pompe
    "nu_m2s": 1.004e-6,  # Viscosité cinématique de l'eau en m²/s (20 °C)
    "g_ms2": 9.81,       # Accélération de la pesanteur en m/s²
    "rho_kgm3": 1000.0,  # Masse volumique du fluide en kg/m³
}


def solve(inp: dict) -> dict:
    Q = inp["Q_m3h"] / 3600.0
    D = inp["D_m"]
    A = math.pi * D * D / 4.0
    v = Q / A
    Re = v * D / inp["nu_m2s"]
    f = 0.25 / (math.log10(inp["eps_m"] / (3.7 * D) + 5.74 / (Re ** 0.9)) ** 2)
    hf = f * inp["L_m"] / D * (v * v) / (2.0 * inp["g_ms2"])
    hm = inp["K_sing"] * (v * v) / (2.0 * inp["g_ms2"])
    H = inp["dz_m"] + hf + hm
    P = inp["rho_kgm3"] * inp["g_ms2"] * Q * H / inp["eta"]
    return {
        "v": v,
        "Re": Re,
        "f": f,
        "hf": hf,
        "hm": hm,
        "H": H,
        "P": P,
    }


def render(inp: dict, res: dict) -> dict:
    context = (
        "Une unité de transformation alimente un réservoir en hauteur depuis une cuve de réception. "
        "La pompe actuelle consomme trop d'énergie par rapport au besoin hydraulique réel. "
        "Un technicien junior doit vérifier la hauteur manométrique réelle et proposer une pompe adaptée."
    )
    data = [
        ["Débit", "Q", f"{fr(inp['Q_m3h'], 0)} m³/h"],
        ["Longueur", "L", f"{fr(inp['L_m'], 0)} m"],
        ["Diamètre intérieur", "D", f"{fr(inp['D_m']*1000, 0)} mm"],
        ["Dénivelé", "Δz", f"{fr(inp['dz_m'], 0)} m"],
        ["Rugosité", "ε", f"{fr(inp['eps_m']*1000, 3)} mm"],
        ["Singularités", "ΣK", f"{fr(inp['K_sing'], 1)}"],
        ["Viscosité cinématique", "ν", "1,004·10⁻⁶ m²/s"],
        ["Rendement", "η", f"{fr(inp['eta'], 2)}"],
    ]
    questions = [
        "La vitesse v, le nombre de Reynolds Re et le coefficient de frottement f ;",
        "La hauteur manométrique totale H et la puissance à l'arbre ;",
        "Une recommandation commentée (point de fonctionnement, marge, variateur de vitesse).",
    ]
    formulas = [
        "H = Δz + (f·L/D + ΣK)·v²/2g",
        "f = 0,25 / [log10( ε/(3,7·D) + 5,74/Re^0,9 )]²  (Swamee-Jain)",
        "P = ρ·g·Q·H / η",
    ]
    formulas_tex = [
        "H=\\Delta z+\\Bigl(f\\frac{L}{D}+\\sum K\\Bigr)\\frac{v^{2}}{2g}",
        "f=\\frac{0{,}25}{\\left[\\log_{10}\\!\\left(\\frac{\\varepsilon}{3{,}7\\,D}+\\frac{5{,}74}{\\mathrm{Re}^{0{,}9}}\\right)\\right]^{2}}",
        "P=\\frac{\\rho\\, g\\, Q\\, H}{\\eta}",
    ]
    answer_key = [
        f"v = {fr(res['v'])} m/s ; Re = {fr(res['Re'], 0)} ; f = {fr(res['f'], 4)}",
        f"H = {fr(res['H'], 1)} m (frottement {fr(res['hf'])} m, singularités {fr(res['hm'])} m)",
        f"P arbre = {fr(res['P']/1000.0)} kW",
    ]
    return {
        "context": context,
        "data": data,
        "questions": questions,
        "formulas": formulas,
        "formulas_tex": formulas_tex,
        "answer_key": answer_key,
    }
