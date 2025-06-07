# ==============================================
# File: app/persistence.py
# ==============================================
import os
import csv
import soundfile as sf
import numpy as np
from app.utils import get_timestamp

def save_audio(pcm_audio, filename, sample_rate):
    sf.write(file=filename, data=pcm_audio, samplerate=sample_rate, subtype='PCM_16')

def save_iq(iq_data, filename):
    if iq_data.dtype != np.complex64:
        iq_data = iq_data.astype(np.complex64)
    with open(filename, 'wb') as f:
        iq_data.tofile(f)

def log_contact(freq, timestamp, result, wav_path, iq_path, out_dir, error=None):
    log_file = os.path.join(out_dir, "contacts_log.csv")
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([freq, timestamp, result, wav_path, iq_path, error or "-"])

def generate_file_paths(freq, out_dir):
    ts = get_timestamp(ms=True)
    base = f"{ts}_{int(freq/1e3)}kHz"
    return (
        os.path.join(out_dir, base + ".wav"),
        os.path.join(out_dir, base + ".iq"),
        ts
    )

class Recorder:
    def save(self, *args, **kwargs):
        raise NotImplementedError()

class FileRecorder(Recorder):
    def save(self, freq, timestamp, pcm_audio, iq_data, config, error=None):
        wav_path, iq_path, _ = generate_file_paths(freq, config["output_dir"])
        if error is None:
            save_audio(pcm_audio, wav_path, config["sample_rate"])
            save_iq(iq_data, iq_path)
            log_contact(freq, timestamp, "voice_detected", wav_path, iq_path, config["output_dir"])
        else:
            log_contact(freq, timestamp, "error", "-", "-", config["output_dir"], error=error)
