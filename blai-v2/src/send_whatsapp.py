#!/usr/bin/env python3
"""
Send WhatsApp message via the running BLAI bot.
Writes to a queue file that whatsapp.js reads and sends.
"""

import json
import sys
import time
from pathlib import Path

QUEUE_FILE = Path(__file__).parent.parent / "memory" / "outgoing_queue.json"


def queue_message(phone: str, message: str):
    """Add message to outgoing queue for WhatsApp bot to send."""
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)

    queue = []
    if QUEUE_FILE.exists():
        try:
            queue = json.loads(QUEUE_FILE.read_text())
        except:
            queue = []

    queue.append({
        "phone": phone,
        "message": message,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "sent": False
    })

    QUEUE_FILE.write_text(json.dumps(queue, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 send_whatsapp.py <phone> <message>")
        sys.exit(1)
    queue_message(sys.argv[1], sys.argv[2])
    print(f"Queued message to {sys.argv[1]}")
