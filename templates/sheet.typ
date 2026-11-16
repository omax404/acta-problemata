// ACTA PROBLEMATA — sheet.typ : problem sheet & solution sheet (FR/EN).
// Art direction: Roman identity (engraved serif caps) x industrial brutalism (orange slabs)
// x tactical telemetry (mono serials; every label carries real data) x Swiss grid.
// Contract: ALWAYS one A4 page; body type auto-fits by bisection; no packages, no network.
#let d = json("sheet.json")
#let T = d.t
#let orange = rgb("#E65B18")
#let ink = rgb("#111111")
#let paper = rgb("#DCD7CF")
#let grey = rgb("#6d675d")
#let mono = ("DejaVu Sans Mono",)
#let sans = ("Inter", "DejaVu Sans")
#let rom = ("Libertinus Serif",)

#set document(title: d.title + " — Acta Problemata " + d.code, author: "Acta Problemata")
#set page(paper: "a4", fill: paper, margin: (left: 27mm, right: 15mm, top: 14mm, bottom: 41mm),
  background: {
    // spine: orange rule + ticks + end discs (position ticks every 4mm)
    place(top + left, dx: 14mm, dy: 10mm, line(angle: 90deg, length: 277mm, stroke: 0.7pt + orange))
    place(top + left, dx: 14mm - 3mm, dy: 10mm - 3mm, circle(radius: 3mm, fill: orange, stroke: none))
    place(top + left, dx: 14mm - 3mm, dy: 287mm - 3mm, circle(radius: 3mm, fill: orange, stroke: none))
    for i in range(0, 61) {
      place(top + left, dx: 14mm - 0.5mm, dy: 30mm + i * 4mm, circle(radius: 0.35mm, fill: ink, stroke: none))
    }
    // registration marks
    for (x, y) in ((196mm, 10mm), (196mm, 287mm), (24mm, 287mm)) {
      place(top + left, dx: x - 2mm, dy: y, line(length: 4mm, stroke: 0.3pt + ink))
      place(top + left, dx: x, dy: y - 2mm, line(angle: 90deg, length: 4mm, stroke: 0.3pt + ink))
    }
  },
  footer: {
    set text(font: mono, size: 5.6pt, fill: ink)
    // 1-bit dither fingerprint: density ramps left->right, seeded by the edition code
    block(height: 11mm, width: 100%, {
      for (j, row) in d.finger.enumerate() {
        for (i, on) in row.enumerate() {
          if on == 1 { place(top + left, dx: i * 1.3mm, dy: j * 1.3mm, circle(radius: 0.42mm, fill: ink, stroke: none)) }
        }
      }
      place(top + right, dx: 0mm, block(stroke: 1.2pt + orange, inset: 1.2mm, fill: white, image("qr.svg", width: 19mm)))
    })
    v(1mm)
    grid(columns: (1fr, auto), gutter: 4mm,
      [#upper(T.finger) \/\/ #d.code \ ACTA_PROBLEMATA \/\/ #d.date \/\/ #T.scan],
      align(right, [#T.honest]))
  },
  footer-descent: 4mm,
)
#set text(font: sans, size: 9pt, fill: ink, lang: d.lang, hyphenate: true)
#set par(justify: false, leading: 0.62em, spacing: 0.8em)

#let sec(n, label) = {
  v(0.9em)
  grid(columns: (auto, auto, 1fr), gutter: 2mm, align: horizon,
    text(font: mono, fill: orange, size: 0.9em)[\[#n\]],
    text(weight: "bold", size: 0.85em, tracking: 0.8pt)[#upper(label)],
    line(length: 100%, stroke: 0.4pt + ink))
  v(0.25em)
}

// ── masthead: monumental Roman title + big thin number + dot-grid ──
#block(width: 100%, height: 30mm, {
  for i in range(5) { for j in range(3) { place(top + left, dx: i * 3.4mm, dy: j * 3.4mm, circle(radius: 0.7mm, fill: orange, stroke: none)) } }
  place(top + left, dx: 0mm, dy: 11mm, text(font: sans, weight: "thin", size: 40pt, tracking: -1.5pt)[#d.number])
  place(top + left, dy: 23mm, text(font: mono, size: 6.4pt)[#upper(T.no) #d.number \/\/ #d.code])
  place(top + right, dy: 1mm, align(right, [
    #text(font: rom, weight: "bold", size: 24pt, tracking: 5pt)[ACTA \ PROBLEMATA]
    #v(-1mm)
    #text(font: mono, size: 5.8pt, tracking: 1pt, fill: grey)[#upper(d.mode_label) \/\/ #d.date]
  ]))
})
#v(3mm)

// ── title ──
#text(font: mono, fill: orange, size: 6.8pt, tracking: 0.6pt)[#upper(d.kicker)]
#v(1mm)
#text(font: sans, weight: "light", size: 21pt, tracking: 0pt)[#upper(d.title)]
#v(2mm)
// status slab
#block(width: 100%, fill: orange, inset: (x: 3mm, y: 2.2mm))[
  #text(font: mono, weight: "bold", size: 7.2pt)[#upper(T.status) : #d.status_label] #h(2mm) #text(size: 8pt)[#d.status_note]
]
#v(1mm)
#text(font: mono, size: 6pt)[#upper(T.source) : #d.source]

// ── body: auto-fit ──
#block(width: 100%, height: 1fr, clip: true, layout(size => {
  let body(s) = {
    set text(size: s)
    set par(leading: 0.6em)
    if d.mode == "problem" {
      sec("01", T.context)
      d.context
      sec("02", T.data)
      block(width: 100%, stroke: (top: 0.5pt + ink, bottom: 0.5pt + ink), inset: (y: 1.4mm),
        grid(columns: (1fr, auto, 1.1fr, 1fr, auto, 1.1fr), column-gutter: 3mm, row-gutter: 1.1mm,
          ..d.data.map(r => (text(size: 0.92em)[#r.at(0)], text(font: mono, fill: orange, size: 0.88em)[#r.at(1)], text(font: mono, size: 0.88em)[#r.at(2)])).flatten()))
      sec("03", T.ask)
      for (i, q) in d.questions.enumerate() {
        grid(columns: (7mm, 1fr), text(font: mono, fill: orange)[#(i + 1).], q)
        v(0.25em)
      }
      sec("04", T.form)
      for f in d.formulas {
        block(width: 100%, fill: rgb("#e9e5dd"), stroke: (left: 2.4pt + orange), inset: (x: 2.6mm, y: 1.6mm), below: 1.2mm,
          text(font: mono, size: 0.92em)[#f])
      }
    } else {
      sec("01", T.problem)
      d.context
      sec("02", T.assump)
      for a in d.s.assumptions { [— #a \ ] }
      sec("03", T.calc)
      for (i, st) in d.s.steps.enumerate() {
        grid(columns: (7mm, 1fr), text(font: mono, fill: orange)[#(i + 1).], text(font: mono, size: 0.92em)[#st])
        v(0.2em)
      }
      sec("04", T.result)
      block(width: 100%, fill: ink, inset: 3mm, text(fill: paper)[#strong(d.s.result) \ #d.s.recommendation])
    }
  }
  let (lo, hi) = (7pt, 10.4pt)
  let fits(s) = measure(width: size.width, body(s)).height <= size.height - 14mm
  let best = lo
  if fits(hi) { best = hi } else if fits(lo) {
    let (a, b) = (lo, hi)
    for _ in range(9) { let m = (a + b) / 2; if fits(m) { a = m } else { b = m } }
    best = a
  }
  assert(fits(best) or best == lo and measure(width: size.width, body(lo)).height <= size.height - 6mm, message: "sheet content overflows the page")
  body(best)
  if d.mode == "solution" {
    v(1fr)
    text(font: mono, fill: orange, size: 6.4pt)[#upper(T.by)]; h(2mm); strong(d.s.name); linebreak()
    text(font: mono, size: 6.2pt)[#upper(T.contact) : #d.s.contact]
  }
}))