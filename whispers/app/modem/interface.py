# ==============================================
# File: app/modem/interface.py
# ==============================================
class Demodulator:
    def demodulate(self, iq_data, sample_rate):
        raise NotImplementedError("Demodulate method must be implemented by subclasses")
