# detection.py (Silero VAD + otimização de buffer no resample)

import torch
import numpy as np
from scipy.signal import resample_poly

# Load Silero VAD model from TorchHub with trust_repo=True
model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=False,
    trust_repo=True
)
(get_speech_timestamps, _, _, _, _) = utils

# Constants
TARGET_SAMPLE_RATE = 16000


def resample_audio(pcm_audio, original_sr, reuse_buffer=False):
    """Resample audio to 16 kHz required by Silero VAD."""
    if original_sr == TARGET_SAMPLE_RATE:
        return pcm_audio
    # Use resample_poly for better performance and quality
    from math import gcd
    g = gcd(int(original_sr), TARGET_SAMPLE_RATE)
    up = TARGET_SAMPLE_RATE // g
    down = original_sr // g
    audio_resampled = resample_poly(pcm_audio, up, down)
    if reuse_buffer:
        pcm_out = np.empty_like(audio_resampled, dtype=np.int16)
        np.multiply(audio_resampled, 1, out=pcm_out, casting='unsafe')
        return pcm_out
    return audio_resampled.astype(np.int16)


def detect_voice(pcm_audio, sample_rate):
    """Detects if there is human voice in the given PCM audio using Silero VAD."""
    pcm_resampled = resample_audio(pcm_audio, sample_rate, reuse_buffer=True)
    audio_tensor = torch.from_numpy(pcm_resampled).float() / 32768.0
    audio_tensor = audio_tensor.unsqueeze(0)  # Add batch dim

    try:
        segments = get_speech_timestamps(audio_tensor, model, sampling_rate=TARGET_SAMPLE_RATE)
        if segments:
            print(f"[VAD] Detected {len(segments)} voice segment(s):")
            for seg in segments:
                start_ms = int(seg['start'] * 1000 / TARGET_SAMPLE_RATE)
                end_ms = int(seg['end'] * 1000 / TARGET_SAMPLE_RATE)
                print(f"   ↳ from {start_ms} ms to {end_ms} ms")
            return True
        else:
            print("[VAD] No voice detected.")
            return False
    except Exception as e:
        print(f"[ERROR] Silero VAD failed: {e}")
        return False
