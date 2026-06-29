"""
alerts.py
Email alerting via Gmail SMTP + a persistent log of what was sent.

Environment variables (set in .env):
  GMAIL_ADDRESS        sender Gmail address, e.g. you@gmail.com
  GMAIL_APP_PASSWORD   16-char Google App Password (NOT your normal password)
  ALERT_RECIPIENT      default recipient address

Gmail App Password: enable 2-Step Verification on your Google account, then
create an App Password at https://myaccount.google.com/apppasswords
"""

from __future__ import annotations

import json
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from core import config

LOG_FILE = Path(__file__).resolve().parent.parent / "data" / "alert_log.json"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL


# ── Config helpers ───────────────────────────────────────────────────────────
def email_configured() -> bool:
    return bool(os.environ.get("GMAIL_ADDRESS") and os.environ.get("GMAIL_APP_PASSWORD"))


def default_recipient() -> str:
    return os.environ.get("ALERT_RECIPIENT", "")


# ── Alert log (persistent) ───────────────────────────────────────────────────
def load_log() -> list[dict]:
    if LOG_FILE.exists():
        try:
            return json.loads(LOG_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def _save_log(entries: list[dict]) -> None:
    LOG_FILE.write_text(json.dumps(entries, indent=2, default=str), encoding="utf-8")


def already_alerted(change_id: str) -> bool:
    return any(e["change_id"] == change_id and e["status"] == "sent" for e in load_log())


def _record(change: dict, recipient: str, status: str, detail: str = "") -> dict:
    entry = {
        "change_id": change["id"],
        "headline": change["headline"],
        "severity": change["severity"],
        "country": change["country"],
        "recipient": recipient,
        "status": status,            # "sent" | "failed" | "test"
        "detail": detail,
        "sent_at": datetime.now().isoformat(timespec="seconds"),
    }
    log = load_log()
    log.insert(0, entry)
    _save_log(log)
    return entry


# ── Email body ───────────────────────────────────────────────────────────────
def build_html(change: dict, affected_count: int) -> str:
    sev = config.SEVERITY.get(change["severity"], {})
    color = sev.get("color", "#4FB6A6")
    label = sev.get("label", change["severity"].title())
    eff = change["effective_at"].strftime("%d %B %Y")
    return f"""\
<div style="font-family:Arial,Helvetica,sans-serif;background:#0A0E1A;padding:28px;color:#ECE7DA;">
  <div style="max-width:560px;margin:auto;background:#111729;border:1px solid #232C46;border-radius:12px;overflow:hidden;">
    <div style="border-left:4px solid {color};padding:22px 24px;">
      <div style="font-size:11px;letter-spacing:2px;color:#4FB6A6;text-transform:uppercase;">
        {config.APP_SHORT} · Regulatory Alert
      </div>
      <div style="display:inline-block;margin-top:10px;font-size:11px;font-weight:bold;
                  color:{color};border:1px solid {color};padding:3px 9px;border-radius:4px;
                  letter-spacing:1px;">{label.upper()}</div>
      <h1 style="font-size:20px;line-height:1.3;margin:14px 0 6px;color:#ECE7DA;">
        {change['headline']}
      </h1>
      <div style="font-size:12px;color:#8A93A8;letter-spacing:1px;">
        {change['flag']} {change['country'].upper()} · {change['category'].upper()} · EFFECTIVE {eff.upper()}
      </div>
      <p style="font-size:14px;line-height:1.6;color:#C7C3B8;margin-top:16px;">
        {change['summary']}
      </p>
      <div style="background:#18203A;border-radius:8px;padding:12px 14px;margin-top:14px;">
        <span style="font-size:13px;color:#ECE7DA;">
          <b style="color:#E0A93D;">{affected_count}</b> employee(s) potentially affected in {change['country']}.
        </span>
      </div>
      <p style="font-size:12px;color:#8A93A8;margin-top:18px;border-top:1px dashed #232C46;padding-top:12px;">
        Source: {change['source_name']}<br>
        Sent by {config.APP_NAME} — automated monitoring.
      </p>
    </div>
  </div>
</div>"""


# ── Sending ──────────────────────────────────────────────────────────────────
def _send_raw(recipient: str, subject: str, html: str) -> None:
    sender = os.environ["GMAIL_ADDRESS"]
    password = os.environ["GMAIL_APP_PASSWORD"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{config.APP_SHORT} Monitor <{sender}>"
    msg["To"] = recipient
    msg.attach(MIMEText("Your email client does not support HTML.", "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.login(sender, password)
        server.sendmail(sender, [recipient], msg.as_string())


def send_alert(change: dict, affected_count: int, recipient: str | None = None) -> dict:
    """Send one change alert and log the result. Returns the log entry."""
    recipient = recipient or default_recipient()
    if not email_configured():
        return _record(change, recipient, "failed", "Email not configured (set GMAIL_ADDRESS & GMAIL_APP_PASSWORD).")
    if not recipient:
        return _record(change, recipient, "failed", "No recipient set (ALERT_RECIPIENT).")
    sev = config.SEVERITY.get(change["severity"], {}).get("label", change["severity"]).upper()
    subject = f"[{sev}] {change['country']}: {change['headline']}"
    try:
        _send_raw(recipient, subject, build_html(change, affected_count))
        return _record(change, recipient, "sent")
    except Exception as exc:  # noqa: BLE001
        return _record(change, recipient, "failed", f"{exc.__class__.__name__}: {exc}")


def send_test(recipient: str | None = None) -> dict:
    """Send a harmless test email to confirm the Gmail setup works."""
    recipient = recipient or default_recipient()
    sample = {
        "id": "test-0000", "headline": "Test alert — your setup works",
        "severity": "medium", "country": "Test", "flag": "✅",
        "category": "Configuration", "summary": "If you can read this, RCIM can send alerts from your Gmail.",
        "source_name": "RCIM self-test",
    }
    # build_html needs effective_at; add a dummy
    sample["effective_at"] = datetime.now()
    if not email_configured():
        return _record(sample, recipient, "failed", "Email not configured.")
    if not recipient:
        return _record(sample, recipient, "failed", "No recipient set.")
    try:
        _send_raw(recipient, f"[TEST] {config.APP_SHORT} email setup", build_html(sample, 0))
        return _record(sample, recipient, "test")
    except Exception as exc:  # noqa: BLE001
        return _record(sample, recipient, "failed", f"{exc.__class__.__name__}: {exc}")
