// ACTA PROBLEMATA — sheet.typ : industrial brutalist technical dossier (FR/EN)
// Aesthetics: ISO 128 / DIN 6771 technical documentation x Behance Synthetic Logistics.
// Color palette: Signal Orange (#FF4600), Deep Graphite (#121212 / #181818), Industrial Light Grey (#ECECE9 / #F3F1EC).
// Contract: ALWAYS exactly ONE A4 page.

#let d = json("sheet.json")
#let T = d.t

#let orange = rgb("#FF4600")
#let dark = rgb("#101010")
#let graphite = rgb("#181818")
#let soft-dark = rgb("#252525")
#let paper = rgb("#F3F1EC")
#let line-grey = rgb("#D1CEC7")
#let mid-grey = rgb("#88857F")
#let light-card = rgb("#E9E6E0")

#let mono = ("DejaVu Sans Mono",)
#let sans = ("Inter", "DejaVu Sans", "Helvetica Neue", "Arial")

#set document(title: d.title + " - Acta Problemata " + d.code, author: "Acta Problemata")
#let ed = if type(d.number) == int { d.number } else { 7 }
#let num = { let s = str(d.number); "0" * calc.max(0, 3 - s.len()) + s }

#let barcode(seed, w, h, fg: dark) = box(width: w, height: h, {
  let s = seed
  let x = 0mm
  while x < w - 0.8mm {
    s = calc.rem(s * 1103515245 + 12345, 2147483648)
    let bw = (1 + calc.rem(int(s / 65536), 3)) * 0.26mm
    place(top + left, dx: x, rect(width: bw, height: h, fill: fg, stroke: none))
    x += bw + (1 + calc.rem(int(s / 4096), 2)) * 0.28mm
  }
})

#let micro(s) = text(font: mono, size: 4.8pt, fill: mid-grey, tracking: 0.5pt)[#s]
#let micro-dark(s) = text(font: mono, size: 4.8pt, fill: dark, tracking: 0.5pt, weight: "bold")[#s]
#let micro-white(s) = text(font: mono, size: 4.8pt, fill: rgb("#C8C6C0"), tracking: 0.5pt)[#s]
#let micro-orange(s) = text(font: mono, size: 4.8pt, fill: orange, tracking: 0.5pt, weight: "bold")[#s]

