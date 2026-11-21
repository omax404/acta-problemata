#!/usr/bin/env python3
"""Generates data/bank/*.json. Every number in answer_key is COMPUTED here from the data, so key and statement cannot drift.
Statuses are all 'realistic' (problem classes) except explicitly sourced public documents."""
import json, math, pathlib
fr = lambda x, n=2: f"{x:,.{n}f}".replace(",", " ").replace(".", ",")
OUT = pathlib.Path(__file__).parent / "data" / "bank"; OUT.mkdir(parents=True, exist_ok=True)
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

# 7 -- REAL public case (unit-mismatch, NASA Mars Climate Orbiter)
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

# 8 -- REALISTIC: Kanban line dimensioning (automotive wiring, inspiration Yazaki / FSDM)
D_dem=480; L_lead=0.75; alpha_sec=0.20; C_cont=25
K_exact=D_dem*L_lead*(1+alpha_sec)/C_cont
K_cards=math.ceil(K_exact)
WIP_max=K_cards*C_cont
add("kanban-cablage", title="Dimensionnement d'une boucle Kanban en câblage automobile", sector="Automobile & Électromécanique", sector_code="AUT", region="Rabat-Salé-Kénitra", level=2,
 context="Sur une ligne d'assemblage de faisceaux électriques automobiles, les ruptures de connecteurs provoquent des arrêts de ligne non planifiés. L'ingénieur méthodes doit dimensionner la boucle Kanban (nombre d'étiquettes) entre le magasin et le poste d'encliquetage.",
 data=[["Demande journalière moyenne","D","480 connecteurs/jour"],["Délai de réapprovisionnement (lead time)","L","0,75 jour (6 h de poste)"],["Facteur de sécurité aléas","α","20 % (0,20)"],["Capacité unitaire d'un bac (contenant)","C","25 connecteurs/bac"]],
 questions=["Le nombre théorique et le nombre entier de cartes Kanban (bacs en circulation) ;","L'en-cours maximum (WIP) garanti au poste de travail ;","L'impact sur le flux si la digitalisation du Kanban réduit le délai L de 0,75 jour à 0,25 jour."],
 formulas=["K = [D · L · (1 + α)] / C","\\text{WIP}_{\\max} = K \\cdot C"],
 answer_key=[f"K théorique = {fr(K_exact,2)} ; K retenu = {K_cards} cartes (bacs)", f"WIP max = {WIP_max} connecteurs", f"Avec L = 0,25 j : K = {math.ceil(D_dem*0.25*(1+alpha_sec)/C_cont)} cartes (baisse de l'en-cours de {WIP_max - math.ceil(D_dem*0.25*(1+alpha_sec)/C_cont)*C_cont} connecteurs)"])

# 9 -- REALISTIC: OEE / TRS diagnosis (bag manufacturing, inspiration Papsac Casablanca)
T_ouv=8*3600; T_arrets=78*60; T_fonction=T_ouv-T_arrets
Dispo=T_fonction/T_ouv
Cadence_theorique=1/1.5 # 1 sac toutes les 1.5 s
Prod_totale=11200 # sacs produits
Prod_conforme=10850 # sacs conformes
T_net=Prod_totale*1.5
Perf=T_net/T_fonction
Qual=Prod_conforme/Prod_totale
TRS=Dispo*Perf*Qual
add("trs-ensachage", title="Diagnostic TRS et pertes d'une ligne de sacs industriels", sector="Emballage & Chimie", sector_code="EMB", region="Casablanca-Settat", level=2,
 context="Lors d'un audit de productivité sur une ligne de fabrication de sacs industriels (fond de sac), le Taux de Rendement Synthétique (TRS) moyen s'avère anormalement bas (~49 %). L'ingénieur de production doit décomposer les 3 taux pour identifier le levier prioritaire.",
 data=[["Temps d'ouverture poste (1 poste de 8 h)","T_ouv","28 800 s (8 h)"],["Arrêts non planifiés cumulés (pannes, réglages)","T_arr","4 680 s (78 min)"],["Production totale enregistrée","N_tot","11 200 sacs"],["Production conforme livrable","N_bon","10 850 sacs"],["Temps de cycle nominal machine","t_cycle","1,5 s/sac"]],
 questions=["Le taux de disponibilité temporelle de la ligne ;","Le taux de performance machine (perte de cadence) ;","Le taux de qualité et le TRS global, avec identification de la perte principale (disponibilité vs cadence)."],
 formulas=["\\text{Disponibilité} = \\frac{T_{\\text{fonctionnement}}}{T_{\\text{ouverture}}}", "\\text{Performance} = \\frac{N_{\\text{tot}} \\cdot t_{\\text{cycle}}}{T_{\\text{fonctionnement}}}", "\\text{Qualité} = \\frac{N_{\\text{bon}}}{N_{\\text{tot}}}", "\\text{TRS} = D \\cdot P \\cdot Q"],
 answer_key=[f"Disponibilité = {fr(Dispo*100,1)} %", f"Performance = {fr(Perf*100,1)} %", f"Qualité = {fr(Qual*100,1)} % ; TRS = {fr(TRS*100,2)} % (perte principale : cadence/micro-arrêts, perte de performance = {fr((1-Perf)*100,1)} %)"])

# 10 -- REALISTIC: Little's Law / Queue bottleneck (fertilizer chemical processing, inspiration OCP/ENSMR)
lambda_arr=45.0 # tonnes/heure reçues
W_sejour=2.4 # heures de séjour moyen cuve/broyage
L_en_cours=lambda_arr*W_sejour
lambda_pic=lambda_arr*1.40 # +40%
add("goulot-engrais", title="Loi de Little et engorgement d'une unité de broyage d'engrais", sector="Mines & Chimie lourde", sector_code="CHM", region="Casablanca-Settat", level=2,
 context="Une unité de traitement chimique de phosphate et engrais reçoit un flux continu de matière broyée. Les ingénieurs observent qu'une augmentation de 40 % de la demande amène l'atelier à saturation. Il faut quantifier l'en-cours moyen et la capacité critique de l'installation.",
 data=[["Débit moyen d'alimentation matière","λ","45 t/h"],["Temps de séjour moyen dans le process","W","2,4 h"],["Augmentation de charge prévue","ΔD","+40 % (63 t/h)"],["Capacité nominale de stockage tampon","L_max","120 tonnes"]],
 questions=["L'en-cours moyen matière L dans le système en régime nominal (loi de Little) ;","L'en-cours prévu sous une hausse de 40 % si le temps de séjour reste identique ;","Le temps de séjour critique W_critique au-delà duquel la cuve tampon de 120 t déborde à 63 t/h."],
 formulas=["L = \\lambda \\cdot W \\quad (\\text{Loi de Little})", "W_{\\text{crit}} = \\frac{L_{\\max}}{\\lambda_{\\text{pic}}}"],
 answer_key=[f"L nominal = {fr(L_en_cours,1)} tonnes", f"L à +40 % = {fr(lambda_pic*W_sejour,1)} tonnes", f"W critique à 63 t/h = {fr(120/lambda_pic,2)} h ({fr(120/lambda_pic*60,0)} min) avant saturation du stockage tampon"])

