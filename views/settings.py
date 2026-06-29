"""View 7 - Settings (configuration status & how to wire up live features)."""

from __future__ import annotations

import os

import streamlit as st

from core import alerts, analyzer, config, ui

ui.masthead("Settings", "Configuration & Status")

ai_ok = analyzer.has_api_key()
mail_ok = alerts.email_configured()
recipient = alerts.default_recipient()

# ── System status ────────────────────────────────────────────────────────────
st.markdown('<div class="brief-label">System status</div>', unsafe_allow_html=True)
s1, s2, s3 = st.columns(3)
s1.markdown(ui.metric_tile("Portals", len(config.SOURCES), "configured & active"), unsafe_allow_html=True)
s2.markdown(ui.metric_tile("AI Engine", "ON" if ai_ok else "OFF",
                           "Anthropic key found" if ai_ok else "no key - using rules"),
            unsafe_allow_html=True)
s3.markdown(ui.metric_tile("Email Alerts", "ARMED" if mail_ok else "OFF",
                           "Gmail configured" if mail_ok else "not configured"),
            unsafe_allow_html=True)

st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

# ── Environment keys ─────────────────────────────────────────────────────────
st.markdown('<div class="brief-label">Environment keys</div>', unsafe_allow_html=True)
st.markdown(
    "RCIM reads secrets from environment variables - never hard-code them. "
    "Copy `.env.example` to `.env`, fill in your keys, then restart the app."
)
st.code(
    "ANTHROPIC_API_KEY=sk-ant-...        # AI Analysis page\n"
    "GMAIL_ADDRESS=you@gmail.com         # Alert Center - sender\n"
    "GMAIL_APP_PASSWORD=16-char-app-pass # NOT your normal password\n"
    "ALERT_RECIPIENT=team@company.com    # default alert recipient",
    language="bash",
)

# live read-out of what is currently detected (values hidden for safety)
def _mask(v: str) -> str:
    return "✓ set" if v else "✗ not set"

c1, c2 = st.columns(2)
with c1:
    st.markdown(
        f"""
        <div class="source-card"><div><div class="source-name">ANTHROPIC_API_KEY</div>
        <div class="source-country">{_mask(os.environ.get('ANTHROPIC_API_KEY',''))}</div></div></div>
        <div class="source-card"><div><div class="source-name">GMAIL_ADDRESS</div>
        <div class="source-country">{_mask(os.environ.get('GMAIL_ADDRESS',''))}</div></div></div>
        """, unsafe_allow_html=True)
with c2:
    st.markdown(
        f"""
        <div class="source-card"><div><div class="source-name">GMAIL_APP_PASSWORD</div>
        <div class="source-country">{_mask(os.environ.get('GMAIL_APP_PASSWORD',''))}</div></div></div>
        <div class="source-card"><div><div class="source-name">ALERT_RECIPIENT</div>
        <div class="source-country">{recipient if recipient else '✗ not set'}</div></div></div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

# ── Monitoring cadence (illustrative) ────────────────────────────────────────
st.markdown('<div class="brief-label">Monitoring cadence</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
col1.select_slider("Check portals every", options=["1h", "3h", "6h", "12h", "24h"], value="6h")
col2.multiselect("Alert me on", ["Critical", "High", "Medium", "Low"], default=["Critical", "High"])
st.caption(
    "In the app these controls are illustrative. For real scheduling, run `auto_alert.py` "
    "via cron / Task Scheduler / GitHub Actions - see the Alert Center page for the exact commands."
)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
with st.expander("About this build"):
    st.markdown(
        f"**{config.APP_NAME}** ({config.APP_SHORT})  \n"
        f"{config.APP_TAGLINE}  \n"
        f"Version {config.APP_VERSION} · Built by {config.AUTHOR}  \n\n"
        "Part of the Weekend Build Series. Sample data is used for demonstration; "
        "swap in the live scraper (`core/scraper.py`) and your own employee dataset to run it for real."
    )

ui.footer()
