# This is currently a mock script that uses manually injected test images
# in the container. In the future, it will be replaced by a real uploader
# that captures images from a camera or capture device.

import requests
import os
import random
import time
from pathlib import Path
import sys


# Server configuration
IP = os.getenv("IP")  # Default value: localhost
PORT = os.getenv("PORT")  # Default value: 8000
API_URL = f"http://{IP}:{PORT}/detect"

# Directory with test images
MOCK_IMAGES_DIR = Path("/data/mock_images")  # Docker volume
SEND_INTERVAL = 3


def send_image(image_path):
    try:
        with open(image_path, "rb") as f:
            files = {"file": (image_path.name, f, "image/jpeg")}
            response = requests.post(API_URL, files=files)
            print(f"[INFO] Sent {image_path.name} -> {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERROR] Failed to send {image_path.name}: {e}")


def main():

    sys.stdout.reconfigure(line_buffering=True)

    if not MOCK_IMAGES_DIR.exists():
        print(f"[ERROR] Directory {MOCK_IMAGES_DIR} does not exist")
        return

    print(f"[INFO] Starting cyclic sending of mock images to {API_URL}")

    while True:
        images = list(MOCK_IMAGES_DIR.glob("*.jpg")) + list(MOCK_IMAGES_DIR.glob("*.jpeg")) + list(MOCK_IMAGES_DIR.glob("*.png"))
        if not images:
            print("[WARN] No images currently available.")
            time.sleep(SEND_INTERVAL)
            continue

        image = random.choice(images)
        send_image(image)
        time.sleep(SEND_INTERVAL)


if __name__ == "__main__":
    main()