# 11 -- REALISTIC: Dual-resource sewing line balancing (textile garment manufacturing, inspiration EMO SAS/ROADEF)
T_total=320.0 # secondes de travail par vêtement
T_cadence=45.0 # temps de cycle takt time souhaité
N_theo=T_total/T_cadence
N_postes=math.ceil(N_theo)
efficience=T_total/(N_postes*T_cadence)
add("equilibrage-textile", title="Équilibrage de ligne d'assemblage textile sous contraintes d'opérateurs", sector="Textile & Confection", sector_code="TEX", region="Tanger-Tétouan-Al Hoceïma", level=3,
 context="Un atelier de confection textile produit des blousons techniques. Face à des commandes instables et des temps de réglage machine, le chef d'atelier doit rééquilibrer la ligne de couture pour atteindre le temps de cycle client (takt time).",
 data=[["Somme des temps opératoires d'une pièce","Σt","320 s (5 min 20 s)"],["Temps de cycle requis (takt time client)","Tc","45 s/pièce"],["Temps d'ouverture d'un poste","T_ouv","7,5 h/jour (27 000 s)"],["Objectif de production journalier","Obj","600 pièces/jour"]],
 questions=["Le nombre théorique et le nombre entier minimum de postes opérateurs requis ;","L'efficience d'équilibrage de la ligne théorique ;","Le temps d'inactivité cumulé (perte d'équilibrage) par pièce produite."],
 formulas=["N_{\\text{théo}} = \\frac{\\sum t_i}{T_c}", "\\text{Efficience} = \\frac{\\sum t_i}{N_{\\text{retenu}} \\cdot T_c}", "\\text{Perte d'équilibrage} = (N \\cdot T_c) - \\sum t_i"],
 answer_key=[f"N théorique = {fr(N_theo,2)} ; N retenu = {N_postes} postes de travail", f"Efficience = {fr(efficience*100,1)} %", f"Perte d'équilibrage = {fr((N_postes*T_cadence)-T_total,0)} s par vêtement (soit {fr(((N_postes*T_cadence)-T_total)*600/3600,2)} h d'inactivité cumulée par jour)"])


# --- Batch 1, 2, 3: problems 12 to 30 ---
# Problems 12 to 30 extension for gen_bank.py

# 12 -- Electrical: Cos phi compensation (power factor correction)
P_act12 = 250.0  # kW
cos_phi1 = 0.72
cos_phi2 = 0.93
tan_phi1 = math.tan(math.acos(cos_phi1))
tan_phi2 = math.tan(math.acos(cos_phi2))
Q_c12 = P_act12 * (tan_phi1 - tan_phi2)  # kVAr
add("compensation-cosphi", title="Compensation d'énergie réactive par batterie de condensateurs",
 sector="Agroalimentaire", sector_code="AGR", region="Fès-Meknès", level=1,
 context="Une minoterie industrielle subit des pénalités pour dépassement de puissance réactive sur sa facture moyenne tension ONEE. Le responsable électrique doit dimensionner la batterie de condensateurs automatique pour remonter le facteur de puissance.",
 data=[["Puissance active moyenne","P","250 kW"],["Facteur de puissance initial","cos φ₁","0,72"],["Facteur de puissance visé","cos φ₂","0,93"],["Tension réseau","U","400 V triphasé"]],
 questions=["La puissance réactive initiale et finale ;","La puissance capacitive de la batterie à installer ;","Le choix d'un gradinage standard et l'économie sur les pénalités réactives."],
 formulas=["Q_c = P \\cdot (\\tan \\varphi_1 - \\tan \\varphi_2)", "S = \\sqrt{P^2 + Q^2}"],
 answer_key=[f"tan φ₁ = {fr(tan_phi1,3)} ; tan φ₂ = {fr(tan_phi2,3)}", f"Q_c nécessaire = {fr(Q_c12,1)} kVAr", f"Batterie normalisée recommandée = {math.ceil(Q_c12/25)*25} kVAr (gradins de 25 kVAr)"])

# 13 -- Electrical: Cable sizing by voltage drop
L_cable13 = 180.0 # m
I_b13 = 145.0 # A
cos_phi13 = 0.85
sin_phi13 = math.sin(math.acos(cos_phi13))
rho_cu = 0.0225 # ohm.mm²/m (Cuivre à 70°C)
du_max_pct = 3.0 # % de 400V
du_max_v = du_max_pct * 400.0 / 100.0 # 12V
S_calc13 = math.sqrt(3) * L_cable13 * I_b13 * (rho_cu * cos_phi13) / du_max_v
S_std13 = next(s for s in [35, 50, 70, 95, 120, 150] if s >= S_calc13)
add("section-cable", title="Dimensionnement de câble par chute de tension admissible",
 sector="Automobile & Électromécanique", sector_code="AUT", region="Tanger-Tétouan-Al Hoceïma", level=2,
 context="Une nouvelle cellule robotisée est raccordée au TGBT de l'usine par une liaison cuivre enterrée de 180 m. La chute de tension ne doit pas dépasser 3 % en régime nominal pour garantir le fonctionnement des variateurs.",
 data=[["Courant d'emploi nominal","Ib","145 A"],["Longueur de la liaison","L","180 m"],["Facteur de puissance","cos φ","0,85"],["Tension nominale","Un","400 V triphasé"],["Chute de tension maximale","Δu_max","3 % (12 V)"],["Résistivité cuivre en service","ρ","0,0225 Ω·mm²/m"]],
 questions=["La chute de tension maximale admise en volts ;","La section théorique minimale du câble cuivre ;","La section normalisée à retenir et la chute de tension réelle correspondante."],
 formulas=["\\Delta U = \\sqrt{3} \\cdot I_b \\cdot \\frac{L}{S} \\cdot \\rho \\cdot \\cos \\varphi", "S_{\\min} = \\frac{\\sqrt{3} \\cdot I_b \\cdot L \\cdot \\rho \\cdot \\cos \\varphi}{\\Delta U_{\\max}}"],
 answer_key=[f"ΔU max = {fr(du_max_v,1)} V", f"Section minimale calculée = {fr(S_calc13,1)} mm²", f"Section normalisée retenue = {S_std13} mm²"])

# 14 -- Electrical: Solar PV factory roof yield
A_pv14 = 1200.0 # m²
P_spec14 = 0.20 # kWc/m² (200 Wc/m²)
P_crete14 = A_pv14 * P_spec14 # 240 kWc
H_sun14 = 1850.0 # kWh/m²/an (ensoleillement plan incliné région Marrakech)
PR14 = 0.78 # Performance Ratio
E_prod14 = P_crete14 * H_sun14 * PR14 / 1.0 # kWh/an (environ 346 320 kWh/an)
c_elec14 = 1.15 # MAD/kWh
add("solaire-toiture", title="Productible d'une centrale solaire photovoltaïque en toiture",
 sector="Chimie & Plasturgie", sector_code="CHM", region="Marrakech-Safi", level=2,
 context="Une usine d'injection plastique dispose d'une toiture bien orientée et souhaite installer des panneaux solaires en autoconsommation sans injection réseau pour écrêter sa facture électrique ONEE.",
 data=[["Surface disponible en toiture","S","1 200 m²"],["Puissance surfacique des modules","p","200 Wc/m² (0,20 kWc/m²)"],["Gisement solaire annuel incliné","H","1 850 kWh/m²/an"],["Facteur de performance de l'installation","PR","0,78 (78 %)"],["Tarif électricité réseau","c","1,15 MAD/kWh"]],
 questions=["La puissance crête totale installable ;","La production annuelle d'électricité estimée ;","L'économie annuelle réalisée sur la facture d'électricité."],
 formulas=["P_c = S \\cdot p", "E_{\\text{an}} = P_c \\cdot H_{\\text{site}} \\cdot \\text{PR} / 1\\text{ kW/m}^2", "\\text{Gain} = E_{\\text{an}} \\cdot c"],
 answer_key=[f"Puissance crête = {fr(P_crete14,0)} kWc", f"Production annuelle = {fr(E_prod14,0)} kWh/an", f"Économie annuelle = {fr(E_prod14*c_elec14,0)} MAD/an"])

