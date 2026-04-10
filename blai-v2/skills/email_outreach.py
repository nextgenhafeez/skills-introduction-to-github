#!/usr/bin/env python3
"""
Email Outreach — Send outreach emails via Make.com webhook or direct SMTP.
Template-based with tracking.
"""

import json
import time
import requests
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.brain import think_simple
from skills.make_com import call_webhook_by_name, create_webhook, _load_webhooks, _get_webhooks_config
from pathlib import Path

MEMORY_DIR = Path(__file__).parent.parent / "memory"
OUTREACH_LOG = MEMORY_DIR / "outreach_log.json"

# Email templates
TEMPLATES = {
    "intro": {
        "subject": "Quick question about your {project_type} project",
        "body": """Hi {name},

I noticed you're looking for help with {context}. I'm Abdul Hafeez, founder of Black Layers — we've shipped 20+ iOS/mobile apps, including AdClose which generates $10K+/month.

A few things that set us apart:
- 30-day delivery for MVPs
- Zero App Store rejections across all apps
- Pro Seller on Fiverr with perfect reviews

Would love to hear more about what you're building. Happy to jump on a quick 15-min call or just reply here.

Best,
Abdul Hafeez
Black Layers | blacklayers.ca"""
    },
    "followup": {
        "subject": "Re: {original_subject}",
        "body": """Hi {name},

Just following up on my note from {days_ago} days ago. Wanted to make sure it didn't get lost.

If you've already found someone — no worries at all. But if you're still looking, I'd love to chat about your project.

You can see our work at blacklayers.ca or just reply to this email.

Best,
Abdul Hafeez
Black Layers"""
    },
    "value": {
        "subject": "{topic} — thought this might help",
        "body": """Hi {name},

I came across your post about {context} and thought I'd share something that might be useful.

{value_content}

If you ever need help with mobile development, I'd be happy to chat. No pressure.

Best,
Abdul Hafeez
Black Layers | blacklayers.ca"""
    }
}


def _load_outreach_log() -> list:
    """Load outreach tracking log."""
    if OUTREACH_LOG.exists():
        return json.loads(OUTREACH_LOG.read_text())
    return []


def _save_outreach(entry: dict):
    """Save an outreach entry to the log."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    log = _load_outreach_log()
    log.append(entry)
    # Keep last 200 entries
    OUTREACH_LOG.write_text(json.dumps(log[-200:], indent=2))


def _already_contacted(email_addr: str) -> bool:
    """Check if we already emailed this person."""
    log = _load_outreach_log()
    return any(e.get("to") == email_addr for e in log)


def send_outreach_email(to: str, subject: str, body: str, via: str = "auto") -> str:
    """
    Send an outreach email. Tries Make.com webhook first, falls back to direct SMTP.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
        via: "make" for webhook, "smtp" for direct, "auto" to try both

    Returns: WhatsApp-friendly status message
    """
    if _already_contacted(to):
        return f"Already contacted {to} before. Use follow-up template instead."

    sent = False
    method = "none"

    # Try Make.com webhook first (if configured)
    if via in ("auto", "make"):
        webhooks = _get_webhooks_config()
        saved = _load_webhooks()
        email_webhook = None

        for name in list(saved.keys()) + list(webhooks.keys()):
            if "email" in name.lower() or "outreach" in name.lower():
                email_webhook = name
                break

        if email_webhook:
            result = call_webhook_by_name(email_webhook, {
                "to": to,
                "subject": subject,
                "body": body,
                "from_name": "Abdul Hafeez - Black Layers",
                "from_email": "info@blacklayers.ca",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            })
            if "successfully" in result.lower():
                sent = True
                method = f"make.com ({email_webhook})"

    # Fallback to direct SMTP via email_manager
    if not sent and via in ("auto", "smtp"):
        try:
            from skills.email_manager import send_email
            sent = send_email(to, subject, body)
            if sent:
                method = "smtp (info@blacklayers.ca)"
        except Exception as e:
            pass

    # Log the attempt
    _save_outreach({
        "to": to,
        "subject": subject,
        "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "sent": sent,
        "method": method,
        "template": "custom"
    })

    if sent:
        return f"Email sent to {to} via {method}.\nSubject: {subject}"
    else:
        return (
            f"Failed to send email to {to}.\n"
            "Make.com email webhook not configured and SMTP may not have credentials.\n"
            "Setup option: Create a Make.com scenario with Gmail/SMTP module."
        )


def send_template_email(to: str, template: str, variables: dict) -> str:
    """
    Send a templated outreach email.

    Args:
        to: Recipient email
        template: "intro", "followup", or "value"
        variables: Dict with template variables (name, context, etc.)

    Returns: WhatsApp-friendly status
    """
    if template not in TEMPLATES:
        return f"Unknown template '{template}'. Available: {', '.join(TEMPLATES.keys())}"

    tmpl = TEMPLATES[template]
    try:
        subject = tmpl["subject"].format(**variables)
        body = tmpl["body"].format(**variables)
    except KeyError as e:
        return f"Template '{template}' needs variable: {e}"

    return send_outreach_email(to, subject, body)


def send_ai_outreach(to: str, name: str, context: str) -> str:
    """
    Generate a personalized outreach email using AI and send it.

    Args:
        to: Recipient email
        name: Recipient name
        context: What they need (e.g., "iOS app for restaurant ordering")

    Returns: WhatsApp-friendly status
    """
    if _already_contacted(to):
        return f"Already contacted {to}. Skipping to avoid spam."

    prompt = f"""Write a short cold outreach email from Abdul Hafeez (Black Layers, blacklayers.ca).
