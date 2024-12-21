import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.gui.main_window import SpectrumAnalyzerWindow
from src.sdr_controller import SDRController
from src.signal_processor import SignalProcessor

def main():
    app = QApplication(sys.argv)
    
    # Set style
    app.setStyle('Fusion')
    
    # Initialize components
    window = SpectrumAnalyzerWindow()
    sdr = SDRController()
    processor = SignalProcessor()
    
    if not sdr.initialize():
        print("Failed to initialize SDR device")
        sys.exit(1)
    
    # Create update timer
    timer = QTimer()
    
    def update():
        samples = sdr.get_samples()
        freq, power = processor.compute_fft(samples)
        window.update_spectrum(freq, power)
    
    # Connect controls
    window.center_freq_spin.valueChanged.connect(
        lambda f: sdr.set_center_freq(f * 1e6))
    window.gain_slider.valueChanged.connect(
        lambda g: sdr.set_gain(g))
    
    # Add these new connections
    window.peak_hold_cb.currentTextChanged.connect(
        lambda mode: processor.reset_peak_hold() if mode == "No Peak Hold" else None)
    window.color_scheme_cb.currentTextChanged.connect(
        lambda scheme: window.change_color_scheme(scheme))
    
    # Connect timer to update function
    timer.timeout.connect(update)
    timer.start(50)  # Update every 50ms for smoother display
    
    # Show window and start event loop
    window.show()
    
    try:
        sys.exit(app.exec())
    finally:
        sdr.close()

if __name__ == "__main__":
    main() 