# 15 -- Thermal: Steam trap leak cost
d_orifice15 = 4.0 # mm
P_vap15 = 6.0 # bar relatif (7 bar abs)
# Débit de fuite vapeur saturée selon formule empirique de Napier Q = 0.51 * P_abs(bar) * d(mm)^2 kg/h
Q_vap15 = 0.51 * (P_vap15 + 1.013) * (d_orifice15 ** 2) # ~ 57.2 kg/h
h_run15 = 7500.0 # h/an
M_perte15 = Q_vap15 * h_run15 / 1000.0 # t/an
cost_steam15 = 320.0 # MAD / tonne de vapeur
cost_an15 = M_perte15 * cost_steam15
add("purgeur-vapeur", title="Coût d'un purgeur vapeur bloqué ouvert",
 sector="Agroalimentaire", sector_code="AGR", region="Casablanca-Settat", level=1,
 context="Lors d'une campagne de diagnostic acoustique des purgeurs vapeur sur le collecteur général d'une brasserie, un purgeur thermodynamique est diagnostiqué fuyard en continu avec un orifice équivalent de 4 mm.",
 data=[["Diamètre orifice équivalent","d","4 mm"],["Pression vapeur relative","P","6,0 bar"],["Heures de service annuel","h","7 500 h/an"],["Coût de production vapeur","c_vap","320 MAD/tonne"]],
 questions=["Le débit de fuite horaire de vapeur vive (formule de Napier) ;","La masse totale de vapeur perdue par an ;","Le coût financier annuel de cette fuite et le délai de remplacement du purgeur."],
 formulas=["Q = 0{,}51 \\cdot P_{\\text{abs}} \\cdot d^2 \\quad [\\text{kg/h}]", "\\text{Perte annuelle} = Q \\cdot h / 1000", "\\text{Coût} = \\text{Perte} \\cdot c_{\\text{vap}}"],
 answer_key=[f"Débit de fuite = {fr(Q_vap15,1)} kg/h", f"Vapeur perdue = {fr(M_perte15,1)} t/an", f"Coût annuel = {fr(cost_an15,0)} MAD/an"])

# 16 -- Thermal: Pipe insulation payback
D_ext16 = 0.089 # m (DN80 acier 88.9 mm)
L_pipe16 = 60.0 # m
T_surface16 = 160.0 # °C
T_amb16 = 20.0 # °C
h_ext16 = 15.0 # W/(m²·K) convection + rayonnement combiné
q_bare16 = math.pi * D_ext16 * h_ext16 * (T_surface16 - T_amb16) # W/m
Q_tot_bare16 = q_bare16 * L_pipe16 / 1000.0 # kW
eta_iso16 = 0.88 # 88% de réduction des pertes avec laine de roche 50mm
P_saved16 = Q_tot_bare16 * eta_iso16 # kW
h_an16 = 6000.0 # h/an
c_kwh_th16 = 0.42 # MAD/kWh thermique gaz
sav_mad16 = P_saved16 * h_an16 * c_kwh_th16
cost_iso16 = 350.0 * L_pipe16 # MAD (350 MAD/m installé)
tri16 = cost_iso16 / sav_mad16
add("calorifugeage-tuyauterie", title="Rentabilité du calorifugeage d'une ligne vapeur nue",
 sector="Chimie lourde", sector_code="CHM", region="Souss-Massa", level=3,
 context="Une ligne de distribution de vapeur saturée de 60 mètres n'a jamais été calorifugée suite à des travaux de maintenance. L'ingénieur utilités doit justifier l'investissement de calorifugeage auprès de la direction financière.",
 data=[["Diamètre extérieur tube","De","89 mm (DN80)"],["Longueur de ligne nue","L","60 m"],["Température de surface du tube","Tp","160 °C"],["Température ambiante moyenne","Ta","20 °C"],["Coefficient d'échange global vers l'air","h","15 W/(m²·K)"],["Efficacité thermique isolant 50 mm","η_iso","88 %"],["Coût énergie thermique gaz","c_th","0,42 MAD/kWh"],["Coût des travaux de calorifugeage","C_inv","350 MAD/m"],["Fonctionnement annuel","t","6 000 h/an"]],
 questions=["La déperdition thermique linéique et totale de la ligne nue ;","L'économie thermique annuelle apportée par le calorifuge ;","L'économie en MAD et le temps de retour sur investissement (TRI en mois)."],
 formulas=["q = \\pi \\cdot D_e \\cdot h \\cdot (T_p - T_a)", "\\Phi = q \\cdot L", "\\text{Gain} = \\Phi \\cdot \\eta_{\\text{iso}} \\cdot t \\cdot c_{\\text{th}}", "\\text{TRI} = \\frac{C_{\\text{inv}}}{\\text{Gain}}"],
 answer_key=[f"Perte linéique = {fr(q_bare16,1)} W/m ; Puissance perdue totale = {fr(Q_tot_bare16,1)} kW", f"Économie annuelle = {fr(P_saved16*h_an16,0)} kWh/an", f"Gain = {fr(sav_mad16,0)} MAD/an ; TRI = {fr(tri16*12,1)} mois"])

# 17 -- Fluids: Water hammer (Joukowsky surge)
c_celerity17 = 1150.0 # m/s celerite onde eau dans acier
v_flow17 = 2.4 # m/s
rho_water17 = 1000.0 # kg/m³
g17 = 9.81
delta_P_jouk17 = rho_water17 * c_celerity17 * v_flow17 # Pa
delta_H_jouk17 = delta_P_jouk17 / (rho_water17 * g17) # mCE
add("coup-de-belier", title="Surpression de coup de bélier selon Joukowsky",
 sector="Hydraulique & Eau", sector_code="AGR", region="Gharb-Chrarda-Béni Hsen", level=3,
 context="Sur une conduite d'adduction d'eau brute agricole, une vanne papillon motorisée se ferme brutalement lors d'un déclenchement électrique d'urgence. L'ingénieur d'exploitation calcule la surpression maximale pour dimensionner la soupape de décharge.",
 data=[["Vitesse nominale d'écoulement","v","2,4 m/s"],["Célérité de l'onde de pression","c","1 150 m/s"],["Masse volumique de l'eau","ρ","1 000 kg/m³"],["Accélération pesanteur","g","9,81 m/s²"]],
 questions=["La surpression théorique instantanée selon Joukowsky en Pascals et en bars ;","La hauteur manométrique équivalente de surpression en mètres de colonne d'eau (mCE) ;","Le temps de fermeture critique de la vanne pour éviter le coup de bélier franc sur une conduite de 450 m."],
 formulas=["\\Delta P = \\rho \\cdot c \\cdot \\Delta v", "\\Delta H = \\frac{c \\cdot \\Delta v}{g}", "T_{\\text{crit}} = \\frac{2 \\cdot L}{c}"],
 answer_key=[f"Surpression = {fr(delta_P_jouk17/1e5,2)} bar ({fr(delta_P_jouk17/1e6,2)} MPa)", f"Surpression = {fr(delta_H_jouk17,1)} mCE", f"Temps de manœuvre critique (L=450m) = {fr(2*450/c_celerity17,2)} s"])

# 18 -- Fluids: NPSH available vs required
P_atm18 = 101325.0 # Pa
P_vap18 = 2338.0 # Pa (eau à 20°C)
H_asp18 = 3.5 # m (pompe au-dessus de la cuve)
h_frott18 = 1.2 # m (pertes d'aspiration)
rho18 = 1000.0
NPSHa18 = (P_atm18 - P_vap18)/(rho18 * g17) - H_asp18 - h_frott18
NPSHr18 = 3.8 # m (fourni par catalogue constructeur)
marge18 = NPSHa18 - NPSHr18
add("cavitation-npsh", title="Vérification du non-risque de cavitation (NPSH disponible)",
 sector="Agroalimentaire", sector_code="AGR", region="Rabat-Salé-Kénitra", level=2,
 context="Une pompe centrifuge aspire du jus de fruit clarifié depuis une cuve ouverte en contrebas. En période de forte production, des bruits de crépitement anormaux font craindre une entrée en cavitation destructive.",
 data=[["Pression atmosphérique du site","Patm","1 013 mbar (101 325 Pa)"],["Pression de vapeur saturante du fluide","Pv","2 338 Pa (20 °C)"],["Hauteur géométrique d'aspiration","Ha","3,5 m"],["Pertes de charge à l'aspiration","Δha","1,2 m"],["NPSH requis constructeur au point Q","NPSHr","3,8 m"]],
 questions=["La charge absolue disponible au plan d'eau ;","Le NPSH disponible réel à l'ouïe de la pompe ;","La comparaison avec le NPSH requis constructeur et la marge de sécurité recommandée (≥ 0,5 m)."],
 formulas=["\\text{NPSH}_a = \\frac{P_{\\text{atm}} - P_v}{\\rho \\cdot g} - H_a - \\Delta h_a", "\\text{Marge} = \\text{NPSH}_a - \\text{NPSH}_r \\ge 0{,}5\\text{ m}"],
 answer_key=[f"Charge atmosphérique nette = {fr((P_atm18-P_vap18)/(rho18*g17),2)} m", f"NPSH disponible = {fr(NPSHa18,2)} m", f"Marge de sécurité = {fr(marge18,2)} m (Conforme car > 0,5 m)"])

