# ==============================================
# File: app/__main__.py
# ==============================================
import argparse
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor, wait

from app.bands import BAND_CONFIGS
from app.utils import ensure_output_dir, get_timestamp
from app.capture import create_sdr_stream, capture_samples, close_sdr_stream
from app.demodulation import demodulate
from app.detection import detect_voice
from app.persistence import FileRecorder
from app.health import SystemHealthMonitor

AUDIO_FRAME_MS = 30
AUDIO_SAMPLE_WIDTH = 2
CAPTURE_DURATION = 2
CYCLE_TIMEOUT = 60

recorder = FileRecorder()

def batch_scan(freq_list, config, driver, gain):
    try:
        sdr, stream = create_sdr_stream(freq_list[0], driver, gain, config["sample_rate"])
    except Exception as e:
        print(f"[ERROR] SDR init error: {e}")
        for freq in freq_list:
            recorder.save(freq, get_timestamp(), None, None, config, error=str(e))
        return

    try:
        for freq in freq_list:
            print(f"[INFO] Scanning {freq/1e6:.3f} MHz")
            try:
                sdr.setFrequency(0, freq)
                time.sleep(0.1)
                iq_data = capture_samples(sdr, stream, CAPTURE_DURATION, config["sample_rate"])

                if len(iq_data) < int(CAPTURE_DURATION * 0.8 * config["sample_rate"]):
                    print("[WARNING] Incomplete IQ capture.")
                    recorder.save(freq, get_timestamp(), None, None, config, error="Incomplete IQ")
                    continue

                pcm_audio = demodulate(iq_data, config["demod"], config["sample_rate"])
                has_voice = detect_voice(pcm_audio, config["sample_rate"])
                timestamp = get_timestamp(ms=True)

                if has_voice:
                    recorder.save(freq, timestamp, pcm_audio, iq_data, config)
                    print("[DETECTED] Voice found.")
                else:
                    recorder.save(freq, timestamp, None, None, config, error="no_voice")
                    print("[INFO] No voice detected.")

            except Exception as inner:
                print(f"[ERROR] Scan failed for {freq/1e6:.3f} MHz: {inner}")
                recorder.save(freq, get_timestamp(), None, None, config, error=str(inner))

    finally:
        close_sdr_stream(sdr, stream)

def run_parallel_scan(band, driver, gain, max_workers=4, batch_size=4):
    if band not in BAND_CONFIGS:
        raise ValueError(f"Unsupported band: {band}")
    config = BAND_CONFIGS[band]
    ensure_output_dir(config["output_dir"])

    health = SystemHealthMonitor(config["output_dir"])
    health.start()

    print(f"[INFO] Voice Monitor Started (band={band}) with {max_workers} workers")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        freqs = config["frequencies"]
        while True:
            futures = []
            for i in range(0, len(freqs), batch_size):
                batch = freqs[i:i+batch_size]
                futures.append(executor.submit(batch_scan, batch, config, driver, gain))
            done, _ = wait(futures, timeout=CYCLE_TIMEOUT)
            for f in done:
                try:
                    f.result()
                except Exception as e:
                    print(f"[THREAD ERROR] {e}")
            time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--band", required=True, choices=["hf", "vhf", "uhf"])
    parser.add_argument("--driver", default=None)
    parser.add_argument("--gain", default=40, type=int)
    parser.add_argument("--workers", default=4, type=int, help="Number of parallel scan threads")
    parser.add_argument("--batch", default=4, type=int, help="Number of frequencies per SDR session")
    args = parser.parse_args()

    try:
        run_parallel_scan(
            band=args.band,
            driver=args.driver,
            gain=args.gain,
            max_workers=args.workers,
            batch_size=args.batch
        )
    except KeyboardInterrupt:
        print("[INFO] Stopped by user.")
    except Exception as e:
        print(f"[FATAL] {e}")
