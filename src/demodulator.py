import numpy as np
from scipy import signal

class Demodulator:
    def __init__(self, sample_rate=2.4e6):
        self.sample_rate = sample_rate
        self.last_phase = 0
        self.audio_rate = 48000  # Audio sample rate
        
    def demodulate_am(self, samples):
        """AM demodulation"""
        # Envelope detection
        analytic_signal = signal.hilbert(samples)
        envelope = np.abs(analytic_signal)
        
        # DC removal
        envelope = envelope - np.mean(envelope)
        
        # Resample to audio rate
        audio = signal.resample(envelope, int(len(envelope) * self.audio_rate / self.sample_rate))
        return audio
        
    def demodulate_fm(self, samples):
        """FM demodulation"""
        # Convert to analytic signal
        analytic_signal = signal.hilbert(samples)
        
        # Extract instantaneous phase
        instantaneous_phase = np.unwrap(np.angle(analytic_signal))
        
        # Calculate frequency deviation
        freq_deviation = np.diff(instantaneous_phase) / (2.0 * np.pi) * self.sample_rate
        
        # Resample to audio rate
        audio = signal.resample(freq_deviation, int(len(freq_deviation) * self.audio_rate / self.sample_rate))
        return audio
        
    def demodulate_ssb(self, samples, mode='USB'):
        """SSB demodulation"""
        # Hilbert transform for analytic signal
        analytic = signal.hilbert(samples)
        
        if mode == 'LSB':
            # For LSB, conjugate the analytic signal
            analytic = np.conjugate(analytic)
            
        # Extract real part
        demodulated = np.real(analytic)
        
        # Resample to audio rate
        audio = signal.resample(demodulated, int(len(demodulated) * self.audio_rate / self.sample_rate))
        return audio 