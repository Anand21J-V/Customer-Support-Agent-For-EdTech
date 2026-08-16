"""Pydantic schemas for LLM structured output."""

from typing import Literal

from pydantic import BaseModel, Field


class DemoClassification(BaseModel):
    """Phase 3 demo schema for validated structured Gemini output."""

    intent: Literal["refund", "payment", "enrollment", "other"]
    confidence: float = Field(ge=0, le=1)
    summary: str
