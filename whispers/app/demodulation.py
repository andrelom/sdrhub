# ==============================================
# File: app/demodulation.py
# ==============================================
import numpy as np

def demodulate(iq_data, demod_type, sample_rate):
    if demod_type == "am":
        envelope = np.abs(iq_data)
        max_val = np.max(envelope) + 1e-6
        norm = envelope / max_val
        return (norm * 32767).astype(np.int16)

    elif demod_type == "fm":
        phase = np.angle(iq_data)
        dphase = np.diff(phase)
        dphase = np.unwrap(dphase)
        audio = np.concatenate([[0], dphase]) * sample_rate / (2 * np.pi)
        audio /= np.max(np.abs(audio)) + 1e-6
        return (audio * 32767).astype(np.int16)

    else:
        raise ValueError(f"Unknown demod type: {demod_type}")
