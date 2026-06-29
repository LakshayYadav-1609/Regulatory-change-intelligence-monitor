"""
config.py
Single source of truth for app constants, monitored sources, and taxonomy.
Edit this file to add/remove the government sources you watch.
"""

from __future__ import annotations

# ── App identity ─────────────────────────────────────────────────────────────
APP_NAME = "Regulatory Change Intelligence Monitor"
APP_SHORT = "RCIM"
APP_TAGLINE = "Silent government rule changes, caught in hours — not weeks."
APP_VERSION = "2.0.0"
AUTHOR = "Lalit Yadav"

# ── Alerting defaults ────────────────────────────────────────────────────────
# Only changes at or above this severity rank trigger an email alert.
DEFAULT_ALERT_SEVERITY = "high"   # one of: critical | high | medium | low

# ── Severity taxonomy ────────────────────────────────────────────────────────
# Order matters: higher index = more urgent. Used for sorting and colour.
SEVERITY = {
    "critical": {"label": "Critical", "rank": 3, "color": "#D85A5A"},
    "high":     {"label": "High",     "rank": 2, "color": "#E0A93D"},
    "medium":   {"label": "Medium",   "rank": 1, "color": "#4FB6A6"},
    "low":      {"label": "Low",      "rank": 0, "color": "#8A93A8"},
}

# ── Change categories (what kind of rule moved) ──────────────────────────────
CATEGORIES = [
    "Work Visa",
    "Permanent Residency",
    "Labor Law",
    "Tax & Payroll",
    "Compliance Filing",
    "Travel & Entry",
    "Salary Threshold",
]

# ── Monitored sources ────────────────────────────────────────────────────────
# This is the watch-list. Each entry is one government / regulatory source.
# `url` is the page RegWatch polls; `hash` baseline is stored at runtime.
SOURCES = [
    {"id": "uk-homeoffice", "name": "UK Home Office — Immigration Rules", "country": "United Kingdom", "flag": "🇬🇧", "url": "https://www.gov.uk/guidance/immigration-rules", "category": "Work Visa"},
    {"id": "us-uscis",      "name": "USCIS — Policy Manual",               "country": "United States",  "flag": "🇺🇸", "url": "https://www.uscis.gov/policy-manual", "category": "Work Visa"},
    {"id": "us-dol",        "name": "US Dept of Labor — OFLC",             "country": "United States",  "flag": "🇺🇸", "url": "https://www.dol.gov/agencies/eta/foreign-labor", "category": "Labor Law"},
    {"id": "ca-ircc",       "name": "IRCC — Canada Immigration",          "country": "Canada",         "flag": "🇨🇦", "url": "https://www.canada.ca/en/immigration-refugees-citizenship.html", "category": "Permanent Residency"},
    {"id": "au-homeaffairs","name": "Dept of Home Affairs — Australia",   "country": "Australia",      "flag": "🇦🇺", "url": "https://immi.homeaffairs.gov.au/", "category": "Work Visa"},
    {"id": "de-bamf",       "name": "BAMF — Germany",                     "country": "Germany",        "flag": "🇩🇪", "url": "https://www.bamf.de/EN/", "category": "Work Visa"},
    {"id": "sg-mom",        "name": "MOM — Singapore",                    "country": "Singapore",      "flag": "🇸🇬", "url": "https://www.mom.gov.sg/passes-and-permits", "category": "Salary Threshold"},
    {"id": "ae-gdrfa",      "name": "GDRFA — United Arab Emirates",       "country": "UAE",            "flag": "🇦🇪", "url": "https://gdrfad.gov.ae/en", "category": "Travel & Entry"},
    {"id": "in-mha",        "name": "MHA — Bureau of Immigration India",  "country": "India",          "flag": "🇮🇳", "url": "https://boi.gov.in/", "category": "Travel & Entry"},
    {"id": "ie-inis",       "name": "ISD — Ireland Immigration",          "country": "Ireland",        "flag": "🇮🇪", "url": "https://www.irishimmigration.ie/", "category": "Work Visa"},
    {"id": "nl-ind",        "name": "IND — Netherlands",                  "country": "Netherlands",    "flag": "🇳🇱", "url": "https://ind.nl/en", "category": "Salary Threshold"},
    {"id": "fr-ofii",       "name": "OFII — France",                      "country": "France",         "flag": "🇫🇷", "url": "https://www.ofii.fr/", "category": "Work Visa"},
    {"id": "ch-sem",        "name": "SEM — Switzerland",                  "country": "Switzerland",    "flag": "🇨🇭", "url": "https://www.sem.admin.ch/sem/en/home.html", "category": "Work Visa"},
    {"id": "jp-isa",        "name": "ISA — Japan Immigration",            "country": "Japan",          "flag": "🇯🇵", "url": "https://www.isa.go.jp/en/", "category": "Work Visa"},
    {"id": "sa-dha",        "name": "DHA — South Africa",                 "country": "South Africa",   "flag": "🇿🇦", "url": "https://www.dha.gov.za/", "category": "Work Visa"},
    {"id": "br-pf",         "name": "Polícia Federal — Brazil",           "country": "Brazil",         "flag": "🇧🇷", "url": "https://www.gov.br/pf/pt-br", "category": "Travel & Entry"},
    {"id": "sa-mol",        "name": "Ministry of HR — Saudi Arabia",      "country": "Saudi Arabia",   "flag": "🇸🇦", "url": "https://www.hrsd.gov.sa/en", "category": "Labor Law"},
    {"id": "qa-moi",        "name": "MOI — Qatar",                        "country": "Qatar",          "flag": "🇶🇦", "url": "https://portal.moi.gov.qa/", "category": "Labor Law"},
    {"id": "hk-immd",       "name": "ImmD — Hong Kong",                   "country": "Hong Kong",      "flag": "🇭🇰", "url": "https://www.immd.gov.hk/eng/", "category": "Work Visa"},
    {"id": "eu-comm",       "name": "European Commission — Migration",    "country": "European Union", "flag": "🇪🇺", "url": "https://home-affairs.ec.europa.eu/", "category": "Compliance Filing"},
    {"id": "us-irs",        "name": "IRS — International Taxpayers",       "country": "United States",  "flag": "🇺🇸", "url": "https://www.irs.gov/individuals/international-taxpayers", "category": "Tax & Payroll"},
    {"id": "uk-hmrc",       "name": "HMRC — Expat Tax",                   "country": "United Kingdom", "flag": "🇬🇧", "url": "https://www.gov.uk/government/organisations/hm-revenue-customs", "category": "Tax & Payroll"},
]


def source_by_id(source_id: str) -> dict | None:
    """Return a single source dict by its id, or None."""
    return next((s for s in SOURCES if s["id"] == source_id), None)


def severity_rank(name: str) -> int:
    """Numeric rank for a severity name (unknown -> -1)."""
    return SEVERITY.get(name, {}).get("rank", -1)


def severity_color(name: str) -> str:
    return SEVERITY.get(name, {}).get("color", "#8A93A8")
