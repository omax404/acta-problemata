// ACTA PROBLEMATA — broadside design v3 "telemetry": signal orange / industrial bone / deep graphite.
// Data arrives via edition.json. Design contract: (1) the page is ALWAYS exactly one A4 sheet;
// (2) body type is auto-scaled by bisection to fill its box; (3) every ornament is native vector
// geometry, and every label/serial on the page carries real data (edition, date, lot, micrograph stats).
// Fonts (OFL) are bundled in ./fonts: Anton (display), Space Mono (telemetry), Barlow Semi Condensed (text).
#let d = json("edition.json")

#set document(title: "Acta Problemata № " + str(d.edition_number) + " — " + d.headline,
  author: "Acta Problemata", keywords: (d.domain, d.difficulty, "engineering", "problem"))

#let orange   = rgb("#ff4d00")
#let bone     = rgb("#ebebeb")
#let graphite = rgb("#121212")
#let mid      = rgb("#8d8d8d")
#let grid-c   = rgb("#cfcfcf")
#let disp = ("Anton", "DejaVu Sans")
#let mono = ("Space Mono", "DejaVu Sans Mono")
#let body = ("Barlow", "DejaVu Sans")

#let pad3(n) = { let s = str(n); "0" * calc.max(0, 3 - s.len()) + s }
#let ed3 = pad3(d.edition_number)
#let date8 = d.date.replace("-", "")
#let lot = "AP-" + date8 + "-" + ed3

// ── robust scaling: largest text size (lo..hi) whose content fits the box ──
#let fit-text(make, lo: 7.2pt, hi: 11.4pt, steps: 9) = layout(size => {
  let fits(s) = measure(width: size.width, make(s)).height <= size.height
  if not fits(lo) { make(lo) }
  else if fits(hi) { make(hi) }
  else {
    let a = lo
    let b = hi
    for _ in range(steps) {
      let m = (a + b) / 2
      if fits(m) { a = m } else { b = m }
    }
    make(a)
  }
})

// ── ornaments: registration corners, barcode, tag ───────────
#let corners(c: graphite, len: 2.6mm, w: 0.9pt) = {
  place(top + left, line(length: len, stroke: w + c))
  place(top + left, line(angle: 90deg, length: len, stroke: w + c))
  place(top + right, dx: -len, line(length: len, stroke: w + c))
  place(top + right, line(angle: 90deg, length: len, stroke: w + c))
  place(bottom + left, line(length: len, stroke: w + c))
  place(bottom + left, dy: -len, line(angle: 90deg, length: len, stroke: w + c))
  place(bottom + right, dx: -len, line(length: len, stroke: w + c))
  place(bottom + right, dy: -len, line(angle: 90deg, length: len, stroke: w + c))
}

// Bars are the bit pattern of the serial itself, so the barcode encodes the real lot code.
#let barcode(seed, h: 9mm, mod: 0.32mm, c: graphite) = {
  let bars = ()
  let i = 0
  for ch in seed.clusters() {
    let n = calc.rem(str.to-unicode(ch) * 167 + i * 91, 251)
    for k in range(8) { bars.push(calc.rem(calc.quo(n, calc.pow(2, 7 - k)), 2) == 1) }
    bars.push(false)
    i += 1
  }
  box(height: h, stack(dir: ltr, ..bars.map(b => rect(width: mod, height: h, fill: if b { c } else { none }, stroke: none))))
}

#let tag(t, c: graphite, size: 6pt) = text(font: mono, size: size, weight: "bold", fill: c, tracking: 0.4pt)[#t]

