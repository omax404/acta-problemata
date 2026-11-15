"""FR-02: structured synthesis. Provider chain Gemini -> Groq -> OpenAI.
All providers are optional; with zero keys the pipeline runs on the vault.
REST is used directly (requests) to keep the dependency footprint tiny.
"""
from __future__ import annotations

import json
import logging
import os
import time

import requests

from .schemas import LLMCase, gemini_response_schema

log = logging.getLogger("acta.synth")

PRIVACY_ON = ("PRIVACY: never name any company, brand, person, tender number or site. Describe only the "
              "sector and the region (e.g. 'a cement plant in the Meknes region'). The source may be a "
              "forum post or tender: paraphrase into an ORIGINAL scenario, never quote it.")
PRIVACY_OFF = ("The organisation's sector and city may be kept if the source states them; never invent "
               "company names, never quote the source verbatim.")

SYSTEM = """You are the content engine of Acta Problemata, a daily engineering
broadside. From the source text, invent ONE realistic, self-contained engineering
failure scenario inspired by it (do not copy the source verbatim) and return JSON:
- title: industrial failure headline, max 10 words.
- domain: exactly {domain}.
- narrative: 120-150 words of operational context, ending with the givens.
- boundary_conditions: 3-8 {{name, value}} pairs, every value WITH units.
- formula: one closed-form equation. 'symbolic' is ASCII parseable by SymPy
  (use *, **, sqrt(), pi; no LaTeX, no '='). 'variables' lists every symbol
  with a realistic SI numerical value. 'unit' is the SI unit of the result.
- challenge_question: ask the reader to compute that result (3 s.f.).
- diagram: pick the closest kind from the allowed enum; params optional.
Difficulty: {difficulty}. Never state the numerical answer anywhere.
{privacy}
Return ONLY the JSON object."""


class SynthesisError(RuntimeError):
    pass


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):]
    return json.loads(text[text.find("{"): text.rfind("}") + 1])


def _call_gemini(prompt: str, cfg: dict, timeout: float) -> str:
    model = cfg.get("gemini_model", "gemini-3.6-flash")
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}],
              "generationConfig": {"responseMimeType": "application/json",
                                   "responseSchema": gemini_response_schema(LLMCase),
                                   "temperature": 0.2, "maxOutputTokens": 4096}},
        timeout=timeout)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def _call_openai_compat(base: str, key_env: str, model: str, prompt: str, timeout: float) -> str:
    r = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {os.environ[key_env]}"},
        json={"model": model, "temperature": 0.2,
              "response_format": {"type": "json_object"},
              "messages": [{"role": "system", "content": "Output only valid JSON."},
                           {"role": "user", "content": prompt}]},
        timeout=timeout)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def synthesize(source_text: str, domain: str, difficulty: str, llm_cfg: dict,
               deadline: float | None = None, anonymize: bool = True) -> LLMCase:
    timeout = float(llm_cfg.get("timeout_s", 20))
    privacy = PRIVACY_ON if anonymize else PRIVACY_OFF
    prompt = (SYSTEM.format(domain=domain, difficulty=difficulty, privacy=privacy)
              + "\n\nSOURCE TEXT:\n" + source_text[:6000])
    keys = {"gemini": "GEMINI_API_KEY", "groq": "GROQ_API_KEY", "openai": "OPENAI_API_KEY"}
    errors = []
    for provider in llm_cfg.get("provider_order", ["gemini", "groq", "openai"]):
        if not os.environ.get(keys.get(provider, "")):
            continue
        feedback = ""
        for attempt in range(2):                      # one validation retry
            if deadline and time.monotonic() > deadline - 5:
                raise SynthesisError("time budget exhausted: " + "; ".join(errors))
            try:
                if provider == "gemini":
                    raw = _call_gemini(prompt + feedback, llm_cfg, timeout)
                elif provider == "groq":
                    raw = _call_openai_compat("https://api.groq.com/openai/v1", "GROQ_API_KEY",
                                              llm_cfg.get("groq_model", "llama-3.3-70b-versatile"),
                                              prompt + feedback, timeout)
                else:
                    raw = _call_openai_compat("https://api.openai.com/v1", "OPENAI_API_KEY",
                                              llm_cfg.get("openai_model", "gpt-4o-mini"),
                                              prompt + feedback, timeout)
                case = LLMCase.model_validate(_extract_json(raw))
                log.info("synthesis: %s ok (attempt %d)", provider, attempt + 1)
                return case
            except Exception as exc:  # noqa: BLE001 - any provider error -> retry / next provider
                errors.append(f"{provider}#{attempt + 1}: {exc}")
                feedback = f"\n\nYour previous output was rejected: {exc}. Fix it and return valid JSON."
                log.warning("synthesis: %s attempt %d failed: %s", provider, attempt + 1, exc)
    raise SynthesisError("; ".join(errors) or "no LLM API keys configured")
