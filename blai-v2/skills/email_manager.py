#!/usr/bin/env python3
"""
Email Manager — Read inbox, send replies, cold outreach.
Uses info@blacklayers.ca via Zoho SMTP/IMAP.
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.brain import think_simple
from pathlib import Path

MEMORY_DIR = Path(__file__).parent.parent / "memory"
CONFIG_DIR = Path(__file__).parent.parent / "config"

# Email config
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.zoho.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
IMAP_HOST = os.environ.get("IMAP_HOST", "imap.zoho.com")
EMAIL_ADDR = os.environ.get("SMTP_EMAIL", "info@blacklayers.ca")
EMAIL_PASS = os.environ.get("SMTP_PASSWORD", "")


def send_email(to: str, subject: str, body: str, is_html: bool = False) -> bool:
    """Send email from info@blacklayers.ca."""
    try:
        msg = MIMEMultipart()
        msg["From"] = f"Abdul Hafeez - Black Layers <{EMAIL_ADDR}>"
        msg["To"] = to
        msg["Subject"] = subject

        content_type = "html" if is_html else "plain"
        msg.attach(MIMEText(body, content_type))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDR, EMAIL_PASS)
            server.send_message(msg)

        # Log
        log_file = MEMORY_DIR / "email_log.json"
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        logs = []
        if log_file.exists():
            logs = json.loads(log_file.read_text())
        logs.append({
            "to": to,
            "subject": subject,
            "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "type": "outreach"
        })
        log_file.write_text(json.dumps(logs[-100:], indent=2))
        return True

    except Exception as e:
        print(f"[Email] Send failed: {e}", file=sys.stderr)
        return False


def read_inbox(limit: int = 10) -> list:
    """Read recent unread emails from inbox."""
    emails = []
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(EMAIL_ADDR, EMAIL_PASS)
        mail.select("INBOX")

        _, message_ids = mail.search(None, "UNSEEN")
        ids = message_ids[0].split()[-limit:]

        for mid in ids:
            _, msg_data = mail.fetch(mid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            sender = email.utils.parseaddr(msg["From"])[1]
            subject = msg["Subject"] or "(no subject)"
            date = msg["Date"] or ""

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            emails.append({
                "from": sender,
                "subject": subject,
                "body": body[:500],
                "date": date
            })

        mail.logout()
    except Exception as e:
        print(f"[Email] Read failed: {e}", file=sys.stderr)

    return emails


def send_cold_outreach(name: str, company: str, email_addr: str, context: str) -> bool:
    """Generate and send personalized cold outreach email."""
    prompt = f"""Write a short, personalized cold email from Abdul Hafeez (Black Layers).
Target: {name} at {company}
Context: {context}
Key points: 20+ apps shipped, AdClose makes $10K+/month, Pro Seller on Fiverr.
Tone: Professional but human. Short. Not salesy.
Include CTA: 15-min call or just reply to chat.
Sign off as: Abdul Hafeez, Black Layers | blacklayers.ca
MAX 150 words."""

    body = think_simple(prompt)
    if not body:
        return False

    subject_prompt = f"Write a 5-8 word email subject line for a cold outreach to {name} at {company} about mobile app development. No quotes."
    subject = think_simple(subject_prompt) or f"Quick question about {company}'s mobile strategy"
    subject = subject.strip().strip('"').strip("'")

    return send_email(email_addr, subject, body)


if __name__ == "__main__":
    # Test: read inbox
    emails = read_inbox(5)
    for e in emails:
        print(f"From: {e['from']}\nSubject: {e['subject']}\n")
