# SDR Spectrum Analyzer
A modern spectrum analyzer application for Software Defined Radio (SDR) devices built with PyQt6.
## Features
- Real-time spectrum display with waterfall and spectrogram views
 Advanced signal measurements and analysis
 Marker system for precise measurements
 Recording capabilities (IQ, Power Spectrum, Raw Data)
 Signal detection and classification
 Configurable trigger system
 Measurement masks
 Dark theme UI with customizable settings
## Requirements
- Python 3.8+
 PyQt6
 NumPy
 Matplotlib
 PyQtGraph
 SoundDevice
 SoundFile
 Additional dependencies in requirements.txt
## Installation
1. Clone the repository:
bash
git clone https://github.com/Vigh24/sdr-spectrum-analyzer.git
cd sdr-spectrum-analyzer

2. Install dependencies:
bash
pip install -r requirements.txt

## Usage

Run the application:
bash
python -m src.main

## Controls

### Frequency Settings
- Center frequency adjustment
- Span control with presets
- Start/Stop frequency display

### Gain Settings
- Auto/Manual gain control
- Reference level adjustment
- Gain presets

### Display Settings
- Peak hold options
- Averaging control
- Grid display
- Color scheme selection

### Measurements
- Multiple marker types
- Peak search
- Delta measurements
- Automated measurements

### Recording
- Multiple format support (IQ, Spectrum, Raw)
- Timestamp-based file naming
- Recording duration display

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
