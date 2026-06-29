"""
data.py
Loads sample data, computes live timestamps, and provides query helpers.
All Streamlit pages read data through this module so the storage format
can change later without touching the UI.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from core import config

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
NOW = datetime.now()


# ── Loaders ──────────────────────────────────────────────────────────────────
def _load_json(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def get_changes() -> list[dict]:
    """
    Return detected changes enriched with source metadata and live timestamps.
    Timestamps are derived from `hours_ago` so the feed always looks current.
    """
    raw = _load_json("sample_changes.json")
    enriched: list[dict] = []
    for c in raw:
        src = config.source_by_id(c["source_id"]) or {}
        detected = NOW - timedelta(hours=c["hours_ago"])
        effective = NOW + timedelta(days=c["effective_in_days"])
        enriched.append(
            {
                **c,
                "source_name": src.get("name", c["source_id"]),
                "country": src.get("country", "—"),
                "flag": src.get("flag", "🏳️"),
                "source_url": src.get("url", "#"),
                "detected_at": detected,
                "effective_at": effective,
                "severity_rank": config.severity_rank(c["severity"]),
                "severity_color": config.severity_color(c["severity"]),
            }
        )
    enriched.sort(key=lambda x: x["detected_at"], reverse=True)
    return enriched


def get_change(change_id: str) -> dict | None:
    return next((c for c in get_changes() if c["id"] == change_id), None)


def get_employees() -> pd.DataFrame:
    return pd.DataFrame(_load_json("sample_employees.json"))


# ── Affected-employee matching ───────────────────────────────────────────────
def affected_employees(change: dict) -> pd.DataFrame:
    """
    Heuristic match: an employee is 'affected' when the change country equals
    their host country. A simple, explainable rule that is easy to demo and
    easy to extend (e.g. add visa_type matching).
    """
    df = get_employees()
    if df.empty:
        return df
    matched = df[df["host"] == change["country"]].copy()
    matched["urgent"] = matched["assignment_end_days"] <= 120
    return matched.sort_values("assignment_end_days")


# ── Metrics for the dashboard ────────────────────────────────────────────────
def dashboard_metrics() -> dict:
    changes = get_changes()
    last_7d = [c for c in changes if c["detected_at"] >= NOW - timedelta(days=7)]
    critical = [c for c in changes if c["severity"] == "critical"]
    affected_total = 0
    for c in changes:
        affected_total += len(affected_employees(c))
    return {
        "sources": len(config.SOURCES),
        "changes_7d": len(last_7d),
        "critical": len(critical),
        "employees_affected": affected_total,
    }


# ── Aggregations for charts ──────────────────────────────────────────────────
def changes_by_country() -> pd.DataFrame:
    df = pd.DataFrame(get_changes())
    if df.empty:
        return df
    out = (
        df.groupby("country").size().reset_index(name="count").sort_values("count", ascending=True)
    )
    return out


def changes_by_category() -> pd.DataFrame:
    df = pd.DataFrame(get_changes())
    if df.empty:
        return df
    out = (
        df.groupby("category").size().reset_index(name="count").sort_values("count", ascending=True)
    )
    return out


# ── Display helpers ──────────────────────────────────────────────────────────
def humanize_age(dt: datetime) -> str:
    """Turn a datetime into 'wire service' relative text: '2h ago', '3d ago'."""
    delta = NOW - dt
    secs = delta.total_seconds()
    if secs < 3600:
        mins = max(1, int(secs // 60))
        return f"{mins}m ago"
    if secs < 86400:
        return f"{int(secs // 3600)}h ago"
    return f"{int(secs // 86400)}d ago"


def dateline(change: dict) -> str:
    """Reuters-style dateline: 'LONDON · 06:14 · UK HOME OFFICE'."""
    city = change["country"].upper()
    t = change["detected_at"].strftime("%H:%M")
    return f"{city} · {t}"
