# CRE Brokerage Operating System (Ajit Negi)

A virtual brokerage firm of AI agents that runs daily on GitHub Actions (free) and emails an executive briefing.

## Flow
RSS / Google Alerts -> Occupier, Supply, Market agents -> BD agent (who/why/how + drafts) ->
CRM Follow-up agent (CSV) -> Meeting, Legal, Finance, Presentation support agents ->
**Chief of Staff** merges everything -> `output/briefing_DATE.md` + email.

## Setup (about 15 minutes)
1. Create a private GitHub repo and upload this folder.
2. Repo > Settings > Secrets and variables > Actions, add:
   - `ANTHROPIC_API_KEY`
   - `SMTP_USER`, `SMTP_PASS` (Outlook app password), `SMTP_HOST` (smtp.office365.com), `SMTP_PORT` (587)
   - If Outlook blocks SMTP basic auth, use Gmail: smtp.gmail.com + app password.
3. Edit `config.yaml`: set `email_to`, tweak micro-markets, add Google Alerts RSS URLs.
4. Edit `data/crm_contacts.csv` (open in Excel; keep dates as YYYY-MM-DD). Export from OneDrive and commit weekly, or edit directly on GitHub.
5. Actions tab > Daily Executive Briefing > Run workflow to test. It then runs daily at 07:00 IST.

## Local test
```
pip install -r requirements.txt
python run_daily.py --dry-run      # no API cost, no email
ANTHROPIC_API_KEY=... python run_daily.py
```

## Cost control
`limits.max_items_per_agent` and `model.name` in config.yaml. Roughly 10 API calls per day.

## Safety notes
- Agents are told never to invent names or contact details; verify every lead before outreach.
- Legal output is a checklist, not legal advice.
- Keep the repo private; the CRM CSV contains client data.

## Roadmap
Outlook sent-mail sync for CRM, Excel financial model generator (openpyxl), PPTX deck generator, competitor deal tracker, Telegram/WhatsApp alerts.