// ── metric rulers in the page margins: true 1 mm ticks, 5 mm / 10 mm marks, cm numerals (A4 = 210 x 297 mm) ──
#let ruler-bg = {
  let tk = 0.22pt + graphite
  let tlen(i) = if calc.rem(i, 10) == 0 { 4mm } else if calc.rem(i, 5) == 0 { 2.6mm } else { 1.5mm }
  let num(t) = text(font: mono, size: 3.6pt, fill: graphite, weight: "bold")[#t]
  for i in range(0, 211) {
    place(top + left, dx: i * 1mm, line(angle: 90deg, length: tlen(i), stroke: tk))
    place(bottom + left, dx: i * 1mm, dy: -tlen(i), line(angle: 90deg, length: tlen(i), stroke: tk))
    if calc.rem(i, 10) == 0 and i > 0 and i < 210 and i != 100 and i != 110 {
      place(top + left, dx: i * 1mm + 0.5mm, dy: 4.2mm, num(str(calc.quo(i, 10))))
      place(bottom + left, dx: i * 1mm + 0.5mm, dy: -7.4mm, num(str(calc.quo(i, 10))))
    }
  }
  for j in range(0, 298) {
    place(top + left, dy: j * 1mm, line(length: tlen(j), stroke: tk))
    place(top + right, dy: j * 1mm, dx: -tlen(j), line(length: tlen(j), stroke: tk))
    if calc.rem(j, 10) == 0 and j > 0 and j < 297 and j != 150 {
      place(top + left, dx: 4.4mm, dy: j * 1mm - 0.5mm, rotate(-90deg, origin: top + left, num(str(calc.quo(j, 10)))))
      place(top + right, dx: -7.4mm, dy: j * 1mm - 0.5mm, rotate(-90deg, origin: top + left, num(str(calc.quo(j, 10)))))
    }
  }
  place(top + center, dy: 4.6mm, box(fill: bone, inset: (x: 1mm), text(font: mono, size: 4pt, weight: "bold", fill: orange)[#sym.arrow.l  210 MM  #sym.arrow.r]))
  place(left + horizon, dx: -2.4mm, rotate(-90deg, box(fill: bone, inset: (x: 1mm), text(font: mono, size: 4pt, weight: "bold", fill: orange)[#sym.arrow.l  297 MM  #sym.arrow.r])))
  place(bottom + right, dx: -11mm, dy: -4.6mm, box(fill: bone, inset: (x: 1mm), text(font: mono, size: 3.8pt, weight: "bold", fill: graphite)[A4  210 #sym.times 297 MM  \/\/  SCALE 1:1  \/\/  TICK 1 MM]))
}
#set page(paper: "a4", fill: bone, margin: 10mm, background: ruler-bg)
#set text(font: body, stretch: 87.5%, size: 9.4pt, fill: graphite, hyphenate: true, lang: "en")
#set par(justify: false, leading: 0.58em, spacing: 0.8em)

// ── top strip: boarding-pass style header ───────────────────
#block(width: 100%, height: 7mm, fill: graphite, inset: (x: 3mm), {
  set text(fill: bone)
  grid(columns: (auto, 1fr, auto), gutter: 3mm, align: horizon + left,
    tag("ACTA PROBLEMATA  //  DAILY BROADSIDE", c: bone, size: 6.2pt),
    line(length: 100%, stroke: 0.6pt + orange),
    tag("DOSSIER ID: " + lot, c: bone, size: 6.2pt))
})

// ── hero: signal-orange block, giant edition number, micrograph plate ──
#let mg = d.at("micrograph", default: none)
#block(width: 100%, height: 80mm, fill: orange, clip: true, {
  grid(columns: if mg != none { (1fr, 58mm) } else { (1fr,) }, gutter: 0pt, rows: (1fr, 9mm),
    block(width: 100%, height: 100%, inset: (x: 6mm, top: 5mm, bottom: 0mm), {
      place(top + left, {
        tag("[" + upper(d.domain) + "]  ::  " + upper(d.difficulty) + "  ::  PROBLEMA DIEI", size: 6.4pt)
        v(2.5mm)
        block(width: 100%, height: 22mm, fit-text(
          s => text(font: disp, size: s, fill: graphite, hyphenate: false, top-edge: "cap-height", bottom-edge: "baseline")[#upper(d.headline)],
          lo: 13pt, hi: 28pt, steps: 7))
      })
      place(bottom + left, dy: -1.5mm, text(font: disp, size: 100pt, tracking: -2.5pt, fill: graphite,
        top-edge: "cap-height", bottom-edge: "baseline")[#ed3])
    }),
    ..if mg != none { (block(width: 100%, height: 100%, inset: (right: 6mm, top: 5mm, bottom: 0mm), {
      block(width: 100%, height: 34mm, {
        image("micrograph.png", width: 100%, height: 100%, fit: "cover")
        corners(c: graphite, len: 3mm, w: 1.1pt)
      })
      v(1.6mm)
      let rows = (("MATERIAL", mg.material), ("ETCHANT", mg.etchant), ("MAGNIFICATION", str(mg.mag) + "x"),
        ("GRAINS", str(mg.grains)), ("MEAN D", str(mg.mean_d_um) + " um"), ("ASTM E112 G", str(mg.astm_g)),
        ("SCALE BAR", str(mg.bar_um) + " um"))
      set text(font: mono, size: 5.2pt, fill: graphite)
      grid(columns: (auto, 1fr), column-gutter: 2mm, row-gutter: 0.6mm, stroke: none,
        ..rows.map(r => (text(fill: rgb("#3a1100"))[#r.at(0)], align(right, text(weight: "bold")[#r.at(1)]))).flatten())
      v(0.8mm)
      text(font: mono, size: 4.6pt, fill: rgb("#3a1100"))[PLATE #mg.seed \/\/ SYNTHETIC MICROSTRUCTURE]
    }),) } else { () },
    grid.cell(colspan: if mg != none { 2 } else { 1 }, block(width: 100%, height: 100%, stroke: (top: 1pt + graphite),
      inset: (x: 6mm), grid(columns: (1fr, auto), align: horizon,
        text(font: disp, size: 14pt, fill: graphite, tracking: 0.4pt)[DATA_STREAM_V1.0],
        text(font: disp, size: 14pt, fill: graphite, tracking: 0.4pt)[#upper(d.date_display)]))))
})

// ── info bar ─────────────────────────────────────────────────
#block(width: 100%, fill: graphite, inset: (x: 4mm, y: 2.4mm), {
  set text(fill: bone)
  grid(columns: (1fr, 1fr, 1fr, 1fr), column-gutter: 3mm,
    ..(("DOMAIN", upper(d.domain)), ("DIFFICULTY", upper(d.difficulty)), ("EDITION", "N. " + ed3), ("LOT", lot)).map(p => {
      text(font: mono, size: 4.8pt, fill: mid, tracking: 0.6pt)[#p.at(0)]
      linebreak()
      text(font: mono, size: 7pt, weight: "bold", fill: if p.at(0) == "EDITION" { orange } else { bone })[#p.at(1)]
    }))
})
#v(3mm)

// ── worksheet: graph paper that absorbs whatever height remains ──
#let worksheet(ht) = block(width: 100%, height: ht, clip: true, stroke: 0.8pt + graphite, fill: rgb("#f4f4f4"), {
  let pitch = 5mm
  for i in range(1, calc.floor((ht - 9mm) / pitch) + 1) {
    place(top + left, dy: 7mm + i * pitch, line(length: 100%, stroke: 0.25pt + grid-c))
  }
  for j in range(1, 40) { place(top + left, dx: j * pitch, line(angle: 90deg, length: 100%, stroke: 0.25pt + grid-c)) }
  place(top + left, dx: 0mm, dy: 0mm, block(width: 100%, height: 7mm, fill: graphite, inset: (x: 3mm), align(horizon,
    tag("WORKINGS  //  SPACE FOR YOUR SOLUTION", c: bone, size: 6pt))))
  place(top + right, dx: -3mm, dy: 1.7mm, tag("LOT " + lot, c: orange, size: 5.6pt))
  place(bottom + right, dx: -3mm, dy: -2mm,
    text(font: mono, size: 6.6pt, fill: graphite, weight: "bold")[ANSWER: #box(width: 30mm, stroke: (bottom: 0.8pt + graphite))[#h(30mm)] #d.formula.unit])
  corners(c: orange, len: 3mm, w: 1.1pt)
})

// ── body: bisect-scaled content; leftover height becomes the worksheet ──
#block(width: 100%, height: 1fr, layout(size => {
  let make(s) = {
    set text(size: s)
    set par(leading: 0.58em)
    grid(columns: (2.05fr, 1fr), gutter: 5mm,
      [
        #grid(columns: (auto, 1fr), gutter: 2mm, align: horizon,
          rect(width: 2.4mm, height: 2.4mm, fill: orange, stroke: none), tag("CASE_FILE  //  NARRATIVE", size: 5.8pt))
        #v(1.6mm)
        #d.narrative
        #v(0.8em)
        #block(width: 100%, fill: graphite, inset: 0.75em, stroke: (left: 3pt + orange))[
          #text(font: mono, size: 0.62em, tracking: 0.8pt, fill: orange, weight: "bold")[PROBLEMA DIEI]
          #v(0.3em)
          #text(fill: bone, weight: 600)[#d.challenge_question]
        ]
        #v(0.8em)
        #block(width: 100%, stroke: 0.8pt + graphite, fill: white, inset: (x: 0.8em, y: 0.6em))[
          #align(center)[
            #text(font: mono, size: 0.82em, weight: "bold")[#d.formula.symbolic]
            #v(0.3em)
            #text(font: mono, size: 0.95em, weight: "bold", fill: orange)[\= #if d.reveal_answer [#d.formula.result_display] else [#box(width: 22mm, stroke: (bottom: 0.8pt + orange))[#h(22mm)]] #h(3pt) #d.formula.unit]
            #v(0.2em)
            #text(font: mono, size: 0.52em, fill: mid)[#if d.reveal_answer [COMPUTED AND VERIFIED DETERMINISTICALLY BY SYMPY - 3 S.F.] else [ANSWER VERIFIED BY SYMPY - SCAN THE CODE TO CHECK YOURS]]
          ]
        ]
      ],
      [
        #block(width: 100%, stroke: 0.8pt + graphite, fill: white, {
          block(width: 100%, fill: graphite, inset: (x: 0.5em, y: 0.35em), tag("BOUNDARY_CONDITIONS", c: bone, size: 5.8pt))
          pad(x: 0.5em, y: 0.15em, for (i, (name, val)) in d.boundary_conditions.pairs().enumerate() {
            if i > 0 { line(length: 100%, stroke: 0.3pt + grid-c) }
            block(width: 100%, inset: (y: 0.28em), {
              text(size: 0.82em)[#name]
              linebreak()
              text(font: mono, size: 0.7em, weight: "bold", fill: graphite)[#val]
            })
          })
        })
        #v(0.7em)
        #block(width: 100%, fill: white, stroke: 0.5pt + graphite, inset: 0.45em, {
          // tall figures (e.g. buckled strut) are capped so they cannot starve the text
          if d.at("diagram_aspect", default: 0.5) > 0.62 { image("diagram.svg", width: 100%, height: 38mm, fit: "contain") }
          else { image("diagram.svg", width: 100%) }
          corners(c: orange, len: 2.2mm, w: 0.9pt)
        })
        #v(0.25em)
        #text(font: mono, size: 0.56em, fill: graphite, hyphenate: false)[#upper(d.diagram_caption)]
      ])
  }
  let gap = 4mm
  let (lo, hi, steps) = (7.2pt, 11.2pt, 9)
  let height-at(s) = measure(width: size.width, make(s)).height
  // Prefer leaving >= 30% of the box for the worksheet; otherwise use the whole box.
  let limit = if height-at(lo) <= size.height * 0.70 { size.height * 0.70 } else { size.height }
  let best = lo
  if height-at(hi) <= limit { best = hi }
  else if height-at(lo) <= limit {
    let (a, b) = (lo, hi)
    for _ in range(steps) {
      let m = (a + b) / 2
      if height-at(m) <= limit { a = m } else { b = m }
    }
    best = a
  }
  let used = height-at(best)
  make(best)
  let left = size.height - used - gap
  if left >= 26mm { v(gap); worksheet(left) }
}))

// ── footer bar ───────────────────────────────────────────────
#v(3mm)
#block(width: 100%, height: 20mm, fill: graphite, inset: (x: 4mm, y: 3mm), {
  set text(fill: bone)
  grid(columns: (auto, 1fr, auto), gutter: 5mm, align: horizon,
    [#barcode(lot, h: 9.5mm, c: bone)
     #v(0.8mm)
     #tag(lot + "  //  " + upper(d.domain), c: mid, size: 4.8pt)],
    [#text(font: body, stretch: 87.5%, size: 8pt, style: "italic", fill: bone)[#d.source_line]
     #v(0.6mm)
     #tag("ACTA PROBLEMATA PRESS  //  GITHUB.COM/" + upper(d.repo_slug), c: mid, size: 4.8pt)
     #linebreak()
     #tag("SET IN ANTON / SPACE MONO / BARLOW SEMI CONDENSED", c: mid, size: 4.4pt)],
    grid(columns: (auto, auto), gutter: 2.5mm, align: horizon,
      text(font: mono, size: 5.6pt, weight: "bold", fill: orange, align(right)[SCAN FOR \ SOLUTION]),
      box(fill: bone, inset: 0.9mm, image("qr.svg", width: 12.5mm))))
})
