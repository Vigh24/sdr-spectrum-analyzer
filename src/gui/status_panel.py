class StatusPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Create status indicators
        self.indicators = {
            "device": QLabel("Device: RTL-SDR"),
            "freq": QLabel("CF: 100.000 MHz"),
            "span": QLabel("Span: 2.400 MHz"),
            "rbw": QLabel("RBW: 10 kHz"),
            "peak": QLabel("Peak: -40.0 dB"),
            "marker": QLabel("M1: 0.000 MHz"),
        }
        
        # Add indicators to layout
        for indicator in self.indicators.values():
            indicator.setStyleSheet("""
                QLabel {
                    color: #cccccc;
                    background: #333333;
                    padding: 2px 8px;
                    border: 1px solid #555555;
                    border-radius: 3px;
                }
            """)
            layout.addWidget(indicator)
            
        # Add buffer status
        self.buffer_status = QProgressBar()
        self.buffer_status.setMaximumWidth(100)
        self.buffer_status.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00aa00;
            }
        """)
        layout.addWidget(self.buffer_status) 