# Problem sources — how the 19 registered sources are used

`data/sources.json` lists every source with a **mode**. Nothing external is enabled by default.

| Mode | Sources | How it feeds the daily problem |
|---|---|---|
| `manual` | 4 Moroccan tender sites, 4 gig marketplaces | You save a CPS/notice PDF into `data/inbox/` or paste its public URL into `data/inbox/urls.txt` |
| `listing` | GrabCAD Challenges, Wazoku, NineSigma, CADCrowd contests, Eng-Tips | Automatic once you enable it (see below) |
| `leads` | Kerix, Telecontact, Kompass | **Not problems** — company directories for juniors' outreach. Company-level only |
| `reference` | GrabCAD Library, TraceParts, McMaster-Carr | For *solving* (datasheets/CAD), not ingested |

Built-in automatic sources: `inbox` → `listing` → `market` (8 curated briefs) → NASA NTRS → arXiv → vault.

## The inbox (recommended, works today)
Drop files in `data/inbox/` (see `data/inbox/README.md`). One item is consumed per day, oldest first; 30 items = 30 real-problem days.
The AI is told to describe **sector and region only** (`name_companies: false`) and to paraphrase, never quote.
The solution page links the original public source so juniors can find the real lead.

## Enabling a `listing` source (3 steps)
1. GitHub → Actions → **Sources check** → Run. It prints, per source, robots.txt verdict and reachability.
2. For an allowed source, open its page, find a regex that matches individual challenge/thread links, then in
   `data/sources.json` set `listing_url`, `link_pattern` and `"enabled": true`.
3. Re-run **Sources check**: the `links` column should show a number > 0.

## Guardrails built into the code (`src/acta/sources.py`)
robots.txt honoured (unreadable/forbidden = blocked) · 1 request per host per 1.5 s · 10 s timeout · 2 MB cap ·
honest User-Agent · on-disk cache · a failing URL is skipped, never fatal · gig/marketplace and directory sites
are deliberately not crawled.

## Legal guardrails (not legal advice: have a Moroccan lawyer / the CNDP confirm before launch)
- **Rewritten, not copied.** `src/acta/originality.py` rejects any live-sourced case that shares 8+ consecutive words with its
  source page; the pipeline then falls back to the bank. Facts and numbers may be reused, sentences may not.
- **Link, don't mirror.** The original public URL is shown on the solution page and in the email; the source document is never republished.
- **No personal data / no company names** in published text (`name_companies: false`); form data is used only to email the requester's PDF.
- **Takedown path.** `docs/legal.html` (FR+EN) + the `takedown` issue template. Treat requests as priority and remove first, discuss after.
- **Non-affiliation notice** on every solution page; no logos.
- **Before listing "who solved it" publicly** (company-facing page): collect explicit, revocable opt-in from each solver first (law 09-08).
- Site terms still apply: where a platform's terms forbid reuse, use `manual` mode (you save the public notice) or ask permission.

## Not verified yet
The sandbox used to build this cannot reach any of these sites, so **no live site has been tested**. The adapters are
covered by offline fixture tests only. Run **Sources check** before trusting any `listing` source.
