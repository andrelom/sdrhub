# ==============================================
# File: app/bands.py
# ==============================================
import numpy as np

def generate_band_range(start_mhz, end_mhz, step_khz):
    return list(np.arange(start_mhz * 1e6, end_mhz * 1e6 + 1, step_khz * 1e3))

BAND_CONFIGS = {
    "hf": {
        "frequencies": [3.7e6, 7.1e6, 14.2e6, 21.3e6],
        "sample_rate": 48000,
        "demod": "am",
        "output_dir": "recordings_hf",
    },
    "vhf": {
        "frequencies": generate_band_range(144, 148, 25),
        "sample_rate": 240000,
        "demod": "fm",
        "output_dir": "recordings_vhf",
    },
    "uhf": {
        "frequencies": [433.92e6, 446.0e6],
        "sample_rate": 240000,
        "demod": "fm",
        "output_dir": "recordings_uhf",
    },
    # "fm_wide": {
    #     "frequencies": [88.0e6, 92.1e6, 100.1e6, 107.9e6],
    #     "sample_rate": 500000,
    #     "demod": "fm",
    #     "output_dir": "recordings_fmwide",
    # },
}
