"""Email -> inbox/: forward a tender, PDF or link to a dedicated mailbox and the daily job picks it up.

Security model (fail closed):
  * only senders listed in INBOX_ALLOWED_SENDERS are read; an empty list accepts nothing;
  * only .pdf/.txt/.md attachments, <= 2 MB, names sanitised (no paths);
  * mails are marked read only after their content was saved; rejected mails stay untouched;
  * everything saved is later treated as untrusted text: the LLM output is schema-validated
    and the math is recomputed deterministically, so a hostile mail cannot change the answer logic.
Configure with env/secrets: IMAP_HOST, IMAP_USER, IMAP_PASS (use an app password), INBOX_ALLOWED_SENDERS.
Subject "[Fluids] ..." sets the domain. Never raises: a mailbox problem must not stop publication.
"""
from __future__ import annotations

import email
import imaplib
import logging
import os
import re
from datetime import UTC, datetime
from email import policy
from email.utils import parseaddr
from pathlib import Path

from .sources import MIN_TEXT

log = logging.getLogger("acta.mailbox")
MAX_ATTACH = 2_000_000
MAX_MAILS = 25
OK_EXT = (".pdf", ".txt", ".md")
DOMAINS = ("Mechanical", "Aerospace", "Electrical", "Chemical", "Civil", "Thermal", "Materials", "Fluids")


def _safe(name: str) -> str:
    base = Path(name.replace("\\", "/")).name
    return re.sub(r"[^A-Za-z0-9._-]+", "-", base).strip(".-")[:60] or "file"


def _domain(subject: str) -> str:
    m = re.match(r"\s*\[(\w+)\]", subject or "")
    return m.group(1).capitalize() if m and m.group(1).capitalize() in DOMAINS else ""


def _store(msg, inbox: Path, stamp: str, idx: int) -> int:
    subject = str(msg.get("Subject", ""))
    prefix = f"{_domain(subject)}__" if _domain(subject) else ""
    saved = 0
    body = msg.get_body(preferencelist=("plain",))
    text = body.get_content().strip() if body else ""
    if len(text) >= MIN_TEXT:
        (inbox / f"{prefix}mail-{stamp}-{idx}.txt").write_text(subject + "\n\n" + text, encoding="utf-8")
        saved += 1
    else:
        urls = re.findall(r"https?://[^\s<>\"']+", subject + "\n" + text)
        if urls:
            with (inbox / "urls.txt").open("a", encoding="utf-8") as fh:
                for u in urls:
                    fh.write(f"{u} | {_domain(subject)}\n" if _domain(subject) else f"{u}\n")
            saved += 1
    for part in msg.iter_attachments():
        name = _safe(part.get_filename() or "")
        data = part.get_payload(decode=True) or b""
        if not name.lower().endswith(OK_EXT) or not data or len(data) > MAX_ATTACH:
            log.warning("mailbox: skipped attachment %r (type/size)", name)
            continue
        (inbox / f"{prefix}{stamp}-{idx}-{name}").write_bytes(data)
        saved += 1
    return saved


def pull(root: Path) -> int:
    """Save new mail from allowed senders into inbox/. Returns the number of items saved."""
    host, user, pw = (os.environ.get(k) for k in ("IMAP_HOST", "IMAP_USER", "IMAP_PASS"))
    allowed = {a.strip().lower() for a in os.environ.get("INBOX_ALLOWED_SENDERS", "").split(",") if a.strip()}
    if not (host and user and pw):
        log.info("mailbox: IMAP not configured - skipping")
        return 0
    if not allowed:
        log.warning("mailbox: INBOX_ALLOWED_SENDERS is empty - accepting nothing")
        return 0
    inbox = root / "inbox"
    inbox.mkdir(exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    total = 0
    try:
        conn = imaplib.IMAP4_SSL(host)
        conn.login(user, pw)
        conn.select("INBOX")
        _, data = conn.search(None, "UNSEEN")
        for idx, num in enumerate(data[0].split()[:MAX_MAILS], 1):
            _, parts = conn.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(parts[0][1], policy=policy.default)
            if parseaddr(str(msg.get("From", "")))[1].lower() not in allowed:
                continue                                   # stranger: leave untouched
            if (n := _store(msg, inbox, stamp, idx)):
                total += n
                conn.store(num, "+FLAGS", "\\Seen")
        conn.logout()
    except Exception as exc:  # noqa: BLE001 - a mailbox problem must never block publication
        log.error("mailbox: failed (%s)", exc)
    log.info("mailbox: saved %d item(s)", total)
    return total
