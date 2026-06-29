"""View 6 - History (a chronological ledger of detected changes & alerts)."""

from __future__ import annotations

from collections import defaultdict

import streamlit as st

from core import alerts, config, data, ui

ui.masthead("History", "The Permanent Record")

changes = data.get_changes()
log = alerts.load_log()
alerted_ids = {e["change_id"] for e in log if e["status"] == "sent"}

# ── Filters / summary ────────────────────────────────────────────────────────
f1, f2 = st.columns([1, 3])
sev = f1.selectbox("Severity", ["All"] + list(config.SEVERITY.keys()),
                   format_func=lambda s: "All" if s == "All" else config.SEVERITY[s]["label"])
rows = changes if sev == "All" else [c for c in changes if c["severity"] == sev]

t1, t2, t3 = st.columns(3)
t1.markdown(ui.metric_tile("Total Detected", len(changes), "in the ledger"), unsafe_allow_html=True)
t2.markdown(ui.metric_tile("Alerts Logged", len(log), "send events"), unsafe_allow_html=True)
t3.markdown(ui.metric_tile("Showing", len(rows), "after filter"), unsafe_allow_html=True)

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

# ── Timeline grouped by detection day ────────────────────────────────────────
by_day: dict[str, list[dict]] = defaultdict(list)
for c in rows:
    by_day[c["detected_at"].strftime("%A · %d %B %Y")].append(c)

if not rows:
    st.info("Nothing matches this filter.")
else:
    for day, items in by_day.items():
        st.markdown(f'<div class="timeline-day">{day}</div>', unsafe_allow_html=True)
        for c in items:
            mark = '<span class="tl-alert">✉ ALERTED</span>' if c["id"] in alerted_ids else ""
            st.markdown(
                f"""
                <div class="timeline-row timeline-{c['severity']}">
                  <div class="tl-time">{c['detected_at'].strftime('%H:%M')}</div>
                  <div class="tl-body">
                    <div class="tl-headline">{c['flag']} {c['headline']}</div>
                    <div class="tl-meta">
                      {ui.severity_badge(c['severity'])}
                      <span class="chip">{c['country']}</span>
                      <span class="chip chip-quiet">{c['category']}</span>
                      {mark}
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

# ── Raw alert log ────────────────────────────────────────────────────────────
with st.expander("Full alert send log"):
    if not log:
        st.caption("No alerts have been sent yet.")
    else:
        import pandas as pd
        df = pd.DataFrame(log)[["sent_at", "status", "severity", "country", "headline", "recipient", "detail"]]
        df.columns = ["When", "Status", "Severity", "Country", "Headline", "To", "Detail"]
        st.dataframe(df, width='stretch', hide_index=True)

ui.footer()
