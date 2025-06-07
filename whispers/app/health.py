import os
import time
import shutil
import threading
from datetime import datetime

class SystemHealthMonitor:
    def __init__(self, output_dir, interval_sec=60, min_disk_mb=100):
        self.output_dir = output_dir
        self.interval_sec = interval_sec
        self.min_disk_mb = min_disk_mb
        self._running = False
        self._thread = None
        self._last_heartbeat = None

    def _check_disk_space(self):
        total, used, free = shutil.disk_usage(self.output_dir)
        free_mb = free / (1024 * 1024)
        if free_mb < self.min_disk_mb:
            print(f"[ERROR] Low disk space: {free_mb:.1f} MB available.")
            return False
        return True

    def _log_heartbeat(self):
        self._last_heartbeat = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        log_file = os.path.join(self.output_dir, "heartbeat.log")
        with open(log_file, "a") as f:
            f.write(f"{self._last_heartbeat} - Alive\n")

    def _monitor_loop(self):
        while self._running:
            try:
                if not self._check_disk_space():
                    print("[WARNING] Insufficient disk space.")
                self._log_heartbeat()
            except Exception as e:
                print(f"[ERROR] Health monitor failed: {e}")
            time.sleep(self.interval_sec)

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()

    def get_last_heartbeat(self):
        return self._last_heartbeat
