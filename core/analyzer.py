"""
analyzer.py
Turns a detected regulatory change + affected employees into an impact brief.

Two modes:
  1. AI mode  — uses the Anthropic API when ANTHROPIC_API_KEY is set.
  2. Rule mode — a deterministic fallback so the app always works in a demo,
                 even with no key and no internet.
"""

from __future__ import annotations

import json
import os

import pandas as pd

MODEL = "claude-sonnet-4-6"


def has_api_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


# ── Public entry point ───────────────────────────────────────────────────────
def analyze_impact(change: dict, employees: pd.DataFrame) -> dict:
    """
    Return a structured impact brief:
      { 'summary': str, 'risk_level': str, 'actions': [str], 'source': 'ai'|'rule' }
    Falls back to rule-based analysis on any error.
    """
    if has_api_key():
        try:
            return _ai_analysis(change, employees)
        except Exception as exc:  # noqa: BLE001 - demo should never hard-crash
            result = _rule_analysis(change, employees)
            result["note"] = f"AI call failed, used rule-based fallback ({exc.__class__.__name__})."
            return result
    return _rule_analysis(change, employees)


# ── AI mode ──────────────────────────────────────────────────────────────────
def _ai_analysis(change: dict, employees: pd.DataFrame) -> dict:
    import anthropic

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

    roster = employees[
        ["name", "host", "visa_type", "assignment_end_days", "dependents"]
    ].to_dict("records") if not employees.empty else []

    prompt = f"""You are a global mobility compliance analyst. A government regulatory
change has been detected. Assess its impact on the affected employee population.

CHANGE
- Headline: {change['headline']}
- Country: {change['country']}
- Category: {change['category']}
- Effective in: {change['effective_in_days']} days
- Summary: {change['summary']}

AFFECTED EMPLOYEES ({len(roster)})
{json.dumps(roster, indent=2)}

Respond with ONLY a JSON object, no markdown, in this exact shape:
{{
  "summary": "2-3 sentence executive impact statement",
  "risk_level": "Critical | High | Medium | Low",
  "actions": ["action 1", "action 2", "action 3"]
}}"""

    resp = client.messages.create(
        model=MODEL,
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(block.text for block in resp.content if block.type == "text")
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(text)
    data["source"] = "ai"
    return data


# ── Rule mode (fallback) ─────────────────────────────────────────────────────
def _rule_analysis(change: dict, employees: pd.DataFrame) -> dict:
    n = len(employees)
    urgent = int((employees["assignment_end_days"] <= 120).sum()) if n else 0
    sev = change["severity"]

    risk_map = {"critical": "Critical", "high": "High", "medium": "Medium", "low": "Low"}
    risk = risk_map.get(sev, "Medium")
    if urgent >= 2 and risk in ("Medium", "Low"):
        risk = "High"

    if n == 0:
        summary = (
            f"{change['headline']} takes effect in {change['effective_in_days']} days. "
            f"No employees in {change['country']} are currently impacted, but monitor new assignments."
        )
        actions = ["No immediate population impact — keep on watch list."]
    else:
        summary = (
            f"{change['headline']} affects {n} employee(s) in {change['country']}, "
            f"of whom {urgent} have an assignment ending within 120 days. "
            f"Takes effect in {change['effective_in_days']} days — action window is limited."
        )
        actions = [
            f"Review {n} affected case(s) in {change['country']} against the new {change['category'].lower()} rule.",
            "Confirm whether any in-flight or upcoming filings must be re-priced or re-submitted.",
            "Notify the regional mobility lead and flag urgent assignment-end cases first.",
        ]

    return {"summary": summary, "risk_level": risk, "actions": actions, "source": "rule"}


# ── Natural-language Q&A over the change feed ────────────────────────────────
def ask_about_changes(question: str, changes: list[dict]) -> dict:
    """
    Answer a free-text question about the detected changes using Claude.
    Returns { 'answer': str, 'source': 'ai'|'rule' }.
    """
    if not has_api_key():
        return {
            "answer": "AI Q&A needs an Anthropic API key. Add ANTHROPIC_API_KEY to your .env "
                      "to ask free-text questions about the feed.",
            "source": "rule",
        }
    try:
        import anthropic

        client = anthropic.Anthropic()
        context = [
            {
                "headline": c["headline"],
                "country": c["country"],
                "category": c["category"],
                "severity": c["severity"],
                "effective_in_days": c["effective_in_days"],
                "summary": c["summary"],
            }
            for c in changes
        ]
        prompt = f"""You are a global mobility regulatory analyst. Answer the user's question
using ONLY the detected changes below. Be concise and specific. If the answer is not in
the data, say so.

DETECTED CHANGES:
{json.dumps(context, indent=2)}

QUESTION: {question}"""
        resp = client.messages.create(
            model=MODEL,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = "".join(b.text for b in resp.content if b.type == "text").strip()
        return {"answer": answer, "source": "ai"}
    except Exception as exc:  # noqa: BLE001
        return {"answer": f"AI call failed ({exc.__class__.__name__}). Check your API key and connection.",
                "source": "rule"}
