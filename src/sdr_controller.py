import numpy as np
from scipy import signal

class SDRController:
    def __init__(self):
        self.sample_rate = 2.4e6
        self.center_freq = 100e6
        self.gain = 'auto'
        self.t = 0  # Time counter for simulation
        self.modulation_phase = 0  # For FM simulation
        
    def initialize(self):
        """Initialize the simulated SDR device"""
        return True

    def get_samples(self, num_samples=256*1024):
        """Generate simulated RF samples"""
        try:
            # Time points
            t = np.arange(self.t, self.t + num_samples) / self.sample_rate
            
            # Generate various simulated signals
            signals = []
            
            # Main carrier signal
            signals.append(0.5 * np.exp(2j * np.pi * 0 * t))
            
            # AM modulated signal
            am_mod = (1 + 0.5 * np.sin(2 * np.pi * 1000 * t))  # 1 kHz modulation
            signals.append(0.3 * am_mod * np.exp(2j * np.pi * 200e3 * t))
            
            # FM modulated signal
            self.modulation_phase += 2 * np.pi * 1000 * (1/self.sample_rate) * num_samples
            fm_mod = np.exp(2j * np.pi * 50e3 * np.sin(2 * np.pi * 1000 * t + self.modulation_phase))
            signals.append(0.2 * fm_mod * np.exp(2j * np.pi * -400e3 * t))
            
            # Pulsed signal
            pulse = (np.sin(2 * np.pi * 10 * t) > 0).astype(float)
            signals.append(0.4 * pulse * np.exp(2j * np.pi * 600e3 * t))
            
            # Add some noise
            noise = np.random.normal(0, 0.1, len(t)) + 1j * np.random.normal(0, 0.1, len(t))
            signals.append(noise)
            
            # Combine all signals
            samples = sum(signals)
            
            # Update time counter
            self.t += num_samples
            
            return samples
            
        except Exception as e:
            print(f"Error generating samples: {e}")
            return None

    def set_center_freq(self, freq):
        self.center_freq = freq
        
    def set_gain(self, gain):
        self.gain = gain
        
    def set_sample_rate(self, rate):
        self.sample_rate = rate

    def close(self):
        """Clean up (not needed for simulation)"""
        pass 