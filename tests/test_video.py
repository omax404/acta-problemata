import json
import shutil
from email import message_from_bytes, policy
from pathlib import Path

import pytest

from acta import deliver, pipeline, video
from acta.cli import main as cli_main
from acta.diagrams import render_diagram
from acta.render import render_edition

ROOT = Path(__file__).resolve().parents[1]
NEEDS_CLI = pytest.mark.skipif(video.find_cli() is None or not shutil.which("ffmpeg"),
                               reason="hyperframes + ffmpeg not installed")


@pytest.fixture
def repo(tmp_path):
    for name in ("templates", "data"):
        shutil.copytree(ROOT / name, tmp_path / name)
    shutil.copy(ROOT / "config.json", tmp_path / "config.json")
    (tmp_path / "data" / "ledger.json").unlink(missing_ok=True)
    return tmp_path


def _edition(**over):
    e = {"edition_number": 7, "date": "2026-11-15", "date_display": "15 November 2026",
         "domain": "Mechanical", "difficulty": "Intermediate", "headline": "Short title here",
         "narrative": "Word " * 140, "boundary_conditions": {f"Quantity {i}": f"{i}.5 m" for i in range(4)},
         "formula": {"symbolic": "P*L/E", "variables": {"P": 1.0}, "computed_result": 1.0,
                     "result_display": "1.00", "unit": "m"},
         "challenge_question": "Compute the result in metres to three significant figures.",
         "diagram_caption": "Fig. 1 - test", "source_line": "Source: test.",
         "repo_slug": "me/acta", "solution_url": "https://example.org/s/7", "reveal_answer": False}
    e.update(over)
    return e


def _built(repo, **over):
    """A repo whose build/ holds what render_edition leaves behind (edition.json, diagram.svg, qr.svg)."""
    svg = render_diagram("cantilever_point_load", {}, repo / "build" / "d.svg")
    ed = _edition(**over)
    render_edition(ed, svg, "https://example.org/s/7", repo, repo / "out.pdf")
    return ed


def test_build_project_is_self_contained_and_script_safe(repo):
    ed = _built(repo, headline='Breaks </script><b>out</b> & "quotes"')
    proj = video.build_project(ed, repo / "build", repo)
    html = (proj / "index.html").read_text(encoding="utf-8")
    assert "/*EDITION_JSON*/ null" not in html                 # marker replaced
    assert "</script><b>" not in html                          # payload cannot close the script tag
    payload = html.split("window.EDITION = ", 1)[1].split(";</script>", 1)[0]
    assert json.loads(payload.replace("<\\/", "</"))["headline"] == ed["headline"]
    for f in ("gsap.min.js", "diagram.svg", "qr.svg", "fonts/libertinus-serif-latin-700-normal.woff2"):
        assert (proj / f).exists(), f
    assert "http" not in "".join(ln for ln in html.splitlines() if "src=" in ln)   # no network assets


def test_build_project_requires_pdf_artifacts(repo):
    with pytest.raises(video.VideoError, match="diagram.svg missing"):
        video.build_project(_edition(), repo / "build", repo)


def test_maybe_render_disabled_or_unavailable_is_none(repo, monkeypatch):
    ed = _built(repo)
    monkeypatch.delenv("ACTA_VIDEO")
    monkeypatch.delenv("ACTA_HYPERFRAMES", raising=False)
    monkeypatch.setattr(video.shutil, "which", lambda *_: None)
    assert video.maybe_render(ed, repo, repo / "o", {}) is None                    # no CLI
    assert video.maybe_render(ed, repo, repo / "o", {"video": {"enabled": False}}) is None
    monkeypatch.setenv("ACTA_VIDEO", "off")
    monkeypatch.setenv("ACTA_HYPERFRAMES", "hyperframes")
    assert video.maybe_render(ed, repo, repo / "o", {}) is None                    # env kill-switch


def test_maybe_render_never_raises(repo, monkeypatch):
    ed = _built(repo)
    monkeypatch.delenv("ACTA_VIDEO")
    monkeypatch.setenv("ACTA_HYPERFRAMES", "hyperframes")
    monkeypatch.setattr(video, "render_video", lambda *a, **k: (_ for _ in ()).throw(video.VideoError("boom")))
    assert video.maybe_render(ed, repo, repo / "o", {}) is None
    monkeypatch.setattr(video, "render_video", lambda *a, **k: (_ for _ in ()).throw(ValueError("odd")))
    assert video.maybe_render(ed, repo, repo / "o", {}) is None


