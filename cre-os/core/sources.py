"""RSS / Google Alerts ingestion with de-duplication and age filter."""
import calendar
import time

import feedparser


def fetch(urls, max_age_days=3, max_items=25):
    cutoff = time.time() - max_age_days * 86400
    seen, items = set(), []
    for url in urls:
        try:
            feed = feedparser.parse(url)
        except Exception as e:  # network or parse failure should not kill the run
            print(f"WARN feed failed {url}: {e}")
            continue
        for e in feed.entries:
            ts = None
            if getattr(e, "published_parsed", None):
                ts = calendar.timegm(e.published_parsed)
            if ts and ts < cutoff:
                continue
            title = (e.get("title") or "").strip()
            key = title.lower()[:90]
            if not title or key in seen:
                continue
            seen.add(key)
            items.append({
                "title": title,
                "link": e.get("link", ""),
                "summary": (e.get("summary") or "")[:300],
                "ts": ts or 0,
            })
    items.sort(key=lambda x: x["ts"], reverse=True)
    return items[:max_items]


def as_text(items):
    if not items:
        return "(no new items)"
    return "\n".join(f"- {i['title']} | {i['link']}" for i in items)
