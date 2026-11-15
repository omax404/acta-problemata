#!/usr/bin/env python3
"""Generates bank/*.json. Every number in answer_key is COMPUTED here from the data, so key and statement cannot drift.
Statuses are all 'realistic' (problem classes). Sector-level only, no company named."""
import json, math, pathlib
fr = lambda x, n=2: f"{x:,.{n}f}".replace(",", " ").replace(".", ",")
OUT = pathlib.Path(__file__).parent / "bank"; OUT.mkdir(exist_ok=True)
bank = []
def add(slug, **k): bank.append({"slug": slug, "lang": "fr", "status": "realistic", "source_url": "", **k})

# 1 -- pump line
Q=40/3600; D=.105; L=250; dz=18; eps=4.5e-5; K=6.5; eta=.68; nu=1.004e-6; g=9.81
A=math.pi*D*D/4; v=Q/A; Re=v*D/nu
f=.25/math.log10(eps/(3.7*D)+5.74/Re**.9)**2
hf=f*L/D*v*v/(2*g); hm=K*v*v/(2*g); H=dz+hf+hm; P=1000*g*Q*H/eta
add("pompage", title="Dimensionnement d'une ligne de pompage", sector="Agroalimentaire", sector_code="AGR", region="Fès-Meknès", level=2,
 context="Une unité de transformation alimente un réservoir en hauteur depuis une cuve de réception. La pompe actuelle est surdimensionnée et consomme trop d'énergie. Un technicien junior doit vérifier la hauteur manométrique réelle et proposer une pompe adaptée.",
 data=[["Débit","Q","40 m³/h"],["Longueur","L","250 m"],["Diamètre intérieur","D","105 mm"],["Dénivelé","Δz","18 m"],["Rugosité","ε","0,045 mm"],["Singularités","ΣK","6,5"],["Viscosité cinématique","ν","1,004·10⁻⁶ m²/s"],["Rendement","η","0,68"]],
 questions=["La vitesse v, le nombre de Reynolds Re et le coefficient de frottement f ;","La hauteur manométrique totale H et la puissance à l'arbre ;","Une recommandation commentée (point de fonctionnement, marge, variateur de vitesse)."],
 formulas=["H = Δz + (f·L/D + ΣK)·v²/2g","f = 0,25 / [log10( ε/(3,7·D) + 5,74/Re^0,9 )]²  (Swamee-Jain)","P = ρ·g·Q·H / η"],
 answer_key=[f"v = {fr(v)} m/s ; Re = {fr(Re,0)} ; f = {fr(f,4)}", f"H = {fr(H,1)} m (frottement {fr(hf)} m, singularités {fr(hm)} m)", f"P arbre = {fr(P/1000)} kW"])

# 2 -- heat exchanger (pasteurisation, counter-flow)
mm=2.0; cpm=3.93; Tmi,Tmo=5,72; Thi,Tho=90,80; cpw=4.18; U=1500
Qth=mm*cpm*(Tmo-Tmi); mw=Qth/(cpw*(Thi-Tho)); d1=Thi-Tmo; d2=Tho-Tmi; lm=(d2-d1)/math.log(d2/d1); Ar=Qth*1000/(U*lm)
add("echangeur", title="Surface d'un échangeur de pasteurisation", sector="Agroalimentaire", sector_code="AGR", region="Casablanca-Settat", level=2,
 context="Une laiterie veut chauffer son lait avant pasteurisation avec de l'eau chaude de récupération, dans un échangeur à plaques à contre-courant. Il faut déterminer la puissance échangée, le débit d'eau chaude et la surface d'échange nécessaires.",
 data=[["Débit de lait","ṁ","2,0 kg/s"],["Cp du lait","cp","3,93 kJ/(kg·K)"],["Lait : entrée → sortie","T","5 °C → 72 °C"],["Eau chaude : entrée → sortie","T","90 °C → 80 °C"],["Cp de l'eau","cp","4,18 kJ/(kg·K)"],["Coefficient global","U","1 500 W/(m²·K)"]],
 questions=["La puissance thermique à transférer ;","Le débit d'eau chaude nécessaire ;","La DTLM puis la surface d'échange, avec une marge de 15 % recommandée."],
 formulas=["Φ = ṁ·cp·ΔT","ΔTlm = (ΔT₂ − ΔT₁) / ln(ΔT₂/ΔT₁)","A = Φ / (U·ΔTlm)"],
 answer_key=[f"Φ = {fr(Qth,1)} kW", f"ṁ eau = {fr(mw)} kg/s", f"ΔTlm = {fr(lm)} K ; A = {fr(Ar)} m² ; avec 15 % de marge : {fr(Ar*1.15)} m²"])