# Problems 19 to 24 extension for gen_bank.py

# 19 -- Mechanical: Shaft diameter under combined torsion and bending
P_moteur19 = 45000.0 # W (45 kW)
N_rot19 = 750.0 # tr/min
omega19 = 2.0 * math.pi * N_rot19 / 60.0
C_torsion19 = P_moteur19 / omega19 # N.m (Mt ~ 572.96 N.m)
M_flexion19 = 420.0 # N.m (effort radial courroie)
M_ideal19 = math.sqrt(M_flexion19**2 + C_torsion19**2) # Tresca / Guest
Rpe19 = 50.0 * 1e6 # Pa (limite élastique admissible 50 MPa avec coef sécurité)
d_arbre_min19 = (32.0 * M_ideal19 / (math.pi * Rpe19)) ** (1.0/3.0) * 1000.0 # mm
d_std19 = next(d for d in [45, 50, 55, 60, 65, 70, 75] if d >= d_arbre_min19)
add("arbre-torsion-flexion", title="Dimensionnement d'arbre en torsion et flexion combinées",
 sector="Mécanique & Machinisme", sector_code="MEC", region="Fès-Meknès", level=3,
 context="L'arbre de sortie d'un broyeur à marteaux supporte à la fois le couple moteur de 45 kW et la tension radiale d'une transmission par poulie-courroie. Le bureau des méthodes doit vérifier le diamètre minimal d'arbre en acier C45.",
 data=[["Puissance transmise","P","45 kW"],["Vitesse de rotation","N","750 tr/min"],["Moment de flexion maximal estimé","Mf","420 N·m"],["Contrainte admissible en fatigue/sécurité","Rpe","50 MPa (50 N/mm²)"]],
 questions=["Le couple de torsion nominal transmis par l'arbre ;","Le moment idéal équivalent selon le critère de Tresca ;","Le diamètre théorique minimal et le diamètre standard d'arbre à retenir."],
 formulas=["C = \\frac{P}{\\omega} = \\frac{60 \\cdot P}{2\\pi \\cdot N}", "M_{\\text{id}} = \\sqrt{M_f^2 + C^2}", "d_{\\min} = \\left( \\frac{32 \\cdot M_{\\text{id}}}{\\pi \\cdot R_{pe}} \\right)^{1/3}"],
 answer_key=[f"Couple de torsion = {fr(C_torsion19,1)} N·m", f"Moment idéal Tresca = {fr(M_ideal19,1)} N·m", f"Diamètre calculé = {fr(d_arbre_min19,1)} mm ; Diamètre standard = {d_std19} mm"])

# 20 -- Mechanical: Bolt preload tightening torque
d_vis20 = 16.0 # mm (vis M16 classe 8.8)
pitch20 = 2.0 # mm
d2_vis20 = 14.701 # mm
mu_thread20 = 0.14 # coeff frottement filets et tête lubrifiée
F0_preload20 = 62.0 * 1000.0 # N (62 kN précharge vis M16 8.8)
# Couple de serrage K * F0 * d ou formule précise Motosh
# C = F0 * [ 0.16 * p + 0.58 * d2 * mu + mu * r_m ] approx C = 0.2 * F0 * d
C_serrage20 = 0.20 * F0_preload20 * (d_vis20 / 1000.0) # N.m (environ 198.4 N.m)
add("serrage-boulon", title="Couple de serrage au couple d'un assemblage boulonné précontraint",
 sector="Mines & Équipements", sector_code="MIN", region="Béni Mellal-Khénifra", level=1,
 context="Lors de la révision d'un concasseur giratoire, les techniciens de maintenance doivent resserrer les vis de fixation du carter avec une clé dynamométrique étalonnée pour éviter le desserrage sous vibrations.",
 data=[["Type de boulonnerie","Vis","M16 classe 8.8"],["Précharge axiale recommandée (70 % Re)","F₀","62 kN (62 000 N)"],["Facteur de serrage global estimé (lubrifié)","k","0,20"],["Diamètre nominal de vis","d","16 mm"]],
 questions=["Le couple de serrage théorique préconisé à la clé dynamométrique ;","La tension dans le fût de vis en MPa pour une section résistante de 157 mm² ;","La procédure de contrôle de serrage en croix sur une bride circulaire."],
 formulas=["C_s = k \\cdot F_0 \\cdot d", "\\sigma = \\frac{F_0}{A_s}"],
 answer_key=[f"Couple de serrage = {fr(C_serrage20,1)} N·m", f"Contrainte de traction = {fr(F0_preload20/157.0,1)} MPa", "Serrage préalable à 50 %, puis à 100 % en croix avec marquage témoin"])

# 21 -- Mechanical: Bearing L10 life calculation
C_dyn21 = 81.5 * 1000.0 # N (capacité dynamique roulement 6310)
P_eq21 = 11.2 * 1000.0 # N (charge équivalente radiale)
N_tour21 = 1480.0 # tr/min
p_exp21 = 3.0 # roulement à billes p=3
L10_rev21 = (C_dyn21 / P_eq21) ** p_exp21 # millions de tours (~ 385.4 millions de tours)
L10_h21 = (1e6 * L10_rev21) / (60.0 * N_tour21) # heures (~ 4340 h)
add("duree-roulement", title="Calcul de la durée de vie nominale L10 d'un roulement",
 sector="Automobile & Électromécanique", sector_code="AUT", region="Casablanca-Settat", level=3,
 context="Le roulement côté entraînement d'une pompe haute pression de lavage industriel a subi deux défaillances prématurées. L'ingénieur fiabilité recalcule la durée de vie théorique nominale L10h selon la norme ISO 281.",
 data=[["Capacité de charge dynamique catalogue","C","81,5 kN"],["Charge dynamique radiale équivalente","P","11,2 kN"],["Vitesse de rotation nominale","n","1 480 tr/min"],["Exposant de la loi de fatigue (billes)","p","3 (10/3 pour rouleaux)"]],
 questions=["La durée de vie nominale en millions de révolutions L10 ;","La durée de vie nominale en heures de service L10h ;","L'évaluation de la suffisance pour un fonctionnement continu 24/7 sur 2 ans."],
 formulas=["L_{10} = \\left( \\frac{C}{P} \\right)^p \\quad [10^6\\text{ tr}]", "L_{10h} = \\frac{10^6 \\cdot L_{10}}{60 \\cdot n} \\quad [\\text{heures}]"],
 answer_key=[f"L10 = {fr(L10_rev21,1)} millions de tours", f"L10h = {fr(L10_h21,0)} heures", "Insuffisant pour 2 ans continu (17 500 h) : passer sur série renforcée ou roulement à rouleaux"])

