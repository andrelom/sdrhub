BAND_CONFIGS = {
    "hf": {
        "frequencies": [3.7e6, 7.1e6, 14.2e6, 21.3e6],
        "sample_rate": 48000,
        "demod": "am",
        "output_dir": "recordings_hf",
    },
    "vhf": {
        "frequencies": [145.5e6, 146.52e6],
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
}
