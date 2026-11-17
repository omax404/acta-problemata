"""Motion companion to the printable broadside: a short MP4 (+ small GIF) of the same edition.

The PDF stays the authoritative, printable page. The clip is best-effort garnish for the email:
it is rendered from templates/video/index.html (HyperFrames: HTML + GSAP -> MP4) using the SAME
edition.json the Typst template reads, so every number on screen is real data.
Nothing here may ever cost us the edition: callers treat VideoError / None as "no clip today".
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger("acta.video")
RENDER_TIMEOUT_S = 240
FPS = 30


class VideoError(RuntimeError):
    pass


def find_cli() -> list[str] | None:
    """`hyperframes` on PATH (CI: npm i -g hyperframes) or ACTA_HYPERFRAMES="npx --no-install hyperframes"."""
    override = os.environ.get("ACTA_HYPERFRAMES")
    if override:
        return override.split()
    exe = shutil.which("hyperframes")
    return [exe] if exe else None


def build_project(edition: dict, build: Path, repo_root: Path) -> Path:
    """Materialise a self-contained HyperFrames project in build/video (no network needed)."""
    src = repo_root / "templates" / "video"
    proj = build / "video"
    if proj.exists():
        shutil.rmtree(proj)
    proj.mkdir(parents=True)
    shutil.copy(src / "gsap.min.js", proj / "gsap.min.js")
    shutil.copytree(src / "fonts", proj / "fonts")
    for name in ("diagram.svg", "qr.svg"):
        if not (build / name).exists():
            raise VideoError(f"{name} missing in {build}: render the PDF first")
        shutil.copy(build / name, proj / name)
    # "</" inside a <script> would end it early: escape so any headline/narrative is safe.
    payload = json.dumps(edition, ensure_ascii=False).replace("</", "<\\/")
    html = (src / "index.html").read_text(encoding="utf-8")
    marker = "/*EDITION_JSON*/ null"
    if marker not in html:
        raise VideoError("templates/video/index.html lost its /*EDITION_JSON*/ marker")
    (proj / "index.html").write_text(html.replace(marker, payload), encoding="utf-8")
    return proj


def _run(cmd: list[str], cwd: Path, what: str) -> None:
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=RENDER_TIMEOUT_S)
    except subprocess.TimeoutExpired as exc:
        raise VideoError(f"{what} timed out after {RENDER_TIMEOUT_S}s") from exc
    except OSError as exc:
        raise VideoError(f"{what} could not start: {exc}") from exc
    if r.returncode:
        tail = (r.stderr or r.stdout).strip().splitlines()[-6:]
        raise VideoError(f"{what} failed (exit {r.returncode}): " + " | ".join(tail))


def make_gif(mp4: Path, gif: Path, width: int = 420, fps: int = 12) -> Path:
    """Email-inline GIF (clients do not play MP4 inline). Two-pass palette keeps the paper tones clean."""
    ff = shutil.which("ffmpeg")
    if not ff:
        raise VideoError("ffmpeg not found (needed for the GIF)")
    vf = (f"fps={fps},scale={width}:-1:flags=lanczos,split[a][b];"
          "[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4")
    _run([ff, "-y", "-loglevel", "error", "-i", str(mp4), "-vf", vf, "-loop", "0", str(gif)],
         mp4.parent, "ffmpeg gif")
    return gif


def render_video(edition: dict, repo_root: Path, out_stem: Path, gif: bool = True) -> dict:
    """Render out_stem.mp4 (and .gif). Raises VideoError; returns {"mp4": Path, "gif": Path|None}."""
    cli = find_cli()
    if not cli:
        raise VideoError("hyperframes CLI not installed")
    build = repo_root / "build"
    proj = build_project(edition, build, repo_root)
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    mp4 = out_stem.with_suffix(".mp4")
    mp4.unlink(missing_ok=True)
    _run([*cli, "render", str(proj), "-o", str(mp4), "--fps", str(FPS), "--crf", "24", "--quiet"],
         repo_root, "hyperframes render")
    if not mp4.exists() or mp4.stat().st_size < 10_000:
        raise VideoError("hyperframes produced no usable MP4")
    out = {"mp4": mp4, "gif": None}
    if gif:
        try:
            out["gif"] = make_gif(mp4, out_stem.with_suffix(".gif"))
        except VideoError as exc:                      # the MP4 alone is still worth sending
            log.warning("gif skipped: %s", exc)
    log.info("video: %s (%.1f MB)%s", mp4.name, mp4.stat().st_size / 1e6,
             f" + {out['gif'].name} ({out['gif'].stat().st_size / 1e6:.1f} MB)" if out["gif"] else "")
    return out


def maybe_render(edition: dict, repo_root: Path, out_stem: Path, cfg: dict) -> dict | None:
    """Pipeline entry point: never raises, returns None when disabled/unavailable/failed."""
    vcfg = cfg.get("video", {})
    off = os.environ.get("ACTA_VIDEO", "").lower() in ("0", "off", "false", "no")
    if off or not vcfg.get("enabled", True):
        return None
    if find_cli() is None:
        log.info("video: hyperframes not installed — skipping motion clip")
        return None
    try:
        return render_video(edition, repo_root, out_stem, gif=vcfg.get("gif", True))
    except Exception as exc:  # noqa: BLE001 - a missing clip must never block publication
        log.error("video: %s", exc)
        return None
