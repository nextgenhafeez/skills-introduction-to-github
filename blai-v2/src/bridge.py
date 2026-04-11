#!/usr/bin/env python3
"""
Bridge: WhatsApp.js calls this script for each message.
Decodes the message, calls the brain, prints the reply.
"""

import argparse
import base64
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.brain import think


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phone', required=True)
    parser.add_argument('--message', required=True, help='Base64 encoded message')
    parser.add_argument('--image', default=None, help='Path to image file')
    parser.add_argument('--video', default=None, help='Path to video file')
    args = parser.parse_args()

    message = base64.b64decode(args.message).decode('utf-8')

    image_data = None
    if args.image and os.path.exists(args.image):
        with open(args.image, 'rb') as f:
            image_data = f.read()

    reply = think(args.phone, message, image_data, video_path=args.video)
    print(reply)


if __name__ == '__main__':
    main()
