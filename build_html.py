#!/usr/bin/env python3
"""Fill template.html from an edition JSON.  usage: build_html.py edition.json out.html [--inline]
--inline embeds the images as base64 (single-file page); default keeps relative assets/ paths
(upload assets and use absolute URLs for email)."""
import json, sys, random, base64, html, pathlib, os
from PIL import Image, ImageDraw
HERE = pathlib.Path(__file__).parent
L = {
 "fr": dict(no="N°",kind="Fiche problème",sector="Secteur",region="Région",level="Niveau",status="Statut",source="Source",
   realistic="Problème réaliste",real="Cas public réel",
   note_realistic="Classe de problèmes typique d'un site industriel. Aucune entreprise n'est désignée, aucun besoin d'une entreprise précise n'est affirmé.",
   note_real="Cas public documenté. La source ci-dessous fait foi.",
   nosrc="— (aucune source : problème réaliste)",ctx="Contexte",data="Données",ask="À déterminer",form="Formules utiles",
   finger="Empreinte de l'édition",scan="Archive et dépôt de solution",archive="Voir l'archive",unsub="Se désinscrire",
   foot="Vous recevez ce message car vous êtes inscrit(e) à Acta Problemata. Chaque fiche est soit un cas public sourcé, soit un problème réaliste, jamais présenté comme le besoin d'une entreprise nommée."),
 "en": dict(no="No.",kind="Problem sheet",sector="Sector",region="Region",level="Level",status="Status",source="Source",
   realistic="Realistic problem",real="Real public case",
   note_realistic="A problem class typical of an industrial site. No company is named and no need of a specific company is claimed.",
   note_real="Documented public case. The source below is authoritative.",
   nosrc="— (no source: realistic problem)",ctx="Context",data="Given data",ask="To determine",form="Useful formulas",
   finger="Edition fingerprint",scan="Archive and solution upload",archive="Open the archive",unsub="Unsubscribe",
   foot="You receive this because you subscribed to Acta Problemata. Each sheet is either a sourced public case or a realistic problem, never presented as the need of a named company."),
}
def fingerprint(seed, path, cols=64, rows=14, pitch=8, r=3):
    rnd = random.Random(seed); S = 2
    im = Image.new("RGBA", (cols*pitch*S, rows*pitch*S), (0,0,0,0)); d = ImageDraw.Draw(im)
    for i in range(cols):
        p = 0.04 + 0.96*((i+1)/cols)**1.5
        for j in range(rows):
            if rnd.random() < p:
                x, y = (i+.5)*pitch*S, (j+.5)*pitch*S
                d.ellipse([x-r*S, y-r*S, x+r*S, y+r*S], fill=(21,21,21,255))
    im.resize((cols*pitch, rows*pitch), Image.LANCZOS).save(path)
def sec(n, title, body):
    return (f'<div style="font-family:\'Courier New\',monospace;font-size:10px;margin:18px 0 6px 0;border-bottom:1px solid #151515;padding-bottom:3px;text-transform:uppercase;letter-spacing:1px;">'
            f'<span style="color:#E8500C;">[{n:02d}]</span>&nbsp; <b style="font-family:Inter,Helvetica,Arial,sans-serif;font-size:11px;">{html.escape(title)}</b></div>{body}')
def main():
    ed_raw = pathlib.Path(sys.argv[1]).read_bytes()
    try:
        ed = json.loads(ed_raw.decode("utf-8-sig"))
    except UnicodeDecodeError:
        ed = json.loads(ed_raw.decode("utf-16"))
    out = sys.argv[2]; inline = "--inline" in sys.argv
    t = L[ed["lang"]]; e = html.escape
    realistic = ed["status"] == "realistic"
    rows = "".join(
        f'<tr><td style="padding:2px 12px 2px 0;font-size:12px;">{e(a)}</td><td style="padding:2px 12px 2px 0;font-size:12px;font-style:italic;font-family:Georgia,serif;">{e(b)}</td><td style="padding:2px 0;font-size:12px;font-family:\'Courier New\',monospace;">{e(c)}</td></tr>'
        for a, b, c in ed["data"])
    qs = "".join(f'<tr><td valign="top" style="font-family:\'Courier New\',monospace;color:#E8500C;font-size:11px;padding:2px 8px 2px 0;">{i+1}.</td><td style="font-size:12.5px;line-height:18px;padding:2px 0;">{e(q)}</td></tr>' for i, q in enumerate(ed["questions"]))
    fm = "".join(f'<div style="font-family:\'Courier New\',monospace;font-size:12px;line-height:20px;background:#E7E2DA;padding:2px 10px;margin:3px 0;border-left:3px solid #E8500C;">{e(f)}</div>' for f in ed["formulas"])
    sections = (sec(1, t["ctx"], f'<div style="font-size:12.5px;line-height:19px;">{e(ed["context"])}</div>')
      + sec(2, t["data"], f'<table role="presentation" cellpadding="0" cellspacing="0" border="0">{rows}</table>')
      + sec(3, t["ask"], f'<table role="presentation" cellpadding="0" cellspacing="0" border="0">{qs}</table>')
      + sec(4, t["form"], fm))
    assets = HERE / "assets"; fp = f"fingerprint_{ed['edition_no']}.png"; fingerprint(ed["edition_no"], assets / fp)
    def src(name):
        if not inline:
            base = os.environ.get("ASSET_BASE", "assets").rstrip("/")
            return f"{base}/{name}"
        return "data:image/png;base64," + base64.b64encode((assets/name).read_bytes()).decode()
    src_txt = t["nosrc"] if (realistic or not ed["source_url"]) else ed["source_url"]
    m = {"LANG": ed["lang"], "CODE": ed["code"], "EDITION_NO": str(ed["edition_no"]), "NO_LABEL": t["no"], "KIND": t["kind"],
         "SECTOR_L": t["sector"], "SECTOR": e(ed["sector"]), "REGION_L": t["region"], "REGION": e(ed["region"]),
         "LEVEL_L": t["level"], "STARS": "★"*ed["level"] + "☆"*(3-ed["level"]), "TITLE": e(ed["title"]),
         "STATUS_L": t["status"], "STATUS": t["realistic"] if realistic else t["real"],
         "STATUS_NOTE": t["note_realistic"] if realistic else t["note_real"], "SOURCE_L": t["source"], "SOURCE": e(src_txt),
         "SECTIONS": sections, "FINGER_L": t["finger"], "SCAN_L": t["scan"], "ARCHIVE_URL": ed["archive_url"],
         "ARCHIVE_LABEL": t["archive"], "UNSUB_URL": ed["unsubscribe_url"], "UNSUB_LABEL": t["unsub"], "FOOTNOTE": t["foot"],
         "LOGO_SRC": src("logo.png"), "FINGER_SRC": src(fp), "QR_SRC": src("qr.png")}
    h = (HERE / "template.html").read_text(encoding="utf-8")
    for k, v in m.items(): h = h.replace("{{%s}}" % k, v)
    left = [x for x in __import__("re").findall(r"\{\{[A-Z_]+\}\}", h) if x != "{{UNSUB_URL}}"]
    assert not left, left
    pathlib.Path(out).write_text(h, encoding="utf-8"); print("wrote", out, len(h)//1024, "KB")
main()
