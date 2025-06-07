import os
from datetime import datetime

def get_timestamp(ms=False):
    now = datetime.utcnow()
    return now.strftime("%Y%m%dT%H%M%S%fZ")[:-3] if ms else now.strftime("%Y%m%dT%H%M%SZ")

def ensure_output_dir(path):
    os.makedirs(path, exist_ok=True)
    if not os.access(path, os.W_OK):
        raise PermissionError(f"No write permission in {path}")
