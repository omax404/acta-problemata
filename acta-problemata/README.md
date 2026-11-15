# Acta Problemata

A fully automated daily broadside of engineering failures & applied physics.
AI writes the content; SymPy verifies every number; a fixed Typst design
typesets one pixel-stable A4 page; GitHub Actions delivers it at 06:00 UTC.
**Infrastructure cost: $0.** Public repo ⇒ unlimited Actions minutes.

## Quick start
    pip install -e ".[dev]"
    acta preview            # offline: vault case → build/ + docs/archive PDF
    acta check 8.10e-4      # verify your answer against the latest edition
    acta run --dry-run      # full pipeline, no delivery

## Secret handling
AI keys and mail secrets are never committed to this repository.
Use GitHub Actions secrets (or a local `.env` file that is ignored by git) instead.
Set these values in the repo settings or environment variables before running live AI generation:

- `GEMINI_API_KEY`
- `GROQ_API_KEY`
- `OPENAI_API_KEY`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `MAIL_TO`

## Daily automation
1. Fork, then add Repository Secrets (all optional): `GEMINI_API_KEY`,
   `GROQ_API_KEY`, `OPENAI_API_KEY`, `SMTP_HOST/PORT/USER/PASS`, `MAIL_TO`.
   Gmail: use an app password, host `smtp.gmail.com`, port 465.
2. Settings → Pages → deploy from branch `main`, folder `/docs`.
3. Edit `config.json` (domain, difficulty). Enable Actions. Done.
With zero keys the pipeline publishes verified vault cases — the streak never dies.

## Architecture
AI = content engine only (strict JSON). Diagrams = audited deterministic
renderers (no generated code is ever executed). Math = whitelisted SymPy,
3 s.f., LLM answers always overwritten. Layout = one fixed Typst template;
overflow is fixed by narrative truncation, never by redesign.

## Page design (v2)
- **Robust scaling:** body type is bisection-fitted inside the column box (7.2–11.6 pt); leftover height
  becomes a ruled *Workings* worksheet, so the sheet is always exactly one A4 page and always full.
  Layout is stress-tested (`tests/test_pipeline.py`) with minimal and worst-case content.
- **Ornaments:** double frame, four mirrored corner flourishes, rosette masthead + watermark, diamond
  dividers, drop-cap — all native Typst vector geometry (no packages, no network, no fonts to install).
- `config.json → reveal_answer` (default `false`) prints the answer on the sheet; off, it lives behind the QR.

## Problem sources (see docs/SOURCES.md)
Real problems: drop tender PDFs / forum text / URLs into `inbox/` — one is consumed per day (`inbox/README.md`).
All 19 registered sources, their modes and the enabling procedure: `docs/SOURCES.md`; probe them with `acta sources-check`.

### Original notes
`config.json → source_order` (default `market → ntrs → arxiv`). `market` = curated industrial-maintenance
briefs modelled on CPS/tender families (offline, `data/market_briefs.json`). See `docs/SOURCES.md` for
research leads. Briefs only become cases with an LLM key; without one the verified vault runs.

<!-- ACTA:BEGIN -->
*(the daily workflow replaces this block with the streak badge, archive table and domain chart)*
<!-- ACTA:END -->

MIT License.
