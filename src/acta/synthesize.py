"""FR-02: structured synthesis. Provider chain Gemini -> Groq -> OpenAI.
All providers are optional; with zero keys the pipeline runs on the vault.
Two entry points: `synthesize` rewrites a fetched source into a case; `synthesize_ideation`
invents one from scratch (no source) so the daily edition stays fresh even when every
scraper fails. REST is used directly (requests) to keep the dependency footprint tiny.
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import date

import requests

from .schemas import LLMCase, gemini_response_schema

log = logging.getLogger("acta.synth")

PRIVACY_ON = ("PRIVACY: never name any company, brand, person, tender number or site. Describe only the "
              "sector and the region (e.g. 'a cement plant in the Meknes region'). The source may be a "
              "forum post or tender: paraphrase into an ORIGINAL scenario, never quote it.")
PRIVACY_OFF = ("The organisation's sector and city may be kept if the source states them; never invent "
               "company names, never quote the source verbatim.")

_FIELD_SPEC = """- title: industrial failure headline, max 10 words.
- domain: exactly {domain}.
- narrative: 120-150 words of operational context, ending with the givens.
- boundary_conditions: 3-8 {{name, value}} pairs, every value WITH units.
- formula: one closed-form equation. 'symbolic' is ASCII parseable by SymPy
  (use *, **, sqrt(), pi; no LaTeX, no '='). 'variables' lists every symbol
  with a realistic SI numerical value. 'unit' is the SI unit of the result.
- challenge_question: ask the reader to compute that result (3 s.f.).
- diagram: pick the closest kind from the allowed enum; params optional.
Difficulty: {difficulty}. Never state the numerical answer anywhere."""

SYSTEM = """You are the content engine of Acta Problemata, a daily engineering
broadside. From the source text, invent ONE realistic, self-contained engineering
failure scenario inspired by it (do not copy the source verbatim) and return JSON:
""" + _FIELD_SPEC + """
{privacy}
Return ONLY the JSON object."""

IDEATION = """You are the content engine of Acta Problemata, a daily engineering broadside.
No source text is available today: invent ONE fresh, realistic, self-contained industrial
failure or maintenance scenario from scratch, in the {domain} domain. Treat the theme
"{theme}" as a starting point, not a constraint; avoid the most common textbook setups.
""" + _FIELD_SPEC + """
{privacy}
Return ONLY the JSON object."""

# Rotating seeds keep ideation from converging on the same scenario on every run.
DOMAIN_THEMES: dict[str, tuple[str, ...]] = {
    "Mechanical": ("conveyor drive line", "gearbox bearing", "hydraulic press",
                   "compressor valve deck", "shaft misalignment"),
    "Aerospace": ("avionics rack cooling", "landing-gear actuator", "cabin pressurisation",
                  "fuel pump cavitation", "wing rib fatigue"),
    "Electrical": ("motor winding insulation", "UPS battery room", "cable ampacity derating",
                   "VFD harmonics", "switchgear hot joint"),
    "Chemical": ("reactor overpressure margin", "cooling-tower scaling", "acid line pump seal",
                 "exothermic batch cooling", "tank venting"),
    "Civil": ("formwork shoring load", "sheet-pile seepage", "expansion joint seizure",
              "scaffold anchorage", "early-age concrete strength"),
    "Thermal": ("industrial dryer air recycling", "chiller fouling", "failed steam trap",
                "kiln refractory loss", "exhaust heat recovery"),
    "Materials": ("weld HAZ cracking", "fastener galvanic corrosion", "coating adhesion",
                  "polymer creep under load", "casting porosity"),
    "Fluids": ("irrigation main surge", "fire line pressure drop", "intake channel sediment",
               "transfer pump cavitation", "compressed-air ring main leak"),
}

GEMINI_MODEL_FALLBACK = ("gemini-flash-latest", "gemini-2.0-flash")


class SynthesisError(RuntimeError):
    pass


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):]
    return json.loads(text[text.find("{"): text.rfind("}") + 1])


def _gemini_models(cfg: dict) -> list[str]:
    """Explicit list wins; a legacy single `gemini_model` is honoured; else the default pair."""
    if cfg.get("gemini_models"):
        models = list(cfg["gemini_models"])
    elif cfg.get("gemini_model"):
        models = [cfg["gemini_model"]]
    else:
        models = list(GEMINI_MODEL_FALLBACK)
    return [m for m in models if m] or list(GEMINI_MODEL_FALLBACK)


def _gemini_key() -> str | None:
    """GEMINI_API_KEY first; GOOGLE_API_KEY accepted as the Google-SDK-compatible alias."""
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def _call_gemini(prompt: str, cfg: dict, timeout: float) -> str:
    """One prompt -> text, trying each configured model in order. Raises the last error."""
    last: Exception = RuntimeError("no Gemini model attempted")
    for model in _gemini_models(cfg):
        gen: dict = {"responseMimeType": "application/json",
                     "responseSchema": gemini_response_schema(LLMCase),
                     "temperature": 0.2,
                     "maxOutputTokens": int(cfg.get("max_output_tokens", 8192))}
        if "2.5" in model or model.endswith("-latest"):
            # 2.5-class models spend thinking tokens inside maxOutputTokens; a small
            # structured JSON does not need them, so the whole budget goes to the answer.
            gen["thinkingConfig"] = {"thinkingBudget": 0}
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers={"x-goog-api-key": _gemini_key(),
                         "Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": gen},
                timeout=timeout)
            r.raise_for_status()
            parts = ((r.json().get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
            text = "".join(p.get("text", "") for p in parts).strip()
            if not text:
                raise RuntimeError("empty response (blocked or thinking-only output)")
            return text
        except Exception as exc:  # noqa: BLE001 - try the next model, surface the last error
            last = exc
            log.warning("gemini: model %s failed: %s", model, exc)
    raise last


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


def _run_providers(prompt: str, llm_cfg: dict, deadline: float | None) -> LLMCase:
    timeout = float(llm_cfg.get("timeout_s", 20))
    keys = {"gemini": "GEMINI_API_KEY", "groq": "GROQ_API_KEY", "openai": "OPENAI_API_KEY"}
    errors = []
    for provider in llm_cfg.get("provider_order", ["gemini", "groq", "openai"]):
        has_key = _gemini_key() if provider == "gemini" else os.environ.get(keys.get(provider, ""))
        if not has_key:
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


def synthesize(source_text: str, domain: str, difficulty: str, llm_cfg: dict,
               deadline: float | None = None, anonymize: bool = True) -> LLMCase:
    privacy = PRIVACY_ON if anonymize else PRIVACY_OFF
    prompt = (SYSTEM.format(domain=domain, difficulty=difficulty, privacy=privacy)
              + "\n\nSOURCE TEXT:\n" + source_text[:6000])
    return _run_providers(prompt, llm_cfg, deadline)


def synthesize_ideation(domain: str, difficulty: str, llm_cfg: dict, today: date,
                        deadline: float | None = None) -> LLMCase:
    """No-source ideation: a fresh scenario invented from a rotating theme seed.
    Always anonymised: ideation sheets are 'realistic problem' class (Honesty Rule)."""
    themes = DOMAIN_THEMES.get(domain) or ("plant utilities", "rotating equipment", "process line")
    theme = themes[today.toordinal() % len(themes)]
    prompt = IDEATION.format(domain=domain, difficulty=difficulty, theme=theme, privacy=PRIVACY_ON)
    return _run_providers(prompt, llm_cfg, deadline)
