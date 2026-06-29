"""View 5 - Alert Center (Gmail email alerts: configure, send, log)."""

from __future__ import annotations

import streamlit as st

from core import alerts, config, data, ui

ui.masthead("Alert Center", "Auto Email Alerts")

mail_on = alerts.email_configured()
recipient_default = alerts.default_recipient()

# ── Status ───────────────────────────────────────────────────────────────────
s1, s2 = st.columns(2)
s1.markdown(
    ui.metric_tile("Email Engine", "ARMED" if mail_on else "OFF",
                   "Gmail configured" if mail_on else "set GMAIL_ADDRESS + APP_PASSWORD"),
    unsafe_allow_html=True)
sent_count = sum(1 for e in alerts.load_log() if e["status"] == "sent")
s2.markdown(ui.metric_tile("Alerts Sent", sent_count, "all time"), unsafe_allow_html=True)

if not mail_on:
    st.warning(
        "Email is not configured yet. Add these to your `.env`, then restart the app:\n\n"
        "`GMAIL_ADDRESS=you@gmail.com`  ·  `GMAIL_APP_PASSWORD=16-char-app-password`  ·  "
        "`ALERT_RECIPIENT=team@company.com`\n\n"
        "App Password is created at https://myaccount.google.com/apppasswords "
        "(needs 2-Step Verification on)."
    )

st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

# ── Controls ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])
recipient = col1.text_input("Send alerts to", value=recipient_default,
                            placeholder="team@company.com")
threshold = col2.selectbox(
    "Minimum severity", list(config.SEVERITY.keys()),
    index=list(config.SEVERITY.keys()).index(config.DEFAULT_ALERT_SEVERITY),
    format_func=lambda s: config.SEVERITY[s]["label"])

min_rank = config.severity_rank(threshold)
changes = data.get_changes()
qualifying = [c for c in changes if c["severity_rank"] >= min_rank]

# ── Pending list ─────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="brief-label">{len(qualifying)} change(s) at or above '
    f'{config.SEVERITY[threshold]["label"]} severity</div>', unsafe_allow_html=True)

for c in qualifying:
    done = alerts.already_alerted(c["id"])
    state = ('<span class="status-text">SENT</span>' if done
             else '<span style="color:var(--amber);font-family:var(--mono);font-size:0.68rem;">PENDING</span>')
    st.markdown(
        f"""
        <div class="source-card">
          <div style="display:flex;align-items:center;">
            <span class="source-flag">{c['flag']}</span>
            <div>
              <div class="source-name">{c['headline']}</div>
              <div class="source-country">{c['country'].upper()} · {config.SEVERITY[c['severity']]['label'].upper()}</div>
            </div>
          </div>
          <div style="white-space:nowrap;">{state}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Action buttons ───────────────────────────────────────────────────────────
b1, b2 = st.columns(2)
if b1.button("Send test email", width='stretch'):
    if not recipient:
        st.warning("Enter a recipient first.")
    else:
        with st.spinner("Sending test email…"):
            r = alerts.send_test(recipient)
        if r["status"] == "test":
            st.success(f"Test email sent to {recipient}. Check the inbox.")
        else:
            st.error(f"Failed: {r['detail']}")

if b2.button("Send pending alerts", type="primary", width='stretch'):
    if not recipient:
        st.warning("Enter a recipient first.")
    else:
        pending = [c for c in qualifying if not alerts.already_alerted(c["id"])]
        if not pending:
            st.info("Nothing pending - all qualifying changes were already alerted.")
        else:
            ok, fail = 0, 0
            with st.spinner(f"Sending {len(pending)} alert(s)…"):
                for c in pending:
                    r = alerts.send_alert(c, len(data.affected_employees(c)), recipient)
                    ok += r["status"] == "sent"
                    fail += r["status"] == "failed"
            if ok:
                st.success(f"Sent {ok} alert(s) to {recipient}.")
            if fail:
                st.error(f"{fail} failed - see the log below for details.")
            st.rerun()

# ── Recent log ───────────────────────────────────────────────────────────────
st.markdown('<div class="brief-label">Recent alert activity</div>', unsafe_allow_html=True)
log = alerts.load_log()[:12]
if not log:
    st.caption("No alerts sent yet. Send a test email to confirm your setup, then send pending alerts.")
else:
    import pandas as pd
    df = pd.DataFrame(log)[["sent_at", "status", "severity", "country", "headline", "recipient"]]
    df.columns = ["When", "Status", "Severity", "Country", "Headline", "To"]
    st.dataframe(df, width='stretch', hide_index=True)

with st.expander("Make alerts fully automatic (no clicking)"):
    st.markdown(
        "Run `auto_alert.py` on a schedule - it checks the feed and emails only **new** "
        "qualifying changes (it reads the same alert log, so nothing is sent twice).\n\n"
        "**Windows (Task Scheduler):** create a task that runs every few hours:\n"
        "```\npython C:\\path\\to\\auto_alert.py\n```\n"
        "**Mac/Linux (cron), every 6 hours:**\n"
        "```\n0 */6 * * * cd /path/to/project && .venv/bin/python auto_alert.py\n```\n"
        "**GitHub Actions:** schedule a workflow with `cron` and store keys as repository secrets."
    )

ui.footer()
