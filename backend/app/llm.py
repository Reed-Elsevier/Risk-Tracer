"""Optional narrative generation over cited investigation evidence."""

from __future__ import annotations

import json
import re
from typing import Any

from app.models import ExplainResponse, Investigation


SOURCE_ID_PATTERN = re.compile(r"\b(?:INV|PAY|OWN|WL|IEX|PO|SUP|ENT|EMP)\d+\b")


def _evidence_payload(investigation: Investigation) -> dict[str, Any]:
    return {
        "invoice": investigation.invoice.model_dump(mode="json"),
        "supplier": investigation.supplier.model_dump(mode="json"),
        "entity": investigation.entity.model_dump(mode="json"),
        "signals": investigation.signals.model_dump(mode="json"),
        "evidence_brief": investigation.evidence_brief.model_dump(mode="json"),
    }


def _complete(prompt: str, *, api_key: str, model: str) -> str:
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if getattr(block, "text", None)).strip()


def request_narrative_account(payload: dict[str, Any], *, api_key: str, model: str) -> str:
    """Ask for a cited narrative and checklist. The caller decides whether to show them."""

    prompt = (
        "You are writing for a human invoice reviewer. Use only the counts in the JSON. "
        "Cite only ids listed in allowed_source_ids, even when other ids appear elsewhere in the JSON. "
        "Do not invent a count. Do not mention fraud, priority, High, Medium, No flagged signals, "
        "duplicate payment, or beneficial owner. Do not say hold the payment. "
        "Return only JSON, with no markdown fence, and two string keys: narrative and checklist. "
        "The narrative must be concise Markdown using exactly these sections: "
        "'## Case summary' with one short paragraph, "
        "'## Review points' with two to four bullet points, and "
        "'## Supplier history' with one to three bullet points. "
        "Use only level-two headings, plain paragraphs, and dash bullets; do not use tables or inline formatting. "
        "The checklist says what to verify and cites record ids. "
        "The checklist must not say escalate, clear, or needs more information.\n\n"
        f"Evidence JSON:\n{json.dumps(payload, ensure_ascii=False, default=str)}"
    )
    text = _complete(prompt, api_key=api_key, model=model)
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def explain_investigation(
    investigation: Investigation,
    *,
    api_key: str,
    model: str,
) -> ExplainResponse:
    """Ask the configured Anthropic model for a cited narrative, never a priority."""

    payload = _evidence_payload(investigation)
    prompt = (
        "Explain the evidence in this RiskTracer investigation for a human reviewer. "
        "Cite source IDs exactly as provided. Do not assign, recommend, or restate a review "
        "priority, do not conclude fraud, and do not use the phrases 'fraud score', "
        "'duplicate payment', or 'beneficial owner'. Return a short factual narrative.\n\n"
        f"Evidence JSON:\n{json.dumps(payload, ensure_ascii=False)}"
    )
    narrative = _complete(prompt, api_key=api_key, model=model)
    allowed_ids = {
        source_id
        for sentence in investigation.evidence_brief.sentences
        for source_id in sentence.source_ids
    }
    cited_ids = [source_id for source_id in SOURCE_ID_PATTERN.findall(narrative) if source_id in allowed_ids]
    return ExplainResponse(narrative=narrative.strip(), source_ids=list(dict.fromkeys(cited_ids)))
