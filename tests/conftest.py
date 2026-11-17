import pytest


@pytest.fixture(autouse=True)
def _no_motion_clip_by_default(monkeypatch):
    """A real clip render takes ~30 s: only tests that ask for it (tests/test_video.py) pay for it."""
    monkeypatch.setenv("ACTA_VIDEO", "off")