# 22 -- Industrial Engineering: EOQ Wilson stock optimization
D_an22 = 12000.0 # filtres consommés par an
S_order22 = 180.0 # MAD par commande (coût de passation)
H_holding22 = 4.5 # MAD par unité et par an (possession stock ~ 15% prix unitaire)
Q_star22 = math.sqrt(2.0 * D_an22 * S_order22 / H_holding22) # Q* ~ 979.8 -> 980
N_comm22 = D_an22 / Q_star22
add("quantite-economique-stock", title="Optimisation de stock par la quantité économique de Wilson",
 sector="Logistique & Distribution", sector_code="LOG", region="Casablanca-Settat", level=1,
 context="Le magasin central des pièces de rechange d'un groupe industriel gère une référence de filtre hydraulique à rotation élevée. Pour réduire les coûts combinés de commande et de stockage, le logisticien applique le modèle de Wilson.",
 data=[["Consommation annuelle régulière","D","12 000 unités/an"],["Coût administratif d'une passation de commande","S","180 MAD/commande"],["Coût unitaire annuel de possession de stock","H","4,50 MAD/(unité·an)"]],
 questions=["La quantité économique optimale de commande Q* ;","Le nombre optimal de commandes par an et la périodicité de réapprovisionnement ;","Le coût global annuel de gestion du stock à l'optimum."],
 formulas=["Q^* = \\sqrt{\\frac{2 \\cdot D \\cdot S}{H}}", "N = \\frac{D}{Q^*}", "\\text{Coût total} = \\sqrt{2 \\cdot D \\cdot S \\cdot H}"],
 answer_key=[f"Lot économique Q* = {fr(Q_star22,0)} unités", f"Nombre de commandes = {fr(N_comm22,1)} commandes/an", f"Coût total optimal = {fr(math.sqrt(2*D_an22*S_order22*H_holding22),0)} MAD/an"])

# 23 -- Industrial Engineering: SMED changeover reduction gain
T_chg_init23 = 75.0 # min
T_chg_final23 = 22.0 # min (après externalisation et standardisation)
gain_chg23 = T_chg_init23 - T_chg_final23 # 53 min gagnées
N_chg_hebdo23 = 14 # 14 changements de format par semaine
gain_h_an23 = (gain_chg23 * N_chg_hebdo23 * 48.0) / 60.0 # h/an pour 48 semaines
prod_horaire23 = 1200.0 # briques/heure
prod_sup23 = gain_h_an23 * prod_horaire23
add("gain-changement-format-smed", title="Gain de capacité par réduction de temps de changement (SMED)",
 sector="Agroalimentaire", sector_code="AGR", region="Fès-Meknès", level=2,
 context="Une ligne de conditionnement de jus d'agrumes subit de fréquents changements de formats de briques. Un chantier SMED a permis de convertir les réglages internes en tâches externes préparées à l'avance.",
 data=[["Temps initial de changement de format","T₁","75 min"],["Temps de changement atteint après SMED","T₂","22 min"],["Nombre de changements de série","N","14 changements/semaine"],["Semaines d'activité annuelle","S","48 semaines/an"],["Cadence nominale de la ligne","C","1 200 briques/h"]],
 questions=["Le gain de temps de calage par changement et en pourcentage ;","Le nombre d'heures de production libérées sur l'année ;","Le supplément de production annuel permis par cette disponibilité recouvrée."],
 formulas=["\\Delta t = T_1 - T_2", "\\text{Heures gagnées} = \\frac{\\Delta t \\cdot N \\cdot S}{60}", "\\text{Gain production} = \\text{Heures} \\cdot C"],
 answer_key=[f"Gain par changement = {fr(gain_chg23,0)} min ({fr(gain_chg23/T_chg_init23*100,1)} %)", f"Temps de production dégagé = {fr(gain_h_an23,0)} heures/an", f"Production additionnelle possible = {fr(prod_sup23,0)} briques/an"])

# 24 -- Industrial Engineering: MTBF and MTTR Reliability Analysis
T_oper24 = 30.0 * 24.0 # 720 heures sur le mois
N_pannes24 = 12 # pannes
T_arret_tot24 = 42.0 # heures d'arrêt cumulées
MTTR24 = T_arret_tot24 / N_pannes24 # 3.5 h
MTBF24 = (T_oper24 - T_arret_tot24) / N_pannes24 # 56.5 h
Dispo_intr24 = MTBF24 / (MTBF24 + MTTR24) # 94.17 %
add("fiabilite-mtbf-mttr", title="Calcul de fiabilité opérationnelle par les indicateurs MTBF et MTTR",
 sector="Automobile & Électromécanique", sector_code="AUT", region="Tanger-Tétouan-Al Hoceïma", level=1,
 context="Dans le cadre du tableau de bord de maintenance préventive d'une presse d'emboutissage, l'analyste méthodes consolide les interventions curatives du mois écoulé pour juger de la politique de maintenance.",
 data=[["Période d'analyse continue","T_tot","720 heures (30 jours)"],["Nombre d'arrêts pour pannes constatés","N","12 pannes"],["Temps cumulé d'indisponibilité pour réparation","T_rep","42 heures"]],
 questions=["Le temps moyen de réparation (MTTR) ;","Le temps moyen de bon fonctionnement entre pannes (MTBF) ;","Le taux de disponibilité opérationnelle intrinsèque de la presse."],
 formulas=["\\text{MTTR} = \\frac{\\sum T_{\\text{arrêt}}}{N}", "\\text{MTBF} = \\frac{T_{\\text{ouverture}} - \\sum T_{\\text{arrêt}}}{N}", "D_i = \\frac{\\text{MTBF}}{\\text{MTBF} + \\text{MTTR}}"],
 answer_key=[f"MTTR = {fr(MTTR24,2)} h ({fr(MTTR24*60,0)} min)", f"MTBF = {fr(MTBF24,1)} h", f"Disponibilité intrinsèque = {fr(Dispo_intr24*100,2)} %"])

# Problems 25 to 30 extension for gen_bank.py

# 25 -- Industrial Engineering: M/M/1 Queue at factory loading dock
lambda_camion25 = 3.2 # camions qui arrivent par heure
mu_quai25 = 4.0 # camions traités par heure par le poste de chargement
rho_quai25 = lambda_camion25 / mu_quai25 # 0.80 (taux d'occupation)
L_file25 = (rho_quai25 ** 2) / (1.0 - rho_quai25) # 3.2 camions en attente
L_sys25 = rho_quai25 / (1.0 - rho_quai25) # 4.0 camions dans le système
W_attente25 = L_file25 / lambda_camion25 # 1.0 heure d'attente
W_sejour25 = 1.0 / (mu_quai25 - lambda_camion25) # 1.25 heure
add("file-attente-quai", title="Modélisation de file d'attente M/M/1 à un quai d'expédition",
 sector="Logistique & Distribution", sector_code="LOG", region="Casablanca-Settat", level=3,
 context="Le quai de pesée et de chargement d'un silo portuaire connaît des congestions répétées de camions aux heures de pointe. Le responsable d'exploitation utilise le modèle de file d'attente markovien M/M/1 pour évaluer l'opportunité d'ouvrir une seconde balance.",
 data=[["Taux moyen d'arrivée des camions","λ","3,2 camions/h (loi de Poisson)"],["Capacité moyenne de traitement du quai","μ","4,0 camions/h (loi exponentielle)"]],
 questions=["Le taux d'utilisation du quai (intensité de trafic ρ) ;","Le nombre moyen de camions qui patientent dans la file d'attente (Lq) ;","Le temps moyen d'attente d'un transporteur avant le début du chargement (Wq en minutes)."],
 formulas=["\\rho = \\frac{\\lambda}{\\mu}", "L_q = \\frac{\\rho^2}{1 - \\rho}", "W_q = \\frac{L_q}{\\lambda} = \\frac{\\rho}{\\mu - \\lambda}"],
 answer_key=[f"Intensité de trafic ρ = {fr(rho_quai25*100,1)} %", f"Longueur moyenne de file Lq = {fr(L_file25,1)} camions", f"Temps d'attente moyen Wq = {fr(W_attente25*60,0)} min ({fr(W_attente25,2)} h)"])