# 3 -- compressed-air leak
d=3e-3; pg=7e5; p0=101325; T0=293.15; Cd=.65; gam=1.4; R=287
Ao=math.pi*d*d/4; pabs=pg+p0
mdot=Cd*Ao*pabs*math.sqrt(gam/(R*T0))*(2/(gam+1))**((gam+1)/(2*(gam-1)))
rho0=p0/(R*T0); Qn=mdot/rho0*3600; kwh_m3=.11; hours=8000; tar=1.2
kw=Qn*kwh_m3; cost=kw*hours*tar
add("fuite-air", title="Coût d'une fuite d'air comprimé", sector="Textile", sector_code="TEX", region="Tanger-Tétouan-Al Hoceïma", level=1,
 context="Lors d'un audit énergétique d'un atelier de confection, une fuite de 3 mm est repérée sur un réseau d'air comprimé qui tourne en continu. Le responsable maintenance demande de chiffrer ce que coûte cette seule fuite par an.",
 data=[["Diamètre de l'orifice","d","3 mm"],["Pression relative réseau","pg","7 bar"],["Température de l'air","T","20 °C"],["Coefficient de décharge","Cd","0,65"],["Énergie spécifique du compresseur","e","0,11 kWh/Nm³"],["Fonctionnement","h","8 000 h/an"],["Tarif électricité","c","1,2 MAD/kWh"]],
 questions=["Le débit massique de la fuite (écoulement supposé sonique) ;","Le débit volumique en Nm³/h ;","La puissance perdue et le coût annuel, puis le gain d'une campagne de réparation."],
 formulas=["ṁ = Cd·A·p·√(γ/(R·T)) · (2/(γ+1))^((γ+1)/(2(γ−1)))","Qₙ = ṁ / ρₙ  avec ρₙ = p₀/(R·T₀)","Coût = Qₙ · e · h · c"],
 answer_key=[f"ṁ = {fr(mdot*1000,2)} g/s", f"Qn = {fr(Qn,1)} Nm³/h", f"Puissance perdue = {fr(kw,1)} kW ; coût annuel = {fr(cost,0)} MAD"])

# 4 -- VFD on fan
Pn=55; share=.85; fl=.7; eta_v=.97; hrs=7000; c=1.1
P_damp=Pn*share; P_vfd=Pn*fl**3/eta_v; sav=(P_damp-P_vfd)*hrs; sav_mad=sav*c
add("variateur-ventilateur", title="Gain d'un variateur sur un ventilateur de process", sector="Matériaux de construction", sector_code="MAT", region="Marrakech-Safi", level=2,
 context="Un ventilateur de dépoussiérage de 55 kW est régulé par un volet d'étranglement et tourne en moyenne à 70 % du débit nominal. L'équipe maintenance envisage un variateur de fréquence et veut savoir s'il se rembourse vite.",
 data=[["Puissance nominale","Pn","55 kW"],["Puissance avec volet à 70 % de débit","Pv","85 % de Pn"],["Débit moyen","Q/Qn","0,70"],["Rendement du variateur","ηv","0,97"],["Fonctionnement","h","7 000 h/an"],["Tarif électricité","c","1,1 MAD/kWh"]],
 questions=["La puissance absorbée avec volet et avec variateur (lois de similitude) ;","L'économie annuelle en kWh et en MAD ;","Le temps de retour sur investissement pour un variateur dont le prix est à demander à un fournisseur."],
 formulas=["P ∝ n³  et  Q ∝ n  ⇒  P = Pn·(Q/Qn)³","P_variateur = Pn·(Q/Qn)³ / ηv"],
 answer_key=[f"Volet : {fr(P_damp)} kW ; variateur : {fr(P_vfd)} kW", f"Économie = {fr(sav,0)} kWh/an = {fr(sav_mad,0)} MAD/an", "Retour = prix installé / économie annuelle (prix fournisseur à renseigner)"])

