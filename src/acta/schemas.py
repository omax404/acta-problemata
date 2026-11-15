"""Pydantic v2 models. The LLM-facing schema deliberately uses arrays of
{name, value} objects instead of open maps: Gemini's structured-output
subset rejects additionalProperties. Maps are built internally afterwards.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

DOMAINS = ("Mechanical", "Aerospace", "Electrical", "Chemical",
           "Civil", "Thermal", "Materials", "Fluids")
DIFFICULTIES = ("Foundational", "Intermediate", "Advanced")
DIAGRAM_KINDS = ("cantilever_point_load", "thermal_wall", "pipe_flow",
                 "crack_plate", "voltage_divider", "column_buckling")


class Domain(StrEnum):
    mechanical = "Mechanical"; aerospace = "Aerospace"; electrical = "Electrical"
    chemical = "Chemical"; civil = "Civil"; thermal = "Thermal"
    materials = "Materials"; fluids = "Fluids"


class NameValue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=60)
    value: str = Field(min_length=1, max_length=60)


class Variable(BaseModel):
    model_config = ConfigDict(extra="forbid")
    symbol: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]{0,15}$")
    value: float


class FormulaIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    symbolic: str = Field(min_length=3, max_length=400)
    variables: list[Variable] = Field(min_length=1, max_length=12)
    unit: str = Field(min_length=1, max_length=24)


class DiagramIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["cantilever_point_load", "thermal_wall", "pipe_flow",
                  "crack_plate", "voltage_divider", "column_buckling"]
    params: list[Variable] = Field(default_factory=list, max_length=8)
    caption: str = Field(min_length=4, max_length=120)


class LLMCase(BaseModel):
    """The six FR-02 entities + diagram spec. This is the AI's only output."""
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=8, max_length=80)
    domain: Domain
    narrative: str = Field(min_length=200, max_length=1200)
    boundary_conditions: list[NameValue] = Field(min_length=3, max_length=8)
    formula: FormulaIn
    challenge_question: str = Field(min_length=20, max_length=300)
    diagram: DiagramIn

    @field_validator("title")
    @classmethod
    def _title_words(cls, v: str) -> str:
        if len(v.split()) > 10:
            raise ValueError("title must be at most 10 words")
        return v

    @field_validator("narrative")
    @classmethod
    def _narrative_words(cls, v: str) -> str:
        n = len(v.split())
        if not 120 <= n <= 150:
            raise ValueError(f"narrative must be 120-150 words, got {n}")
        return v


def gemini_response_schema(model: type[BaseModel]) -> dict:
    """Inline $refs and strip keys outside Gemini's supported JSON-Schema subset."""
    raw = model.model_json_schema()
    defs = raw.get("$defs", {})
    keep = {"type", "properties", "items", "required", "enum", "anyOf"}

    def resolve(node):
        if isinstance(node, dict):
            if "$ref" in node:
                return resolve(defs[node["$ref"].rsplit("/", 1)[-1]])
            return {k: resolve(v) for k, v in node.items() if k in keep}
        if isinstance(node, list):
            return [resolve(x) for x in node]
        return node

    return resolve(raw)