# 26 -- Thermal: Cold storage room thermal refrigeration load
A_paroi26 = 340.0 # m² (surface parois + sol + plafond)
U_paroi26 = 0.22 # W/(m²·K) panneaux sandwich PIR 100 mm
T_ext26 = 38.0 # °C été marocain
T_chambre26 = 2.0 # °C conservation fruits
Q_trans26 = A_paroi26 * U_paroi26 * (T_ext26 - T_chambre26) / 1000.0 # kW (~ 2.69 kW)
M_marchandise26 = 5000.0 # kg de denrées admises par jour
cp_fruit26 = 3.8 # kJ/(kg·K)
T_in_fruit26 = 25.0 # °C
T_final_fruit26 = 2.0 # °C
t_refroid26 = 18.0 * 3600.0 # 18 h
Q_produit26 = M_marchandise26 * cp_fruit26 * (T_in_fruit26 - T_final_fruit26) / t_refroid26 # kW (~ 6.75 kW)
Q_divers26 = 1.8 # kW (éclairage, ventilateurs évaporateur, ouvertures de portes)
Q_froid_tot26 = (Q_trans26 + Q_produit26 + Q_divers26) * 1.15 # marge sécurité 15%
add("bilan-chambre-froide", title="Bilan thermique frigorifique d'une chambre froide de conservation",
 sector="Agroalimentaire", sector_code="AGR", region="Souss-Massa", level=2,
 context="Une station d'emballage d'agrumes installe une chambre froide positive pour le stockage temporaire avant expédition frigorifique. L'ingénieur utilités doit calculer le bilan frigorifique pour dimensionner le groupe compresseur.",
 data=[["Surface totale de l'enveloppe isolée","S","340 m²"],["Coefficient de transmission thermique parois","U","0,22 W/(m²·K)"],["Température extérieure maximale été","Text","38 °C"],["Température de consigne chambre","Tint","2 °C"],["Entrée journalière de fruits","m","5 000 kg/jour"],["Chaleur massique des fruits","cp","3,8 kJ/(kg·K)"],["Refroidissement du produit","T_fruit","25 °C → 2 °C en 18 h"],["Charges internes annexes (ventilateurs, éclairage)","Q_int","1,8 kW"]],
 questions=["La charge thermique transmise par conduction à travers les parois ;","La puissance frigorifique requise pour le refroidissement des fruits en 18 h ;","La puissance frigorifique nominale de l'évaporateur avec 15 % de marge de sécurité."],
 formulas=["\\Phi_{\\text{paroi}} = U \\cdot S \\cdot (T_{\\text{ext}} - T_{\\text{int}})", "\\Phi_{\\text{prod}} = \\frac{m \\cdot c_p \\cdot \\Delta T}{\\Delta t}", "\\Phi_{\\text{tot}} = (\\Phi_{\\text{paroi}} + \\Phi_{\\text{prod}} + Q_{\\text{int}}) \\cdot 1{,}15"],
 answer_key=[f"Transmission parois = {fr(Q_trans26,2)} kW", f"Puissance refroidissement produit = {fr(Q_produit26,2)} kW", f"Puissance frigorifique à installer = {fr(Q_froid_tot26,2)} kW (marge 15 %)"])

# 27 -- Thermal: Cooling tower makeup water consumption
Q_rej27 = 2400.0 # kW thermiques évacués par la tour
cp_eau27 = 4.18 # kJ/(kg·K)
delta_T_tour27 = 6.0 # °C (par ex. 36°C -> 30°C)
Q_eau_circ27 = Q_rej27 / (cp_eau27 * delta_T_tour27) # kg/s (~ 95.69 kg/s = 344.5 m³/h)
# Évaporation approximative ~ 0.00153 * Q_rej(kW) ou 1.8 kg d'eau évaporée par 1000 kcal (~0.62 L/kWh)
# E = Q_rej / h_fg_eau (h_fg = 2450 kJ/kg) -> E = Q_rej / 2450 = 0.98 kg/s
Q_evap27 = (Q_rej27 / 2420.0) * 3.6 # m³/h (~ 3.57 m³/h)
# Purge de déconcentration pour Cycles de concentration CC = 3.5
CC27 = 3.5
Q_purge27 = Q_evap27 / (CC27 - 1.0) # m³/h (~ 1.43 m³/h)
Q_appoint27 = Q_evap27 + Q_purge27 # m³/h (~ 5.00 m³/h)
add("eau-appoint-tour-refroidissement", title="Consommation d'eau d'appoint d'une tour de refroidissement",
 sector="Chimie lourde", sector_code="CHM", region="Casablanca-Settat", level=2,
 context="Le complexe de cogénération et de synthèse chimique refroidit ses condenseurs à l'aide d'une tour aéroréfrigérante semi-fermée. Face aux restrictions hydriques, l'usine doit estimer son débit d'eau d'appoint (évaporation + déconcentration).",
 data=[["Puissance thermique dissipée par la tour","Pth","2 400 kW"],["Chaleur latente d'évaporation de l'eau","Lv","2 420 kJ/kg"],["Cycles de concentration maintenus","CC","3,5"],["Heures de marche continue","h","8 000 h/an"]],
 questions=["Le débit d'eau évaporé dans l'atmosphère en m³/h ;","Le débit de purge de déconcentration nécessaire pour stabiliser le salinité ;","Le débit horaire et le volume annuel global d'eau d'appoint fraîche requis."],
 formulas=["Q_{\\text{evap}} = \\frac{P_{\\text{th}}}{L_v} \\cdot 3{,}6 \\quad [\\text{m}^3/\\text{h}]", "Q_{\\text{purge}} = \\frac{Q_{\\text{evap}}}{\\text{CC} - 1}", "Q_{\\text{appoint}} = Q_{\\text{evap}} + Q_{\\text{purge}}"],
 answer_key=[f"Évaporation = {fr(Q_evap27,2)} m³/h", f"Purge déconcentration = {fr(Q_purge27,2)} m³/h", f"Appoint horaire = {fr(Q_appoint27,2)} m³/h ; Consommation annuelle = {fr(Q_appoint27*8000,0)} m³/an"])

# 28 -- Fluids: Agricultural drip irrigation network pressure drop (Hazen-Williams)
Q_rampe28 = 18.0 / 3600.0 # m³/s (18 m³/h rampe principale)
D_int28 = 0.082 # m (PEHD 90 mm ext, PN10, Di = 82 mm)
L_irr28 = 420.0 # m
C_hw28 = 140.0 # Hazen-Williams pour PEHD neuf lisse
# Hazen-Williams head loss J = 10.67 * Q^1.852 / (C^1.852 * D^4.87)
J_hw28 = 10.67 * (Q_rampe28 ** 1.852) / ((C_hw28 ** 1.852) * (D_int28 ** 4.87)) # m/m
hf_tot28 = J_hw28 * L_irr28 # mCE
add("perte-charge-irrigation-pehd", title="Pertes de charge d'une rampe d'irrigation goutte-à-goutte en PEHD",
 sector="Agroalimentaire & Hydraulique", sector_code="AGR", region="Souss-Massa", level=2,
 context="Dans une exploitation agricole d'agrumes irriguée au goutte-à-goutte, une conduite principale en PEHD de 420 m alimente les secteurs d'arrosage. L'agronome dimensionne la pression en tête de réseau pour assurer la pression minimale aux goutteurs.",
 data=[["Débit transitant dans la conduite principale","Q","18 m³/h (0,005 m³/s)"],["Diamètre intérieur de la conduite PEHD","Di","82 mm (DN90 PEHD)"],["Longueur totale de la ligne","L","420 m"],["Coefficient de rugosité de Hazen-Williams","C","140 (PEHD neuf)"]],
 questions=["La vitesse d'écoulement de l'eau dans la conduite ;","La perte de charge linéique unitaire selon Hazen-Williams ;","La perte de charge totale sur la longueur et la pression minimale à fournir en tête."],
 formulas=["v = \\frac{4 \\cdot Q}{\\pi \\cdot D_i^2}", "J = 10{,}67 \\cdot \\frac{Q^{1{,}852}}{C^{1{,}852} \\cdot D_i^{4{,}87}} \\quad [\\text{m/m}]", "\\Delta h = J \\cdot L"],
 answer_key=[f"Vitesse d'écoulement = {fr(4*Q_rampe28/(math.pi*D_int28**2),2)} m/s", f"Perte linéique J = {fr(J_hw28*1000,2)} mm/m ({fr(J_hw28,4)} mCE/m)", f"Perte de charge totale = {fr(hf_tot28,2)} mCE ({fr(hf_tot28*0.0981,2)} bar)"])