# 5 -- belt conveyor (simplified)
Qt=400; Lc=300; Hc=12; vb=2.0; fc=.025; mb=45; ed=.92
q_l=Qt*1000/3600/vb; Pl=Qt*1000/3600*9.81*Hc/1000; Fr=fc*9.81*Lc*(mb+q_l); Pf=Fr*vb/1000; Pm=(Pl+Pf)/ed
std=next(s for s in [18.5,22,30,37,45,55,75] if s >= Pm*1.1)
add("convoyeur", title="Puissance moteur d'un convoyeur à bande", sector="Mines et carrières", sector_code="MIN", region="Oriental", level=3,
 context="Une carrière veut remplacer le convoyeur qui alimente son concasseur. La bande transporte du tout-venant avec un faible dénivelé. Il faut estimer la puissance de motorisation par une méthode simplifiée (frottement équivalent).",
 data=[["Débit massique","Q","400 t/h"],["Longueur","L","300 m"],["Dénivelé","H","12 m"],["Vitesse de bande","v","2,0 m/s"],["Coefficient de frottement équivalent","f","0,025"],["Masse linéique bande + rouleaux","m'","45 kg/m"],["Rendement de transmission","η","0,92"]],
 questions=["La charge linéique de matière ;","La puissance de levage et la puissance de frottement ;","La puissance moteur requise et la puissance normalisée à retenir avec 10 % de marge."],
 formulas=["q = Q / (3,6·v)  [kg/m]","P_lev = (Q/3,6)·g·H","P_fr = f·g·L·(m' + q)·v","P_moteur = (P_lev + P_fr) / η"],
 answer_key=[f"q = {fr(q_l,1)} kg/m", f"P levage = {fr(Pl,1)} kW ; P frottement = {fr(Pf,1)} kW", f"P moteur = {fr(Pm,1)} kW ; puissance normalisée retenue = {fr(std,1)} kW"])

# 6 -- boiler efficiency
ms=5000; hs=2781; hfw=335; fuel=380; pci=35.8; hfw2=419
Pu=ms*(hs-hfw)/3600; Pc=fuel*pci*1000/3600; etab=Pu/Pc
fuel2=ms*(hs-hfw2)/(etab*pci*1000)
add("chaudiere", title="Rendement d'une chaudière vapeur", sector="Agroalimentaire", sector_code="AGR", region="Souss-Massa", level=2,
 context="Une conserverie exploite une chaudière au gaz qui produit de la vapeur saturée. Avant d'investir dans un économiseur sur les fumées, la direction veut connaître le rendement actuel et l'économie de gaz si l'eau d'alimentation passe de 80 °C à 100 °C.",
 data=[["Production de vapeur","ṁ","5 000 kg/h"],["Enthalpie vapeur (11 bar abs, saturée)","hv","2 781 kJ/kg"],["Enthalpie eau d'alimentation à 80 °C","h₁","335 kJ/kg"],["Enthalpie eau d'alimentation à 100 °C","h₂","419 kJ/kg"],["Consommation de gaz","G","380 Nm³/h"],["PCI du gaz","PCI","35,8 MJ/Nm³"]],
 questions=["La puissance utile et la puissance combustible ;","Le rendement actuel de la chaudière ;","La consommation de gaz à rendement constant avec l'eau à 100 °C, et l'économie en Nm³/h."],
 formulas=["P_utile = ṁ·(h_v − h_eau) / 3600","P_comb = G·PCI","η = P_utile / P_comb"],
 answer_key=[f"P utile = {fr(Pu,0)} kW ; P combustible = {fr(Pc,0)} kW", f"η = {fr(etab*100,1)} %", f"Gaz à 100 °C : {fr(fuel2,1)} Nm³/h ; économie = {fr(fuel-fuel2,1)} Nm³/h"])


