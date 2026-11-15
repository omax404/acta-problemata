# Acta Problemata

A daily engineering problem sheet and archive for junior engineers. The current vault contains realistic practice scenarios, so generated sheets are clearly labelled **Realistic problem** and never claim that a named company has a particular issue.

## Run locally

```bash
cd acta-problemata
python build_daily.py
```

This uses only Python's standard library. It writes the day's HTML sheet to `docs/archive/` and refreshes the archive at `docs/index.html`. Set `"language": "fr"` or `"language": "en"` in `config.json` to choose the sheet language (French is the default). To preview the page, open `docs/index.html` in a browser.

## Daily GitHub Pages publishing

The `Acta daily archive` workflow runs at 06:00 UTC and can also be started from **Actions → Acta daily archive → Run workflow**. It builds the page, commits the generated archive, and deploys `acta-problemata/docs` to GitHub Pages. Enable Pages with **Build and deployment → GitHub Actions** in repository settings. No AI or email secrets are required for this vault-based build.

## Provenance and safe AI configuration

- Public, verifiable source material may be added with its source URL and labelled as a documented public case.
- Vault scenarios are explicitly labelled realistic; they are not attributed to real companies.
- AI API keys must only be supplied as environment variables or GitHub Actions secrets. Never commit keys to config, scripts, or `.env` files.
- An exposed Gemini key should be revoked and replaced in Google AI Studio. Add the replacement as a repository Actions secret if you later enable AI.

The existing `acta` CLI and PDF pipeline remain available; this static archive is an independent, no-secret daily publishing path.
