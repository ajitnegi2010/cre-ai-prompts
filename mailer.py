"""Send the briefing by SMTP. Works with Gmail or Outlook/Microsoft 365 using an app password.

Env vars (GitHub Secrets): SMTP_HOST (default smtp.gmail.com), SMTP_PORT (587),
SMTP_USER, SMTP_PASS. Empty values fall back to defaults. A mail failure never
crashes the run: the briefing is still saved to output/.
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send(to, subject, html, text):
    user = (os.environ.get("SMTP_USER") or "").strip()
    pw = (os.environ.get("SMTP_PASS") or "").replace(" ", "").strip()
    host = (os.environ.get("SMTP_HOST") or "").strip() or "smtp.gmail.com"
    port = int((os.environ.get("SMTP_PORT") or "").strip() or 587)
    if not (user and pw):
        print("SMTP_USER / SMTP_PASS not set - skipping email, report saved to output/ only.")
        return False
    if "YOUR_OUTLOOK_ADDRESS" in to:
        print("config.yaml email_to is still the placeholder - skipping email.")
        return False
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, user, to
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    try:
        with smtplib.SMTP(host, port, timeout=30) as s:
            s.starttls()
            s.login(user, pw)
            s.sendmail(user, [to], msg.as_string())
        print(f"Email sent to {to}")
        return True
    except Exception as e:
        print(f"EMAIL FAILED ({type(e).__name__}): {e}")
        return False
