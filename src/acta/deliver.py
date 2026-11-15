"""FR-05: SMTP router + optional raw-socket / lp printer router.
Everything is configured via environment (GitHub Secrets, NFR-04);
unconfigured channels are skipped, never fatal.
"""
from __future__ import annotations

import logging
import os
import smtplib
import socket
import subprocess
from email.message import EmailMessage
from pathlib import Path

log = logging.getLogger("acta.deliver")


def send_email(pdf: Path, edition: dict, to: str | None = None,
               answer: float | None = None, unit: str = "") -> bool:
    host, user, pw = os.environ.get("SMTP_HOST"), os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS")
    to = to or os.environ.get("MAIL_TO", "")
    if not (host and user and pw and to):
        log.info("deliver: SMTP not configured — skipping email")
        return False
    port = int(os.environ.get("SMTP_PORT", "465"))
    msg = EmailMessage()
    msg["Subject"] = f"Acta Problemata — No. {edition['edition_number']} — {edition['headline']}"
    msg["From"] = os.environ.get("MAIL_FROM", user)
    msg["To"] = to
    msg.set_content(
        f"{edition['headline']}\n\n{edition['challenge_question']}\n\n"
        f"Solution gateway: {edition['solution_url']}\n"
        "Verify your answer locally:  acta check <value>\n"
        + (f"Check value (3 s.f.): {answer:.3g} {unit}\n" if answer is not None else "")
    )
    msg.add_attachment(pdf.read_bytes(), maintype="application", subtype="pdf", filename=pdf.name)
    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=15) as s:
            s.login(user, pw); s.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=15) as s:
            s.starttls(); s.login(user, pw); s.send_message(msg)
    log.info("deliver: emailed %s to %s", pdf.name, to)
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
