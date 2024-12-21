MODERN_STYLE = """
    QTabWidget::pane {
        border: 1px solid #555555;
        background: #2b2b2b;
        border-radius: 5px;
    }
    QTabBar::tab {
        background: #404040;
        color: #cccccc;
        padding: 8px 15px;
        border: 1px solid #555555;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        min-width: 100px;
    }
    QTabBar::tab:selected {
        background: #505050;
        color: white;
    }
    QTabBar::tab:hover {
        background: #454545;
    }
    
    QGroupBox {
        background: #333333;
        border: 1px solid #555555;
        border-radius: 5px;
        margin-top: 10px;
        padding: 15px;
        font-weight: bold;
    }
    QGroupBox::title {
        color: #00aa00;
    }
    
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #505050, stop:1 #404040);
        color: white;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 5px 15px;
        min-width: 80px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #606060, stop:1 #505050);
    }
    
    QComboBox, QSpinBox, QDoubleSpinBox {
        background: #404040;
        color: white;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 5px;
        min-width: 100px;
    }
    
    QSlider::groove:horizontal {
        border: 1px solid #555555;
        height: 8px;
        background: #404040;
        margin: 2px 0;
        border-radius: 4px;
    }
    QSlider::handle:horizontal {
        background: #00aa00;
        border: 1px solid #008800;
        width: 18px;
        margin: -5px 0;
        border-radius: 9px;
    }
""" 