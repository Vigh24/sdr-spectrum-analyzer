import sqlite3
import pandas as pd
from datetime import datetime

class SignalDatabase:
    def __init__(self, db_path="signals.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    frequency REAL,
                    bandwidth REAL,
                    power REAL,
                    modulation TEXT,
                    description TEXT,
                    timestamp DATETIME
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY,
                    signal_id INTEGER,
                    frequency REAL,
                    power REAL,
                    timestamp DATETIME,
                    FOREIGN KEY(signal_id) REFERENCES signals(id)
                )
            """)
    
    def add_signal(self, name, frequency, bandwidth, power, modulation="Unknown", description=""):
        """Add a new signal to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO signals 
                (name, frequency, bandwidth, power, modulation, description, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, frequency, bandwidth, power, modulation, description, datetime.now()))
            return cursor.lastrowid
            
    def add_measurement(self, signal_id, frequency, power):
        """Add a measurement for a signal"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO measurements 
                (signal_id, frequency, power, timestamp)
                VALUES (?, ?, ?, ?)
            """, (signal_id, frequency, power, datetime.now()))
            
    def get_signals(self):
        """Get all signals"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query("SELECT * FROM signals", conn)
            
    def get_measurements(self, signal_id):
        """Get measurements for a signal"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(
                "SELECT * FROM measurements WHERE signal_id = ?", 
                conn, 
                params=(signal_id,)
            ) 
            
    def search_signals(self, criteria):
        """Search signals based on criteria"""
        query = "SELECT * FROM signals WHERE 1=1"
        params = []
        
        if 'name' in criteria:
            query += " AND name LIKE ?"
            params.append(f"%{criteria['name']}%")
            
        if 'freq_min' in criteria:
            query += " AND frequency >= ?"
            params.append(criteria['freq_min'])
            
        if 'freq_max' in criteria:
            query += " AND frequency <= ?"
            params.append(criteria['freq_max'])
            
        if 'power_min' in criteria:
            query += " AND power >= ?"
            params.append(criteria['power_min'])
            
        if 'modulation' in criteria:
            query += " AND modulation = ?"
            params.append(criteria['modulation'])
            
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)
            
    def get_statistics(self):
        """Get signal statistics"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Frequency distribution
            stats['freq_dist'] = pd.read_sql_query(
                "SELECT MIN(frequency) as min_freq, MAX(frequency) as max_freq, "
                "AVG(frequency) as avg_freq FROM signals", conn)
                
            # Power distribution
            stats['power_dist'] = pd.read_sql_query(
                "SELECT MIN(power) as min_power, MAX(power) as max_power, "
                "AVG(power) as avg_power FROM signals", conn)
                
            # Modulation types
            stats['modulations'] = pd.read_sql_query(
                "SELECT modulation, COUNT(*) as count FROM signals "
                "GROUP BY modulation", conn)
                
            return stats 