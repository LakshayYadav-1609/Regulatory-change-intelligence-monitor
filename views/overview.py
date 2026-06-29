"""View 1 - Overview (command center)."""

from __future__ import annotations

import streamlit as st

from core import alerts, analyzer, charts, data, ui

ui.masthead("Overview", "Live Intelligence Feed")

# ── Hero strip ───────────────────────────────────────────────────────────────
ai_on = analyzer.has_api_key()
mail_on = alerts.email_configured()
st.markdown(
    f"""
    <div class="hero">
      <div class="hero-line">Watching <b>22</b> government portals across <b>18</b> jurisdictions.
      A silent rule change is caught and impact-assessed in <b>hours</b>, not weeks.</div>
      <div class="hero-status">
        <span class="pill {'pill-on' if ai_on else 'pill-off'}">AI {'ONLINE' if ai_on else 'OFFLINE'}</span>
        <span class="pill {'pill-on' if mail_on else 'pill-off'}">EMAIL {'ARMED' if mail_on else 'OFF'}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Metrics ──────────────────────────────────────────────────────────────────
m = data.dashboard_metrics()
c1, c2, c3, c4 = st.columns(4)
c1.markdown(ui.metric_tile("Sources Monitored", m["sources"], "across 18 jurisdictions"), unsafe_allow_html=True)
c2.markdown(ui.metric_tile("Changes · 7 days", m["changes_7d"], "detected automatically"), unsafe_allow_html=True)
c3.markdown(ui.metric_tile("Critical Alerts", m["critical"], "need action now"), unsafe_allow_html=True)
c4.markdown(ui.metric_tile("Employees Affected", m["employees_affected"], "across active cases"), unsafe_allow_html=True)

st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

# ── Latest dispatches + charts ───────────────────────────────────────────────
left, right = st.columns([1.7, 1])
with left:
    st.markdown('<div class="brief-label">Latest dispatches</div>', unsafe_allow_html=True)
    for change in data.get_changes()[:4]:
        st.markdown(ui.dispatch_card(change, len(data.affected_employees(change))), unsafe_allow_html=True)
    st.caption("Open **Change Feed** for the full wire.")

with right:
    st.markdown('<div class="brief-label">Changes by category</div>', unsafe_allow_html=True)
    st.plotly_chart(charts.donut(data.changes_by_category(), "category", "count"),
                    width='stretch', config={"displayModeBar": False})
    st.markdown('<div class="brief-label">Changes by country</div>', unsafe_allow_html=True)
    st.plotly_chart(charts.horizontal_bar(data.changes_by_country(), "country", "count"),
                    width='stretch', config={"displayModeBar": False})

ui.footer()
