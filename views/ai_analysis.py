"""View 4 - AI Analysis (impact briefs + natural-language Q&A via Claude)."""

from __future__ import annotations

import streamlit as st

from core import analyzer, data, ui

ui.masthead("AI Analysis", "Who It Hits, And What To Do")

mode = "Claude (Anthropic)" if analyzer.has_api_key() else "Rule-based (no API key set)"
st.caption(f"Engine: **{mode}** - set `ANTHROPIC_API_KEY` in `.env` to use Claude.")

tab_impact, tab_ask = st.tabs(["⚖️  Impact brief", "💬  Ask the feed"])

# ── Tab 1: per-change impact brief ───────────────────────────────────────────
with tab_impact:
    changes = data.get_changes()
    labels = {f"{c['flag']}  {c['headline']}": c["id"] for c in changes}
    choice = st.selectbox("Select a detected change", list(labels.keys()))
    change = data.get_change(labels[choice])

    affected = data.affected_employees(change)
    st.markdown(ui.dispatch_card(change, len(affected)), unsafe_allow_html=True)

    st.markdown('<div class="brief-label">Affected employees</div>', unsafe_allow_html=True)
    if affected.empty:
        st.info(f"No employees currently in {change['country']}. This change is on watch only.")
    else:
        show = affected[["emp_id", "name", "host", "visa_type", "salary_local",
                         "currency", "assignment_end_days", "dependents", "urgent"]].rename(
            columns={"emp_id": "ID", "name": "Employee", "host": "Host", "visa_type": "Visa",
                     "salary_local": "Salary", "currency": "Cur",
                     "assignment_end_days": "Days left", "dependents": "Deps", "urgent": "Urgent"})
        st.dataframe(show, width='stretch', hide_index=True)

    if st.button("Generate impact brief", type="primary"):
        with st.spinner("Assessing impact across the affected population…"):
            brief = analyzer.analyze_impact(change, affected)
        tag = "tag-ai" if brief["source"] == "ai" else "tag-rule"
        tag_text = "CLAUDE" if brief["source"] == "ai" else "RULE-BASED"
        actions_html = "".join(
            f'<div class="brief-action"><span class="brief-num">{i+1:02d}</span><span>{a}</span></div>'
            for i, a in enumerate(brief["actions"]))
        st.markdown(
            f"""
            <div class="brief">
              <div class="brief-label">Executive impact brief
                <span class="brief-tag {tag}">{tag_text}</span>
                <span class="brief-tag tag-rule">RISK: {brief['risk_level'].upper()}</span>
              </div>
              <div class="brief-summary">{brief['summary']}</div>
              <div style="height:1rem"></div>
              <div class="brief-label">Recommended actions</div>
              {actions_html}
            </div>
            """, unsafe_allow_html=True)
        if brief.get("note"):
            st.caption(brief["note"])

# ── Tab 2: ask anything about the feed ───────────────────────────────────────
with tab_ask:
    st.markdown('<div class="brief-label">Ask a question about the detected changes</div>',
                unsafe_allow_html=True)
    examples = [
        "Which changes affect salary thresholds and when do they take effect?",
        "What's the most urgent change for UK employees?",
        "Summarise everything happening in the next 30 days.",
    ]
    pick = st.selectbox("Example questions", ["- write your own -"] + examples)
    default_q = "" if pick == "- write your own -" else pick
    question = st.text_area("Your question", value=default_q, height=90,
                            placeholder="e.g. Which countries raised salary thresholds this week?")

    if st.button("Ask", type="primary"):
        if not question.strip():
            st.warning("Type a question first.")
        else:
            with st.spinner("Claude is reading the feed…"):
                res = analyzer.ask_about_changes(question, data.get_changes())
            tag = "tag-ai" if res["source"] == "ai" else "tag-rule"
            tag_text = "CLAUDE" if res["source"] == "ai" else "RULE-BASED"
            st.markdown(
                f"""
                <div class="brief">
                  <div class="brief-label">Answer <span class="brief-tag {tag}">{tag_text}</span></div>
                  <div class="brief-summary" style="white-space:pre-wrap">{res['answer']}</div>
                </div>
                """, unsafe_allow_html=True)

ui.footer()
