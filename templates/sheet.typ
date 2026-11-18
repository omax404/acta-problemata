// ACTA PROBLEMATA — sheet.typ : problem sheet & solution sheet (FR/EN).
// Art direction: Roman identity (engraved serif caps) x industrial brutalism (orange slabs)
// x tactical telemetry (mono serials; every label carries real data) x Swiss grid.
// Contract: ALWAYS one A4 page; body type auto-fits by bisection; no packages, no network.
#let d = json("sheet.json")
#let T = d.t
#let orange = rgb("#FF4600")
#let ink = rgb("#121212")
#let paper = rgb("#E6E6E3")
#let grey = rgb("#6b6b68")
#let mono = ("DejaVu Sans Mono",)
#let sans = ("Inter", "DejaVu Sans")
#let rom = ("Libertinus Serif",)

#set document(title: d.title + " - Acta Problemata " + d.code, author: "Acta Problemata")
#let ed = if type(d.number) == int { d.number } else { 7 }
#let num = { let s = str(d.number); "0" * calc.max(0, 3 - s.len()) + s }
#let gsrc = rgb("#121212")
#let barcode(seed, w, h, fg: ink) = box(width: w, height: h, {
  let s = seed
  let x = 0mm
  while x < w - 1mm {
    s = calc.rem(s * 1103515245 + 12345, 2147483648)
    let bw = (1 + calc.rem(int(s / 65536), 3)) * 0.3mm
    place(top + left, dx: x, rect(width: bw, height: h, fill: fg, stroke: none))
    x += bw + (1 + calc.rem(int(s / 4096), 2)) * 0.3mm
  }
})
#set page(paper: "a4", fill: paper, margin: (left: 14mm, right: 14mm, top: 64mm, bottom: 41mm),
  background: {
    // paper grain (deterministic)
    let s = 11 + calc.rem(ed, 997)
    for k in range(420) {
      s = calc.rem(s * 1103515245 + 12345, 2147483648)
      let px = s / 2147483648 * 210
      s = calc.rem(s * 1103515245 + 12345, 2147483648)
      let py = s / 2147483648 * 297
      place(top + left, dx: px * 1mm, dy: py * 1mm, circle(radius: 0.2mm, fill: rgb("#cdcdc9"), stroke: none))
    }
    // tick ruler with orange centre mark + header labels
    for i in range(0, 183) {
      let h = if calc.rem(i, 10) == 0 { 2.4mm } else if calc.rem(i, 5) == 0 { 1.8mm } else { 1mm }
      place(top + left, dx: (14 + i) * 1mm, dy: 9mm, line(angle: 90deg, length: h, stroke: 0.25pt + ink))
    }
    place(top + left, dx: 105mm, dy: 8mm, line(angle: 90deg, length: 4mm, stroke: 0.6pt + orange))
    place(top + left, dx: 14mm, dy: 4mm, text(font: mono, size: 5.6pt)[ACTA_PROBLEMATA \/\/ #d.date])
    place(top + right, dx: -14mm, dy: 4mm, text(font: mono, size: 5.6pt)[#upper(d.mode_label) \/\/ #d.code])
    // crop marks
    for (x, y, sx, sy) in ((8mm, 8mm, 1, 1), (202mm, 8mm, -1, 1), (8mm, 289mm, 1, -1), (202mm, 289mm, -1, -1)) {
      place(top + left, dx: x, dy: y, line(length: 4mm * sx, stroke: 0.4pt + ink))
      place(top + left, dx: x, dy: y, line(angle: 90deg, length: 4mm * sy, stroke: 0.4pt + ink))
    }
    // masthead: orange slab with giant numeral
    place(top + left, dx: 14mm, dy: 16mm, rect(width: 78mm, height: 42mm, fill: orange, stroke: none))
    place(top + left, dx: 16mm, dy: 17mm, text(font: sans, weight: "bold", size: 84pt, tracking: -3pt, fill: ink)[#num])
    place(top + left, dx: 17mm, dy: 53mm, text(font: mono, size: 5.2pt, fill: ink)[#upper(T.no) #num \/\/ #d.code])
    // graphite spec card
    place(top + left, dx: 96mm, dy: 16mm, rect(width: 74mm, height: 42mm, fill: gsrc, stroke: none))
    place(top + left, dx: 99mm, dy: 18mm, text(font: mono, size: 4.8pt, fill: rgb("#8a8a8a"))[#upper(d.mode_label)])
    place(top + left, dx: 99mm, dy: 20.6mm, text(font: sans, weight: "bold", size: 13pt, fill: rgb("#d4d4d1"))[ACTA PROBLEMATA])
    place(top + left, dx: 162.5mm, dy: 18.5mm, rect(width: 2.6mm, height: 2.6mm, fill: orange, stroke: none))
    place(top + left, dx: 98mm, dy: 29mm, grid(columns: (17mm, 53mm), rows: 3.5mm, stroke: 0.3pt + rgb("#5a5a5a"),
      inset: (x: 1mm), align: horizon,
      ..((("CODE", d.code), ("DATE", d.date), ("MODE", upper(d.mode_label)), ("EDITION", num)).map(r => (
        text(font: mono, size: 4.4pt, fill: rgb("#7d7d7d"))[#r.at(0)],
        text(font: mono, size: 4.4pt, fill: rgb("#c9c9c6"))[#r.at(1)])).flatten())))
    place(top + left, dx: 98mm, dy: 46mm, barcode(ed * 13 + 5, 30mm, 7mm, fg: rgb("#c9c9c6")))
    place(top + left, dx: 131mm, dy: 46.5mm, text(font: mono, size: 4.2pt, fill: rgb("#7d7d7d"))[\[SHEET_ID\] \ #d.code \/\/ #upper(d.lang)])
    // logo
    place(top + left, dx: 174mm, dy: 16mm, image("logo.svg", height: 26mm))
    
  },
  footer: {
    set text(font: mono, size: 5.6pt, fill: ink)
    block(height: 11mm, width: 100%, {
      for (j, row) in d.finger.enumerate() {
        for (i, on) in row.enumerate() {
          if on == 1 { place(top + left, dx: i * 1.3mm, dy: j * 1.3mm, circle(radius: 0.42mm, fill: ink, stroke: none)) }
        }
      }
      place(top + left, dx: 90mm, dy: 0mm, barcode(ed * 7 + 1, 40mm, 8mm))
      place(top + left, dx: 90mm, dy: 8.6mm, text(size: 4.4pt, fill: grey)[#d.code])
      place(top + right, dx: 0mm, block(stroke: 1.2pt + orange, inset: 1.2mm, fill: white, image("qr.svg", width: 19mm)))
    })
    v(1mm)
    grid(columns: (1fr, auto), gutter: 4mm,
      [\[#upper(T.finger)\] \/\/ #d.code \ ACTA_PROBLEMATA \/\/ #d.date \/\/ #upper(T.scan)],
      align(right, [\[#T.honest\]]))
  },
  footer-descent: 4mm,
)
#set text(font: sans, size: 9pt, fill: ink, lang: d.lang, hyphenate: true)
#set par(justify: false, leading: 0.62em, spacing: 0.8em)

#let sec(n, label) = {
  v(0.9em)
  grid(columns: (auto, auto, 1fr), gutter: 2mm, align: horizon,
    box(fill: ink, inset: (x: 1.3mm, y: 0.9mm), text(font: mono, fill: paper, size: 0.82em, weight: "bold")[#n]),
    text(weight: "bold", size: 0.9em, tracking: 0.8pt)[#upper(label)],
    line(length: 100%, stroke: 0.4pt + ink))
  v(0.25em)
}

// title
#text(font: mono, fill: orange, size: 6.8pt, tracking: 0.6pt)[\[#upper(d.kicker)\]]
#v(1mm)
#text(font: sans, weight: "bold", size: 21pt, tracking: -0.3pt)[#upper(d.title)]
#v(2mm)
#block(width: 100%, fill: orange, inset: (x: 3mm, y: 2.2mm))[
  #text(font: mono, weight: "bold", size: 7.2pt)[#upper(T.status) : #d.status_label] #h(2mm) #text(size: 8pt)[#d.status_note]
]
#v(1mm)
#text(font: mono, size: 6pt)[#upper(T.source) : #d.source]

#block(width: 100%, height: 1fr, clip: true, layout(size => {
  let body(s) = {
    set text(size: s)
    set par(leading: 0.6em)
    if d.mode == "problem" {
      sec("01", T.context)
      d.context
      sec("02", T.data)
      block(width: 100%, stroke: 0.5pt + ink,
        grid(columns: (1fr, auto, 1.1fr, 1fr, auto, 1.1fr), stroke: 0.3pt + ink, inset: (x: 1.5mm, y: 1.2mm),
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