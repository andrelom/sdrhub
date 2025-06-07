# demodulation.py (com buffer reutilizável)

import numpy as np

def demodulate(iq_data, demod_type, sample_rate, reuse_buffer=False):
    if demod_type == "am":
        envelope = np.abs(iq_data)
        norm = envelope / (np.max(envelope) + 1e-6)
        if reuse_buffer:
            pcm = np.empty_like(norm, dtype=np.int16)
            np.multiply(norm, 32767, out=pcm, casting='unsafe')
        else:
            pcm = (norm * 32767).astype(np.int16)
        return pcm

    elif demod_type == "fm":
        phase = np.angle(iq_data)
        dphase = np.diff(phase)
        dphase = np.unwrap(dphase)
        audio = np.concatenate([[0], dphase]) * sample_rate / (2 * np.pi)
        audio /= np.max(np.abs(audio)) + 1e-6
        if reuse_buffer:
            pcm = np.empty_like(audio, dtype=np.int16)
            np.multiply(audio, 32767, out=pcm, casting='unsafe')
        else:
            pcm = (audio * 32767).astype(np.int16)
        return pcm

    else:
        raise ValueError(f"Unknown demod type: {demod_type}")
