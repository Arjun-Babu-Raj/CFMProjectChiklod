"""
Database schema initialization for Village Health Tracking System.
Creates SQLite tables for residents, visits, and medical history.
"""

import sqlite3
from typing import Optional


def init_database(db_path: str = "health_tracking.db") -> None:
    """
    Initialize the database with all required tables.
    
    Args:
        db_path: Path to the SQLite database file
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create residents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS residents (
            unique_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            address TEXT,
            phone TEXT,
            village_area TEXT,
            photo_path TEXT,
            registration_date TEXT,
            registered_by TEXT
        )
    """)
    
    # Create visits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            resident_id TEXT,
            visit_date TEXT,
            visit_time TEXT,
            health_worker TEXT,
            bp_systolic INTEGER,
            bp_diastolic INTEGER,
            temperature REAL,
            pulse INTEGER,
            weight REAL,
            height REAL,
            bmi REAL,
            spo2 INTEGER,
            complaints TEXT,
            observations TEXT,
            photo_paths TEXT,
            FOREIGN KEY (resident_id) REFERENCES residents(unique_id)
        )
    """)
    
    # Create medical_history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            resident_id TEXT,
            chronic_conditions TEXT,
            past_diagnoses TEXT,
            current_medications TEXT,
            allergies TEXT,
            family_history TEXT,
            notes TEXT,
            last_updated TEXT,
            updated_by TEXT,
            FOREIGN KEY (resident_id) REFERENCES residents(unique_id)
        )
    """)
    
    # Create indexes for better query performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_resident_id ON visits(resident_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_visit_date ON visits(visit_date)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_medical_history_resident ON medical_history(resident_id)
    """)
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
    print("Database initialized successfully!")
