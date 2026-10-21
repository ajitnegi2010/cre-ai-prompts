"""Daily orchestrator: ingest -> specialist agents -> Chief of Staff -> save + email."""
import argparse
import html
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from agents import prompts as P  # noqa: E402
from core import crm, llm, mailer, sources  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="no API calls, no email")
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    b, lim, mdl = cfg["broker"], cfg["limits"], cfg["model"]
    today = date.today()
    fmt = dict(
        name=b["name"], years=b["experience_years"], geo=", ".join(b["geography"]),
        spec=", ".join(b["specialties"]), mm=", ".join(b["micro_markets"]), date=today.strftime("%A, %d %B %Y"),
    )

    def run(prompt, user):
        return llm.ask(prompt.format(**fmt), user, mdl["name"], mdl["max_tokens"], args.dry_run)

    src = cfg["sources"]
    alerts = src.get("google_alerts") or []
    news = {
        k: sources.as_text(sources.fetch(urls + alerts if k == "occupier" else urls, lim["max_age_days"], lim["max_items_per_agent"]))
        for k, urls in src["rss"].items()
    }

    rows = crm.load(ROOT / "data" / "crm_contacts.csv")
    due, expiring = crm.due_followups(rows, today), crm.lease_expiry_watch(rows, today)

    out = {}
    out["occupier"] = run(P.OCCUPIER, news["occupier"])
    out["bd"] = run(P.BD, f"OCCUPIER LEADS:\n{out['occupier']}")
    out["supply"] = run(P.SUPPLY, news["supply"])
    out["market"] = run(P.MARKET, news["market"])
    out["followup"] = run(P.FOLLOWUP, f"DUE:\n{crm.as_text(due)}\n\nLEASE EXPIRY WATCH:\n{crm.as_text(expiring)}\n\nMARKET CONTEXT:\n{out['market'][:1500]}")
    out["meeting"] = run(P.MEETING, f"CRM:\n{crm.as_text(due[:3] or rows[:3])}\n\nLEADS:\n{out['occupier'][:2000]}")
    out["legal"] = run(P.LEGAL, "Produce today's checklist.")
    out["finance"] = run(P.FINANCE, f"Top lead context:\n{out['occupier'][:1500]}")
    out["presentation"] = run(P.PRESENTATION, f"Top lead context:\n{out['occupier'][:1500]}\nSupply:\n{out['supply'][:1000]}")

    bundle = "\n\n".join(f"=== {k.upper()} AGENT ===\n{v}" for k, v in out.items())
    report = run(P.CHIEF, bundle)

    outdir = ROOT / "output"
    outdir.mkdir(exist_ok=True)
    stamp = today.isoformat()
    (outdir / f"briefing_{stamp}.md").write_text(report, encoding="utf-8")
    (outdir / f"raw_agents_{stamp}.md").write_text(bundle, encoding="utf-8")
    print(f"Saved output/briefing_{stamp}.md ({len(report)} chars)")

    if args.dry_run:
        print("Dry run: email skipped.")
        return
    body = f"<html><body><pre style='font-family:Segoe UI,Arial,sans-serif;white-space:pre-wrap;font-size:14px'>{html.escape(report)}</pre></body></html>"
    mailer.send(b["email_to"], f"Executive Briefing - {today.strftime('%d %b %Y')}", body, report)


if __name__ == "__main__":
    main()
