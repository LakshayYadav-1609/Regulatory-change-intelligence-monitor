"""
scraper.py
OPTIONAL / ADVANCED — real change detection.

How it works:
  1. Fetch a source page's visible text.
  2. Hash it and compare against the last stored hash.
  3. If the hash differs, the page changed -> a candidate change is raised.

This module is not required for the demo (the app ships with curated sample
changes). Wire it in once you are comfortable, and always respect each site's
robots.txt and terms of use. Add polite delays; never hammer a government site.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent.parent / "data" / "_snapshots.json"
HEADERS = {"User-Agent": "RegWatch/1.0 (+monitoring; contact: you@example.com)"}
TIMEOUT = 20


def _load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def fetch_text(url: str) -> str:
    """Fetch a page and return its visible text. Requires requests + bs4."""
    import requests
    from bs4 import BeautifulSoup

    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ").split())


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check_source(source: dict) -> dict:
    """
    Check one source for change.
    Returns: { 'source_id', 'changed': bool, 'first_seen': bool, 'hash' }
    """
    state = _load_state()
    sid = source["id"]
    try:
        text = fetch_text(source["url"])
    except Exception as exc:  # noqa: BLE001
        return {"source_id": sid, "changed": False, "error": str(exc)}

    new_hash = content_hash(text)
    old_hash = state.get(sid)
    first_seen = old_hash is None
    changed = (old_hash is not None) and (old_hash != new_hash)

    state[sid] = new_hash
    _save_state(state)

    return {"source_id": sid, "changed": changed, "first_seen": first_seen, "hash": new_hash[:12]}
