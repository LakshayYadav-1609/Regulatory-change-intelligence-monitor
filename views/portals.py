"""View 3 - Portals (the government & regulatory portals being watched)."""

from __future__ import annotations

import streamlit as st

from core import config, ui

ui.masthead("Portals", "The Watch List")

countries = ["All countries"] + sorted({s["country"] for s in config.SOURCES})
cats = ["All categories"] + config.CATEGORIES

f1, f2, f3 = st.columns([1, 1, 2])
country = f1.selectbox("Country", countries)
category = f2.selectbox("Category", cats)
query = f3.text_input("Search", placeholder="Search portal name…")

rows = config.SOURCES
if country != "All countries":
    rows = [s for s in rows if s["country"] == country]
if category != "All categories":
    rows = [s for s in rows if s["category"] == category]
if query:
    rows = [s for s in rows if query.lower() in s["name"].lower()]

st.markdown(
    f'<div class="brief-label">{len(rows)} of {len(config.SOURCES)} portals · '
    f'<span style="color:var(--emerald)">all active</span></div>',
    unsafe_allow_html=True,
)

cols = st.columns(2)
for i, s in enumerate(rows):
    with cols[i % 2]:
        st.markdown(
            f"""
            <div class="source-card">
              <div style="display:flex; align-items:center;">
                <span class="source-flag">{s['flag']}</span>
                <div>
                  <div class="source-name">{s['name']}</div>
                  <div class="source-country">{s['country'].upper()} · {s['category'].upper()}</div>
                </div>
              </div>
              <div style="text-align:right; white-space:nowrap;">
                <span class="status-dot"></span><span class="status-text">ACTIVE</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
with st.expander("How live monitoring works"):
    st.markdown(
        "Each portal is polled on a schedule. RCIM stores a fingerprint (hash) of the "
        "page's visible text. When the fingerprint changes, the page has changed and a "
        "candidate dispatch is raised. The engine lives in `core/scraper.py` - enable it "
        "when ready, and always respect each site's robots.txt and rate limits."
    )

ui.footer()
