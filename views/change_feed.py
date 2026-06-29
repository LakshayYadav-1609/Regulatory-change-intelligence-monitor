"""View 2 - Change Feed (the full wire of detected changes)."""

from __future__ import annotations

import streamlit as st

from core import config, data, ui

ui.masthead("Change Feed", "Every Dispatch, Newest First")

changes = data.get_changes()

f1, f2, f3 = st.columns(3)
sev = f1.multiselect("Severity", list(config.SEVERITY.keys()),
                     format_func=lambda s: config.SEVERITY[s]["label"])
country = f2.multiselect("Country", sorted({c["country"] for c in changes}))
category = f3.multiselect("Category", config.CATEGORIES)

filtered = changes
if sev:
    filtered = [c for c in filtered if c["severity"] in sev]
if country:
    filtered = [c for c in filtered if c["country"] in country]
if category:
    filtered = [c for c in filtered if c["category"] in category]

st.markdown(f'<div class="brief-label">{len(filtered)} dispatch(es)</div>', unsafe_allow_html=True)

if not filtered:
    st.info("No dispatches match these filters. Clear a filter to see more.")
else:
    for change in filtered:
        st.markdown(ui.dispatch_card(change, len(data.affected_employees(change))), unsafe_allow_html=True)
        with st.expander(f"Read the rule text & source · {change['id']}"):
            st.markdown("**Change excerpt**")
            st.markdown(f"> {change['change_excerpt']}")
            st.markdown(
                f"**Tags:** {', '.join(change['tags'])}  \n"
                f"**Effective:** {change['effective_at'].strftime('%d %B %Y')}  \n"
                f"**Source:** [{change['source_name']}]({change['source_url']})"
            )

ui.footer()
