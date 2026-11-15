// ACTA PROBLEMATA — fixed broadside design v2. Data arrives via edition.json.
// Design contract: (1) the page is ALWAYS exactly one A4 sheet; (2) body type is
// auto-scaled by bisection to fill the column box — no manual font tuning;
// (3) every ornament is native vector geometry (no packages, no network).
#let d = json("edition.json")

#set document(title: "Acta Problemata № " + str(d.edition_number) + " — " + d.headline,
  author: "Acta Problemata", keywords: (d.domain, d.difficulty, "engineering", "problem"))

// ── palette & metrics ───────────────────────────────────────
#let ink   = rgb("#1b1814")
#let rust  = rgb("#8a3b1f")      // accent: rules, ornaments
#let paper = rgb("#fbf7ee")
#let soft  = rgb("#8a7f6a")

// ── ornament library ────────────────────────────────────────
// One quarter-flourish, drawn from the corner outward. Rotated for the 4 corners.
#let flourish(c: rust) = box(width: 19mm, height: 19mm, {
  // L-bracket
  place(curve(stroke: 1.1pt + c,
    curve.move((0mm, 17mm)), curve.line((0mm, 3mm)),
    curve.cubic((0mm, 1mm), (1mm, 0mm), (3mm, 0mm)), curve.line((17mm, 0mm))))
  // inner scroll
  place(curve(stroke: 0.6pt + c,
    curve.move((3.2mm, 12mm)), curve.line((3.2mm, 5.5mm)),
    curve.cubic((3.2mm, 4.2mm), (4.2mm, 3.2mm), (5.5mm, 3.2mm)), curve.line((12mm, 3.2mm))))
  // curl
  place(curve(stroke: 0.7pt + c,
    curve.move((6.4mm, 6.4mm)),
    curve.cubic((11mm, 6.4mm), (11mm, 11.5mm), (8mm, 11.5mm)),
    curve.cubic((6mm, 11.5mm), (6mm, 9mm), (7.6mm, 9mm))))
  place(dx: 5.4mm, dy: 5.4mm, circle(radius: 0.9mm, fill: c, stroke: none))
  place(dx: 16.2mm, dy: -0.8mm, rotate(45deg, rect(width: 1.7mm, height: 1.7mm, fill: c, stroke: none)))
  place(dx: -0.8mm, dy: 16.2mm, rotate(45deg, rect(width: 1.7mm, height: 1.7mm, fill: c, stroke: none)))
})

// Eight-petal rosette (rotated ellipses) — used in the masthead and as watermark.
#let rosette(r, c: rust, w: 0.5pt, dot: true) = box(width: 2 * r, height: 2 * r, {
  for k in range(8) {
    place(center + horizon, rotate(k * 22.5deg, ellipse(width: 2 * r, height: r * 0.46, stroke: w + c, fill: none)))
  }
  if dot { place(center + horizon, circle(radius: r * 0.2, fill: c, stroke: none)) }
})

// Divider: line — diamond — line, with optional centre text.
#let divider(label: none, c: rust) = {
  let mid = if label == none {
    rotate(45deg, rect(width: 2.2mm, height: 2.2mm, fill: c, stroke: none))
  } else {
    text(size: 6.8pt, tracking: 1.6pt, fill: c, weight: "bold")[#h(2mm)#upper(label)#h(2mm)]
  }
  grid(columns: (1fr, auto, 1fr), gutter: 2mm, align: horizon,
    line(length: 100%, stroke: 0.45pt + c), mid, line(length: 100%, stroke: 0.45pt + c))
}

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

// ── page: double frame + corner flourishes + faint watermark ─
#set page(
  paper: "a4",
  fill: paper,
  margin: (x: 19mm, top: 17mm, bottom: 39mm),
  background: {
    place(top + left, dx: 7mm, dy: 7mm, rect(width: 196mm, height: 283mm, stroke: 1.4pt + ink))
    place(top + left, dx: 8.8mm, dy: 8.8mm, rect(width: 192.4mm, height: 279.4mm, stroke: 0.4pt + rust))
    place(top + left, dx: 9.5mm, dy: 9.5mm, flourish())
    place(top + right, dx: -9.5mm, dy: 9.5mm, scale(x: -100%, flourish()))
    place(bottom + right, dx: -9.5mm, dy: -9.5mm, scale(x: -100%, y: -100%, flourish()))
    place(bottom + left, dx: 9.5mm, dy: -9.5mm, scale(y: -100%, flourish()))
    place(center + horizon, dy: 14mm, rosette(62mm, c: rgb("#8a3b1f14"), w: 0.8pt, dot: false))
  },
  footer: context {
    set text(size: 6.8pt, fill: soft)
    divider()
    v(1.6mm)
    pad(x: 11mm, grid(columns: (1fr, auto), gutter: 4mm, align: horizon,
      [#text(style: "italic", fill: ink)[#d.source_line] \ Acta Problemata press · github.com/#d.repo_slug · set in New Computer Modern & Libertinus],
      grid(columns: (auto, auto), gutter: 2.2mm, align: horizon,
        text(size: 6pt, tracking: 0.8pt, fill: ink, align(right)[SCAN FOR \ SOLUTION]),
        box(stroke: 0.6pt + ink, inset: 0.8mm, fill: white, image("qr.svg", width: 12.5mm)))))
  },
  footer-descent: 6mm,
)
#set text(font: "New Computer Modern", size: 9.6pt, fill: ink, hyphenate: true)
#set par(justify: true, leading: 0.64em, spacing: 0.9em)

