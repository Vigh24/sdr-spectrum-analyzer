from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QSlider, QLabel, QComboBox, QSpinBox,
                            QDockWidget, QToolBar, QStatusBar, QGroupBox, 
                            QTabWidget, QDoubleSpinBox, QCheckBox, QTableWidget,
                            QTableWidgetItem, QLineEdit, QFormLayout, QGridLayout,
                            QProgressBar, QScrollArea, QSplitter, QFrame,
                            QAbstractItemView, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, QSize, QPropertyAnimation
from PyQt6.QtGui import QIcon, QFont, QActionGroup, QAction, QPainter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import pyqtgraph as pg
import colorcet as cc
from .spectrogram_view import SpectrogramView
from .markers import Marker, MarkerType
from src.signal_database import SignalDatabase
from src.measurement_mask import MeasurementMask
from src.trigger_system import TriggerSystem, TriggerType, TriggerMode
from src.gui.database_viewer import DatabaseViewer
from src.gui.mask_editor import MaskEditor
from datetime import datetime
from src.demodulator import Demodulator
from src.signal_analyzer import SignalAnalyzer
from src.gui.mask_visualizer import MaskVisualizer
from src.signal_processor import SignalProcessor
import sounddevice as sd
import wave
import soundfile as sf
from PyQt6 import QtCore

class SpectrumAnalyzerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SDR Spectrum Analyzer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set application style
        self.apply_dark_theme()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main layout with splitters
        self.create_main_layout()
        
        # Initialize components
        self.initialize_components()
        
        # Create status bar
        self.create_status_bar()
        
        # Connect marker buttons
        marker_buttons = self.findChildren(QPushButton)
        for btn in marker_buttons:
            if btn.text() == "Add Marker":
                btn.clicked.connect(self.add_marker)
            elif btn.text() == "Peak Search":
                btn.clicked.connect(self.peak_search)
            elif btn.text() == "Clear All":
                btn.clicked.connect(self.clear_markers)

    def create_main_layout(self):
        """Create the main layout with better organization"""
        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Create splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create left panel (plots)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        self.create_plot_tabs(left_layout)
        
        # Create right panel (controls and measurements)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create scroll area for controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Enable viewport optimization
        scroll.viewport().setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        scroll.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        # Configure smooth scrolling
        scroll_bar = scroll.verticalScrollBar()
        scroll_bar.setSingleStep(10)  # Smaller steps for smoother scrolling
        
        scroll.setFrameShape(QFrame.Shape.NoFrame)  # Remove frame
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #2b2b2b;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #404040;
                min-height: 20px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #505050;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Optimize the scroll widget
        scroll_widget = QWidget()
        scroll_widget.setObjectName("scrollContent")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add control sections to scroll area
        self.create_frequency_controls(scroll_layout)
        self.create_gain_controls(scroll_layout)
        self.create_display_controls(scroll_layout)
        self.create_measurement_panel(scroll_layout)
        self.create_analysis_panel(scroll_layout)
        self.create_recording_controls(scroll_layout)
        
        scroll.setWidget(scroll_widget)
        right_layout.addWidget(scroll)
        
        # Add widgets to splitter
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)
        
        # Set initial sizes (70-30 split)
        self.splitter.setSizes([700, 300])
        self.splitter.setStretchFactor(0, 1)  # Make left side stretchable
        self.splitter.setStretchFactor(1, 0)  # Keep right side fixed width
        
        # Add splitter to main layout
        main_layout.addWidget(self.splitter)

    def initialize_components(self):
        """Initialize all components and connections"""
        # Initialize data storage
        self.waterfall_data = np.zeros((100, 1024))
        
        # Initialize processors
        self.processor = SignalProcessor()
        self.demodulator = Demodulator()
        self.analyzer = SignalAnalyzer()
        
        # Initialize systems
        self.signal_db = SignalDatabase()
        self.measurement_mask = MeasurementMask("Default")
        self.trigger_system = TriggerSystem()
        
        # Initialize state
        self.auto_track_peaks = False
        self.continuous_capture = False
        
        # Setup timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

    def create_toolbar(self):
        """Create main toolbar with better organization"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        toolbar.setStyleSheet("""
            QToolBar {
                spacing: 5px;
                background-color: #1e1e1e;
                border-bottom: 1px solid #555555;
            }
            QToolButton {
                color: white;
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                min-width: 80px;
            }
        """)
        
        # File operations
        toolbar.addAction(self.create_action("Save", "💾", "Save data", self.save_data))
        toolbar.addAction(self.create_action("Load", "📂", "Load data", self.load_data))
        toolbar.addAction(self.create_action("Clear", "🗑️", "Clear display", self.clear_display))
        toolbar.addSeparator()
        
        # Capture controls
        toolbar.addAction(self.create_action("Start", "▶️", "Start capture", self.start_capture))
        toolbar.addAction(self.create_action("Stop", "⏹️", "Stop capture", self.stop_capture))
        toolbar.addAction(self.create_action("Single", "⏺️", "Single capture", self.single_capture))
        
        self.addToolBar(toolbar)

    def create_action(self, text, icon, tooltip, callback):
        """Helper to create toolbar actions"""
        action = QAction(QIcon(icon), text, self)
        action.setToolTip(tooltip)
        action.triggered.connect(callback)
        return action

    def create_plot_tabs(self, layout):
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555555;
                background: #2b2b2b;
            }
            QTabBar::tab {
                background: #404040;
                color: white;
                padding: 5px;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background: #505050;
            }
        """)
        
        # Spectrum tab
        spectrum_widget = QWidget()
        spectrum_layout = QVBoxLayout(spectrum_widget)
        self.create_spectrum_plot(spectrum_layout)
        tab_widget.addTab(spectrum_widget, "Spectrum")
        
        # Waterfall tab
        waterfall_widget = QWidget()
        waterfall_layout = QVBoxLayout(waterfall_widget)
        self.create_waterfall_plot(waterfall_layout)
        tab_widget.addTab(waterfall_widget, "Waterfall")
        
        # Add spectrogram tab
        spectrogram_widget = QWidget()
        spectrogram_layout = QVBoxLayout(spectrogram_widget)
        self.spectrogram_view = SpectrogramView()
        spectrogram_layout.addWidget(self.spectrogram_view)
        tab_widget.addTab(spectrogram_widget, "Spectrogram")
        
        layout.addWidget(tab_widget)

    def create_control_panel(self):
        dock = QDockWidget("Controls", self)
        dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | 
                        QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        
        # Frequency control group
        freq_group = QGroupBox("Frequency Settings")
        freq_layout = QVBoxLayout()
        
        # Center frequency
        center_freq_layout = QHBoxLayout()
        center_freq_layout.addWidget(QLabel("Center Freq (MHz):"))
        self.center_freq_spin = QDoubleSpinBox()
        self.center_freq_spin.setRange(0, 2000)
        self.center_freq_spin.setDecimals(3)
        self.center_freq_spin.setValue(100)
        center_freq_layout.addWidget(self.center_freq_spin)
        freq_layout.addLayout(center_freq_layout)
        
        # Span
        span_layout = QHBoxLayout()
        span_layout.addWidget(QLabel("Span (MHz):"))
        self.span_spin = QDoubleSpinBox()
        self.span_spin.setRange(0.1, 100)
        self.span_spin.setValue(2.4)
        span_layout.addWidget(self.span_spin)
        freq_layout.addLayout(span_layout)
        
        freq_group.setLayout(freq_layout)
        control_layout.addWidget(freq_group)
        
        # Gain control group
        gain_group = QGroupBox("Gain Settings")
        gain_layout = QVBoxLayout()
        
        # Auto gain checkbox
        self.auto_gain_cb = QCheckBox("Auto Gain")
        self.auto_gain_cb.setChecked(True)
        gain_layout.addWidget(self.auto_gain_cb)
        
        # Manual gain control
        gain_slider_layout = QHBoxLayout()
        gain_slider_layout.addWidget(QLabel("Gain:"))
        self.gain_slider = QSlider(Qt.Orientation.Horizontal)
        self.gain_slider.setRange(0, 100)
        self.gain_value_label = QLabel("0 dB")
        gain_slider_layout.addWidget(self.gain_slider)
        gain_slider_layout.addWidget(self.gain_value_label)
        gain_layout.addLayout(gain_slider_layout)
        
        gain_group.setLayout(gain_layout)
        control_layout.addWidget(gain_group)
        
        # Display options group
        display_group = QGroupBox("Display Settings")
        display_layout = QVBoxLayout()
        
        # Add peak tracking checkbox
        self.peak_track_cb = QCheckBox("Auto Track Peaks")
        self.peak_track_cb.setChecked(False)
        self.peak_track_cb.toggled.connect(self.toggle_peak_tracking)
        display_layout.addWidget(self.peak_track_cb)
        
        # Peak hold options
        self.peak_hold_cb = QComboBox()
        self.peak_hold_cb.addItems(["No Peak Hold", "Peak Hold", "Max Hold"])
        display_layout.addWidget(self.peak_hold_cb)
        
        # Color scheme
        self.color_scheme_cb = QComboBox()
        self.color_scheme_cb.addItems(["Default", "Dark", "Viridis", "Plasma"])
        display_layout.addWidget(self.color_scheme_cb)
        
        # Averaging
        avg_layout = QHBoxLayout()
        avg_layout.addWidget(QLabel("Averaging:"))
        self.avg_spin = QSpinBox()
        self.avg_spin.setRange(1, 100)
        self.avg_spin.setValue(1)
        avg_layout.addWidget(self.avg_spin)
        display_layout.addLayout(avg_layout)
        
        display_group.setLayout(display_layout)
        control_layout.addWidget(display_group)
        
        # Add stretch to push controls to the top
        control_layout.addStretch()
        
        dock.setWidget(control_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def create_status_bar(self):
        """Create enhanced status bar"""
        # Create status bar instance
        self.status_bar = self.statusBar()  # Get the status bar and store it
        
        # Create permanent widgets
        self.freq_label = QLabel("CF: 100.000 MHz")
        self.span_label = QLabel("Span: 2.400 MHz")
        self.peak_label = QLabel("Peak: -40.0 dB")
        self.marker_label = QLabel("M1: 0.000 MHz")
        self.ref_level_label = QLabel("Ref: 0 dB")
        
        # Add widgets to status bar
        self.status_bar.addPermanentWidget(self.freq_label)
        self.status_bar.addPermanentWidget(self.span_label)
        self.status_bar.addPermanentWidget(self.peak_label)
        self.status_bar.addPermanentWidget(self.marker_label)
        self.status_bar.addPermanentWidget(self.ref_level_label)

    # Add new methods for toolbar actions
    def start_capture(self):
        """Start continuous capture"""
        self.continuous_capture = True
        self.timer.start(50)  # Update every 50ms
        self.status_bar.showMessage("Capture started")

    def stop_capture(self):
        """Stop continuous capture"""
        self.continuous_capture = False
        self.timer.stop()
        self.status_bar.showMessage("Capture stopped")

    def show_settings(self):
        pass  # Implement settings dialog

    # Update existing methods to work with new UI
    def update_status_bar(self, freq, power):
        peak_idx = np.argmax(power)
        self.peak_label.setText(f"Peak: {power[peak_idx]:.1f} dB")
        self.freq_label.setText(f"Freq: {freq[peak_idx]:.3f} MHz")
        self.bw_label.setText(f"BW: {self.span_spin.value():.1f} MHz")
        self.gain_label.setText(f"Gain: {self.gain_slider.value()} dB")

    def create_spectrum_plot(self, layout):
        # Create matplotlib figure for spectrum
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Initialize plot
        self.ax = self.figure.add_subplot(111)
        self.line, = self.ax.plot([], [])
        self.peak_lines = []
        
        self.ax.set_xlabel('Frequency (MHz)')
        self.ax.set_ylabel('Power (dB)')
        self.ax.grid(True)
        self.ax.set_facecolor('#1e1e1e')
        self.figure.set_facecolor('#2b2b2b')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        
    def create_waterfall_plot(self, layout):
        """Create enhanced waterfall plot"""
        # Create pyqtgraph plot for waterfall
        self.waterfall = pg.PlotWidget()
        self.waterfall.setMinimumHeight(300)
        self.waterfall.setBackground('#1e1e1e')
        
        # Configure axes with better styling
        left_axis = self.waterfall.getAxis('left')
        bottom_axis = self.waterfall.getAxis('bottom')
        
        # Set axis labels with custom style
        label_style = {'color': '#cccccc', 'font-size': '12pt'}
        left_axis.setLabel('Time', units='s', **label_style)
        bottom_axis.setLabel('Frequency', units='MHz', **label_style)
        
        # Set axis colors and grid
        left_axis.setPen('#cccccc')
        bottom_axis.setPen('#cccccc')
        self.waterfall.showGrid(x=True, y=True, alpha=0.3)
        
        # Create and configure image item with better initial settings
        self.waterfall_img = pg.ImageItem()
        self.waterfall_img.setOpts(axisOrder='row-major')  # Better image orientation
        self.waterfall.addItem(self.waterfall_img)
        
        # Set default colormap with better contrast
        self.waterfall_colormap = pg.colormap.get('viridis')
        self.waterfall_img.setLookupTable(self.waterfall_colormap.getLookupTable())
        
        # Add color bar with proper styling
        self.waterfall_bar = pg.ColorBarItem(
            values=(-100, 0),
            colorMap=self.waterfall_colormap,
            label='Power (dB)',
            width=15
        )
        # Style the color bar label
        self.waterfall_bar.axis.setLabel(text='Power', units='dB', **label_style)
        self.waterfall_bar.axis.setPen('#cccccc')
        self.waterfall_bar.setImageItem(self.waterfall_img)
        
        # Configure view settings
        self.waterfall.setAspectLocked(False)  # Allow independent x/y scaling
        self.waterfall.setMouseEnabled(x=True, y=True)  # Enable mouse interaction
        self.waterfall.enableAutoRange(axis='y')  # Auto-range for time axis
        
        layout.addWidget(self.waterfall)

    def save_data(self):
        """Save spectrum data to file"""
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Data", "", "CSV Files (*.csv);;All Files (*)")
        if filename:
            try:
                freq = self.line.get_xdata()
                power = self.line.get_ydata()
                np.savetxt(filename, np.column_stack((freq, power)), 
                          delimiter=',', header='Frequency (MHz),Power (dB)')
            except Exception as e:
                self.show_error("Save Error", f"Failed to save data: {str(e)}")

    def load_data(self):
        """Load spectrum data from file"""
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Data", "", "CSV Files (*.csv);;All Files (*)")
        if filename:
            try:
                data = np.loadtxt(filename, delimiter=',', skiprows=1)
                self.line.set_data(data[:, 0], data[:, 1])
                self.canvas.draw()
            except Exception as e:
                self.show_error("Load Error", f"Failed to load data: {str(e)}")

    def clear_display(self):
        """Clear all display data"""
        self.line.set_data([], [])
        self.waterfall_data.fill(0)
        self.waterfall_img.setImage(self.waterfall_data)
        self.canvas.draw()

    def show_error(self, title, message):
        """Show error dialog"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, title, message)

    def update_spectrum(self, freq, power):
        """Update the spectrum plot"""
        if freq is None or power is None:
            return
            
        self.line.set_data(freq/1e6, power)
        
        # Update peak markers
        self.update_peak_markers(freq/1e6, power)
        
        # Update measurements
        self.update_measurements(freq/1e6, power)
        
        # Update waterfall and spectrogram
        self.update_waterfall(power)
        self.spectrogram_view.update_spectrogram(power)
        
        # Check measurement mask if enabled
        if self.measurement_mask.enabled:
            violations = self.measurement_mask.check_violations(freq/1e6, power)
            if violations:
                self.status_bar.showMessage("Mask violation detected!", 2000)
        
        self.canvas.draw()
        
    def update_peak_markers(self, freq, power):
        # Find peaks
        peaks = self.find_peaks(power)
        
        # Remove old peak markers
        for line in self.peak_lines:
            line.remove()
        self.peak_lines = []
        
        # Add new peak markers
        for peak in peaks:
            line = self.ax.axvline(x=freq[peak], color='r', linestyle='--', alpha=0.5)
            self.peak_lines.append(line)
            
    def update_waterfall(self, power):
        """Update waterfall with improved visualization"""
        # Roll waterfall data
        self.waterfall_data = np.roll(self.waterfall_data, 1, axis=0)
        self.waterfall_data[0] = power
        
        # Get current frequency range
        center = self.center_freq_spin.value()
        span = self.span_spin.value()
        start = center - span/2
        stop = center + span/2
        
        # Calculate time range
        time_range = np.arange(self.waterfall_data.shape[0]) * 0.05  # 50ms per row
        
        # Update image with proper scaling
        self.waterfall_img.setImage(
            self.waterfall_data,
            autoLevels=False,
            levels=(-100, 0),
            rect=QtCore.QRectF(
                start,          # left
                0,             # top
                stop - start,  # width
                time_range[-1] # height in seconds
            )
        )
        
        # Update axes ranges
        self.waterfall.setXRange(start, stop, padding=0)
        self.waterfall.setYRange(0, time_range[-1], padding=0)

    def find_peaks(self, power, threshold=-60):
        # Simple peak finding
        peaks = []
        for i in range(1, len(power)-1):
            if power[i] > threshold and power[i] > power[i-1] and power[i] > power[i+1]:
                peaks.append(i)
        return peaks

    def create_measurement_panel(self, parent_layout):
        """Create measurement panel"""
        # Measurements group
        meas_group = QGroupBox("Measurements")
        meas_layout = QVBoxLayout()
        
        # Markers group
        marker_group = QGroupBox("Markers")
        marker_layout = QVBoxLayout()
        
        # Add marker controls
        self.marker_table = QTableWidget(3, 3)
        self.marker_table.setHorizontalHeaderLabels(["Marker", "Freq (MHz)", "Power (dB)"])
        self.marker_table.verticalHeader().setVisible(False)
        marker_layout.addWidget(self.marker_table)
        
        # Marker buttons
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("Add Marker"))
        btn_layout.addWidget(QPushButton("Peak Search"))
        btn_layout.addWidget(QPushButton("Clear All"))
        marker_layout.addLayout(btn_layout)
        
        # Add marker type selection
        marker_type_layout = QHBoxLayout()
        marker_type_layout.addWidget(QLabel("Marker Type:"))
        self.marker_type_cb = QComboBox()
        self.marker_type_cb.addItems([t.value for t in MarkerType])
        self.marker_type_cb.currentTextChanged.connect(self._change_marker_type)
        marker_type_layout.addWidget(self.marker_type_cb)
        marker_layout.addLayout(marker_type_layout)
        
        marker_group.setLayout(marker_layout)
        meas_layout.addWidget(marker_group)
        
        # Add measurement displays
        self.measurement_labels = {}
        measurements = [
            ("Peak Power:", "N/A dB"),
            ("Center Freq:", "N/A MHz"),
            ("Bandwidth:", "N/A MHz"),
            ("SNR:", "N/A dB"),
        ]
        
        # Update measurement displays with better styling
        for label, value in measurements:
            row = QHBoxLayout()
            label_widget = QLabel(label)
            value_widget = QLabel(value)
            value_widget.setProperty("labelType", "value")  # Apply value style
            value_widget.setMinimumWidth(100)  # Ensure enough space for values
            self.measurement_labels[label.replace(":", "")] = value_widget
            row.addWidget(label_widget)
            row.addWidget(value_widget)
            row.addStretch()  # Add stretch to keep alignment
            meas_layout.addLayout(row)
        
        meas_group.setLayout(meas_layout)
        parent_layout.addWidget(meas_group)

    def create_analysis_panel(self, parent_layout):
        """Create analysis panel"""
        # Signal detection
        detect_group = QGroupBox("Signal Detection")
        detect_layout = QVBoxLayout()
        
        # Threshold control
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Threshold:"))
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(-120, 0)
        self.threshold_spin.setValue(-60)
        self.threshold_spin.setSuffix(" dB")
        threshold_layout.addWidget(self.threshold_spin)
        detect_layout.addLayout(threshold_layout)
        
        # Detection options
        self.auto_detect_cb = QCheckBox("Auto Detection")
        self.mark_peaks_cb = QCheckBox("Mark Peaks")
        self.track_signals_cb = QCheckBox("Track Signals")
        
        detect_layout.addWidget(self.auto_detect_cb)
        detect_layout.addWidget(self.mark_peaks_cb)
        detect_layout.addWidget(self.track_signals_cb)
        
        detect_group.setLayout(detect_layout)
        parent_layout.addWidget(detect_group)
        
        # Add signal classification
        classify_group = QGroupBox("Signal Classification")
        classify_layout = QVBoxLayout()
        
        self.class_result = QLabel("Type: Unknown")
        self.confidence = QLabel("Confidence: 0%")
        self.auto_classify = QCheckBox("Auto Classify")
        
        classify_layout.addWidget(self.class_result)
        classify_layout.addWidget(self.confidence)
        classify_layout.addWidget(self.auto_classify)
        
        classify_group.setLayout(classify_layout)
        parent_layout.addWidget(classify_group)

    def toggle_markers(self):
        """Toggle marker visibility"""
        self.show_markers = not getattr(self, 'show_markers', False)
        if hasattr(self, 'peak_lines'):
            for line in self.peak_lines:
                line.set_visible(self.show_markers)
        self.canvas.draw()

    def show_measurements(self):
        """Update measurement panel with current data"""
        if not hasattr(self, 'line') or len(self.line.get_xdata()) == 0:
            return
            
        freq = self.line.get_xdata()
        power = self.line.get_ydata()
        
        # Find peaks for markers
        peaks = self.find_peaks(power)
        
        # Update marker table
        self.marker_table.setRowCount(len(peaks))
        for i, peak_idx in enumerate(peaks):
            self.marker_table.setItem(i, 0, QTableWidgetItem(f"M{i+1}"))
            self.marker_table.setItem(i, 1, QTableWidgetItem(f"{freq[peak_idx]:.3f}"))
            self.marker_table.setItem(i, 2, QTableWidgetItem(f"{power[peak_idx]:.1f}"))

    def single_capture(self):
        """Perform a single capture"""
        self.continuous_capture = False
        self.timer.stop()
        self.update()  # Trigger one update
        self.status_bar.showMessage("Single capture completed")

    def add_marker(self, marker_type=MarkerType.NORMAL):
        """Add a new marker"""
        marker = Marker(self.ax, marker_type)
        if not hasattr(self, 'markers'):
            self.markers = []
        self.markers.append(marker)
        return marker

    def add_delta_marker(self, reference_marker):
        """Add a delta marker referenced to another marker"""
        marker = self.add_marker(MarkerType.DELTA)
        marker.set_reference(reference_marker)
        return marker

    def add_band_marker(self):
        """Add a band marker"""
        return self.add_marker(MarkerType.BAND)

    def _on_click(self, event):
        if not event.inaxes or not hasattr(self, 'current_marker_type'):
            return
        
        if self.current_marker_type == MarkerType.BAND:
            if not hasattr(self, 'band_start'):
                self.band_start = event.xdata
            else:
                marker = self.add_band_marker()
                marker.set_band(self.band_start, event.xdata)
                delattr(self, 'band_start')
        else:
            marker = self.add_marker(self.current_marker_type)
            marker.set_position(event.xdata, event.ydata)

    def clear_markers(self):
        """Clear all markers"""
        if hasattr(self, 'markers'):
            for marker in self.markers:
                marker.remove()
            self.markers = []
        self.marker_table.setRowCount(0)
        self.canvas.draw()

    def peak_search(self):
        """Find peaks and add markers"""
        if not hasattr(self, 'line') or len(self.line.get_xdata()) == 0:
            return
            
        self.clear_markers()
        freq = self.line.get_xdata()
        power = self.line.get_ydata()
        peaks = self.find_peaks(power)
        
        for peak_idx in peaks:
            marker = self.ax.axvline(x=freq[peak_idx], color='y', linestyle='--', alpha=0.5)
            self.markers.append(marker)
            
            # Update marker table
            row = self.marker_table.rowCount()
            self.marker_table.insertRow(row)
            self.marker_table.setItem(row, 0, QTableWidgetItem(f"M{row+1}"))
            self.marker_table.setItem(row, 1, QTableWidgetItem(f"{freq[peak_idx]:.3f}"))
            self.marker_table.setItem(row, 2, QTableWidgetItem(f"{power[peak_idx]:.1f}"))
        
        self.canvas.draw()

    def _change_marker_type(self, type_name):
        """Change current marker type"""
        self.current_marker_type = MarkerType(type_name)

    def create_advanced_features(self):
        # Initialize systems
        self.signal_db = SignalDatabase()
        self.measurement_mask = MeasurementMask("Default")
        self.trigger_system = TriggerSystem()
        
        # Create advanced features dock
        dock = QDockWidget("Advanced Features", self)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Trigger controls
        trigger_group = QGroupBox("Trigger")
        trigger_layout = QVBoxLayout()
        
        # Trigger type
        trigger_type = QComboBox()
        trigger_type.addItems([t.value for t in TriggerType])
        trigger_type.currentTextChanged.connect(self._change_trigger_type)
        trigger_layout.addWidget(trigger_type)
        
        # Trigger level
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Level:"))
        self.trigger_level = QSpinBox()
        self.trigger_level.setRange(-120, 0)
        self.trigger_level.setValue(-50)
        self.trigger_level.valueChanged.connect(
            lambda v: setattr(self.trigger_system, 'level', v)
        )
        level_layout.addWidget(self.trigger_level)
        trigger_layout.addLayout(level_layout)
        
        # Edge slope control (initially hidden)
        self.edge_slope_cb = QComboBox()
        self.edge_slope_cb.addItems(["Rising", "Falling"])
        self.edge_slope_cb.currentTextChanged.connect(
            lambda v: setattr(self.trigger_system, 'edge_slope', v.lower())
        )
        self.edge_slope_cb.setVisible(False)
        trigger_layout.addWidget(self.edge_slope_cb)
        
        # Pattern control (initially hidden)
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText("Enter trigger pattern (e.g., 1010)")
        self.pattern_edit.textChanged.connect(self._update_trigger_pattern)
        self.pattern_edit.setVisible(False)
        trigger_layout.addWidget(self.pattern_edit)
        
        trigger_group.setLayout(trigger_layout)
        layout.addWidget(trigger_group)
        
        # Mask controls
        mask_group = QGroupBox("Measurement Mask")
        mask_layout = QVBoxLayout()
        
        # Mask enable
        self.mask_enable = QCheckBox("Enable Mask")
        self.mask_enable.toggled.connect(
            lambda v: setattr(self.measurement_mask, 'enabled', v)
        )
        mask_layout.addWidget(self.mask_enable)
        
        # Mask editor button
        mask_edit = QPushButton("Edit Mask")
        mask_edit.clicked.connect(self.show_mask_editor)
        mask_layout.addWidget(mask_edit)
        
        mask_group.setLayout(mask_layout)
        layout.addWidget(mask_group)
        
        # Signal database controls
        db_group = QGroupBox("Signal Database")
        db_layout = QVBoxLayout()
        
        # Database viewer button
        db_view = QPushButton("View Database")
        db_view.clicked.connect(self.show_database_viewer)
        db_layout.addWidget(db_view)
        
        # Quick save signal button
        save_signal = QPushButton("Save Current Signal")
        save_signal.clicked.connect(self.save_current_signal)
        db_layout.addWidget(save_signal)
        
        db_group.setLayout(db_layout)
        layout.addWidget(db_group)
        
        dock.setWidget(widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def show_database_viewer(self):
        """Show the database viewer dialog"""
        viewer = DatabaseViewer(self.signal_db, self)
        viewer.exec()
    
    def show_mask_editor(self):
        """Show the mask editor dialog"""
        editor = MaskEditor(self.measurement_mask, self)
        editor.exec()
    
    def save_current_signal(self):
        """Save current signal to database"""
        if not hasattr(self, 'line') or len(self.line.get_xdata()) == 0:
            return
        
        freq = self.line.get_xdata()
        power = self.line.get_ydata()
        
        # Find main peak
        peak_idx = np.argmax(power)
        peak_freq = freq[peak_idx]
        peak_power = power[peak_idx]
        
        # Estimate bandwidth
        bandwidth = self.estimate_bandwidth(freq, power, peak_idx)
        
        try:
            self.signal_db.add_signal(
                name=f"Signal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                frequency=peak_freq,
                bandwidth=bandwidth,
                power=peak_power
            )
            self.status_bar.showMessage("Signal saved to database", 2000)
        except Exception as e:
            self.show_error("Save Error", f"Failed to save signal: {str(e)}")
        
    def estimate_bandwidth(self, freq, power, peak_idx, threshold_db=3):
        """Estimate signal bandwidth"""
        peak_power = power[peak_idx]
        threshold = peak_power - threshold_db
        
        # Find lower edge
        lower_idx = peak_idx
        while lower_idx > 0 and power[lower_idx] > threshold:
            lower_idx -= 1
        
        # Find upper edge
        upper_idx = peak_idx
        while upper_idx < len(power)-1 and power[upper_idx] > threshold:
            upper_idx += 1
        
        return freq[upper_idx] - freq[lower_idx]

    def _change_trigger_type(self, type_name):
        """Change trigger type"""
        try:
            trigger_type = TriggerType(type_name)
            self.trigger_system.type = trigger_type
            
            # Update UI based on trigger type
            if trigger_type == TriggerType.EDGE:
                # Show edge slope controls
                self.edge_slope_cb.setVisible(True)
                self.pattern_edit.setVisible(False)
            elif trigger_type == TriggerType.PATTERN:
                # Show pattern controls
                self.edge_slope_cb.setVisible(False)
                self.pattern_edit.setVisible(True)
            else:  # LEVEL
                # Show only level control
                self.edge_slope_cb.setVisible(False)
                self.pattern_edit.setVisible(False)
                
        except ValueError:
            print(f"Invalid trigger type: {type_name}")

    def _update_trigger_pattern(self, pattern_text):
        """Update trigger pattern from text input"""
        try:
            # Convert string of 1s and 0s to boolean list
            pattern = [c == '1' for c in pattern_text if c in '01']
            self.trigger_system.pattern = pattern
        except Exception as e:
            print(f"Invalid trigger pattern: {e}")

    def toggle_auto_classify(self, state):
        """Toggle auto classify"""
        self.auto_classify.setChecked(state)
        self.update_measurements(self.line.get_xdata(), self.line.get_ydata())

    def update_measurements(self, freq, power):
        """Update all measurements"""
        if not hasattr(self, 'measurement_labels'):
            return
        
        # Find peak
        peak_idx = np.argmax(power)
        peak_freq = freq[peak_idx]
        peak_power = power[peak_idx]
        
        # Calculate SNR
        noise_floor = np.median(power)
        snr = peak_power - noise_floor
        
        # Calculate bandwidth
        bandwidth = self.estimate_bandwidth(freq, power, peak_idx)
        
        # Update measurement labels
        self.measurement_labels["Peak Power"].setText(f"{peak_power:.1f} dB")
        self.measurement_labels["Center Freq"].setText(f"{peak_freq:.3f} MHz")
        self.measurement_labels["Bandwidth"].setText(f"{bandwidth:.3f} MHz")
        self.measurement_labels["SNR"].setText(f"{snr:.1f} dB")

    def start_demodulation(self):
        """Start audio demodulation"""
        if not hasattr(self, 'line') or len(self.line.get_xdata()) == 0:
            return
        
        samples = self.get_current_samples()
        mode = self.demod_combo.currentText()
        
        if mode == 'AM':
            audio = self.demodulator.demodulate_am(samples)
        elif mode == 'FM':
            audio = self.demodulator.demodulate_fm(samples)
        elif mode in ['USB', 'LSB']:
            audio = self.demodulator.demodulate_ssb(samples, mode)
        else:
            return
        
        # Start audio output
        self.audio_output = sd.OutputStream(
            samplerate=self.demodulator.audio_rate,
            channels=1,
            callback=self.audio_callback
        )
        self.audio_buffer = audio
        self.audio_output.start()
    
    def audio_callback(self, outdata, frames, time, status):
        """Audio output callback"""
        if hasattr(self, 'audio_buffer') and len(self.audio_buffer) > 0:
            chunk = self.audio_buffer[:frames]
            self.audio_buffer = self.audio_buffer[frames:]
            outdata[:, 0] = chunk
        else:
            outdata.fill(0)

    def toggle_peak_tracking(self, enabled):
        """Toggle peak tracking"""
        self.auto_track_peaks = enabled

    def create_frequency_controls(self, parent_layout):
        """Create frequency control group"""
        group = QGroupBox("Frequency Settings")
        layout = QVBoxLayout()
        
        # Center frequency with units and step size
        center_layout = QHBoxLayout()
        center_layout.addWidget(QLabel("Center:"))
        self.center_freq_spin = QDoubleSpinBox()
        self.center_freq_spin.setRange(0, 2000)
        self.center_freq_spin.setDecimals(3)
        self.center_freq_spin.setSuffix(" MHz")
        self.center_freq_spin.setSingleStep(0.1)  # Add step size
        self.center_freq_spin.setStyleSheet("min-width: 120px;")
        center_layout.addWidget(self.center_freq_spin)
        layout.addLayout(center_layout)
        
        # Span control with presets
        span_layout = QHBoxLayout()
        span_layout.addWidget(QLabel("Span:"))
        self.span_spin = QDoubleSpinBox()
        self.span_spin.setRange(0.001, 100)
        self.span_spin.setDecimals(3)
        self.span_spin.setSuffix(" MHz")
        self.span_spin.setSingleStep(0.1)
        self.span_spin.setStyleSheet("min-width: 120px;")
        span_layout.addWidget(self.span_spin)
        
        # Span preset buttons
        span_presets = QHBoxLayout()
        for span in ["1 MHz", "2.4 MHz", "10 MHz"]:
            btn = QPushButton(span)
            btn.clicked.connect(lambda checked, s=span: self.set_span_preset(s))
            btn.setStyleSheet("min-width: 60px;")
            span_presets.addWidget(btn)
        layout.addLayout(span_layout)
        layout.addLayout(span_presets)
        
        # Start/Stop frequency display
        freq_info = QGridLayout()
        freq_info.addWidget(QLabel("Start:"), 0, 0)
        self.start_freq_label = QLabel("0.000 MHz")
        freq_info.addWidget(self.start_freq_label, 0, 1)
        freq_info.addWidget(QLabel("Stop:"), 1, 0)
        self.stop_freq_label = QLabel("2.400 MHz")
        freq_info.addWidget(self.stop_freq_label, 1, 1)
        layout.addLayout(freq_info)
        
        # Connect signals
        self.center_freq_spin.valueChanged.connect(self.update_frequency_range)
        self.span_spin.valueChanged.connect(self.update_frequency_range)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_display_controls(self, parent_layout):
        """Create display settings group"""
        group = QGroupBox("Display Settings")
        layout = QVBoxLayout()
        
        # Trace controls
        trace_group = QGroupBox("Traces")
        trace_layout = QVBoxLayout()
        
        # Peak hold dropdown
        peak_hold_layout = QHBoxLayout()
        peak_hold_layout.addWidget(QLabel("Peak Hold:"))
        self.peak_hold_cb = QComboBox()
        self.peak_hold_cb.addItems(["No Hold", "Peak Hold", "Max Hold", "Min Hold"])
        self.peak_hold_cb.setStyleSheet("QComboBox { min-width: 120px; }")
        peak_hold_layout.addWidget(self.peak_hold_cb)
        trace_layout.addLayout(peak_hold_layout)
        
        # Averaging control
        avg_layout = QHBoxLayout()
        avg_layout.addWidget(QLabel("Averaging:"))
        self.averaging_spin = QSpinBox()
        self.averaging_spin.setRange(1, 100)
        self.averaging_spin.setValue(1)
        self.averaging_spin.setSuffix(" samples")
        self.averaging_spin.setStyleSheet("QSpinBox { min-width: 100px; }")
        avg_layout.addWidget(self.averaging_spin)
        trace_layout.addLayout(avg_layout)
        
        trace_group.setLayout(trace_layout)
        layout.addWidget(trace_group)
        
        # Visual settings
        visual_group = QGroupBox("Visual")
        visual_layout = QVBoxLayout()
        
        # Grid control
        self.grid_cb = QCheckBox("Show Grid")
        self.grid_cb.setChecked(True)
        self.grid_cb.toggled.connect(lambda checked: self.ax.grid(checked))
        visual_layout.addWidget(self.grid_cb)
        
        # Color scheme control
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color Scheme:"))
        self.color_scheme_cb = QComboBox()
        self.color_scheme_cb.addItems(["Dark", "Light", "Viridis", "Plasma"])
        self.color_scheme_cb.setStyleSheet("QComboBox { min-width: 120px; }")
        self.color_scheme_cb.currentTextChanged.connect(self.change_color_scheme)
        color_layout.addWidget(self.color_scheme_cb)
        visual_layout.addLayout(color_layout)
        
        visual_group.setLayout(visual_layout)
        layout.addWidget(visual_group)
        
        # Add some spacing between groups
        layout.addSpacing(10)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_gain_controls(self, parent_layout):
        """Create gain control group"""
        group = QGroupBox("Gain Settings")
        layout = QVBoxLayout()
        
        # Auto gain with LED indicator
        auto_layout = QHBoxLayout()
        self.auto_gain_cb = QCheckBox("Auto Gain")
        self.auto_gain_cb.setChecked(True)
        self.auto_gain_cb.toggled.connect(self.toggle_auto_gain)
        auto_layout.addWidget(self.auto_gain_cb)
        
        # Add LED indicator
        self.auto_gain_led = QLabel("●")
        self.auto_gain_led.setStyleSheet("color: #00ff00; font-size: 16px;")
        auto_layout.addWidget(self.auto_gain_led)
        auto_layout.addStretch()
        layout.addLayout(auto_layout)
        
        # Manual gain control with value display
        gain_layout = QHBoxLayout()
        gain_layout.addWidget(QLabel("Gain:"))
        self.gain_slider = QSlider(Qt.Orientation.Horizontal)
        self.gain_slider.setRange(0, 100)
        self.gain_slider.setEnabled(False)
        gain_layout.addWidget(self.gain_slider)
        
        self.gain_value_label = QLabel("0 dB")
        self.gain_value_label.setMinimumWidth(60)
        self.gain_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        gain_layout.addWidget(self.gain_value_label)
        layout.addLayout(gain_layout)
        
        # Gain presets
        preset_layout = QHBoxLayout()
        for gain in ["0 dB", "20 dB", "40 dB"]:
            btn = QPushButton(gain)
            btn.clicked.connect(lambda checked, g=gain: self.set_gain_preset(g))
            btn.setStyleSheet("min-width: 60px;")
            preset_layout.addWidget(btn)
        layout.addLayout(preset_layout)
        
        # Reference level with units
        ref_layout = QHBoxLayout()
        ref_layout.addWidget(QLabel("Ref Level:"))
        self.ref_level_spin = QSpinBox()
        self.ref_level_spin.setRange(-120, 20)
        self.ref_level_spin.setValue(0)
        self.ref_level_spin.setSuffix(" dB")
        self.ref_level_spin.setStyleSheet("min-width: 100px;")
        ref_layout.addWidget(self.ref_level_spin)
        layout.addLayout(ref_layout)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def toggle_auto_gain(self, enabled):
        """Toggle between auto and manual gain"""
        self.gain_slider.setEnabled(not enabled)
        self.auto_gain_led.setStyleSheet(
            f"color: {'#00ff00' if enabled else '#808080'}; font-size: 16px;"
        )
        if enabled:
            self.gain_value_label.setText("Auto")
        else:
            self.update_gain_value(self.gain_slider.value())

    def update_gain_value(self, value):
        """Update gain value display"""
        self.gain_value_label.setText(f"{value} dB")

    def apply_dark_theme(self):
        """Apply modern dark theme"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                color: #00ff00;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
                font-weight: bold;
                font-size: 13px;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: #2b2b2b;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
                padding: 2px;
            }
            QLabel[labelType="value"] {
                color: #ffffff;
                font-weight: bold;
                background-color: #383838;
                border: 1px solid #505050;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #505050, stop:1 #383838);
                color: white;
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #606060, stop:1 #484848);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #383838, stop:1 #505050);
            }
            QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #383838;
                color: white;
                border: 1px solid #505050;
                border-radius: 4px;
                padding: 5px;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #383838;
                color: white;
                selection-background-color: #505050;
            }
            QSlider::groove:horizontal {
                border: 1px solid #505050;
                height: 8px;
                background: #383838;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #00ff00, stop:1 #00cc00);
                border: 1px solid #00aa00;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QCheckBox {
                spacing: 8px;
                color: #e0e0e0;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #505050;
                border-radius: 4px;
                background: #383838;
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #00ff00, stop:1 #00cc00);
                border-color: #00aa00;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #505050;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QTableWidget {
                background-color: #2b2b2b;
                alternate-background-color: #333333;
                gridline-color: #505050;
                border: 1px solid #505050;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 5px;
                color: #e0e0e0;
            }
            QTableWidget::item:selected {
                background-color: #505050;
            }
            QHeaderView::section {
                background-color: #383838;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #505050;
            }
            QLineEdit {
                background-color: #383838;
                color: white;
                border: 1px solid #505050;
                border-radius: 4px;
                padding: 5px;
                selection-background-color: #505050;
            }
        """)
        
        # Add splitter style
        """
        QSplitter::handle {
            background: #404040;
            width: 2px;
        }
        QSplitter::handle:hover {
            background: #666666;
        }
        """

    def change_color_scheme(self, scheme):
        """Change the color scheme of all plots"""
        if scheme == "Dark":
            # Update main plot
            self.ax.set_facecolor('#1e1e1e')
            self.figure.set_facecolor('#2b2b2b')
            self.ax.tick_params(colors='#cccccc')
            self.ax.xaxis.label.set_color('#cccccc')
            self.ax.yaxis.label.set_color('#cccccc')
            self.line.set_color('#00ff00')
            
            # Update waterfall
            self.waterfall.setBackground('#1e1e1e')
            self.waterfall_colormap = pg.colormap.get('viridis')
            self.waterfall_img.setLookupTable(self.waterfall_colormap.getLookupTable())
            self.waterfall_bar.setColorMap(self.waterfall_colormap)
            
            # Update spectrogram
            self.spectrogram_view.plot.setBackground('#1e1e1e')
            self.spectrogram_view.set_colormap('viridis')
            
        elif scheme == "Light":
            # Similar updates for light theme
            pass
        
        self.canvas.draw()

    def update_frequency_range(self):
        """Update frequency range labels"""
        center = self.center_freq_spin.value()
        span = self.span_spin.value()
        start = center - span/2
        stop = center + span/2
        
        self.start_freq_label.setText(f"{start:.3f} MHz")
        self.stop_freq_label.setText(f"{stop:.3f} MHz")
        
        # Update plot limits
        self.ax.set_xlim(start, stop)
        self.canvas.draw()

    def set_span_preset(self, preset):
        """Set span from preset button"""
        value = float(preset.split()[0])
        self.span_spin.setValue(value)

    def set_gain_preset(self, preset):
        """Set gain from preset button"""
        value = int(preset.split()[0])
        self.gain_slider.setValue(value)
        self.auto_gain_cb.setChecked(False)

    def create_recording_controls(self, parent_layout):
        """Create recording controls"""
        group = QGroupBox("Recording")
        layout = QVBoxLayout()
        
        # Recording controls
        rec_layout = QHBoxLayout()
        self.record_btn = QPushButton("⏺ Record")
        self.record_btn.setCheckable(True)
        self.record_btn.toggled.connect(self.toggle_recording)
        self.record_btn.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:checked {
                background-color: #aa0000;
                color: white;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        rec_layout.addWidget(self.record_btn)
        
        # Recording time display
        self.record_time = QLabel("00:00:00")
        self.record_time.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                background-color: #202020;
                border: 1px solid #555555;
                border-radius: 3px;
            }
        """)
        rec_layout.addWidget(self.record_time)
        layout.addLayout(rec_layout)
        
        # Recording settings
        settings_layout = QFormLayout()
        settings_layout.setSpacing(10)
        
        # Filename input
        self.filename_edit = QLineEdit("capture")
        self.filename_edit.setStyleSheet("""
            QLineEdit {
                color: white;
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                selection-background-color: #666666;
            }
            QLineEdit:focus {
                border: 1px solid #888888;
            }
        """)
        
        # Format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(["IQ Data", "Power Spectrum", "Raw Data"])
        self.format_combo.setStyleSheet("""
            QComboBox {
                color: white;
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                color: white;
                background-color: #404040;
                selection-background-color: #666666;
            }
        """)
        
        # Add labels with improved style
        filename_label = QLabel("Filename:")
        format_label = QLabel("Format:")
        label_style = """
            QLabel {
                color: #cccccc;
                font-size: 12px;
                font-weight: bold;
            }
        """
        filename_label.setStyleSheet(label_style)
        format_label.setStyleSheet(label_style)
        
        settings_layout.addRow(filename_label, self.filename_edit)
        settings_layout.addRow(format_label, self.format_combo)
        layout.addLayout(settings_layout)
        
        # Style the group box
        group.setStyleSheet("""
            QGroupBox {
                color: #00ff00;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_trigger_controls(self, parent_layout):
        """Create trigger controls"""
        group = QGroupBox("Trigger Settings")
        layout = QVBoxLayout()
        
        # Trigger mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.trigger_mode = QComboBox()
        self.trigger_mode.addItems(["Free Run", "Normal", "Single"])
        mode_layout.addWidget(self.trigger_mode)
        layout.addLayout(mode_layout)
        
        # Trigger source
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Source:"))
        self.trigger_source = QComboBox()
        self.trigger_source.addItems(["Level", "External", "Pattern"])
        source_layout.addWidget(self.trigger_source)
        layout.addLayout(source_layout)
        
        # Trigger level
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Level:"))
        self.trigger_level = QSpinBox()
        self.trigger_level.setRange(-120, 0)
        self.trigger_level.setSuffix(" dB")
        level_layout.addWidget(self.trigger_level)
        layout.addLayout(level_layout)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_marker_analysis(self, parent_layout):
        """Create marker analysis panel"""
        group = QGroupBox("Marker Analysis")
        layout = QVBoxLayout()
        
        # Marker measurements
        self.marker_table = QTableWidget(0, 4)
        self.marker_table.setHorizontalHeaderLabels([
            "Marker", "Frequency", "Power", "Delta"
        ])
        layout.addWidget(self.marker_table)
        
        # Marker functions
        btn_layout = QHBoxLayout()
        functions = ["Peak", "Next Peak", "Center", "Delta"]
        for func in functions:
            btn = QPushButton(func)
            btn.clicked.connect(lambda checked, f=func: self.marker_function(f))
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_signal_classifier(self, parent_layout):
        """Create signal classifier panel"""
        group = QGroupBox("Signal Classification")
        layout = QVBoxLayout()
        
        # Classification result
        result_layout = QGridLayout()
        result_layout.addWidget(QLabel("Type:"), 0, 0)
        self.signal_type = QLabel("Unknown")
        result_layout.addWidget(self.signal_type, 0, 1)
        
        result_layout.addWidget(QLabel("Modulation:"), 1, 0)
        self.modulation = QLabel("Unknown")
        result_layout.addWidget(self.modulation, 1, 1)
        
        result_layout.addWidget(QLabel("Confidence:"), 2, 0)
        self.confidence = QLabel("0%")
        result_layout.addWidget(self.confidence, 2, 1)
        layout.addLayout(result_layout)
        
        # Classification controls
        self.auto_classify = QCheckBox("Auto Classify")
        layout.addWidget(self.auto_classify)
        
        # Training controls
        train_layout = QHBoxLayout()
        self.train_btn = QPushButton("Train")
        self.train_btn.clicked.connect(self.train_classifier)
        train_layout.addWidget(self.train_btn)
        
        self.load_model = QPushButton("Load Model")
        self.load_model.clicked.connect(self.load_classifier)
        train_layout.addWidget(self.load_model)
        layout.addLayout(train_layout)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_status_info(self, parent_layout):
        """Create status information panel"""
        group = QGroupBox("System Status")
        layout = QGridLayout()
        
        # Device info
        layout.addWidget(QLabel("Device:"), 0, 0)
        self.device_label = QLabel("RTL-SDR")
        layout.addWidget(self.device_label, 0, 1)
        
        # Sample rate
        layout.addWidget(QLabel("Sample Rate:"), 1, 0)
        self.sample_rate = QLabel("2.4 MSps")
        layout.addWidget(self.sample_rate, 1, 1)
        
        # Buffer status
        layout.addWidget(QLabel("Buffer:"), 2, 0)
        self.buffer_status = QProgressBar()
        layout.addWidget(self.buffer_status, 2, 1)
        
        # Temperature
        layout.addWidget(QLabel("Temperature:"), 3, 0)
        self.temp_label = QLabel("25°C")
        layout.addWidget(self.temp_label, 3, 1)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def toggle_recording(self, enabled):
        """Toggle recording state"""
        if enabled:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start recording data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.filename_edit.text()}_{timestamp}"
            
            # Get selected format
            format_type = self.format_combo.currentText()
            
            if format_type == "IQ Data":
                self.record_file = sf.SoundFile(
                    f"{filename}.wav",
                    mode='w',
                    samplerate=int(self.sample_rate),
                    channels=2,
                    format='WAV'
                )
            elif format_type == "Power Spectrum":
                self.record_file = open(f"{filename}.csv", 'w')
                self.record_file.write("Frequency (MHz),Power (dB)\n")
            else:  # Raw Data
                self.record_file = open(f"{filename}.bin", 'wb')
                
            self.recording = True
            self.record_start_time = datetime.now()
            self.update_record_time()
            
            # Start timer for updating record time display
            self.record_timer = QTimer()
            self.record_timer.timeout.connect(self.update_record_time)
            self.record_timer.start(1000)  # Update every second
            
            self.status_bar.showMessage("Recording started")
            
        except Exception as e:
            self.show_error("Recording Error", f"Failed to start recording: {str(e)}")
            self.record_btn.setChecked(False)

    def stop_recording(self):
        """Stop recording data"""
        if hasattr(self, 'record_file'):
            try:
                if isinstance(self.record_file, sf.SoundFile):
                    self.record_file.close()
                else:
                    self.record_file.close()
                    
                self.recording = False
                if hasattr(self, 'record_timer'):
                    self.record_timer.stop()
                
                self.status_bar.showMessage("Recording stopped")
                
            except Exception as e:
                self.show_error("Recording Error", f"Failed to stop recording: {str(e)}")
        
        self.record_btn.setChecked(False)

    def update_record_time(self):
        """Update recording time display"""
        if hasattr(self, 'record_start_time') and self.recording:
            elapsed = datetime.now() - self.record_start_time
            hours = elapsed.seconds // 3600
            minutes = (elapsed.seconds % 3600) // 60
            seconds = elapsed.seconds % 60
            self.record_time.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def write_recording_data(self, data):
        """Write data to recording file"""
        if not hasattr(self, 'recording') or not self.recording:
            return
        
        try:
            format_type = self.format_combo.currentText()
            
            if format_type == "IQ Data":
                self.record_file.write(data)
            elif format_type == "Power Spectrum":
                freq = self.line.get_xdata()
                power = self.line.get_ydata()
                for f, p in zip(freq, power):
                    self.record_file.write(f"{f:.6f},{p:.2f}\n")
            else:  # Raw Data
                data.tofile(self.record_file)
                
        except Exception as e:
            self.show_error("Recording Error", f"Failed to write data: {str(e)}")
            self.stop_recording()

    def wheelEvent(self, event):
        """Handle smooth scrolling"""
        scroll_area = self.findChild(QScrollArea)
        if scroll_area and event.angleDelta().y() != 0:
            scroll_bar = scroll_area.verticalScrollBar()
            # Make scrolling smoother by using smaller steps
            delta = event.angleDelta().y() / 120  # Standard wheel step
            scroll_bar.setValue(scroll_bar.value() - (delta * scroll_bar.singleStep() * 4))
            event.accept()

    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        
        # Adjust font sizes based on window width
        width = self.width()
        if width > 1920:  # For very large screens
            base_size = 13
            right_width = int(width * 0.25)  # 25% of window width
        elif width > 1440:  # For large screens
            base_size = 12
            right_width = int(width * 0.3)  # 30% of window width
        else:  # For normal screens
            base_size = 11
            right_width = int(width * 0.35)  # 35% of window width
        
        # Update font sizes
        self.setStyleSheet(self.styleSheet().replace(
            "font-size: 12px",
            f"font-size: {base_size}px"
        ))
        
        # Update splitter sizes
        total_width = self.splitter.width()
        self.splitter.setSizes([total_width - right_width, right_width])
        
        # Update scroll area
        scroll_area = self.findChild(QScrollArea)
        if scroll_area:
            scroll_area.viewport().update()

    def create_section_header(self, text):
        """Create styled section header"""
        header = QLabel(text)
        header.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                border-bottom: 2px solid #404040;
            }
        """)
        return header

    def add_tooltips(self):
        """Add helpful tooltips"""
        self.center_freq_spin.setToolTip("Set the center frequency of the display")
        self.span_spin.setToolTip("Set the frequency span to display")
        self.gain_slider.setToolTip("Adjust the receiver gain")
        self.auto_gain_cb.setToolTip("Enable automatic gain control")
        self.peak_hold_cb.setToolTip("Hold peak values on the display")
        # ... add more tooltips ...

    def show_status_message(self, message, duration=2000):
        """Show status message with fade effect"""
        self.status_bar.showMessage(message)
        
        # Create fade out animation
        def fade_out():
            self.status_bar.clearMessage()
        
        # Use timer instead of animation
        QTimer.singleShot(duration, fade_out)

    def get_frequency_rect(self):
        """Get frequency rectangle for waterfall display"""
        center = self.center_freq_spin.value()
        span = self.span_spin.value()
        return QtCore.QRectF(
            center - span/2,  # left
            0,               # top
            span,            # width
            100              # height (number of waterfall rows)
        )

    def setup_waterfall_interaction(self):
        """Setup mouse interaction for waterfall display"""
        proxy = pg.SignalProxy(
            self.waterfall.scene().sigMouseMoved,
            rateLimit=60,
            slot=self.waterfall_mouse_moved
        )
        self.waterfall.scene().sigMouseMoved.connect(self.waterfall_mouse_moved)

    def waterfall_mouse_moved(self, event):
        """Handle mouse movement over waterfall"""
        if self.waterfall.sceneBoundingRect().contains(event[0]):
            mouse_point = self.waterfall.plotItem.vb.mapSceneToView(event[0])
            freq = mouse_point.x()
            time = mouse_point.y()
            
            # Update status bar with cursor position
            self.status_bar.showMessage(
                f"Frequency: {freq:.3f} MHz, Time: {time:.2f} s", 
                1000
            )