# 29 -- Electrical: Three-phase motor starting current and torque drop
I_nom29 = 68.0 # A (moteur 37 kW 400V)
ratio_Id29 = 6.8 # Id/In démarrage direct
I_dem_dir29 = I_nom29 * ratio_Id29 # 462.4 A
# En démarrage étoile-triangle (Y-D) : I_dem = 1/3 * I_dem_dir
I_dem_yd29 = I_dem_dir29 / 3.0 # 154.1 A
C_nom29 = 37000.0 / (2.0 * math.pi * 1475.0 / 60.0) # ~ 239.5 N.m
ratio_Cd29 = 2.2 # Cd/Cn en direct
C_dem_dir29 = C_nom29 * ratio_Cd29
C_dem_yd29 = C_dem_dir29 / 3.0 # Couple divisé par 3 en étoile
add("demarrage-moteur-asynchrone", title="Courant d'appel et couple au démarrage étoile-triangle",
 sector="Automobile & Électromécanique", sector_code="AUT", region="Tanger-Tétouan-Al Hoceïma", level=1,
 context="Le démarrage direct d'un broyeur de 37 kW provoque des creux de tension perturbant les automates voisins sur le réseau d'usine. L'électricien étudie le passage en démarreur étoile-triangle pour atténuer l'appel de courant.",
 data=[["Courant nominal moteur à pleine charge","In","68 A"],["Rapport de courant au démarrage direct","Id/In","6,8"],["Rapport de couple au démarrage direct","Cd/Cn","2,2"],["Couple nominal mécanique","Cn","240 N·m"]],
 questions=["Le courant d'appel et le couple de démarrage en démarrage direct ;","Le courant de démarrage et le couple de décollage en montage étoile-triangle ;","La condition de couple résistant pour que le moteur démarre en charge sans caler."],
 formulas=["I_{d,\\text{direct}} = I_n \\cdot (I_d/I_n)", "I_{d,\\text{Y}} = \\frac{1}{3} \\cdot I_{d,\\text{direct}}", "C_{d,\\text{Y}} = \\frac{1}{3} \\cdot C_{d,\\text{direct}}"],
 answer_key=[f"Démarrage direct : Id = {fr(I_dem_dir29,1)} A ; Cd = {fr(C_dem_dir29,1)} N·m", f"Démarrage étoile-triangle : Id = {fr(I_dem_yd29,1)} A ; Cd = {fr(C_dem_yd29,1)} N·m", "Le couple résistant à l'arrêt doit être inférieur à 176 N·m pour permettre le décollage"])

# 30 -- Electrical: Transformer losses and full day efficiency
S_trans30 = 630.0 # kVA (transformateur MT/BT 22kV / 400V)
P_fer30 = 1.3 # kW (pertes à vide fer constantes)
P_cu_nom30 = 6.5 # kW (pertes Joule cuivre à pleine charge)
charge_pct30 = 0.65 # taux de charge moyen journalier (65 %)
cos_phi30 = 0.88
# Pertes cuivre effectives Pcu = Pcu_nom * (charge)^2
P_cu_eff30 = P_cu_nom30 * (charge_pct30 ** 2) # kW (~ 2.746 kW)
P_pertes_tot30 = P_fer30 + P_cu_eff30 # kW (~ 4.046 kW)
P_utile30 = S_trans30 * charge_pct30 * cos_phi30 # kW (~ 360.36 kW)
eta_trans30 = P_utile30 / (P_utile30 + P_pertes_tot30) # ~ 0.9889 (98.89 %)
pertes_kwh_an30 = P_pertes_tot30 * 8760.0 # kWh/an
cost_pertes30 = pertes_kwh_an30 * 1.05 # MAD/an
add("rendement-transformateur", title="Bilan des pertes et rendement d'un transformateur de distribution",
 sector="Matériaux de construction", sector_code="MAT", region="Béni Mellal-Khénifra", level=2,
 context="Une cimenterie alimente son atelier d'ensachage par un transformateur triphasé 630 kVA 22 kV / 400 V. Le service énergie analyse le taux de charge réel pour optimiser le rendement énergétique global de la sous-station.",
 data=[["Puissance apparente nominale transfo","Sn","630 kVA"],["Pertes fer à vide mesurées","P0","1,3 kW (1 300 W)"],["Pertes cuivre à charge nominale","Pcc","6,5 kW (6 500 W)"],["Taux de charge moyen de l'installation","β","0,65 (65 %)"],["Facteur de puissance moyen de l'atelier","cos φ","0,88"],["Tarif électricité moyen","c","1,05 MAD/kWh"]],
 questions=["Les pertes totales du transformateur sous un taux de charge de 65 % ;","La puissance active utile délivrée et le rendement instantané du transformateur ;","L'énergie totale dissipée en pertes thermiques sur une année (8 760 h) et son coût en MAD."],
 formulas=["P_{\\text{pertes}} = P_0 + \\beta^2 \\cdot P_{cc}", "P_{\\text{utile}} = \\beta \\cdot S_n \\cdot \\cos \\varphi", "\\eta = \\frac{P_{\\text{utile}}}{P_{\\text{utile}} + P_{\\text{pertes}}}"],
 answer_key=[f"Pertes cuivre = {fr(P_cu_eff30,2)} kW ; Pertes totales = {fr(P_pertes_tot30,2)} kW", f"Puissance utile = {fr(P_utile30,1)} kW ; Rendement = {fr(eta_trans30*100,2)} %", f"Pertes annuelles = {fr(pertes_kwh_an30,0)} kWh/an ; Coût = {fr(cost_pertes30,0)} MAD/an"])

