# extras

Design and email assets contributed from the original Acta design pack.

- `latex-style/` - LaTeX style (acta2.sty, sheet/solution/cover) behind the PDF designs in `docs/assets`. Needs XeLaTeX + Inter font; not used by CI.
- `email/` - HTML email builder (`build_html.py` + `template.html`, Resend sender). Not wired into the daily job; `daily.yml.disabled` is the old workflow kept for reference (needs secrets RESEND_API_KEY, MAIL_FROM, SUBSCRIBERS_URL, UNSUB_BASE).
- `assets/logo.svg` - the brand mark.
- `docs/sample-edition.html` - sample archive page.

The primary daily pipeline is the Typst one (`daily_gazette.yml`); `acta-daily.yml` is manual-only so the two never collide on `docs/index.html`.
