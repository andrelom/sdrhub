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

        # Sanity checks.
        assert self.sample_rate > 0, "Sample rate must be > 0"
        assert self.duration > 0, "Duration must be > 0"
        assert self.batch_size >= 1, "Batch size must be >= 1"

    def create_sdr(self):
        """
        Create a SoapySDR device instance.
        Returns:
            A SoapySDR device instance configured with the specified driver.
        """
        options = dict(driver=self.driver)
        for attempt in range(3):
            try:
                return SoapySDR.Device(options)
            except Exception as e:
                print(f"[WARN] SDR creation failed (attempt {attempt+1}): {e}")
                time.sleep(1)
        raise RuntimeError("Failed to initialize SDR device after retries.")

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
            elif sr.ret == 0:
                time.sleep(0.01)
            else:
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
        sdr = None
        stream = None
        try:
            sdr = self.create_sdr()
            stream = sdr.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32)
            sdr.activateStream(stream)
            while stop_event is None or not stop_event.is_set():
                for frequency in frequencies:
                    sdr.setFrequency(SoapySDR.SOAPY_SDR_RX, 0, frequency)
                    samples = self.capture_samples(sdr, stream)
                    print(f"[{threading.current_thread().name}] Captured {len(samples)} samples at {frequency/1e6:.3f} MHz")
                    if callback:
                        callback(frequency, samples)
        except Exception as e:
            print(f"[ERROR] Loop scan failed: {e}")
        finally:
            if stream:
                sdr.deactivateStream(stream)
                sdr.closeStream(stream)
            if sdr:
                del sdr

    def batch_scan(self, batch_frequencies, callback=None):
        """
        Perform a batch scan on multiple frequencies using the specified SDR driver.
        Parameters:
            - batch_frequencies: A list of frequencies to scan (in Hz).
            - callback: Optional callback to apply to each (frequency, samples).
        """
        sdr = None
        try:
            sdr = self.create_sdr()
            for frequency in batch_frequencies:
                stream = self.create_sdr_stream(sdr, frequency)
                samples = self.capture_samples(sdr, stream)
                print(f"[BATCH] Captured {len(samples)} samples at {frequency/1e6:.3f} MHz")
                sdr.deactivateStream(stream)
                sdr.closeStream(stream)
                if callback:
                    callback(frequency, samples)
        except Exception as e:
            print(f"[ERROR] Batch failed: {e}")
        finally:
            if sdr:
                del sdr

    def run(self, frequencies, callback=None, stop_events=None):
        """
        Run loop scan in multiple threads, each handling a subset of frequencies.
        Each thread runs loop_scan on its own frequency group until stopped.

        Parameters:
            - frequencies: A list of frequencies to scan (in Hz).
            - callback: Optional function to call with each result.
            - stop_events: Optional list of threading.Event objects to control each thread externally.

        Returns:
            - threads: List of started threading.Thread instances.
            - stop_events: List of corresponding threading.Event objects.
        """
        threads = []
        total_threads = self.max_workers
        groups = [frequencies[i::total_threads] for i in range(total_threads)]
        if stop_events is None:
            stop_events = []
        for i, freq_group in enumerate(groups):
            if not freq_group:
                continue
            if len(stop_events) <= i:
                stop_events.append(threading.Event())
            thread = threading.Thread(
                target=self.loop_scan,
                args=(freq_group,),
                kwargs={"callback": callback, "stop_event": stop_events[i]},
                name=f"LoopScanner-{i+1}",
                daemon=True
            )
            threads.append(thread)
            thread.start()
            print(f"[INFO] Started thread {thread.name} for {len(freq_group)} frequencies.")
        return threads, stop_events


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

    # Optionally, create your own stop_events for external control.
    stop_flags = [threading.Event() for _ in range(scanner.max_workers)]

    # Start loop scan in multiple threads, one group of frequencies per thread.
    threads, stop_flags = scanner.run(
        frequencies=all_frequencies,
        callback=handle_samples,
        stop_events=stop_flags
    )

    # Keep running until interrupted by the user (Ctrl+C).
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping all threads...")
        for flag in stop_flags:
            flag.set()
        for t in threads:
            t.join()
        print("[INFO] All scanner threads stopped gracefully.")
