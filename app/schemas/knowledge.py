"""Pydantic schemas for knowledge retrieval."""

from typing import Literal

from pydantic import BaseModel, Field


class PolicyDocument(BaseModel):
    """Parsed policy section from the knowledge base document."""

    intent: str
    policy_id: str
    category: str
    audience: str = "student"
    route: str
    status: str = "active"
    version: str = "1.0"
    effective_from: str = ""
    region: str = "global_default"
    priority: str = "high"
    source_type: str = "internal_policy"
    confidentiality: str = "student_safe"
    keywords: list[str] = Field(default_factory=list)
    purpose: str = ""
    core_rules: list[str] = Field(default_factory=list)
    agent_behavior: list[str] = Field(default_factory=list)
    grounding_scenarios: list[str] = Field(default_factory=list)


class KnowledgeChunk(BaseModel):
    """A semantic chunk ready for embedding and storage."""

    chunk_id: str
    policy_id: str
    document_type: str = "policy"
    intent: str
    category: str
    audience: str
    route: str
    status: str
    version: str
    section: str
    text: str
    keywords: list[str] = Field(default_factory=list)


class EvidenceChunk(BaseModel):
    """A retrieved evidence chunk returned by hybrid search."""

    chunk_id: str
    policy_id: str
    intent: str
    category: str
    audience: str
    status: str
    section: str
    text: str
    score: float
    source: Literal["bm25", "vector", "hybrid"]
