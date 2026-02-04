#!/usr/bin/env python3
"""
Database Initialization and Setup Script
Run this script to initialize or reset the Village Health Tracking System database.
"""

import os
import sys
from datetime import datetime

def main():
    """Initialize the database with proper setup."""
    print("=" * 60)
    print("Village Health Tracking System - Database Initialization")
    print("=" * 60)
    print()
    
    # Check if database already exists
    db_file = "health_tracking.db"
    db_exists = os.path.exists(db_file)
    
    if db_exists:
        print(f"⚠️  Database '{db_file}' already exists!")
        print()
        response = input("Do you want to reset the database? This will DELETE all data! (yes/no): ")
        
        if response.lower() != 'yes':
            print("Initialization cancelled.")
            return 0
        
        # Create backup before resetting
        print()
        print("Creating backup before reset...")
        backup_file = f"health_tracking_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        try:
            import shutil
            shutil.copy(db_file, backup_file)
            print(f"✓ Backup created: {backup_file}")
        except Exception as e:
            print(f"✗ Backup failed: {e}")
            print("Continuing without backup...")
        
        # Remove existing database
        try:
            os.remove(db_file)
            print(f"✓ Removed existing database")
        except Exception as e:
            print(f"✗ Failed to remove database: {e}")
            return 1
    
    # Initialize new database
    print()
    print("Initializing new database...")
    
    try:
        from database import init_database
        init_database(db_file)
        print(f"✓ Database initialized successfully!")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Verify database
    print()
    print("Verifying database...")
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        expected_tables = ['residents', 'visits', 'medical_history']
        found_tables = [table[0] for table in tables]
        
        print()
        print("Tables created:")
        for table in expected_tables:
            if table in found_tables:
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table} (MISSING)")
        
        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = cursor.fetchall()
        
        print()
        print(f"Indexes created: {len(indexes)}")
        for index in indexes:
            print(f"  - {index[0]}")
        
        # Get database size
        db_size = os.path.getsize(db_file)
        print()
        print(f"Database size: {db_size} bytes ({db_size/1024:.2f} KB)")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return 1
    
    # Create directories
    print()
    print("Creating required directories...")
    
    directories = ['uploaded_photos', 'backups']
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"  ✓ {directory}/")
        except Exception as e:
            print(f"  ✗ {directory}/ - {e}")
    
    # Summary
    print()
    print("=" * 60)
    print("✓ Database Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Configure authentication in config.yaml")
    print("2. Run the application: streamlit run app.py")
    print("3. Log in and start registering residents")
    print()
    print("For backup: Run ./backup_database.sh (or .bat on Windows)")
    print("For testing: Run python test_system.py")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
