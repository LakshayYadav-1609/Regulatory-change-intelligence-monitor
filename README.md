# ◎ Regulatory Change Intelligence Monitor (RCIM)

> Government portals change visa rules, labor laws and compliance requirements **silently**.
> Companies find out too late. RCIM watches 20+ government portals, detects changes
> automatically, tells you **who on your workforce is affected and what to do**, and can
> **email you the moment something critical moves** - in hours, not weeks.

Built as **Weekend Build Series · Project 03**.

---

## The 6 pages

| # | Page | What it does |
|---|------|--------------|
| 1 | **Overview** | Command center - live metrics, latest dispatches, charts |
| 2 | **Change Feed** | Full wire of detected changes; filter by severity / country / category |
| 3 | **Portals** | The watch list - every government portal being monitored |
| 4 | **AI Analysis** | Claude-powered impact briefs + free-text Q&A over the feed |
| 5 | **Alert Center** | Configure & send Gmail alerts; auto-send pending changes |
| 6 | **History** | Chronological ledger of everything detected and alerted |

---

## Features that need your keys (you have both)

- **AI Analysis (Anthropic)** - set `ANTHROPIC_API_KEY`. Generates executive impact
  briefs and answers questions like *"what's the most urgent change for UK employees?"*.
- **Email Alerts (Gmail)** - set `GMAIL_ADDRESS` + `GMAIL_APP_PASSWORD`. Sends a styled
  HTML alert per change; a log prevents duplicates.

> Without keys the app still runs fully - AI falls back to a rule-based engine, and the
> Alert Center clearly shows email is off.

---

## Tech stack

`Python` · `Streamlit` (st.navigation) · `Pandas` · `Plotly` · `Anthropic API` · `smtplib` (Gmail) · `BeautifulSoup`

---

## Project structure

```
regulatory-change-intelligence-monitor/
├── app.py                    # entry - defines the 6-page navigation
├── auto_alert.py             # standalone scheduler script (true auto-alerts)
├── views/
│   ├── overview.py           # 1
│   ├── change_feed.py        # 2
│   ├── portals.py            # 3
│   ├── ai_analysis.py        # 4
│   ├── alert_center.py       # 5
│   └── history.py            # 6
├── core/
│   ├── config.py             # portals, taxonomy, app identity
│   ├── data.py               # data access + employee matching
│   ├── analyzer.py           # AI impact + Q&A (Anthropic) w/ fallback
│   ├── alerts.py             # Gmail email + alert log
│   ├── scraper.py            # live change detection (optional)
│   ├── charts.py             # themed Plotly figures
│   └── ui.py                 # reusable UI components
├── assets/style.css          # the "intelligence wire service" identity
├── data/                     # sample changes + employees (JSON)
├── .streamlit/config.toml
├── .env.example              # copy to .env and add keys
└── requirements.txt
```

---

## Quick start

```bash
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env       # then edit .env with your keys
streamlit run app.py
```

Opens at `http://localhost:8501`.

### Setting up Gmail alerts

1. Turn on **2-Step Verification** for your Google account.
2. Create an **App Password** at https://myaccount.google.com/apppasswords
3. Put it in `.env` as `GMAIL_APP_PASSWORD` (16 characters, spaces are fine).
4. On the **Alert Center** page, click **Send test email** to confirm.

---

## Fully automatic alerts (no clicking)

Run `auto_alert.py` on a schedule - it emails only **new** qualifying changes:

```bash
python auto_alert.py --severity high
```

- **Windows:** Task Scheduler -> run the command every few hours.
- **macOS / Linux:** cron, e.g. `0 */6 * * * cd /path && .venv/bin/python auto_alert.py`
- **GitHub Actions:** scheduled workflow with keys stored as repository secrets.

---

## The demo script (90 seconds)

1. **Overview** - "RCIM watches 22 government portals. Here's the last 7 days."
2. **Change Feed** - "This morning the UK Home Office raised the Skilled Worker salary threshold. We caught it 2 hours ago."
3. **AI Analysis** - select that change -> impact brief -> "4 UK employees affected, one with an assignment ending in 18 days."
4. **Alert Center** - "And it already emailed the mobility lead automatically."
5. Land the line: *"Your legal team would have found this in 2 weeks. RCIM found it in 2 hours."*

---

Built by **Lalit Yadav** · BI & AI Enablement.
