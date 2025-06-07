# ==============================================
# File: app/detection.py
# ==============================================
import torch
import numpy as np
from scipy.signal import resample_poly

torch.set_num_threads(1)  # recomendado para uso server-side

# Load Silero VAD (com utilitários)
model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    trust_repo=True  # necessário para ambientes Docker / GitHub direto
)
(get_speech_timestamps, _, _, _, _) = utils

TARGET_SAMPLE_RATE = 16000

def resample_audio(pcm_audio, original_sr):
    if original_sr == TARGET_SAMPLE_RATE:
        return pcm_audio
    from math import gcd
    g = gcd(int(original_sr), TARGET_SAMPLE_RATE)
    up = TARGET_SAMPLE_RATE // g
    down = original_sr // g
    audio_resampled = resample_poly(pcm_audio, up, down)
    return audio_resampled.astype(np.int16)

def detect_voice(pcm_audio, sample_rate):
    if len(pcm_audio) < 16000:
        print("[VAD] Audio too short for analysis.")
        return False

    pcm_resampled = resample_audio(pcm_audio, sample_rate)
    audio_tensor = torch.from_numpy(pcm_resampled).float() / 32768.0
    audio_tensor = audio_tensor.unsqueeze(0)

    try:
        segments = get_speech_timestamps(audio_tensor, model, sampling_rate=TARGET_SAMPLE_RATE)
        if segments:
            print(f"[VAD] Detected voice segments: {segments}")
            return True
        else:
            print("[VAD] No voice detected.")
            return False
    except Exception as e:
        print(f"[ERROR] Silero VAD failed: {e}")
        return False
