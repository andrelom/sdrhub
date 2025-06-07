import argparse
import time
from bands import BAND_CONFIGS
from utils import ensure_output_dir, get_timestamp
from capture import create_sdr_stream, capture_samples, close_sdr_stream
from demodulation import demodulate
from detection import detect_voice
from persistence import save_audio, save_iq, log_contact, generate_file_paths
from health import SystemHealthMonitor

AUDIO_FRAME_MS = 30
AUDIO_SAMPLE_WIDTH = 2
CAPTURE_DURATION = 2

def scan(freq, config, driver, gain):
    print(f"[INFO] Scanning {freq/1e6:.3f} MHz")
    try:
        sdr, stream = create_sdr_stream(freq, driver, gain, config["sample_rate"])
        iq_data = capture_samples(sdr, stream, CAPTURE_DURATION, config["sample_rate"])
        close_sdr_stream(sdr, stream)
    except Exception as e:
        print(f"[ERROR] SDR error: {e}")
        return

    if len(iq_data) < CAPTURE_DURATION * 0.8 * config["sample_rate"]:
        print("[WARNING] Incomplete IQ capture.")
        return

    pcm_audio = demodulate(iq_data, config["demod"], config["sample_rate"])
    has_voice = detect_voice(pcm_audio, config["sample_rate"])
    wav_path, iq_path, timestamp = generate_file_paths(freq, config["output_dir"])

    if has_voice:
        save_audio(pcm_audio, wav_path, config["sample_rate"])
        save_iq(iq_data, iq_path)
        log_contact(freq, timestamp, "voice_detected", wav_path, iq_path, config["output_dir"])
        print("[DETECTED] Voice found.")
    else:
        log_contact(freq, timestamp, "no_voice", "-", "-", config["output_dir"])
        print("[INFO] No voice detected.")

def main(band, driver, gain):
    if band not in BAND_CONFIGS:
        raise ValueError(f"Unsupported band: {band}")
    config = BAND_CONFIGS[band]
    ensure_output_dir(config["output_dir"])

    health = SystemHealthMonitor(config["output_dir"])
    health.start()

    print(f"[INFO] Voice Monitor Started (band={band})")
    while True:
        for freq in config["frequencies"]:
            scan(freq, config, driver, gain)
            time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--band", required=True, choices=["hf", "vhf", "uhf"])
    parser.add_argument("--driver", default=None)
    parser.add_argument("--gain", default=40, type=int)
    args = parser.parse_args()

    try:
        main(band=args.band, driver=args.driver, gain=args.gain)
    except KeyboardInterrupt:
        print("[INFO] Stopped by user.")
    except Exception as e:
        print(f"[FATAL] {e}")
