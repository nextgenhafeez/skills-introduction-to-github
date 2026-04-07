#!/usr/bin/env python3
"""
BLAI Auto-Email Outreach — Sends personalized cold emails to Product Hunt makers
who launched web-only products (no mobile app).

Runs after lead-hunter.py finds PH leads. Reads from leads-database.json,
finds contact emails from product websites, sends personalized emails.

Requires: SMTP_EMAIL, SMTP_PASSWORD env vars (Gmail App Password recommended)
"""

import requests
import json
import smtplib
import os
import re
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path

DATE = datetime.now().strftime("%Y-%m-%d")
LEADS_FILE = Path.home() / ".openclaw/memory/leads-database.json"
OUTREACH_LOG = Path.home() / ".openclaw/memory/outreach-log.json"

# Email config
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.zoho.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))

# Limits
MAX_EMAILS_PER_DAY = 10  # Don't spam — quality over quantity
DELAY_BETWEEN_EMAILS = 30  # seconds


def load_leads():
    if LEADS_FILE.exists():
        try:
            return json.loads(LEADS_FILE.read_text())
        except Exception:
            pass
    return {"leads": [], "last_scan": None}


def save_leads(data):
    LEADS_FILE.write_text(json.dumps(data, indent=2, default=str))


def load_outreach_log():
    if OUTREACH_LOG.exists():
        try:
            return json.loads(OUTREACH_LOG.read_text())
        except Exception:
            pass
    return {"emails_sent": [], "total_sent": 0}


def save_outreach_log(log):
    OUTREACH_LOG.write_text(json.dumps(log, indent=2, default=str))


def resolve_ph_redirect(url):
    """Follow Product Hunt redirect URL to get the actual website."""
    if not url or "producthunt.com/r/" not in url:
        return url
    try:
        r = requests.head(url, allow_redirects=True, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        final_url = r.url
        # Remove PH tracking params
        if "?" in final_url:
            final_url = final_url.split("?utm_")[0]
        return final_url
    except Exception:
        return url


def find_email_from_website(website_url):
    """Try to find a contact email from a product's website."""
    if not website_url:
        return None

    # Resolve PH redirect first
    website_url = resolve_ph_redirect(website_url)
    if "producthunt.com" in website_url:
        return None  # Still on PH, no real website

    print(f"    Actual website: {website_url}")
    emails_found = set()

    try:
        # Fetch the homepage
        r = requests.get(website_url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        }, timeout=10, allow_redirects=True)

        if r.status_code == 200:
            text = r.text

            # Find email addresses in page content
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            found = re.findall(email_pattern, text)

            for email in found:
                # Skip common non-contact emails
                skip = ["noreply", "no-reply", "support@", "help@", "info@example",
                        "test@", "user@", "email@example", "name@", "your@",
                        ".png", ".jpg", ".svg", ".css", ".js"]
                if not any(s in email.lower() for s in skip):
                    emails_found.add(email.lower())

        # Also try /contact, /about pages
        for page in ["/contact", "/about", "/team"]:
            try:
                r2 = requests.get(website_url.rstrip("/") + page, headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                }, timeout=5, allow_redirects=True)
                if r2.status_code == 200:
                    found = re.findall(email_pattern, r2.text)
                    for email in found:
                        skip = ["noreply", "no-reply", "support@", "help@",
                                "test@", "user@", "email@example", "name@", "your@",
                                ".png", ".jpg", ".svg", ".css", ".js"]
                        if not any(s in email.lower() for s in skip):
                            emails_found.add(email.lower())
            except Exception:
                continue

    except Exception as e:
        print(f"    Error fetching {website_url}: {e}")

    # Prefer founder/personal emails over generic ones
    priority = []
    generic = []
    for email in emails_found:
        if any(g in email for g in ["info@", "contact@", "hello@", "team@"]):
            generic.append(email)
        else:
            priority.append(email)

    if priority:
        return priority[0]
    if generic:
        return generic[0]
    return None