// ── masthead ────────────────────────────────────────────────
#align(center)[
  #grid(columns: (auto, auto, auto), gutter: 7mm, align: horizon,
    rosette(7.5mm),
    [#text(font: "Libertinus Serif", size: 30pt, weight: "bold", tracking: 3pt)[ACTA PROBLEMATA]],
    rosette(7.5mm))
  #v(0.8mm)
  #text(size: 7pt, tracking: 1.7pt, fill: soft)[A DAILY BROADSIDE OF ENGINEERING FAILURES & APPLIED PHYSICS]
]
#v(2mm)
#grid(columns: (1fr, auto, 1fr), align: (left, center, right),
  text(size: 8.5pt, weight: "bold")[№ #d.edition_number],
  text(size: 8pt, style: "italic", fill: rust)[Ratiocinatio · Mensura · Veritas],
  text(size: 8.5pt, weight: "bold")[#d.date_display])
#v(1.2mm)
#line(length: 100%, stroke: 1pt + ink)
#v(0.7mm)
#line(length: 100%, stroke: 0.35pt + rust)
#v(3.2mm)

// ── headline (auto-fit to one or two lines) ─────────────────
#align(center)[
  #block(width: 100%, fit-text(s => text(font: "Libertinus Serif", size: s, weight: "bold")[#d.headline],
    lo: 13pt, hi: 19pt, steps: 6))
  #v(0.8mm)
  #text(size: 7.8pt, tracking: 1.3pt, fill: rust)[#smallcaps(lower(d.domain)) ✦ #smallcaps(lower(d.difficulty))]
]
#v(2mm)
#divider(label: "the case")
#v(2.5mm)

// ── worksheet: ruled workings area that absorbs whatever height remains ──
#let worksheet(ht) = block(width: 100%, height: ht, clip: true, stroke: 0.6pt + ink, fill: white, {
  let pitch = 6.2mm
  for i in range(1, calc.floor((ht - 9mm) / pitch)) {
    place(top + left, dy: 8mm + i * pitch, line(length: 100%, stroke: 0.3pt + rgb("#c9bfa8")))
  }
  place(top + left, dx: 3mm, dy: 2.2mm,
    text(size: 6.8pt, tracking: 1.6pt, fill: rust, weight: "bold")[WORKINGS ✦ SPACE FOR YOUR SOLUTION])
  place(bottom + right, dx: -3mm, dy: -2mm,
    text(size: 7.6pt, fill: ink)[Answer: #box(width: 30mm, stroke: (bottom: 0.6pt + ink))[#h(30mm)] #d.formula.unit])
})

// ── body: bisect-scaled content; leftover height becomes the worksheet ──
#block(width: 100%, height: 1fr, layout(size => {
  let make(s) = {
    set text(size: s)
    set par(leading: 0.62em)
    grid(columns: (2.05fr, 1fr), gutter: 6mm,
      [
        #let words = d.narrative.split(" ")
        #let first = words.first()
        #let cap = first.first()
        #let rest = first.slice(cap.len())
        #par(first-line-indent: 0pt)[
          #box(baseline: 0.1em, text(font: "Libertinus Serif", size: s * 2.6, weight: "bold", fill: rust)[#cap])#rest #words.slice(1).join(" ")
        ]
        #v(0.9em)
        #block(width: 100%, stroke: (left: 2.2pt + rust, rest: 0.5pt + ink), inset: 0.8em, fill: rgb("#f3ecdc"))[
          #text(size: 0.82em, tracking: 1.5pt, fill: rust, weight: "bold")[PROBLEMA DIEI]
          #v(0.35em)
          #text(style: "italic")[#d.challenge_question]
        ]
        #v(0.9em)
        #align(center)[
          #block(inset: (x: 0.8em, y: 0.5em), stroke: (top: 0.5pt + ink, bottom: 0.5pt + ink))[
            #text(font: "DejaVu Sans Mono", size: 0.9em)[#d.formula.symbolic]
            #v(0.3em)
            #text(font: "DejaVu Sans Mono", size: 1.02em, fill: rust)[\= #if d.reveal_answer [#d.formula.result_display] else [#box(width: 22mm, stroke: (bottom: 0.6pt + rust))[#h(22mm)]] #h(3pt) #d.formula.unit]
          ]
          #v(0.2em)
          #text(size: 0.72em, style: "italic", fill: soft)[#if d.reveal_answer [computed & verified deterministically by SymPy — 3 s.f.] else [answer verified by SymPy — scan the code to check yours]]
        ]
      ],
      [
        #set par(justify: false)
        #text(size: 0.74em, tracking: 1pt, fill: rust, weight: "bold", hyphenate: false)[BOUNDARY CONDITIONS]
        #v(0.3em)
        #line(length: 100%, stroke: 0.6pt + ink)
        #for (name, val) in d.boundary_conditions [
          #v(0.25em)
          #text(size: 0.84em)[#name] \
          #text(font: "DejaVu Sans Mono", size: 0.8em, fill: rust)[#val]
        ]
        #v(0.4em)
        #line(length: 100%, stroke: 0.6pt + ink)
        #v(0.8em)
        #block(stroke: 0.5pt + ink, inset: 0.4em, fill: white,
          // tall figures (e.g. buckled strut) are capped so they cannot starve the text
          if d.at("diagram_aspect", default: 0.5) > 0.62 { image("diagram.svg", width: 100%, height: 50mm, fit: "contain") }
          else { image("diagram.svg", width: 100%) })
        #align(center, text(size: 0.78em, style: "italic", hyphenate: false)[#d.diagram_caption])
      ])
  }
  let gap = 5mm
  let (lo, hi, steps) = (7.2pt, 11.6pt, 9)
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
