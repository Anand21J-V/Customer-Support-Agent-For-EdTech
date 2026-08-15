"""Parse the student policy knowledge base DOCX into structured policies."""

from __future__ import annotations

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from app.schemas.knowledge import PolicyDocument

SECTION_HEADING_RE = re.compile(r"^\d+\.\s+(?P<intent>[a-z_]+)$")
SUBSECTION_LABELS = {
    "Policy purpose": "purpose",
    "Core policy rules": "core_rules",
    "Agent behavior": "agent_behavior",
    "Grounding scenarios": "grounding_scenarios",
    "RAG metadata": "rag_metadata",
}
METADATA_KEYS = {
    "policy_id",
    "intent",
    "category",
    "audience",
    "primary_route",
    "status",
    "version",
    "effective_from",
    "region",
    "priority",
    "source_type",
    "confidentiality",
    "action_allowed",
    "escalation_required",
    "keywords",
    "dataset_rows",
}
SKIP_LINES = {"Metadata", "Value", "Scenario", "Expected behavior"}


def _read_docx_paragraphs(docx_path: Path) -> list[str]:
    with zipfile.ZipFile(docx_path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))

    word_ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[str] = []
    for paragraph in root.iter(f"{word_ns}p"):
        texts = [node.text or "" for node in paragraph.iter(f"{word_ns}t")]
        line = "".join(texts).strip()
        if line:
            paragraphs.append(line)
    return paragraphs


def _parse_metadata(lines: list[str]) -> dict[str, str]:
    metadata: dict[str, str] = {}
    index = 0
    while index < len(lines):
        key = lines[index]
        if key == "Policy purpose":
            break
        if key in METADATA_KEYS and index + 1 < len(lines):
            metadata[key] = lines[index + 1]
            index += 2
            continue
        index += 1
    return metadata


def _parse_keywords(raw_value: str) -> list[str]:
    return [part.strip() for part in raw_value.split(",") if part.strip()]


def _parse_subsections(lines: list[str]) -> dict[str, list[str] | str]:
    sections: dict[str, list[str] | str] = {
        "purpose": "",
        "core_rules": [],
        "agent_behavior": [],
        "grounding_scenarios": [],
    }
    current_label: str | None = None
    current_items: list[str] = []

    def flush() -> None:
        nonlocal current_label, current_items
        if not current_label:
            return
        if current_label == "purpose":
            sections["purpose"] = " ".join(current_items).strip()
        else:
            sections[current_label] = list(current_items)
        current_label = None
        current_items = []

    for line in lines:
        if line in SUBSECTION_LABELS:
            flush()
            mapped = SUBSECTION_LABELS[line]
            if mapped == "rag_metadata":
                current_label = None
                current_items = []
                continue
            current_label = mapped
            current_items = []
            continue

        if line.startswith("{") and "policy_id" in line:
            continue
        if line in SKIP_LINES:
            continue
        if current_label:
            current_items.append(line)

    flush()
    return sections


def parse_policy_docx(docx_path: str | Path) -> list[PolicyDocument]:
    """Parse all numbered policy sections from the DOCX knowledge base."""
    path = Path(docx_path)
    if not path.exists():
        raise FileNotFoundError(f"Knowledge base DOCX not found: {path}")

    paragraphs = _read_docx_paragraphs(path)
    section_starts: list[tuple[int, str]] = []
    for index, line in enumerate(paragraphs):
        match = SECTION_HEADING_RE.match(line)
        if match:
            section_starts.append((index, match.group("intent")))

    if len(section_starts) != 20:
        raise ValueError(f"Expected 20 policy sections, found {len(section_starts)}")

    policies: list[PolicyDocument] = []
    for section_index, (start, intent) in enumerate(section_starts):
        end = section_starts[section_index + 1][0] if section_index + 1 < len(section_starts) else len(paragraphs)
        body = paragraphs[start + 1 : end]
        metadata = _parse_metadata(body)
        subsections = _parse_subsections(body)

        policy_id = metadata.get("policy_id", "")
        if not policy_id:
            raise ValueError(f"Missing policy_id for intent '{intent}'")

        policies.append(
            PolicyDocument(
                intent=metadata.get("intent", intent),
                policy_id=policy_id,
                category=metadata.get("category", ""),
                audience=metadata.get("audience", "student"),
                route=metadata.get("primary_route", ""),
                status=metadata.get("status", "active"),
                version=metadata.get("version", "1.0"),
                effective_from=metadata.get("effective_from", ""),
                region=metadata.get("region", "global_default"),
                priority=metadata.get("priority", "high"),
                source_type=metadata.get("source_type", "internal_policy"),
                confidentiality=metadata.get("confidentiality", "student_safe"),
                keywords=_parse_keywords(metadata.get("keywords", "")),
                purpose=str(subsections.get("purpose", "")),
                core_rules=list(subsections.get("core_rules", [])),
                agent_behavior=list(subsections.get("agent_behavior", [])),
                grounding_scenarios=list(subsections.get("grounding_scenarios", [])),
            )
        )

    return policies


def validate_policies(policies: list[PolicyDocument]) -> None:
    """Run quality checks before embedding."""
    if len(policies) != 20:
        raise ValueError(f"Expected 20 policies, found {len(policies)}")

    intents = {policy.intent for policy in policies}
    if len(intents) != 20:
        raise ValueError("Duplicate or missing intents detected in parsed policies")

    for policy in policies:
        if not policy.policy_id.startswith("POL-"):
            raise ValueError(f"Invalid policy_id: {policy.policy_id}")
        if not policy.purpose and not policy.core_rules:
            raise ValueError(f"Policy {policy.policy_id} has no purpose or core rules")
        blob = json.dumps(policy.model_dump())
        if "TODO" in blob or "PLACEHOLDER" in blob.upper():
            raise ValueError(f"Unresolved placeholder text in {policy.policy_id}")
