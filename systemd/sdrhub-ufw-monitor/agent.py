#!/usr/bin/env python3

import base64
import ipaddress
import logging
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin

NTFY_BASE_URL = os.getenv("NTFY_BASE_URL")
NTFY_URL = urljoin(NTFY_BASE_URL, "/ufw")
NTFY_USER = os.getenv("NTFY_USER")
NTFY_PASSWORD = os.getenv("NTFY_PASSWORD")
NTFY_TITLE = "UFW Monitor"
NTFY_CACHE_EXPIRY = 60

# Check if the required environment variables are set.
if not all([NTFY_BASE_URL, NTFY_USER, NTFY_PASSWORD]):
    logging.error("Required environment variables are not set. ")
    sys.exit(1)

# Configure logging to output to stdout.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Cache to track recent alerts.
# This helps prevent spamming notifications for the
# same source IP and port within a short time frame.
recent_alerts = {}

def is_private_ip(ip: str) -> bool:
    """Check if the IP address is private."""
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        logging.error(f"Invalid IP address: {ip}")
        return False

def send_ntfy_notification(message: str, priority: str) -> None:
    """Send a notification to ntfy using standard library with Basic Auth."""
    credentials = f"{NTFY_USER}:{NTFY_PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    auth_header = f"Basic {encoded_credentials}"
    data = message.encode('utf-8')
    req = urllib.request.Request(
        NTFY_URL,
        data=data,
        headers={
            "Title": NTFY_TITLE,
            "Priority": priority,
            "Authorization": auth_header
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            logging.info(f"Notification sent: {message} (status: {response.status})")
    except urllib.error.HTTPError as e:
        logging.error(f"HTTP error: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        logging.error(f"URL error: {e.reason}")

def prune_cache():
    """Remove expired entries from recent_alerts to prevent unbounded growth."""
    current_time = time.time()
    keys_to_delete = [
        key for key, ts in recent_alerts.items()
        if (current_time - ts) > NTFY_CACHE_EXPIRY * 2
    ]
    for key in keys_to_delete:
        del recent_alerts[key]
    if keys_to_delete:
        logging.debug(f"Pruned {len(keys_to_delete)} expired cache entries.")

def should_notify(src_ip: str, dpt: str) -> bool:
    """Check if we should notify for this IP and port based on recent alerts."""
    prune_cache()
    current_time = time.time()
    key = (src_ip, dpt)
    last_alert_time = recent_alerts.get(key)
    if last_alert_time is None or (current_time - last_alert_time) > NTFY_CACHE_EXPIRY:
        recent_alerts[key] = current_time
        return True
    else:
        logging.info(f"Duplicate alert for {src_ip}:{dpt} suppressed.")
        return False

def handle_ufw_alert(src_match, dpt_match, spt_match):
    """Process matched log line components and trigger notification if needed."""
    src_ip = src_match.group(1)
    dpt = dpt_match.group(1) if dpt_match else "0"
    spt = spt_match.group(1) if spt_match else "0"
    is_private = is_private_ip(src_ip)
    ip_type = "Private" if is_private else "Public"
    if should_notify(src_ip, dpt):
        alert_msg = (
            f"Connection attempt detected from:\n"
            f"  - Origin: {ip_type}\n"
            f"  - IP: {src_ip}:{spt}\n"
            f"  - Port: {dpt}"
        )
        logging.warning(alert_msg)
        send_ntfy_notification(alert_msg, "low" if is_private else "high")

def monitor_ufw_logs():
    """Monitor UFW logs and send alert on all connection attempts, indicating if IP is private or public."""
    cmd = ["journalctl", "-f", "-k"]
    src_pattern = re.compile(r"SRC=([\d\.]+)")
    dpt_pattern = re.compile(r"DPT=(\d+)")
    spt_pattern = re.compile(r"SPT=(\d+)")
    logging.info("Starting UFW log monitoring...")
    try:
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
            for line in proc.stdout:
                if "UFW" in line:
                    src_match = src_pattern.search(line)
                    dpt_match = dpt_pattern.search(line)
                    spt_match = spt_pattern.search(line)
                    if src_match:
                        handle_ufw_alert(src_match, dpt_match, spt_match)
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    monitor_ufw_logs()
