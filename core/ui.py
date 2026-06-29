"""
ui.py
Reusable presentation components. Keeps the pages declarative and consistent.
The visual identity ('intelligence wire service') lives here and in style.css.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from core import config, data

ASSETS = Path(__file__).resolve().parent.parent / "assets"


# ── Global setup ─────────────────────────────────────────────────────────────
def load_css() -> None:
    """Inject Google Fonts + the custom stylesheet once per page."""
    css = (ASSETS / "style.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def setup(section: str, kicker: str) -> None:
    """Per-page setup: inject CSS and render the masthead. Call at top of each view."""
    load_css()
    masthead(section, kicker)


def masthead(section: str, kicker: str) -> None:
    """Bulletin-style header: brand, section name, and a live dateline."""
    today = data.NOW.strftime("%A, %d %B %Y · %H:%M")
    st.markdown(
        f"""
        <div class="masthead">
          <div class="masthead-top">
            <span class="brand">◎ {config.APP_SHORT}</span>
            <span class="masthead-date">{today}</span>
          </div>
          <div class="masthead-rule"></div>
          <div class="masthead-bottom">
            <div>
              <div class="kicker">{kicker}</div>
              <h1 class="section-title">{section}</h1>
            </div>
            <span class="edition">GLOBAL MOBILITY EDITION</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Atoms ────────────────────────────────────────────────────────────────────
def severity_badge(severity: str) -> str:
    meta = config.SEVERITY.get(severity, {})
    label = meta.get("label", severity.title())
    return f'<span class="badge badge-{severity}">{label}</span>'


def metric_tile(label: str, value, sub: str = "") -> str:
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    return f"""
      <div class="metric">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {sub_html}
      </div>
    """


def dispatch_card(change: dict, affected_count: int) -> str:
    """A single change rendered as a wire-service dispatch."""
    badge = severity_badge(change["severity"])
    age = data.humanize_age(change["detected_at"])
    line = data.dateline(change)
    eff = change["effective_at"].strftime("%d %b %Y")
    return f"""
      <div class="dispatch dispatch-{change['severity']}">
        <div class="dispatch-head">
          <span class="dateline">{change['flag']} {line}</span>
          <span class="age">{age}</span>
        </div>
        <div class="dispatch-headline">{change['headline']}</div>
        <div class="dispatch-meta">
          {badge}
          <span class="chip">{change['category']}</span>
          <span class="chip chip-quiet">Effective {eff}</span>
          <span class="chip chip-quiet">{affected_count} affected</span>
        </div>
        <div class="dispatch-summary">{change['summary']}</div>
        <div class="dispatch-source">SOURCE — {change['source_name']}</div>
      </div>
    """


def footer() -> None:
    st.markdown(
        f"""
        <div class="footer">
          {config.APP_NAME} v{config.APP_VERSION} · Built by {config.AUTHOR} ·
          Weekend Build Series · Sample data for demonstration
        </div>
        """,
        unsafe_allow_html=True,
    )
