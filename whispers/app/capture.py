# ==============================================
# File: app/capture.py
# ==============================================
import numpy as np
from SoapySDR import *
import SoapySDR
import time

def create_sdr_stream(freq, driver=None, gain=40, sample_rate=48000):
    args = dict(driver=driver) if driver else dict()
    sdr = SoapySDR.Device(args)
    sdr.setSampleRate(SOAPY_SDR_RX, 0, sample_rate)
    sdr.setFrequency(SOAPY_SDR_RX, 0, freq)
    sdr.setGain(SOAPY_SDR_RX, 0, gain)
    stream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
    sdr.activateStream(stream)
    return sdr, stream

def get_capture_buffer(size):
    if not hasattr(get_capture_buffer, "buffer"):
        get_capture_buffer.buffer = np.empty(size, dtype=np.complex64)
    return get_capture_buffer.buffer[:size]

def capture_samples(sdr, stream, duration_secs, sample_rate):
    num_samples = int(sample_rate * duration_secs)
    buff = get_capture_buffer(num_samples)
    samples_received = 0
    start = time.time()
    while samples_received < num_samples:
        if time.time() - start > 5:
            raise TimeoutError("Timeout during capture.")
        sr = sdr.readStream(stream, [buff[samples_received:]], num_samples - samples_received)
        if sr.ret > 0:
            samples_received += sr.ret
    return buff[:samples_received]

def close_sdr_stream(sdr, stream):
    sdr.deactivateStream(stream)
    sdr.closeStream(stream)
