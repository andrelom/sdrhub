import sys
import time
import numpy
import threading

from concurrent.futures import ThreadPoolExecutor

# Optional: Include only if SoapySDR is not reliably in sys.path.
sys.path.append("/opt/homebrew/lib/python3.13/site-packages")

import SoapySDR


class SDRScanner:
    """
    SDRScanner encapsulates a multi-frequency SDR scanner with parallel batch support.
    It creates an SDR device per thread, scans batches of frequencies, captures IQ samples,
    and applies an optional callback to each scan result.
    """

    def __init__(
        self,
        driver="airspy",
        gain=40,
        sample_rate=48000,
        duration=1,
        timeout=10,
        batch_size=2,
        max_workers=4,
    ):
        self.driver = driver
        self.gain = gain
        self.sample_rate = sample_rate
        self.duration = duration
        self.timeout = timeout
        self.batch_size = batch_size
        self.max_workers = max_workers

    def create_sdr(self):
        """
        Create a SoapySDR device instance.
        Returns:
            A SoapySDR device instance configured with the specified driver.
        """
        options = dict(driver=self.driver)
        sdr = SoapySDR.Device(options)
        return sdr

    def create_sdr_stream(self, sdr, frequency):
        """
        Create a stream for receiving samples from the SDR.
        Parameters:
            - sdr: The SoapySDR device instance.
            - frequency: The frequency to tune the SDR to (in Hz).
        Returns:
            A SoapySDR stream instance configured for receiving samples.
        """
        sdr.setFrequency(SoapySDR.SOAPY_SDR_RX, 0, frequency)
        sdr.setGain(SoapySDR.SOAPY_SDR_RX, 0, self.gain)
        sdr.setSampleRate(SoapySDR.SOAPY_SDR_RX, 0, self.sample_rate)
        stream = sdr.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32)
        sdr.activateStream(stream)
        return stream

    def capture_samples(self, sdr, stream):
        """
        Capture samples from the SDR stream.
        Parameters:
            - sdr: The SoapySDR device instance.
            - stream: The SoapySDR stream instance.
        Returns:
            A numpy array containing the captured samples.
        """
        num_samples = int(self.sample_rate * self.duration)
        buff = numpy.empty(num_samples, dtype=numpy.complex64)
        received = 0
        start = time.monotonic()
        while received < num_samples:
            if time.monotonic() - start > self.timeout:
                raise TimeoutError("readStream() timed out")
            sr = sdr.readStream(stream, [buff[received:]], num_samples - received)
            if sr.ret > 0:
                received += sr.ret
            elif sr.ret < 0:
                raise IOError(f"readStream error: {sr.ret}")
        return buff[:received]

    def loop_scan(self, frequencies, callback=None, stop_event=None):
        """
        Continuously scan the list of frequencies in a loop using a persistent SDR device.
        Parameters:
            - frequencies: A list of frequencies to scan (in Hz).
            - callback: Optional callback to apply to each (frequency, samples).
            - stop_event: Optional threading.Event to stop the loop gracefully.
        """
        try:
            sdr = self.create_sdr()
            stream = sdr.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32)
            sdr.activateStream(stream)
            while stop_event is None or not stop_event.is_set():
                for frequency in frequencies:
                    sdr.setFrequency(SoapySDR.SOAPY_SDR_RX, 0, frequency)
                    samples = self.capture_samples(sdr, stream)
                    print(f"Captured {len(samples)} samples at {frequency/1e6:.3f} MHz")
                    if callback:
                        callback(frequency, samples)
            sdr.deactivateStream(stream)
            sdr.closeStream(stream)
            del sdr
        except Exception as e:
            print(f"[ERROR] Loop scan failed: {e}")

    def batch_scan(self, batch_frequencies, callback=None):
        """
        Perform a batch scan on multiple frequencies using the specified SDR driver.
        Parameters:
            - batch_frequencies: A list of frequencies to scan (in Hz).
            - callback: Optional callback to apply to each (frequency, samples).
        """
        try:
            sdr = self.create_sdr()
            for frequency in batch_frequencies:
                stream = self.create_sdr_stream(sdr, frequency)
                samples = self.capture_samples(sdr, stream)
                print(f"Captured {len(samples)} samples at {frequency/1e6:.3f} MHz")
                sdr.deactivateStream(stream)
                sdr.closeStream(stream)
                if callback:
                    callback(frequency, samples)
            del sdr
        except Exception as e:
            print(f"[ERROR] Batch failed: {e}")

    def run(self, frequencies, callback=None):
        """
        Run the full parallel scanning job on a list of frequencies.
        Parameters:
            - frequencies: A list of frequencies to scan (in Hz).
            - callback: Optional function to call with each result (frequency, samples).
        """
        batches = [frequencies[i:i + self.batch_size] for i in range(0, len(frequencies), self.batch_size)]
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for batch in batches:
                executor.submit(self.batch_scan, batch, callback)


def handle_samples(frequency, samples):
    """
    Example callback that logs basic stats for each scanned frequency.
    """
    print(f"[RESULT] {frequency/1e6:.3f} MHz → {len(samples)} samples, avg power: {numpy.mean(numpy.abs(samples)):.4f}")


if __name__ == "__main__":
    # Frequencies to scan (in Hz).
    all_frequencies = [
        144.0e6, 145.0e6, 146.0e6, 147.0e6,
        148.0e6, 149.0e6, 150.0e6, 151.0e6,
    ]

    # Initialize scanner with default or custom parameters.
    scanner = SDRScanner(
        driver="airspy",
        gain=40,
        sample_rate=48000,
        duration=1,
        timeout=10,
        batch_size=2,
        max_workers=4,
    )

    # Option 1: Run batch scan once in parallel.
    scanner.run(all_frequencies, callback=handle_samples)

    # Option 2: Uncomment below to run continuous loop scan instead.
    # stop_flag = threading.Event()
    # scanner.loop_scan(all_frequencies, callback=handle_samples, stop_event=stop_flag)
