from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
                            QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt

class DatabaseViewer(QDialog):
    def __init__(self, signal_db, parent=None):
        super().__init__(parent)
        self.signal_db = signal_db
        self.setWindowTitle("Signal Database")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Create signal table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Frequency (MHz)", "Bandwidth (MHz)", 
            "Power (dB)", "Modulation", "Description"
        ])
        layout.addWidget(self.table)
        
        # Add control buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Signal")
        delete_btn = QPushButton("Delete Signal")
        refresh_btn = QPushButton("Refresh")
        
        add_btn.clicked.connect(self.add_signal)
        delete_btn.clicked.connect(self.delete_signal)
        refresh_btn.clicked.connect(self.refresh_table)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(refresh_btn)
        layout.addLayout(btn_layout)
        
        self.refresh_table()
        
    def refresh_table(self):
        """Refresh the signal table"""
        signals = self.signal_db.get_signals()
        self.table.setRowCount(len(signals))
        
        for i, signal in signals.iterrows():
            self.table.setItem(i, 0, QTableWidgetItem(str(signal['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(signal['name']))
            self.table.setItem(i, 2, QTableWidgetItem(f"{signal['frequency']:.3f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{signal['bandwidth']:.3f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{signal['power']:.1f}"))
            self.table.setItem(i, 5, QTableWidgetItem(signal['modulation']))
            self.table.setItem(i, 6, QTableWidgetItem(signal['description']))
            
    def add_signal(self):
        """Add a new signal to database"""
        dialog = SignalDialog(self)
        if dialog.exec():
            try:
                self.signal_db.add_signal(
                    name=dialog.name_edit.text(),
                    frequency=float(dialog.freq_edit.text()),
                    bandwidth=float(dialog.bw_edit.text()),
                    power=float(dialog.power_edit.text()),
                    modulation=dialog.mod_edit.text(),
                    description=dialog.desc_edit.text()
                )
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add signal: {str(e)}")
                
    def delete_signal(self):
        """Delete selected signal"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            signal_id = int(self.table.item(current_row, 0).text())
            try:
                self.signal_db.delete_signal(signal_id)
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete signal: {str(e)}")

class SignalDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Signal")
        
        layout = QFormLayout(self)
        
        self.name_edit = QLineEdit()
        self.freq_edit = QLineEdit()
        self.bw_edit = QLineEdit()
        self.power_edit = QLineEdit()
        self.mod_edit = QLineEdit()
        self.desc_edit = QLineEdit()
        
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Frequency (MHz):", self.freq_edit)
        layout.addRow("Bandwidth (MHz):", self.bw_edit)
        layout.addRow("Power (dB):", self.power_edit)
        layout.addRow("Modulation:", self.mod_edit)
        layout.addRow("Description:", self.desc_edit)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons) 