# persistence.py (otimizado com gravação sem alocação extra)

import os
import csv
import soundfile as sf
import numpy as np
from utils import get_timestamp


def save_audio(pcm_audio, filename, sample_rate):
    # soundfile lida com np.int16 diretamente, sem alocação extra
    sf.write(file=filename, data=pcm_audio, samplerate=sample_rate, subtype='PCM_16')


def save_iq(iq_data, filename):
    # Garante dtype correto sem criar novo array
    if iq_data.dtype != np.complex64:
        iq_data = iq_data.astype(np.complex64)
    with open(filename, 'wb') as f:
        iq_data.tofile(f)


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
