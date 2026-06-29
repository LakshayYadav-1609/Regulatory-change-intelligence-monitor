"""
auto_alert.py
Run this on a schedule (cron / Windows Task Scheduler / GitHub Actions) for
fully automatic alerting. It emails only NEW qualifying changes — the alert log
prevents duplicates, so it is safe to run as often as you like.

Usage:
    python auto_alert.py
    python auto_alert.py --severity critical
"""

from __future__ import annotations

import argparse
import sys

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from core import alerts, config, data


def main() -> int:
    parser = argparse.ArgumentParser(description="Send email alerts for new regulatory changes.")
    parser.add_argument("--severity", default=config.DEFAULT_ALERT_SEVERITY,
                        choices=list(config.SEVERITY.keys()),
                        help="Minimum severity to alert on.")
    args = parser.parse_args()

    if not alerts.email_configured():
        print("[auto_alert] Email not configured. Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD.")
        return 1
    recipient = alerts.default_recipient()
    if not recipient:
        print("[auto_alert] No recipient. Set ALERT_RECIPIENT in your environment.")
        return 1

    min_rank = config.severity_rank(args.severity)
    changes = data.get_changes()
    pending = [c for c in changes
               if c["severity_rank"] >= min_rank and not alerts.already_alerted(c["id"])]

    if not pending:
        print(f"[auto_alert] No new changes at/above '{args.severity}'. Nothing to send.")
        return 0

    print(f"[auto_alert] {len(pending)} new change(s) to alert -> {recipient}")
    sent, failed = 0, 0
    for c in pending:
        count = len(data.affected_employees(c))
        result = alerts.send_alert(c, count, recipient)
        if result["status"] == "sent":
            sent += 1
            print(f"  ✓ {c['id']}  {c['headline']}")
        else:
            failed += 1
            print(f"  ✗ {c['id']}  {result['detail']}")

    print(f"[auto_alert] done — {sent} sent, {failed} failed.")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
