import numpy as np
from scipy import signal
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

class SignalAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        
    def analyze_modulation(self, samples):
        """Analyze modulation characteristics"""
        # Calculate various signal features
        features = {}
        
        # Amplitude variation
        features['amplitude_std'] = np.std(np.abs(samples))
        
        # Phase variation
        analytic = signal.hilbert(samples)
        phase = np.unwrap(np.angle(analytic))
        features['phase_std'] = np.std(np.diff(phase))
        
        # Frequency variation
        freq = np.diff(phase) / (2.0 * np.pi)
        features['freq_std'] = np.std(freq)
        
        # Classify modulation based on features
        if features['amplitude_std'] > 0.2:
            return 'AM'
        elif features['freq_std'] > 0.1:
            return 'FM'
        elif features['phase_std'] > 0.1:
            return 'PM'
        else:
            return 'CW'
            
    def detect_signals(self, freq, power, threshold=-60):
        """Detect and classify signals"""
        # Find peaks above threshold
        peaks, _ = signal.find_peaks(power, height=threshold)
        
        if len(peaks) == 0:
            return []
            
        # Extract features for clustering
        features = np.column_stack([
            freq[peaks],
            power[peaks],
            np.diff(power[peaks], prepend=power[peaks[0]]),
            np.diff(power[peaks], append=power[peaks[-1]])
        ])
        
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        # Cluster signals
        clusters = DBSCAN(eps=0.5, min_samples=2).fit(scaled_features)
        
        # Group detected signals by cluster
        signals = []
        for cluster_id in np.unique(clusters.labels_):
            if cluster_id == -1:  # Noise points
                continue
                
            mask = clusters.labels_ == cluster_id
            cluster_peaks = peaks[mask]
            
            signals.append({
                'center_freq': np.mean(freq[cluster_peaks]),
                'bandwidth': np.ptp(freq[cluster_peaks]),
                'power': np.max(power[cluster_peaks]),
                'num_components': len(cluster_peaks)
            })
            
        return signals 