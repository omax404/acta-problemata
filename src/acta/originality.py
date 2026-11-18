"""'Rewritten, not copied' made enforceable.

The synthesis prompt already tells the model to paraphrase. A prompt is a request, not a guarantee, so
every live-sourced case is also checked here: if the text we would publish shares a run of RUN consecutive
words with the source page, the case is rejected and the pipeline falls back to the bank/vault.
Facts, numbers and short technical phrases are free to reuse; sentences are not.
"""
from __future__ import annotations

import re

from .schemas import LLMCase

RUN = 8                                    # consecutive shared words that count as copying
_WORD = re.compile(r"[\w'’-]+", re.UNICODE)


class NotOriginalError(ValueError):
    """The generated case reuses a passage of its source verbatim."""


def _words(text: str) -> list[str]:
    return [w.lower() for w in _WORD.findall(text)]


def _grams(words: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def longest_shared_run(source: str, candidate: str, cap: int = 40) -> int:
    """Length (in words) of the longest word sequence found in both texts (stops counting at `cap`)."""
    s, c = _words(source), _words(candidate)
    if not s or not c:
        return 0
    best, prev = 0, {}
    index: dict[str, list[int]] = {}
    for j, w in enumerate(s):
        index.setdefault(w, []).append(j)
    for w in c:                                        # dynamic programme over matching positions only
        cur = {}
        for j in index.get(w, ()):
            cur[j] = prev.get(j - 1, 0) + 1
            if cur[j] > best:
                best = cur[j]
                if best >= cap:
                    return best
        prev = cur
    return best


def published_text(case: LLMCase) -> str:
    parts = [case.title, case.narrative, case.challenge_question, case.diagram.caption]
    parts += [f"{b.name} {b.value}" for b in case.boundary_conditions]
    return "\n".join(parts)


def check_original(source_text: str, case: LLMCase, run: int = RUN) -> int:
    """Return the longest shared run; raise NotOriginalError if it reaches `run` words."""
    longest = longest_shared_run(source_text, published_text(case), cap=run + 1)
    if longest >= run:
        raise NotOriginalError(f"case repeats {longest}+ consecutive words of its source")
    return longest
