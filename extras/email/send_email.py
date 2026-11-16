#!/usr/bin/env python3
"""Send the built edition to subscribers through Resend (https://resend.com).  UNTESTED against a live account.
env: RESEND_API_KEY, MAIL_FROM ("Acta Problemata <acta@yourdomain.ma>"), SUBSCRIBERS_URL (private endpoint returning JSON list of
{"email":..., "token":...}), UNSUB_BASE (e.g. https://yourdomain.ma/unsubscribe?t=)
Subscriber addresses must NOT live in this public repo."""
import os, sys, json, urllib.request
html_path, subject = sys.argv[1], sys.argv[2]
tpl = open(html_path, encoding="utf-8").read()
subs = json.load(urllib.request.urlopen(os.environ["SUBSCRIBERS_URL"]))
for s in subs:
    unsub = os.environ["UNSUB_BASE"] + s["token"]
    body = json.dumps({"from": os.environ["MAIL_FROM"], "to": [s["email"]], "subject": subject,
                       "html": tpl.replace("{{UNSUB_URL}}", unsub),
                       "headers": {"List-Unsubscribe": f"<{unsub}>"}}).encode()
    req = urllib.request.Request("https://api.resend.com/emails", body,
        {"Authorization": "Bearer " + os.environ["RESEND_API_KEY"], "Content-Type": "application/json"})
    urllib.request.urlopen(req)
print("sent", len(subs))
