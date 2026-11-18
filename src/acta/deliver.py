"""FR-05: SMTP router + optional raw-socket / lp printer router.
Everything is configured via environment (GitHub Secrets, NFR-04);
unconfigured channels are skipped, never fatal.
"""
from __future__ import annotations

import html
import logging
import os
import smtplib
import socket
import subprocess
from email.message import EmailMessage
from pathlib import Path

log = logging.getLogger("acta.deliver")


def build_message(pdf: Path, edition: dict, to: str, sender: str, answer: float | None = None,
                  unit: str = "", media: dict | None = None) -> EmailMessage:
    """PDF is always attached. With a motion clip: GIF inline in an HTML part (plays in every mail
    client) and the MP4 attached. Plain text stays the first alternative, so text-only clients lose nothing.
    """
    media = media or {}
    msg = EmailMessage()
    msg["Subject"] = f"Acta Problemata — No. {edition['edition_number']} — {edition['headline']}"
    msg["From"] = sender
    msg["To"] = to
    text = (f"{edition['headline']}\n\n{edition['challenge_question']}\n\n"
            f"Solution gateway: {edition['solution_url']}\n"
            + (f"Original public source: {edition['source_url']}\n"
               if str(edition.get("source_url", "")).startswith(("http://", "https://")) else "")
            + "Verify your answer locally:  acta check <value>\n"
            + (f"Check value (3 s.f.): {answer:.3g} {unit}\n" if answer is not None else ""))
    msg.set_content(text)
    gif, mp4 = media.get("gif"), media.get("mp4")
    if gif and Path(gif).exists():
        esc = html.escape
        msg.add_alternative(
            '<div style="font-family:Georgia,serif;color:#1b1814;max-width:560px">'
            f'<h2 style="margin:0 0 8px">{esc(edition["headline"])}</h2>'
            f'<p style="font-style:italic">{esc(edition["challenge_question"])}</p>'
            '<p style="margin:12px 0"><img src="cid:acta-motion" width="420"'
            ' alt="Acta Problemata broadside, animated"'
            ' style="border:1px solid #1b1814;max-width:100%;height:auto"></p>'
            f'<p>Printable A4 sheet attached (PDF). '
            f'<a href="{esc(edition["solution_url"])}">Solution gateway</a></p></div>',
            subtype="html")
        msg.get_payload()[1].add_related(Path(gif).read_bytes(), maintype="image", subtype="gif",
                                         cid="<acta-motion>", filename=Path(gif).name)
    msg.add_attachment(pdf.read_bytes(), maintype="application", subtype="pdf", filename=pdf.name)
    if mp4 and Path(mp4).exists():
        msg.add_attachment(Path(mp4).read_bytes(), maintype="video", subtype="mp4", filename=Path(mp4).name)
    return msg


def send_email(pdf: Path, edition: dict, to: str | None = None,
               answer: float | None = None, unit: str = "", media: dict | None = None) -> bool:
    host, user, pw = os.environ.get("SMTP_HOST"), os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS")
    to = to or os.environ.get("MAIL_TO", "")
    if not (host and user and pw and to):
        log.info("deliver: SMTP not configured — skipping email")
        return False
    port = int(os.environ.get("SMTP_PORT", "465"))
    msg = build_message(pdf, edition, to, os.environ.get("MAIL_FROM", user), answer, unit, media)
    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=15) as s:
            s.login(user, pw); s.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=15) as s:
            s.starttls(); s.login(user, pw); s.send_message(msg)
    log.info("deliver: emailed %s to %s%s", pdf.name, to, " (with motion clip)" if media else "")
    return True


def send_printer(pdf: Path) -> bool:
    host, queue = os.environ.get("PRINTER_HOST"), os.environ.get("PRINTER_QUEUE")
    if host:
        with socket.create_connection((host, int(os.environ.get("PRINTER_PORT", "9100"))), timeout=10) as s:
            s.sendall(pdf.read_bytes())
        log.info("deliver: pushed %s to %s:9100", pdf.name, host)
        return True
    if queue:
        subprocess.run(["lp", "-d", queue, str(pdf)], check=True, timeout=15)
        log.info("deliver: spooled %s to %s", pdf.name, queue)
        return True
    log.info("deliver: no printer configured — skipping")
    return False
