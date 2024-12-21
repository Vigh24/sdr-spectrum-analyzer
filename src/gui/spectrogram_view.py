from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np
import colorcet as cc
from PyQt6 import QtCore

class SpectrogramView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create pyqtgraph plot with better styling
        self.plot = pg.PlotWidget(background='#1e1e1e')
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        
        # Set labels with better styling
        label_style = {'color': '#ffffff', 'font-size': '12pt'}
        self.plot.setLabel('left', 'Time', units='s', **label_style)
        self.plot.setLabel('bottom', 'Frequency', units='MHz', **label_style)
        
        # Create image item
        self.img = pg.ImageItem()
        self.plot.addItem(self.img)
        
        # Set default colormap with better contrast
        self.set_colormap('viridis')
        
        # Add enhanced color bar
        self.colorbar = pg.ColorBarItem(
            values=(-100, 0),
            colorMap=self.colormap,
            label='Power (dB)',
            width=15
        )
        self.colorbar.setImageItem(self.img)
        
        # Initialize data buffer with better size
        self.buffer_size = 1000
        self.data_buffer = np.zeros((self.buffer_size, 1024))
        
        # Add time axis labels
        self.time_axis = self.plot.getAxis('left')
        self.time_axis.setScale(0.05)  # 50ms per pixel
        
        self.layout.addWidget(self.plot)
        
    def set_colormap(self, cmap_name):
        """Change the colormap"""
        if cmap_name == 'viridis':
            colors = pg.colormap.get('viridis').getLookupTable(0.0, 1.0, 256)
        elif cmap_name == 'plasma':
            colors = pg.colormap.get('plasma').getLookupTable(0.0, 1.0, 256)
        elif cmap_name == 'fire':
            pos = np.linspace(0.0, 1.0, len(cc.fire))
            colors = cc.fire
        else:
            pos = np.linspace(0.0, 1.0, len(cc.rainbow))
            colors = cc.rainbow
            
        self.colormap = pg.ColorMap(pos=np.linspace(0.0, 1.0, len(colors)),
                                  color=colors)
        self.img.setLookupTable(self.colormap.getLookupTable())
        
    def update_spectrogram(self, power_data):
        """Update spectrogram with improved visualization"""
        # Roll buffer and add new data
        self.data_buffer = np.roll(self.data_buffer, 1, axis=0)
        self.data_buffer[0] = power_data
        
        # Get frequency range from parent window
        if hasattr(self.parent(), 'center_freq_spin') and hasattr(self.parent(), 'span_spin'):
            center = self.parent().center_freq_spin.value()
            span = self.parent().span_spin.value()
            start = center - span/2
            stop = center + span/2
            
            # Update image with proper scaling
            self.img.setImage(
                self.data_buffer,
                autoLevels=False,
                levels=(-100, 0),
                rect=QtCore.QRectF(
                    start,          # left
                    0,             # top
                    stop - start,  # width
                    self.buffer_size  # height
                )
            )
            
            # Update axes ranges
            self.plot.setXRange(start, stop)
            self.plot.setYRange(0, self.buffer_size)
        else:
            # Fallback if parent window not available
            self.img.setImage(self.data_buffer, autoLevels=False, levels=(-100, 0))

    def get_display_rect(self):
        """Get display rectangle based on current settings"""
        if hasattr(self.parent(), 'center_freq_spin') and hasattr(self.parent(), 'span_spin'):
            center = self.parent().center_freq_spin.value()
            span = self.parent().span_spin.value()
            return QtCore.QRectF(
                center - span/2,  # left
                0,               # top
                span,           # width
                self.buffer_size * 0.05  # height (time)
            )
        return QtCore.QRectF(0, 0, 1, 1)