# SDR Spectrum Analyzer
A modern spectrum analyzer application for Software Defined Radio (SDR) devices built with PyQt6, offering real-time spectrum analysis, waterfall displays, and advanced signal processing capabilities.
![SDR Spectrum Analyzer](screenshots/main.png)
## Features
### Display Modes
 Real-time spectrum display with configurable settings
 Waterfall view with time history and color mapping
 Spectrogram visualization for signal analysis
 Multiple color schemes and display options
### Signal Analysis
 Multi-marker system for precise measurements
 Automatic peak detection and tracking
 Signal strength and bandwidth measurements
 SNR (Signal-to-Noise Ratio) calculations
 Advanced signal classification
### Core Features
 Automatic and manual gain control
 Configurable trigger system with multiple modes
 Real-time signal recording (IQ, Spectrum, Raw)
 Measurement masks for signal monitoring
 Frequency presets and quick settings
### User Interface
 Modern dark theme with customizable settings
 Intuitive controls and layouts
 Real-time measurement updates
 Comprehensive status information
 Smooth scrolling and responsive design
## Requirements
- Python 3.8+
 PyQt6
 NumPy
 Matplotlib
 PyQtGraph
 Additional dependencies in requirements.txt
## Installation
1. Clone the repository:
git clone https://github.com/Vigh24/sdr-spectrum-analyzer.git
cd sdr-spectrum-analyzer
2. Install the required dependencies:
pip install -r requirements.txt
3. Run the application:
python main.py

### Quick Start Guide

1. **Frequency Settings**
   - Set center frequency using the spin box
   - Adjust span with presets (1 MHz, 2.4 MHz, 10 MHz)
   - Monitor start/stop frequencies

2. **Gain Control**
   - Toggle Auto Gain for automatic adjustment
   - Use slider for manual gain control
   - Set reference level as needed

3. **Display Options**
   - Enable/disable grid
   - Choose color scheme
   - Adjust peak hold and averaging

4. **Measurements**
   - Add markers for precise readings
   - Use peak search for signal detection
   - Monitor bandwidth and power levels

5. **Recording**
   - Select recording format
   - Set filename
   - Start/stop recording with duration display

## Project Structure
sdr-spectrum-analyzer/
├── src/
│ ├── gui/
│ │ ├── main_window.py # Main application window
│ │ ├── spectrogram_view.py
│ │ ├── markers.py
│ │ └── ...
│ ├── signal_processor.py # Signal processing logic
│ ├── sdr_controller.py # SDR device control
│ └── main.py # Application entry point
├── requirements.txt
├── LICENSE
└── README.md


## Contributing

Contributions are welcome! Please feel free to submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/NewFeature`)
3. Commit your changes (`git commit -m 'Add some NewFeature'`)
4. Push to the branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- PyQt6 for the GUI framework
- NumPy and SciPy for signal processing
- PyQtGraph for efficient plotting
- The SDR community for inspiration

## Contact

Project Link: [https://github.com/Vigh24/sdr-spectrum-analyzer](https://github.com/Vigh24/sdr-spectrum-analyzer)