# 7 -- REAL public case (unit-mismatch, NASA Mars Climate Orbiter). Facts come ONLY from the cited source; numbers below are exercise values.
lb=4.448222; J=25.0; m=638.0; n_ev=100
Jtrue=J*lb; dv_true=Jtrue/m; dv_read=J/m; err=dv_true-dv_read
add("mco-unites", status="real", title="Piège d'unités : le cas Mars Climate Orbiter", sector="Aérospatial (cas public)", sector_code="AER", region="International", level=1,
 source_url="http://sunnyday.mit.edu/accidents/MCO_report.pdf", source_title="Mars Climate Orbiter Mishap Investigation Board, Phase I Report", source_publisher="NASA, 10 novembre 1999",
 accessed="2026-11-15",
 source_note="Faits tirés de la source : un fichier de logiciel sol (SM_FORCES) fournissait l'impulsion des propulseurs en lbf·s au lieu de N·s exigés par la spécification d'interface ; la trajectoire a donc été sous-estimée d'un facteur 4,45. Lien cité par une publication tierce ; je n'ai pas pu ouvrir le PDF directement.",
 exercise_note="Les valeurs numériques ci-dessous (impulsion, masse, nombre d'événements) sont celles de l'exercice, pas celles du rapport.",
 context="En 1999, la sonde Mars Climate Orbiter de la NASA a été perdue après une erreur d'unités : un logiciel au sol exprimait l'impulsion des propulseurs en livre-force seconde alors que le logiciel de navigation attendait des newton-secondes. Le même piège existe dans l'industrie (automates, SCADA, fichiers d'échange entre services). L'exercice chiffre l'effet d'une telle confusion.",
 data=[["Impulsion lue dans le fichier","J","25,0 (lbf·s, lue comme N·s)"],["Masse de l'engin (valeur d'exercice)","m","638 kg"],["Nombre d'événements identiques (même sens)","n","100"],["Conversion","1 lbf·s","4,448222 N·s"]],
 questions=["Le facteur d'erreur entre la valeur réelle et la valeur lue ;","La variation de vitesse Δv réelle et celle calculée par le logiciel pour un événement ;","L'erreur cumulée après 100 événements, puis trois mesures concrètes pour qu'une telle erreur ne se produise pas dans une usine."],
 formulas=["1 lbf·s = 4,448222 N·s","Δv = J / m","facteur = J_réel / J_lu"],
 answer_key=[f"facteur = {fr(lb,3)}", f"Δv réel = {fr(dv_true,4)} m/s ; Δv lu = {fr(dv_read,4)} m/s ; écart = {fr(err,4)} m/s par événement", f"Cumul sur {n_ev} événements : {fr(err*n_ev,2)} m/s ; mesures : spécification d'interface avec unités, données étiquetées, test d'intégration croisé"])

TEX = {
 "pompage": ["H=\\Delta z+\\Bigl(f\\frac{L}{D}+\\sum K\\Bigr)\\frac{v^{2}}{2g}", "f=\\frac{0{,}25}{\\left[\\log_{10}\\!\\left(\\frac{\\varepsilon}{3{,}7\\,D}+\\frac{5{,}74}{\\mathrm{Re}^{0{,}9}}\\right)\\right]^{2}}", "P=\\frac{\\rho\\, g\\, Q\\, H}{\\eta}"],
 "echangeur": ["\\Phi=\\dot m\\,c_p\\,\\Delta T", "\\Delta T_{lm}=\\frac{\\Delta T_2-\\Delta T_1}{\\ln\\left(\\Delta T_2/\\Delta T_1\\right)}", "A=\\frac{\\Phi}{U\\,\\Delta T_{lm}}"],
 "fuite-air": ["\\dot m=C_d\\,A\\,p\\sqrt{\\frac{\\gamma}{R\\,T}}\\left(\\frac{2}{\\gamma+1}\\right)^{\\frac{\\gamma+1}{2(\\gamma-1)}}", "Q_n=\\frac{\\dot m}{\\rho_n},\\quad \\rho_n=\\frac{p_0}{R\\,T_0}", "\\text{Coût}=Q_n\\,e\\,h\\,c"],
 "variateur-ventilateur": ["P\\propto n^{3},\\quad Q\\propto n\\;\\Rightarrow\\;P=P_n\\left(\\frac{Q}{Q_n}\\right)^{3}", "P_{var}=\\frac{P_n\\,(Q/Q_n)^{3}}{\\eta_v}"],
 "convoyeur": ["q=\\frac{Q}{3{,}6\\,v}", "P_{lev}=\\frac{Q}{3{,}6}\\,g\\,H", "P_{fr}=f\\,g\\,L\\,(m'+q)\\,v", "P_{mot}=\\frac{P_{lev}+P_{fr}}{\\eta}"],
 "chaudiere": ["P_u=\\frac{\\dot m\\,(h_v-h_e)}{3600}", "P_c=G\\cdot \\mathrm{PCI}", "\\eta=\\frac{P_u}{P_c}"],
 "mco-unites": ["1\\ \\mathrm{lbf\\cdot s}=4{,}448222\\ \\mathrm{N\\cdot s}", "\\Delta v=\\frac{J}{m}", "\\text{facteur}=\\frac{J_{\\text{réel}}}{J_{\\text{lu}}}"],
}
for b in bank: b["formulas_tex"] = TEX[b["slug"]]

for i, b in enumerate(bank, 1):
    b["id"] = i; (OUT / f"{i:02d}-{b['slug']}.json").write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    print(i, b["slug"], "|", " | ".join(b["answer_key"]))

import validate_bank; validate_bank.main()