Target: {name}
Their need: {context}
Key credentials: 20+ apps shipped, AdClose $10K+/month, Fiverr Pro Seller, zero App Store rejections.
Tone: Professional, human, NOT salesy. Short — max 120 words.
Include CTA: 15-min call or just reply.
Sign: Abdul Hafeez, Black Layers | blacklayers.ca
Do NOT include subject line — just the body."""

    body = think_simple(prompt)
    if not body:
        return "Failed to generate email — AI unavailable."

    subject_prompt = f"Write a 5-8 word email subject for cold outreach to {name} about {context}. No quotes, no emojis."
    subject = think_simple(subject_prompt) or f"Quick question about your project"
    subject = subject.strip().strip('"').strip("'")

    return send_outreach_email(to, subject, body)


def setup_email_webhook() -> str:
    """Create a Make.com webhook for email sending automation."""
    result = create_webhook("blai-email-outreach", "Triggers email sending from BLAI")
    return (
        f"{result}\n\n"
        "To complete setup:\n"
        "1. Go to Make.com\n"
        "2. Create a scenario: Webhook -> Gmail (Send Email)\n"
        "3. Map fields: to, subject, body, from_name\n"
        "4. Activate the scenario\n"
        "5. BLAI will use this automatically for outreach"
    )


def get_outreach_stats() -> str:
    """Get outreach statistics."""
    log = _load_outreach_log()
    if not log:
        return "No outreach emails sent yet."

    today = time.strftime("%Y-%m-%d")
    today_sent = [e for e in log if e["date"].startswith(today) and e["sent"]]
    total_sent = [e for e in log if e["sent"]]
    total_failed = [e for e in log if not e["sent"]]

    methods = {}
    for e in total_sent:
        m = e.get("method", "unknown")
        methods[m] = methods.get(m, 0) + 1

    lines = [
        f"OUTREACH STATS:",
        f"Total sent: {len(total_sent)}",
        f"Today: {len(today_sent)}",
        f"Failed: {len(total_failed)}",
    ]
    if methods:
        lines.append("By method:")
        for m, c in methods.items():
            lines.append(f"  {m}: {c}")

    return "\n".join(lines)


if __name__ == "__main__":
    print(get_outreach_stats())
