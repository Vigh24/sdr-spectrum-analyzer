from PyQt6.QtWidgets import QToolBar, QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

class ModernToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QSize(32, 32))
        self.setMovable(False)
        self.setStyleSheet("""
            QToolBar {
                spacing: 10px;
                padding: 5px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #2b2b2b);
                border-bottom: 1px solid #555555;
            }
            QToolButton {
                color: white;
                background: #404040;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                min-width: 80px;
            }
            QToolButton:hover {
                background: #505050;
            }
            QToolButton:pressed {
                background: #606060;
            }
        """)

        # Create button groups
        self.create_file_group()
        self.addSeparator()
        self.create_capture_group()
        self.addSeparator()
        self.create_analysis_group()
        
    def create_file_group(self):
        """Create file operation buttons"""
        file_buttons = [
            ("Save", "💾", "Save current data"),
            ("Load", "📂", "Load data file"),
            ("Export", "📤", "Export as image/CSV"),
        ]
        self.add_button_group(file_buttons)
        
    def create_capture_group(self):
        """Create capture control buttons"""
        capture_buttons = [
            ("Start", "▶️", "Start continuous capture"),
            ("Stop", "⏹️", "Stop capture"),
            ("Single", "⏺️", "Single capture"),
            ("Record", "⏺", "Record data"),
        ]
        self.add_button_group(capture_buttons)
        
    def create_analysis_group(self):
        """Create analysis tool buttons"""
        analysis_buttons = [
            ("Markers", "📍", "Marker tools"),
            ("Measure", "📏", "Measurement tools"),
            ("Analyze", "📊", "Signal analysis"),
            ("Settings", "⚙️", "Settings"),
        ]
        self.add_button_group(analysis_buttons)
        
    def add_button_group(self, buttons):
        """Add a group of buttons"""
        for text, icon, tooltip in buttons:
            btn = QPushButton(icon + " " + text)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    background: #404040;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    padding: 8px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background: #505050;
                }
            """)
            self.addWidget(btn) 