#set page(
  paper: "a4",
  fill: paper,
  margin: (left: 12mm, right: 12mm, top: 50mm, bottom: 24mm),
  background: {
    // Technical boundary border
    place(top + left, dx: 6mm, dy: 6mm, rect(width: 198mm, height: 285mm, stroke: 0.5pt + line-grey))
    
    // Corner crosshairs / registration marks
    for (cx, cy) in ((6mm, 6mm), (204mm, 6mm), (6mm, 291mm), (204mm, 291mm)) {
      place(top + left, dx: cx - 2mm, dy: cy, line(length: 4mm, stroke: 0.4pt + dark))
      place(top + left, dx: cx, dy: cy - 2mm, line(angle: 90deg, length: 4mm, stroke: 0.4pt + dark))
    }
    
    // Top Telemetry Header Bar
    place(top + left, dx: 12mm, dy: 8mm, {
      grid(columns: (1fr, auto, 1fr), align: (left, center, right),
        micro([CORE_MORPHOLOGY \/\/ PROTOCOL_V3 \/\/ SYSTEM_TELEMETRY]),
        micro([+ LAT 31.6295° N, LON 7.9811° W + REF_ISO_128]),
        micro([CLASSIFICATION: INDUSTRIAL_CASE_STUDY \/\/ #d.code])
      )
    })
    
    // Fine-grained ruler scale at 11mm
    for i in range(0, 187) {
      let h = if calc.rem(i, 10) == 0 { 2.4mm } else if calc.rem(i, 5) == 0 { 1.6mm } else { 0.9mm }
      place(top + left, dx: (12 + i) * 1mm, dy: 10.5mm, line(angle: 90deg, length: h, stroke: 0.22pt + if calc.rem(i, 10) == 0 { dark } else { line-grey }))
    }
    place(top + left, dx: 105mm, dy: 10mm, line(angle: 90deg, length: 3.5mm, stroke: 0.7pt + orange))
    
    // ── HERO MASTHEAD (Behance Synthetic Logistics: massive numeral + dark spec matrix + stamp) ──
    let mast-y = 13mm
    let mast-h = 32mm
    
    // 1. SIGNAL ORANGE BLOCK — huge numeral (boarding-pass style, ~1/3 page width)
    place(top + left, dx: 12mm, dy: mast-y, rect(width: 56mm, height: mast-h, fill: orange, stroke: none, {
      place(top + left, dx: 3mm, dy: 1.5mm, micro-dark([#upper(T.no) IDENTIFIER]))
      place(top + left, dx: 1mm, dy: 2.5mm, text(font: sans, weight: "black", size: 62pt, tracking: -4pt, fill: dark)[#num])
      place(bottom + left, dx: 3mm, dy: -2mm, text(font: mono, size: 4.8pt, weight: "bold", fill: dark)[#upper(d.mode_label) \/\/ AP-#num])
    }))
    
    // 2. DEEP GRAPHITE TECHNICAL SPEC MATRIX — full dark card
    place(top + left, dx: 69.5mm, dy: mast-y, rect(width: 93mm, height: mast-h, fill: dark, stroke: none, {
      // Brand name top-left
      place(top + left, dx: 3mm, dy: 2.5mm, text(font: sans, weight: "black", size: 11pt, tracking: 1.5pt, fill: white)[ACTA PROBLEMATA])
      place(top + left, dx: 3mm, dy: 7.5mm, micro-orange([FICHE PROBLÈME \/\/ SYSTÈME DOSSIER \/\/ REPRODUCIBLE ENGINEERING PROBLEM]))
      place(top + right, dx: -3mm, dy: 2.5mm, rect(width: 3mm, height: 3mm, fill: orange))

      // Spec Grid Table (4 cols x 2 rows)
      place(top + left, dx: 3mm, dy: 11.5mm, grid(
        columns: (18mm, 32mm, 16mm, 20mm),
        rows: 4mm,
        stroke: 0.3pt + rgb("#2A2A2A"),
        inset: (x: 1.4mm, y: 0.8mm),
        align: horizon,
        micro([CODE :]), text(font: mono, size: 4.8pt, fill: rgb("#D0CEC8"))[#d.code],
        micro([DATE :]), text(font: mono, size: 4.8pt, fill: rgb("#D0CEC8"))[#d.date],
        micro([MODE :]), text(font: mono, size: 4.8pt, fill: rgb("#D0CEC8"))[#upper(d.mode_label)],
        micro([ÉDITION :]), text(font: mono, size: 4.8pt, fill: orange)[#num]
      ))

      // Barcode + serial
      place(bottom + left, dx: 3mm, dy: -5.5mm, barcode(ed * 17 + 9, 55mm, 5.5mm, fg: rgb("#505050")))
      place(bottom + left, dx: 3mm, dy: -1.8mm, micro-white([AP-#(ed)-SYS-OK \/\/ LANG: #upper(d.lang)]))
    }))

    // 3. RIGHT STAMP / MONOGRAM BOX — minimal dark
    place(top + left, dx: 164mm, dy: mast-y, rect(width: 34mm, height: mast-h, fill: graphite, stroke: 0.4pt + soft-dark, {
      place(top + left, dx: 2mm, dy: 2mm, micro-white([VALIDATION BADGE]))
      place(top + left, dx: 2mm, dy: 5mm, micro([STAMP_DIGITAL_AUTH]))
      place(top + center, dx: 0mm, dy: 8.5mm, box(width: 20mm, height: 17mm, clip: true, image("logo.svg", height: 18mm)))
      place(bottom + left, dx: 2mm, dy: -4.5mm, micro-orange([SECTOR: #upper(d.code.slice(11, 14))]))
      place(bottom + left, dx: 2mm, dy: -1.8mm, micro([UNIT: SI_METRIC]))
    }))
  },
  
  // ── FOOTER TELEMETRY & BARCODES ──
  footer: {
    set text(font: mono, size: 4.8pt, fill: dark)
    line(length: 100%, stroke: 0.4pt + dark)
    v(0.6mm)
    grid(
      columns: (42mm, 1fr, 24mm),
      gutter: 3mm,
      align: horizon,
      {
        barcode(ed * 23 + 3, 38mm, 5.5mm)
        v(0.5mm)
        micro([SECURITY_FINGERPRINT \/\/ #d.code])
      },
      {
        grid(columns: (1fr), gutter: 1mm,
          [#micro-orange([\/\/ NOTICE:]) #text(size: 4.8pt, fill: dark)[#T.honest]],
          micro([ACTA PROBLEMATA DISPATCH — OPEN INDUSTRIAL DOCUMENTATION REPO: github.com/omax404/acta-problemata])
        )
      },
      align(right, {
        box(stroke: 0.6pt + dark, inset: 1mm, fill: white, image("qr.svg", width: 14mm))
      })
    )
  },
  footer-descent: 2mm
)

// Global Typography
#set text(font: sans, size: 8.5pt, fill: dark, lang: d.lang, hyphenate: true)
#set par(justify: false, leading: 0.55em, spacing: 0.65em)

// ── TECHNICAL SECTION HEADER (Micro-numbered pill + hairline) ──
#let sec(num-str, label) = {
  v(0.45em)
  grid(columns: (auto, auto, 1fr), gutter: 2mm, align: horizon,
    box(fill: dark, inset: (x: 1.4mm, y: 0.9mm), text(font: mono, fill: white, size: 0.76em, weight: "bold")[#num-str]),
    text(font: sans, weight: "black", size: 0.82em, tracking: 1.2pt)[#upper(label)],
    line(length: 100%, stroke: 0.35pt + dark)
  )
  v(0.18em)
}

// ── CALCULATION WORKINGS GRID (Absorbs remaining vertical space) ──
#let worksheet(ht) = block(width: 100%, height: ht, stroke: 0.45pt + dark, fill: white, clip: true, {
  let pitch = 4.5mm
  let num-lines = calc.floor((ht - 6mm) / pitch)
  for i in range(1, num-lines) {
    place(top + left, dy: 5.5mm + i * pitch, line(length: 100%, stroke: 0.2pt + rgb("#E0DDD5")))
  }
  // Engineering grid cross marks
  for i in range(1, calc.floor(180mm / 25mm)) {
    place(top + left, dx: i * 25mm, dy: 5.5mm, line(angle: 90deg, length: ht - 6mm, stroke: (paint: rgb("#ECE8E0"), dash: "dotted")))
  }
  
  place(top + left, dx: 3mm, dy: 1.6mm,
    text(font: mono, size: 5pt, tracking: 1pt, fill: orange, weight: "bold")[05. ZONE DE CALCUL \/\/ TECHNICAL WORKINGS \/\/ DÉMARCHE ANALYTIQUE])
  place(bottom + right, dx: -3mm, dy: -2mm,
    text(font: mono, size: 6.2pt, fill: dark, weight: "bold")[RÉSULTAT FORMEL : #box(width: 34mm, stroke: (bottom: 0.7pt + dark))[#h(34mm)]])
})

// ── PRIMARY CASE CONTENT ──

// Category Tag Pill
#grid(columns: (auto, 1fr), gutter: 3mm, align: horizon,
  box(fill: dark, inset: (x: 2mm, y: 1.1mm), text(font: mono, fill: orange, size: 5.6pt, weight: "bold")[#upper(d.kicker)]),
  line(length: 100%, stroke: 0.3pt + line-grey)
)

#v(0.3mm)
// Main Title: bold sans, clean industrial sizing
#text(font: sans, weight: "black", size: 14pt, tracking: -0.3pt)[#upper(d.title)]

#v(0.4mm)
// Case Context Note Bar (clean grey card with subtle orange border-left)
#block(width: 100%, stroke: (left: 2.8pt + orange, rest: 0.3pt + line-grey), inset: (x: 2.8mm, y: 1.8mm), fill: light-card)[
  #grid(columns: (auto, 1fr), gutter: 2.5mm, align: horizon,
    box(fill: orange, inset: (x: 1.2mm, y: 0.6mm), text(font: mono, size: 5pt, weight: "bold", fill: dark)[#upper(T.status)]),
    text(size: 6.8pt, fill: soft-dark)[#strong(d.status_label) — #d.status_note]
  )
]

#v(0.2mm)
#micro([SOURCE_ORIGIN: #d.source])

// Main body block with auto-fill bisection and remaining space absorbed by workings
#block(width: 100%, height: 1fr, clip: true, layout(size => {
  let body_content(s) = {
    set text(size: s)
    set par(leading: 0.52em)
    
    if d.mode == "problem" {
      // 01 CONTEXT
      sec("01", T.context)
      text(size: 0.96em)[#d.context]
      
      // 02 GIVEN DATA TABLE
      sec("02", T.data)
      block(width: 100%, stroke: 0.4pt + dark, fill: white,
        grid(
          columns: (1.2fr, 28mm, 1fr, 1.2fr, 28mm, 1fr),
          stroke: 0.25pt + line-grey,
          inset: (x: 1.8mm, y: 1.4mm),
          align: horizon,
          ..d.data.map(r => (
            text(size: 0.88em, weight: "medium")[#r.at(0)],
            box(fill: rgb("#FFF2EC"), inset: (x: 1.4mm, y: 0.8mm), text(font: mono, fill: orange, size: 0.86em, weight: "bold")[#r.at(1)]),
            text(font: mono, size: 0.86em, fill: dark)[#r.at(2)]
          )).flatten()
        )
      )
      
      // 03 TO DETERMINE / QUESTIONS
      sec("03", T.ask)
      for (i, q) in d.questions.enumerate() {
        grid(columns: (7mm, 1fr),
          box(fill: light-card, inset: (x: 1.2mm, y: 0.6mm), text(font: mono, fill: orange, size: 0.86em, weight: "bold")[0#(i + 1)]),
          text(size: 0.94em, weight: "medium")[#q]
        )
        v(0.16em)
      }
      
      // 04 FORMULAS
      sec("04", T.form)
      for f in d.formulas {
        block(
          width: 100%,
          fill: light-card,
          stroke: (left: 2.2pt + orange, rest: 0.25pt + line-grey),
          inset: (x: 2.8mm, y: 1.4mm),
          below: 1mm,
          text(font: mono, size: 0.88em, weight: "bold", fill: dark)[#f]
        )
      }
    } else {
      sec("01", T.problem)
      text(size: 0.96em)[#d.context]
      
      sec("02", T.assump)
      for a in d.s.assumptions {
        grid(columns: (4mm, 1fr), [•], text(size: 0.92em)[#a])
        v(0.12em)
      }
      
      sec("03", T.calc)
      for (i, st) in d.s.steps.enumerate() {
        grid(columns: (7mm, 1fr),
          box(fill: light-card, inset: (x: 1.2mm, y: 0.6mm), text(font: mono, fill: orange, size: 0.86em, weight: "bold")[0#(i + 1)]),
          text(font: mono, size: 0.88em)[#st]
        )
        v(0.14em)
      }
      
      sec("04", T.result)
      block(width: 100%, fill: dark, inset: 2.6mm, text(fill: white)[
        #text(font: mono, size: 0.82em, fill: orange, weight: "bold")[RÉSULTAT DE L'ANALYSE:] \
        #text(size: 1.05em, weight: "bold")[#d.s.result] \
        #v(0.2em)
        #text(size: 0.85em, fill: rgb("#C8C6C0"))[#d.s.recommendation]
      ])
    }
  }

  let (lo, hi) = (7.5pt, 9.4pt)
  let fits(s) = measure(width: size.width, body_content(s)).height <= size.height - 22mm
  let best = lo
  if fits(hi) { best = hi } else if fits(lo) {
    let (a, b) = (lo, hi)
    for _ in range(8) {
      let m = (a + b) / 2
      if fits(m) { a = m } else { b = m }
    }
    best = a
  }
  
  body_content(best)
  
  if d.mode == "problem" {
    let used = measure(width: size.width, body_content(best)).height
    let remaining = size.height - used - 4mm
    if remaining >= 20mm {
      v(2.5mm)
      worksheet(remaining)
    }
  } else if d.mode == "solution" {
    v(1fr)
    block(stroke: (top: 0.4pt + dark), inset: (top: 1.5mm), width: 100%, {
      grid(columns: (1fr, 1fr),
        [#micro-orange([SIGNATURE AUTEUR :]) #text(size: 7pt, weight: "bold")[#d.s.name]],
        align(right, [#micro([CONTACT :]) #text(size: 6.5pt, font: mono)[#d.s.contact]])
      )
    })
  }
}))
