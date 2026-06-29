"""
Regulatory Change Intelligence Monitor (RCIM)
Entry point — defines the 6-page navigation.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

# Load .env (ANTHROPIC_API_KEY, GMAIL_*) if python-dotenv is installed.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from core import config, ui

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="expanded",
)

ui.load_css()  # global styles, applied before any view renders

# ── 6-page navigation ────────────────────────────────────────────────────────
pages = [
    st.Page("views/overview.py",     title="Overview",     icon=":material/dashboard:",     default=True),
    st.Page("views/change_feed.py",  title="Change Feed",  icon=":material/feed:"),
    st.Page("views/portals.py",      title="Portals",      icon=":material/satellite_alt:"),
    st.Page("views/ai_analysis.py",  title="AI Analysis",  icon=":material/smart_toy:"),
    st.Page("views/alert_center.py", title="Alert Center", icon=":material/notifications_active:"),
    st.Page("views/history.py",      title="History",      icon=":material/history:"),
    st.Page("views/settings.py",     title="Settings",     icon=":material/settings:"),
]

# Brand block above the nav
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-brand">
          <div class="sidebar-mark">◎ {config.APP_SHORT}</div>
          <div class="sidebar-full">{config.APP_NAME}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

nav = st.navigation(pages)
nav.run()
