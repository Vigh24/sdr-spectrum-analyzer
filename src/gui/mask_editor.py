from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QCheckBox)
from PyQt6.QtCore import Qt
import numpy as np

class MaskEditor(QDialog):
    def __init__(self, mask, parent=None):
        super().__init__(parent)
        self.mask = mask
        self.setWindowTitle("Measurement Mask Editor")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Enable checkbox
        self.enable_cb = QCheckBox("Enable Mask")
        self.enable_cb.setChecked(mask.enabled)
        self.enable_cb.toggled.connect(self.toggle_mask)
        layout.addWidget(self.enable_cb)
        
        # Create point table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "Frequency (MHz)", "Upper Limit (dB)", "Lower Limit (dB)"
        ])
        layout.addWidget(self.table)
        
        # Add control buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Point")
        delete_btn = QPushButton("Delete Point")
        clear_btn = QPushButton("Clear All")
        
        add_btn.clicked.connect(self.add_point)
        delete_btn.clicked.connect(self.delete_point)
        clear_btn.clicked.connect(self.clear_points)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)
        
        self.refresh_table()
        
    def refresh_table(self):
        """Refresh the point table"""
        self.table.setRowCount(len(self.mask.points))
        for i, point in enumerate(self.mask.points):
            self.table.setItem(i, 0, QTableWidgetItem(f"{point.frequency:.3f}"))
            self.table.setItem(i, 1, QTableWidgetItem(f"{point.upper_limit:.1f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{point.lower_limit:.1f}"))
            
    def toggle_mask(self, enabled):
        """Toggle mask enable state"""
        self.mask.enabled = enabled
        
    def add_point(self):
        """Add a new mask point"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem("0.000"))
        self.table.setItem(row, 1, QTableWidgetItem("0.0"))
        self.table.setItem(row, 2, QTableWidgetItem("0.0"))
        
    def delete_point(self):
        """Delete selected point"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            
    def clear_points(self):
        """Clear all points"""
        self.table.setRowCount(0)
        self.mask.points.clear()
        
    def accept(self):
        """Save mask points when dialog is accepted"""
        self.mask.points.clear()
        for row in range(self.table.rowCount()):
            freq = float(self.table.item(row, 0).text())
            upper = float(self.table.item(row, 1).text())
            lower = float(self.table.item(row, 2).text())
            self.mask.add_point(freq, upper, lower)
        super().accept() 