TEX_NEW = {
 "compensation-cosphi": ["Q_c = P \\cdot (\\tan \\varphi_1 - \\tan \\varphi_2)", "S = \\sqrt{P^2 + Q^2}"],
 "section-cable": ["\\Delta U = \\sqrt{3} \\cdot I_b \\cdot \\frac{L}{S} \\cdot \\rho \\cdot \\cos \\varphi", "S_{\\min} = \\frac{\\sqrt{3} \\cdot I_b \\cdot L \\cdot \\rho \\cdot \\cos \\varphi}{\\Delta U_{\\max}}"],
 "solaire-toiture": ["P_c = S \\cdot p", "E_{\\text{an}} = P_c \\cdot H_{\\text{site}} \\cdot \\text{PR} / 1\\text{ kW/m}^2", "\\text{Gain} = E_{\\text{an}} \\cdot c"],
 "purgeur-vapeur": ["Q = 0{,}51 \\cdot P_{\\text{abs}} \\cdot d^2", "\\text{Perte} = Q \\cdot h / 1000", "\\text{Coût} = \\text{Perte} \\cdot c_{\\text{vap}}"],
 "calorifugeage-tuyauterie": ["q = \\pi \\cdot D_e \\cdot h \\cdot (T_p - T_a)", "\\Phi = q \\cdot L", "\\text{Gain} = \\Phi \\cdot \\eta_{\\text{iso}} \\cdot t \\cdot c_{\\text{th}}", "\\text{TRI} = \\frac{C_{\\text{inv}}}{\\text{Gain}}"],
 "coup-de-belier": ["\\Delta P = \\rho \\cdot c \\cdot \\Delta v", "\\Delta H = \\frac{c \\cdot \\Delta v}{g}", "T_{\\text{crit}} = \\frac{2 \\cdot L}{c}"],
 "cavitation-npsh": ["\\text{NPSH}_a = \\frac{P_{\\text{atm}} - P_v}{\\rho \\cdot g} - H_a - \\Delta h_a", "\\text{Marge} = \\text{NPSH}_a - \\text{NPSH}_r \\ge 0{,}5\\text{ m}"],
 "arbre-torsion-flexion": ["C = \\frac{60 \\cdot P}{2\\pi \\cdot N}", "M_{\\text{id}} = \\sqrt{M_f^2 + C^2}", "d_{\\min} = \\left( \\frac{32 \\cdot M_{\\text{id}}}{\\pi \\cdot R_{pe}} \\right)^{1/3}"],
 "serrage-boulon": ["C_s = k \\cdot F_0 \\cdot d", "\\sigma = \\frac{F_0}{A_s}"],
 "duree-roulement": ["L_{10} = \\left( \\frac{C}{P} \\right)^p", "L_{10h} = \\frac{10^6 \\cdot L_{10}}{60 \\cdot n}"],
 "quantite-economique-stock": ["Q^* = \\sqrt{\\frac{2 \\cdot D \\cdot S}{H}}", "N = \\frac{D}{Q^*}", "\\text{Coût total} = \\sqrt{2 \\cdot D \\cdot S \\cdot H}"],
 "gain-changement-format-smed": ["\\Delta t = T_1 - T_2", "\\text{Heures gagnées} = \\frac{\\Delta t \\cdot N \\cdot S}{60}", "\\text{Gain prod} = \\text{Heures} \\cdot C"],
 "fiabilite-mtbf-mttr": ["\\text{MTTR} = \\frac{\\sum T_{\\text{arrêt}}}{N}", "\\text{MTBF} = \\frac{T_{\\text{ouv}} - \\sum T_{\\text{arrêt}}}{N}", "D_i = \\frac{\\text{MTBF}}{\\text{MTBF} + \\text{MTTR}}"],
 "file-attente-quai": ["\\rho = \\frac{\\lambda}{\\mu}", "L_q = \\frac{\\rho^2}{1 - \\rho}", "W_q = \\frac{\\rho}{\\mu - \\lambda}"],
 "bilan-chambre-froide": ["\\Phi_{\\text{paroi}} = U \\cdot S \\cdot (T_{\\text{ext}} - T_{\\text{int}})", "\\Phi_{\\text{prod}} = \\frac{m \\cdot c_p \\cdot \\Delta T}{\\Delta t}", "\\Phi_{\\text{tot}} = (\\Phi_{\\text{paroi}} + \\Phi_{\\text{prod}} + Q_{\\text{int}}) \\cdot 1{,}15"],
 "eau-appoint-tour-refroidissement": ["Q_{\\text{evap}} = \\frac{P_{\\text{th}}}{L_v} \\cdot 3{,}6", "Q_{\\text{purge}} = \\frac{Q_{\\text{evap}}}{\\text{CC} - 1}", "Q_{\\text{appoint}} = Q_{\\text{evap}} + Q_{\\text{purge}}"],
 "perte-charge-irrigation-pehd": ["v = \\frac{4 \\cdot Q}{\\pi \\cdot D_i^2}", "J = 10{,}67 \\cdot \\frac{Q^{1{,}852}}{C^{1{,}852} \\cdot D_i^{4{,}87}}", "\\Delta h = J \\cdot L"],
 "demarrage-moteur-asynchrone": ["I_{d,\\text{direct}} = I_n \\cdot (I_d/I_n)", "I_{d,\\text{Y}} = \\frac{1}{3} \\cdot I_{d,\\text{direct}}", "C_{d,\\text{Y}} = \\frac{1}{3} \\cdot C_{d,\\text{direct}}"],
 "rendement-transformateur": ["P_{\\text{pertes}} = P_0 + \\beta^2 \\cdot P_{cc}", "P_{\\text{utile}} = \\beta \\cdot S_n \\cdot \\cos \\varphi", "\\eta = \\frac{P_{\\text{utile}}}{P_{\\text{utile}} + P_{\\text{pertes}}}"],
}

TEX = {
 **TEX_NEW,
 "pompage": ["H=\\Delta z+\\Bigl(f\\frac{L}{D}+\\sum K\\Bigr)\\frac{v^{2}}{2g}", "f=\\frac{0{,}25}{\\left[\\log_{10}\\!\\left(\\frac{\\varepsilon}{3{,}7\\,D}+\\frac{5{,}74}{\\mathrm{Re}^{0{,}9}}\\right)\\right]^{2}}", "P=\\frac{\\rho\\, g\\, Q\\, H}{\\eta}"],
 "echangeur": ["\\Phi=\\dot m\\,c_p\\,\\Delta T", "\\Delta T_{lm}=\\frac{\\Delta T_2-\\Delta T_1}{\\ln\\left(\\Delta T_2/\\Delta T_1\\right)}", "A=\\frac{\\Phi}{U\\,\\Delta T_{lm}}"],
 "fuite-air": ["\\dot m=C_d\\,A\\,p\\sqrt{\\frac{\\gamma}{R\\,T}}\\left(\\frac{2}{\\gamma+1}\\right)^{\\frac{\\gamma+1}{2(\\gamma-1)}}", "Q_n=\\frac{\\dot m}{\\rho_n},\\quad \\rho_n=\\frac{p_0}{R\\,T_0}", "\\text{Coût}=Q_n\\,e\\,h\\,c"],
 "variateur-ventilateur": ["P\\propto n^{3},\\quad Q\\propto n\\;\\Rightarrow\\;P=P_n\\left(\\frac{Q}{Q_n}\\right)^{3}", "P_{var}=\\frac{P_n\\,(Q/Q_n)^{3}}{\\eta_v}"],
 "convoyeur": ["q=\\frac{Q}{3{,}6\\,v}", "P_{lev}=\\frac{Q}{3{,}6}\\,g\\,H", "P_{fr}=f\\,g\\,L\\,(m'+q)\\,v", "P_{mot}=\\frac{P_{lev}+P_{fr}}{\\eta}"],
 "chaudiere": ["P_u=\\frac{\\dot m\\,(h_v-h_e)}{3600}", "P_c=G\\cdot \\mathrm{PCI}", "\\eta=\\frac{P_u}{P_c}"],
 "mco-unites": ["1\\ \\mathrm{lbf\\cdot s}=4{,}448222\\ \\mathrm{N\\cdot s}", "\\Delta v=\\frac{J}{m}", "\\text{facteur}=\\frac{J_{\\text{réel}}}{J_{\\text{lu}}}"],
 "kanban-cablage": ["K = \\frac{D \\cdot L \\cdot (1 + \\alpha)}{C}", "\\text{WIP}_{\\max} = K \\cdot C"],
 "trs-ensachage": ["\\text{Disponibilité} = \\frac{T_{\\text{fonct}}}{T_{\\text{ouv}}}", "\\text{Performance} = \\frac{N_{\\text{tot}} \\cdot t_{\\text{cycle}}}{T_{\\text{fonct}}}", "\\text{Qualité} = \\frac{N_{\\text{bon}}}{N_{\\text{tot}}}", "\\text{TRS} = D \\cdot P \\cdot Q"],
 "goulot-engrais": ["L = \\lambda \\cdot W", "W_{\\text{crit}} = \\frac{L_{\\max}}{\\lambda_{\\text{pic}}}"],
 "equilibrage-textile": ["N_{\\text{théo}} = \\frac{\\sum t_i}{T_c}", "\\text{Efficience} = \\frac{\\sum t_i}{N_{\\text{retenu}} \\cdot T_c}", "\\text{Perte} = (N \\cdot T_c) - \\sum t_i"],
}
for b in bank: b["formulas_tex"] = TEX[b["slug"]]

# Clean old bank json files
for f in OUT.glob("*.json"):
    f.unlink()

for i, b in enumerate(bank, 1):
    b["id"] = i; (OUT / f"{i:02d}-{b['slug']}.json").write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    print(i, b["slug"], "|", " | ".join(b["answer_key"]))

import validate_bank; validate_bank.main()
