import os
import csv
import soundfile as sf
import numpy as np
from utils import get_timestamp

def save_audio(pcm_audio, filename, sample_rate):
    sf.write(filename, pcm_audio, sample_rate, subtype='PCM_16')

def save_iq(iq_data, filename):
    iq_data.astype(np.complex64).tofile(filename)

def log_contact(freq, timestamp, result, wav_path, iq_path, out_dir):
    log_file = os.path.join(out_dir, "contacts_log.csv")
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([freq, timestamp, result, wav_path, iq_path])

def generate_file_paths(freq, out_dir):
    ts = get_timestamp(ms=True)
    base = f"{ts}_{int(freq/1e3)}kHz"
    return (
        os.path.join(out_dir, base + ".wav"),
        os.path.join(out_dir, base + ".iq"),
        ts
    )
