"""CSV-based CRM. Keep the CSV in OneDrive/Excel; commit a copy to the repo for the daily run."""
import csv
from datetime import date, datetime


def load(path):
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def _d(s):
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except Exception:
        return None


def due_followups(rows, today=None):
    today = today or date.today()
    out = []
    for r in rows:
        nf = _d(r.get("next_follow_up", ""))
        if nf and nf <= today:
            r = dict(r)
            r["days_overdue"] = (today - nf).days
            out.append(r)
    return sorted(out, key=lambda r: -r["days_overdue"])


def lease_expiry_watch(rows, today=None, window_days=540):
    today = today or date.today()
    out = []
    for r in rows:
        le = _d(r.get("lease_expiry", ""))
        if le and 0 <= (le - today).days <= window_days:
            r = dict(r)
            r["days_to_expiry"] = (le - today).days
            out.append(r)
    return sorted(out, key=lambda r: r["days_to_expiry"])


def as_text(rows):
    if not rows:
        return "(none)"
    return "\n".join("; ".join(f"{k}={v}" for k, v in r.items() if v) for r in rows)
