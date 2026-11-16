from email.message import EmailMessage

import pytest

from acta import mailbox

LONG = "Cooling water header loses head when a second extruder starts. " * 10


def _msg(sender="boss@example.org", subject="[Fluids] header", body=LONG, attach=None):
    m = EmailMessage()
    m["From"], m["Subject"] = f"Boss <{sender}>", subject
    m.set_content(body)
    for name, data, mt, st in attach or []:
        m.add_attachment(data, maintype=mt, subtype=st, filename=name)
    return m.as_bytes()


class FakeIMAP:
    boxes: list[bytes] = []
    seen: list[str] = []

    def __init__(self, host, *a, **k):
        pass

    def login(self, u, p):
        return "OK", []

    def select(self, box):
        return "OK", []

    def search(self, charset, crit):
        return "OK", [b" ".join(str(i + 1).encode() for i in range(len(self.boxes)))]

    def fetch(self, num, spec):
        return "OK", [(b"1 (RFC822)", self.boxes[int(num) - 1])]

    def store(self, num, op, flag):
        self.seen.append(num.decode() if isinstance(num, bytes) else str(num))
        return "OK", []

    def logout(self):
        return "BYE", []


@pytest.fixture
def env(monkeypatch, tmp_path):
    monkeypatch.setattr(mailbox.imaplib, "IMAP4_SSL", FakeIMAP)
    monkeypatch.setenv("IMAP_HOST", "imap.example.org")
    monkeypatch.setenv("IMAP_USER", "u")
    monkeypatch.setenv("IMAP_PASS", "p")
    monkeypatch.setenv("INBOX_ALLOWED_SENDERS", "boss@example.org, friend@example.org")
    (tmp_path / "data" / "inbox").mkdir(parents=True)
    FakeIMAP.boxes, FakeIMAP.seen = [], []
    return tmp_path


def test_body_and_attachment_saved_with_domain_prefix(env):
    FakeIMAP.boxes = [_msg(attach=[("tender.pdf", b"%PDF-1.4 fake", "application", "pdf")])]
    n = mailbox.pull(env)
    names = sorted(p.name for p in (env / "data" / "inbox").iterdir())
    assert n == 2 and any(x.startswith("Fluids__") and x.endswith(".txt") for x in names)
    assert any(x.endswith("tender.pdf") for x in names)
    assert FakeIMAP.seen == ["1"]                       # marked read only after saving


def test_unknown_sender_ignored_and_left_unread(env):
    FakeIMAP.boxes = [_msg(sender="stranger@evil.example")]
    assert mailbox.pull(env) == 0 and not list((env / "data" / "inbox").iterdir()) and FakeIMAP.seen == []


def test_empty_allowlist_fails_closed(env, monkeypatch):
    monkeypatch.setenv("INBOX_ALLOWED_SENDERS", "")
    FakeIMAP.boxes = [_msg()]
    assert mailbox.pull(env) == 0 and not list((env / "data" / "inbox").iterdir())


def test_unconfigured_mailbox_is_a_noop(env, monkeypatch):
    monkeypatch.delenv("IMAP_HOST")
    assert mailbox.pull(env) == 0


def test_path_traversal_and_bad_types_rejected(env):
    FakeIMAP.boxes = [_msg(body="short", attach=[
        ("../../evil.pdf", b"%PDF-1.4", "application", "pdf"),
        ("run.exe", b"MZ", "application", "octet-stream")])]
    mailbox.pull(env)
    names = [p.name for p in (env / "data" / "inbox").iterdir()]
    assert any(n.endswith("-evil.pdf") for n in names)        # saved under a sanitised name, not dropped
    assert all("/" not in n and ".." not in n for n in names) and not any(n.endswith(".exe") for n in names)
    assert not (env.parent / "evil.pdf").exists()


def test_oversized_attachment_skipped(env):
    FakeIMAP.boxes = [_msg(body="short", attach=[("big.pdf", b"x" * (mailbox.MAX_ATTACH + 1), "application", "pdf")])]
    assert mailbox.pull(env) == 0


def test_urls_in_short_mail_go_to_urls_txt(env):
    FakeIMAP.boxes = [_msg(subject="[Thermal] link", body="see https://example.org/tender/42 please")]
    mailbox.pull(env)
    assert "https://example.org/tender/42 | Thermal" in (env / "data" / "inbox" / "urls.txt").read_text(encoding="utf-8")


def test_network_error_never_raises(env, monkeypatch):
    def boom(*a, **k):
        raise OSError("down")
    monkeypatch.setattr(mailbox.imaplib, "IMAP4_SSL", boom)
    assert mailbox.pull(env) == 0