def generate_email(lead, to_email):
    """Generate a personalized cold email for a Product Hunt maker."""
    title = lead.get("title", "")
    product_name = title.split(" — ")[0] if " — " in title else title[:40]
    author = lead.get("author", "there")
    tagline = ""
    preview = lead.get("preview", "")
    if "Tagline:" in preview:
        tagline = preview.split("Tagline:")[-1].strip()

    subject = f"Loved {product_name} — have you considered a mobile app?"

    body = f"""Hi {author},

Congrats on launching {product_name} on Product Hunt! {f'"{tagline}" — really compelling.' if tagline else 'Looks like a great product.'}

I noticed you don't have a mobile app yet. At Black Layers, we specialize in turning web products into polished iOS apps. A few highlights:

- 20+ apps shipped to the App Store (zero rejections)
- Our own app AdClose generates $10K+/month
- Pro Seller on Fiverr with 5-star reviews across 200+ projects

A mobile app could help {product_name} reach users who prefer native experiences, improve engagement, and open up new distribution through the App Store.

Would it make sense to chat for 15 minutes about what a mobile version could look like? No commitment — just exploring the idea.

You can also reach me directly on WhatsApp: +1 (587) 429-6200

Best,
Abdul Hafeez
Founder, Black Layers
blacklayers.ca"""

    return subject, body


def send_email(to_email, subject, body):
    """Send an email via SMTP."""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print(f"    SMTP not configured. Would send to: {to_email}")
        print(f"    Subject: {subject}")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = f"Black Layers <{SMTP_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["Reply-To"] = "info@blacklayers.ca"

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"    Sent to: {to_email}")
        return True

    except Exception as e:
        print(f"    Failed to send to {to_email}: {e}")
        return False


def main():
    print(f"BLAI Auto-Email Outreach — {DATE}")
    print("=" * 50)

    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("ERROR: Set SMTP_EMAIL and SMTP_PASSWORD env vars.")
        print("  For Gmail: Use an App Password (not your regular password)")
        print("  1. Go to myaccount.google.com/apppasswords")
        print("  2. Create an app password for 'Mail'")
        print("  3. Set SMTP_EMAIL=your@gmail.com SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx")
        print("")
        print("Running in DRY RUN mode (will show emails but not send)...")
        print("")

    db = load_leads()
    log = load_outreach_log()

    # Find PH leads that haven't been emailed yet
    ph_leads = [l for l in db["leads"]
                if l.get("source") == "producthunt"
                and not l.get("outreach_sent")
                and l.get("date_found", "") >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")]

    if not ph_leads:
        print("No new Product Hunt leads to email.")
        return

    print(f"Found {len(ph_leads)} PH leads to process (max {MAX_EMAILS_PER_DAY}/day)")
    print("")

    emails_sent_today = len([e for e in log.get("emails_sent", [])
                            if e.get("date") == DATE])

    sent_count = 0
    for lead in ph_leads:
        if sent_count + emails_sent_today >= MAX_EMAILS_PER_DAY:
            print(f"\nDaily limit reached ({MAX_EMAILS_PER_DAY}). Remaining leads will be emailed tomorrow.")
            break

        product_name = lead["title"].split(" — ")[0] if " — " in lead["title"] else lead["title"][:30]
        print(f"[{sent_count + 1}] {product_name}")

        # Get actual website (resolve PH redirect)
        website = lead.get("website", "") or lead.get("url", "")
        website = resolve_ph_redirect(website)

        if not website or "producthunt.com" in website:
            print(f"    No real website found (PH redirect didn't resolve)")
            continue

        email = find_email_from_website(website)

        if not email:
            print(f"    No email found on {website or 'no website'}")
            lead["outreach_sent"] = False
            lead["notes"] = "No email found"
            continue

        print(f"    Found email: {email}")

        # Generate and send
        subject, body = generate_email(lead, email)
        success = send_email(email, subject, body)

        if success or not SMTP_EMAIL:
            lead["outreach_sent"] = True
            lead["outreach_date"] = DATE
            lead["outreach_email"] = email
            lead["follow_up_date"] = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
            lead["status"] = "outreach_sent"

            log["emails_sent"].append({
                "date": DATE,
                "to": email,
                "product": product_name,
                "subject": subject,
                "lead_url": lead.get("url", "")
            })
            log["total_sent"] = log.get("total_sent", 0) + 1
            sent_count += 1

            if SMTP_EMAIL:
                time.sleep(DELAY_BETWEEN_EMAILS)

    # Save
    save_leads(db)
    save_outreach_log(log)

    print(f"\n{'=' * 50}")
    print(f"OUTREACH COMPLETE")
    print(f"  Emails sent today: {sent_count}")
    print(f"  Total emails sent all-time: {log['total_sent']}")
    print(f"  Follow-ups scheduled: {sent_count} (in 5 days)")


if __name__ == "__main__":
    main()
