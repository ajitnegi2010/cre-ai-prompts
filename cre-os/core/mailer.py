"""Send the briefing by SMTP. Works with Outlook.com / Microsoft 365 using an app password.

Env vars (GitHub Secrets): SMTP_HOST (default smtp.office365.com), SMTP_PORT (587),
SMTP_USER, SMTP_PASS. If Outlook blocks basic auth for your account, use a Gmail
app password with smtp.gmail.com instead - the code is identical.
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send(to, subject, html, text):
    user, pw = os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS")
    if not (user and pw):
        print("SMTP creds not set - skipping email, report saved to output/ only.")
        return False
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, user, to
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    with smtplib.SMTP(os.environ.get("SMTP_HOST", "smtp.office365.com"), int(os.environ.get("SMTP_PORT", 587))) as s:
        s.starttls()
        s.login(user, pw)
        s.sendmail(user, [to], msg.as_string())
    return True
