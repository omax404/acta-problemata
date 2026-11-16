# Inbox — feed real problems to the daily broadside

The daily job reads this folder **first** (`source_order` in `config.json`) and consumes one item per day,
oldest first. Each item is used once (the ledger remembers it), so 30 items ≈ 30 days of real problems.

Drop in any of:
- `*.pdf` — a tender CPS / DCE, a failure report, a supplier incident sheet (first 12 pages are read)
- `*.txt` / `*.md` — pasted text from a forum thread, a challenge page, a maintenance report
- `urls.txt` — one public URL per line, optional `| Domain`; fetched politely by the daily job
  (robots.txt honoured, 1 request/host/1.5 s). `#` starts a comment.

Name a file `Fluids__water-header.txt` to force the domain (`Mechanical`, `Aerospace`, `Electrical`,
`Chemical`, `Civil`, `Thermal`, `Materials`, `Fluids`); otherwise `config.json → target_domain` is used.

Rules of thumb
- Public documents only. Remove or ignore client names — by default the AI is told to describe sector and
  region, never to name a company, person or tender number (`name_companies: false`).
- Never paste credentials, private emails or confidential documents. This folder is committed to Git.
- Forum/gig text is paraphrased into an original scenario, never quoted.

## By email (optional)
Create a dedicated mailbox (e.g. a free Gmail with an **app password**) and add these repo secrets:
`IMAP_HOST` (imap.gmail.com), `IMAP_USER`, `IMAP_PASS`, `INBOX_ALLOWED_SENDERS` (comma-separated addresses
you trust). Then forward a tender, PDF or link to that mailbox. Subject `[Fluids] water header` sets the domain.
Short mails containing links go to `urls.txt`; long text and PDF/TXT/MD attachments (≤ 2 MB) become inbox items.
Mail from anyone else is ignored. The daily job runs `acta mail-pull` before publishing.
