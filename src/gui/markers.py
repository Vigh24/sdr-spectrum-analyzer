from enum import Enum
import numpy as np
from PyQt6.QtCore import Qt
from matplotlib.lines import Line2D

class MarkerType(Enum):
    NORMAL = "Normal"
    DELTA = "Delta"
    BAND = "Band"

class Marker:
    def __init__(self, ax, marker_type=MarkerType.NORMAL):
        self.ax = ax
        self.marker_type = marker_type
        self.x = None
        self.y = None
        self.reference = None  # For delta markers
        self.band_start = None  # For band markers
        self.band_end = None
        
        # Create visual elements
        self.line = None
        self.text = None
        self.band_region = None
        
    def set_position(self, x, y):
        """Set marker position"""
        self.x = x
        self.y = y
        self._update_visuals()
        
    def set_reference(self, ref_marker):
        """Set reference marker for delta measurements"""
        if self.marker_type == MarkerType.DELTA:
            self.reference = ref_marker
            self._update_visuals()
            
    def set_band(self, start, end):
        """Set band start and end for band markers"""
        if self.marker_type == MarkerType.BAND:
            self.band_start = start
            self.band_end = end
            self._update_visuals()
            
    def _update_visuals(self):
        """Update marker visual elements"""
        if self.line:
            self.line.remove()
        if self.text:
            self.text.remove()
        if self.band_region:
            self.band_region.remove()
            
        if self.marker_type == MarkerType.NORMAL:
            self._draw_normal_marker()
        elif self.marker_type == MarkerType.DELTA:
            self._draw_delta_marker()
        elif self.marker_type == MarkerType.BAND:
            self._draw_band_marker()
            
        self.ax.figure.canvas.draw()
        
    def _draw_normal_marker(self):
        """Draw normal marker"""
        if self.x is not None and self.y is not None:
            self.line = self.ax.axvline(x=self.x, color='yellow', linestyle='--', alpha=0.5)
            self.text = self.ax.text(
                self.x, self.y, f'M1\n{self.x:.3f} MHz\n{self.y:.1f} dB',
                color='yellow', bbox=dict(facecolor='black', alpha=0.7)
            )
            
    def _draw_delta_marker(self):
        """Draw delta marker"""
        if self.x is not None and self.y is not None and self.reference:
            self.line = self.ax.axvline(x=self.x, color='cyan', linestyle='--', alpha=0.5)
            dx = self.x - self.reference.x
            dy = self.y - self.reference.y
            self.text = self.ax.text(
                self.x, self.y,
                f'ΔM\n{dx:+.3f} MHz\n{dy:+.1f} dB',
                color='cyan', bbox=dict(facecolor='black', alpha=0.7)
            )
            
    def _draw_band_marker(self):
        """Draw band marker"""
        if self.band_start is not None and self.band_end is not None:
            self.band_region = self.ax.axvspan(
                self.band_start, self.band_end,
                color='green', alpha=0.2
            )
            center = (self.band_start + self.band_end) / 2
            bandwidth = abs(self.band_end - self.band_start)
            self.text = self.ax.text(
                center, self.ax.get_ylim()[1],
                f'BW: {bandwidth:.3f} MHz',
                color='green', bbox=dict(facecolor='black', alpha=0.7),
                horizontalalignment='center'
            ) 