def test_render_failure_is_a_video_error(repo, monkeypatch):
    ed = _built(repo)
    monkeypatch.setenv("ACTA_HYPERFRAMES", "false")             # exits 1 immediately
    with pytest.raises(video.VideoError, match="render failed"):
        video.render_video(ed, repo, repo / "build" / "o" / "x")


def _parse(msg):
    return message_from_bytes(msg.as_bytes(), policy=policy.default)


def test_email_plain_without_media(tmp_path):
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF-1.4 x")
    m = _parse(deliver.build_message(pdf, _edition(), "to@x.org", "me@x.org"))
    assert [p.get_filename() for p in m.iter_attachments()] == ["a.pdf"]
    assert m.get_body(("html",)) is None


def test_email_with_media_inlines_gif_and_attaches_mp4(tmp_path):
    pdf, gif, mp4 = tmp_path / "a.pdf", tmp_path / "a.gif", tmp_path / "a.mp4"
    pdf.write_bytes(b"%PDF-1.4 x"); gif.write_bytes(b"GIF89a" + b"0" * 40); mp4.write_bytes(b"\0\0\0\x18ftypmp42")
    m = _parse(deliver.build_message(pdf, _edition(headline="A <b>&</b> B"), "to@x.org", "me@x.org",
                                     media={"gif": gif, "mp4": mp4}))
    assert "Solution gateway" in m.get_body(("plain",)).get_content()
    html_part = m.get_body(("html",))
    body = html_part.get_content()
    assert "cid:acta-motion" in body and "A &lt;b&gt;&amp;&lt;/b&gt; B" in body       # headline is escaped
    cids = [p["Content-ID"] for p in m.walk() if p.get_content_type() == "image/gif"]
    assert cids == ["<acta-motion>"]
    assert sorted(p.get_filename() for p in m.iter_attachments() if p.get_filename()) == ["a.mp4", "a.pdf"]


def test_email_survives_missing_media_files(tmp_path):
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF-1.4 x")
    m = _parse(deliver.build_message(pdf, _edition(), "to@x.org", "me@x.org",
                                     media={"gif": tmp_path / "gone.gif", "mp4": tmp_path / "gone.mp4"}))
    assert [p.get_filename() for p in m.iter_attachments()] == ["a.pdf"]


def test_pipeline_passes_media_to_delivery_and_summary(repo, monkeypatch):
    fake = {"mp4": repo / "m.mp4", "gif": repo / "m.gif"}
    monkeypatch.setattr(pipeline.video, "maybe_render", lambda *a, **k: fake)
    seen = {}
    monkeypatch.setattr(pipeline.deliver, "send_email", lambda pdf, ed, media=None: seen.update(media=media))
    s = pipeline.run(repo, dry_run=False, force_vault=True)
    assert seen["media"] == fake
    assert s["video"] == {"mp4": str(fake["mp4"]), "gif": str(fake["gif"])}
    assert s["delivery_errors"] == []


def test_pipeline_without_hyperframes_is_unchanged(repo, monkeypatch):
    monkeypatch.delenv("ACTA_HYPERFRAMES", raising=False)
    monkeypatch.setattr(video.shutil, "which", lambda *_: None)
    s = pipeline.run(repo, dry_run=True, force_vault=True)
    assert s["video"] is None and s["pages"] == 1


def test_cli_video_needs_a_build(repo):
    assert cli_main(["--root", str(repo), "video"]) == 2


@NEEDS_CLI
def test_real_render_produces_playable_mp4_and_gif(repo):
    ed = _built(repo)
    out = video.render_video(ed, repo, repo / "build" / "media" / "acta-0007")
    import subprocess
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,duration",
                            "-of", "csv=p=0", str(out["mp4"])], capture_output=True, text=True, check=True).stdout
    assert probe.strip().startswith("840,1188,10.0")
    assert 50_000 < out["mp4"].stat().st_size < 5_000_000
    assert out["gif"] and 50_000 < out["gif"].stat().st_size < 8_000_000
