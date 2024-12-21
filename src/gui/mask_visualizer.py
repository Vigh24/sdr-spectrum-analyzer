from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np

class MaskVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Create plot
        self.plot = pg.PlotWidget()
        self.plot.setLabel('left', 'Power (dB)')
        self.plot.setLabel('bottom', 'Frequency (MHz)')
        
        # Create mask curves
        self.upper_curve = pg.PlotCurveItem(pen='r')
        self.lower_curve = pg.PlotCurveItem(pen='r')
        self.violation_scatter = pg.ScatterPlotItem(pen='r', brush='r')
        
        self.plot.addItem(self.upper_curve)
        self.plot.addItem(self.lower_curve)
        self.plot.addItem(self.violation_scatter)
        
        self.layout.addWidget(self.plot)
        
    def update_mask(self, mask):
        """Update mask visualization"""
        if not mask.points:
            self.upper_curve.setData([], [])
            self.lower_curve.setData([], [])
            return
            
        # Extract frequencies and limits
        freqs = [p.frequency for p in mask.points]
        upper_limits = [p.upper_limit for p in mask.points]
        lower_limits = [p.lower_limit for p in mask.points]
        
        # Create interpolated points
        x = np.linspace(min(freqs), max(freqs), 1000)
        upper_y = np.interp(x, freqs, upper_limits)
        lower_y = np.interp(x, freqs, lower_limits)
        
        self.upper_curve.setData(x, upper_y)
        self.lower_curve.setData(x, lower_y)
        
    def show_violations(self, violations):
        """Show mask violations"""
        if not violations:
            self.violation_scatter.setData([], [])
            return
            
        x = [v[0] for v in violations]
        y = [v[1] for v in violations]
        self.violation_scatter.setData(x, y) 