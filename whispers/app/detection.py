# detection.py (Silero VAD version)

import torch
import numpy as np
from scipy.signal import resample
from pathlib import Path

# Load Silero VAD model from TorchHub only once (optimized)
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)
(get_speech_timestamps, _, _, _, _) = utils

# Constants
TARGET_SAMPLE_RATE = 16000


def resample_audio(pcm_audio, original_sr):
    """Resample audio to 16 kHz required by Silero VAD."""
    if original_sr == TARGET_SAMPLE_RATE:
        return pcm_audio
    duration = len(pcm_audio) / original_sr
    new_len = int(TARGET_SAMPLE_RATE * duration)
    return resample(pcm_audio, new_len).astype(np.int16)


def detect_voice(pcm_audio, sample_rate):
    """Detects if there is human voice in the given PCM audio using Silero VAD."""
    # Resample to 16kHz
    pcm_resampled = resample_audio(pcm_audio, sample_rate)
    audio_tensor = torch.from_numpy(pcm_resampled).float() / 32768.0
    audio_tensor = audio_tensor.unsqueeze(0)  # Add batch dim

    try:
        segments = get_speech_timestamps(audio_tensor, model, sampling_rate=TARGET_SAMPLE_RATE)
        return len(segments) > 0
    except Exception as e:
        print(f"[ERROR] Silero VAD failed: {e}")
        return False
