import numpy as np
from scipy.signal import windows, find_peaks
from scipy import signal

class SignalProcessor:
    def __init__(self, sample_rate=2.4e6):
        self.sample_rate = sample_rate
        self.peak_hold = None
        self.max_hold = None

    def compute_fft(self, samples, num_bins=1024):
        """Compute the FFT of the samples"""
        if samples is None:
            return None, None
        
        # Apply window function
        window = windows.blackman(len(samples))
        windowed_samples = samples * window
        
        # Compute FFT
        fft = np.fft.fft(windowed_samples, num_bins)
        fft = np.fft.fftshift(fft)
        
        # Compute frequency axis
        freq = np.fft.fftshift(np.fft.fftfreq(num_bins, 1/self.sample_rate))
        
        # Convert to dB
        power_db = 20 * np.log10(np.abs(fft))
        
        # Apply peak hold if enabled
        if self.peak_hold is None:
            self.peak_hold = power_db
        else:
            self.peak_hold = np.maximum(self.peak_hold * 0.99, power_db)
            
        # Apply max hold if enabled
        if self.max_hold is None:
            self.max_hold = power_db
        else:
            self.max_hold = np.maximum(self.max_hold, power_db)
        
        return freq, power_db
        
    def reset_peak_hold(self):
        self.peak_hold = None
        self.max_hold = None

    def track_peaks(self, freq, power, threshold=-60, min_distance=10):
        """Track peaks over time"""
        if not hasattr(self, 'peak_history'):
            self.peak_history = []
        
        # Find current peaks
        peaks, _ = signal.find_peaks(power, height=threshold, distance=min_distance)
        current_peaks = [(freq[p], power[p]) for p in peaks]
        
        # Match with previous peaks
        if self.peak_history:
            last_peaks = self.peak_history[-1]
            matched_peaks = []
            
            for curr_freq, curr_power in current_peaks:
                # Find closest previous peak
                if last_peaks:
                    distances = [abs(curr_freq - prev_freq) for prev_freq, _ in last_peaks]
                    min_idx = np.argmin(distances)
                    if distances[min_idx] < 0.1:  # 100 kHz maximum tracking distance
                        matched_peaks.append((curr_freq, curr_power))
                    else:
                        matched_peaks.append((curr_freq, curr_power))  # New peak
                else:
                    matched_peaks.append((curr_freq, curr_power))
                    
            self.peak_history.append(matched_peaks)
        else:
            self.peak_history.append(current_peaks)
            
        # Limit history length
        if len(self.peak_history) > 100:
            self.peak_history.pop(0)
            
        return current_peaks