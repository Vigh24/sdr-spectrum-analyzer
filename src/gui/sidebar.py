class QuickAccessSidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(50)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Quick access buttons
        buttons = [
            ("📊", "Spectrum"),
            ("🌈", "Waterfall"),
            ("📈", "Spectrogram"),
            ("📏", "Measure"),
            ("🔍", "Zoom"),
            ("💾", "Save"),
        ]
        
        for icon, tooltip in buttons:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background: #404040;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background: #505050;
                }
            """)
            layout.addWidget(btn)
            
        layout.addStretch() 