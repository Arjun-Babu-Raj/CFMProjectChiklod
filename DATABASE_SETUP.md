# 🗄️ Database Setup and Configuration Guide

This guide covers SQLite database setup, initialization, backup, and migration for the Village Health Tracking System.

## Table of Contents

- [Quick Start](#quick-start)
- [Database Structure](#database-structure)
- [Initial Setup](#initial-setup)
- [Database Operations](#database-operations)
- [Backup and Restore](#backup-and-restore)
- [Migration Guide](#migration-guide)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Automatic Initialization

The database is automatically initialized when you first run the application:

```bash
# Start the application
streamlit run app.py

# Database 'health_tracking.db' is created automatically on first run
```

### Manual Initialization

To manually initialize or reset the database:

```python
# Using Python
from database import init_database

init_database()
print("Database initialized successfully!")
```

Or using the command line:

```bash
# Initialize database
python -c "from database import init_database; init_database(); print('Database initialized')"
```

---

## Database Structure

### Schema Overview

The system uses SQLite with three main tables:

#### 1. `residents` Table

Stores resident demographic information.

```sql
CREATE TABLE residents (
    unique_id TEXT PRIMARY KEY,           -- VH-YYYY-XXXX format
    name TEXT NOT NULL,                   -- Full name
    age INTEGER,                          -- Age in years
    gender TEXT,                          -- Male/Female/Other
    address TEXT,                         -- Residential address
    phone TEXT,                           -- 10-digit phone number
    village_area TEXT,                    -- Village area/neighborhood
    photo_path TEXT,                      -- Path to profile photo
    registration_date TEXT,               -- YYYY-MM-DD format
    registered_by TEXT                    -- Health worker name
);
```

**Indexes:**
- Primary key on `unique_id`

#### 2. `visits` Table

Records health checkup visits with vitals.

```sql
CREATE TABLE visits (
    visit_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-increment ID
    resident_id TEXT,                            -- Foreign key to residents
    visit_date TEXT,                             -- YYYY-MM-DD format
    visit_time TEXT,                             -- HH:MM:SS format
    health_worker TEXT,                          -- Health worker name
    bp_systolic INTEGER,                         -- Systolic BP (mmHg)
    bp_diastolic INTEGER,                        -- Diastolic BP (mmHg)
    temperature REAL,                            -- Temperature (°F)
    pulse INTEGER,                               -- Pulse rate (bpm)
    weight REAL,                                 -- Weight (kg)
    height REAL,                                 -- Height (cm)
    bmi REAL,                                    -- Body Mass Index
    spo2 INTEGER,                                -- Oxygen saturation (%)
    complaints TEXT,                             -- Chief complaints
    observations TEXT,                           -- Clinical observations
    photo_paths TEXT,                            -- Comma-separated photo paths
    FOREIGN KEY (resident_id) REFERENCES residents(unique_id)
);
```

**Indexes:**
- Primary key on `visit_id`
- Index on `resident_id` for faster lookups
- Index on `visit_date` for date-based queries

#### 3. `medical_history` Table

Stores long-term medical history.

```sql
CREATE TABLE medical_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-increment ID
    resident_id TEXT,                              -- Foreign key to residents
    chronic_conditions TEXT,                       -- Chronic conditions
    past_diagnoses TEXT,                           -- Previous diagnoses
    current_medications TEXT,                      -- Current medications
    allergies TEXT,                                -- Known allergies
    family_history TEXT,                           -- Family health history
    notes TEXT,                                    -- Additional notes
    last_updated TEXT,                             -- Last update timestamp
    updated_by TEXT,                               -- Health worker name
    FOREIGN KEY (resident_id) REFERENCES residents(unique_id)
);
```

**Indexes:**
- Primary key on `history_id`
- Index on `resident_id` for faster lookups

---

## Initial Setup

### Step 1: Create Database Directory

```bash
# Ensure the database directory exists
mkdir -p /path/to/your/app
cd /path/to/your/app
```

### Step 2: Initialize Database

The database is created automatically when you run the app, but you can also initialize it manually:

```bash
# Method 1: Using Python script
python database/schema.py

# Method 2: Using Python REPL
python -c "from database import init_database; init_database()"

# Method 3: Using the test script
python test_system.py
```

### Step 3: Verify Database Creation

```bash
# Check if database file exists
ls -lh health_tracking.db

# Verify tables were created
sqlite3 health_tracking.db ".tables"
# Should show: medical_history  residents  visits
```

### Step 4: Check Database Schema

```bash
# View complete schema
sqlite3 health_tracking.db ".schema"

# Check specific table
sqlite3 health_tracking.db ".schema residents"
```

---

## Database Operations

### Accessing the Database

#### Python API

```python
from database import DatabaseManager

# Create database manager instance
db = DatabaseManager()

# Add a resident
resident_data = {
    'unique_id': 'VH-2026-0001',
    'name': 'John Doe',
    'age': 30,
    'gender': 'Male',
    'address': '123 Main St',
    'phone': '1234567890',
    'village_area': 'North Area',
    'photo_path': None,
    'registration_date': '2026-02-04',
    'registered_by': 'Health Worker 1'
}
db.add_resident(resident_data)

# Get resident
resident = db.get_resident('VH-2026-0001')

# Get all residents
all_residents = db.get_all_residents()
```

#### SQLite Command Line

```bash
# Open database
sqlite3 health_tracking.db

# View all residents
SELECT * FROM residents;

# View visits for a specific resident
SELECT * FROM visits WHERE resident_id = 'VH-2026-0001';

# Count total residents
SELECT COUNT(*) FROM residents;

# Exit
.quit
```

### Common Queries

#### Statistics Queries

```sql
-- Total residents by gender
SELECT gender, COUNT(*) as count 
FROM residents 
GROUP BY gender;

-- Residents by age group
SELECT 
    CASE 
        WHEN age < 18 THEN 'Child (0-17)'
        WHEN age >= 18 AND age < 40 THEN 'Adult (18-39)'
        WHEN age >= 40 AND age < 60 THEN 'Middle Age (40-59)'
        ELSE 'Senior (60+)'
    END as age_group,
    COUNT(*) as count
FROM residents
WHERE age IS NOT NULL
GROUP BY age_group;

-- Visits per health worker
SELECT health_worker, COUNT(*) as visit_count
FROM visits
GROUP BY health_worker
ORDER BY visit_count DESC;

-- Monthly registration trend
SELECT 
    strftime('%Y-%m', registration_date) as month,
    COUNT(*) as registrations
FROM residents
GROUP BY month
ORDER BY month;
```

#### Search Queries

```sql
-- Find resident by name (partial match)
SELECT * FROM residents 
WHERE name LIKE '%John%';

-- Find residents in specific area
SELECT * FROM residents 
WHERE village_area = 'North Area';

-- Find residents with high blood pressure
SELECT DISTINCT r.unique_id, r.name, v.bp_systolic, v.bp_diastolic
FROM residents r
JOIN visits v ON r.unique_id = v.resident_id
WHERE v.bp_systolic > 140 OR v.bp_diastolic > 90;
```

---

## Backup and Restore

### Manual Backup

#### Method 1: Simple File Copy

```bash
# Create backup
cp health_tracking.db health_tracking_backup_$(date +%Y%m%d_%H%M%S).db

# Or with compression
tar -czf health_tracking_backup_$(date +%Y%m%d).tar.gz health_tracking.db uploaded_photos/
```

#### Method 2: SQLite Backup Command

```bash
# Using SQLite backup command
sqlite3 health_tracking.db ".backup health_tracking_backup.db"

# With timestamp
sqlite3 health_tracking.db ".backup health_tracking_backup_$(date +%Y%m%d).db"
```

#### Method 3: SQL Dump

```bash
# Export to SQL file
sqlite3 health_tracking.db .dump > health_tracking_backup.sql

# Compress the backup
gzip health_tracking_backup.sql
```

### Automated Backup Script

Create `backup_database.sh`:

```bash
#!/bin/bash
# Automated backup script for Village Health Tracking System

# Configuration
DB_FILE="health_tracking.db"
BACKUP_DIR="backups"
PHOTOS_DIR="uploaded_photos"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo "Backing up database..."
cp "$DB_FILE" "$BACKUP_DIR/health_tracking_$DATE.db"

# Backup photos
echo "Backing up photos..."
tar -czf "$BACKUP_DIR/photos_$DATE.tar.gz" "$PHOTOS_DIR"

# Export to SQL (for portability)
echo "Creating SQL dump..."
sqlite3 "$DB_FILE" .dump | gzip > "$BACKUP_DIR/health_tracking_$DATE.sql.gz"

# Remove old backups (older than retention period)
echo "Cleaning old backups..."
find "$BACKUP_DIR" -name "health_tracking_*.db" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "photos_*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "health_tracking_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
echo "Location: $BACKUP_DIR"
ls -lh "$BACKUP_DIR" | tail -3
```

Make it executable and run:

```bash
chmod +x backup_database.sh
./backup_database.sh
```

### Schedule Automated Backups

#### Using Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add line to run daily at 2 AM
0 2 * * * /path/to/backup_database.sh >> /path/to/backup.log 2>&1

# Or weekly on Sunday at 3 AM
0 3 * * 0 /path/to/backup_database.sh >> /path/to/backup.log 2>&1
```

#### Using Windows Task Scheduler

Create `backup_database.bat`:

```batch
@echo off
set DB_FILE=health_tracking.db
set BACKUP_DIR=backups
set DATE=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%

mkdir %BACKUP_DIR% 2>nul
copy %DB_FILE% %BACKUP_DIR%\health_tracking_%DATE%.db

echo Backup completed: %DATE%
```

Then schedule via Task Scheduler.

### Restore from Backup

#### Method 1: Replace Database File

```bash
# Stop the application first!
# Then restore
cp backups/health_tracking_20260204.db health_tracking.db

# Restart the application
streamlit run app.py
```

#### Method 2: Restore from SQL Dump

```bash
# Remove existing database
rm health_tracking.db

# Restore from SQL dump
gunzip -c backups/health_tracking_20260204.sql.gz | sqlite3 health_tracking.db

# Or without compression
sqlite3 health_tracking.db < health_tracking_backup.sql
```

#### Method 3: Selective Restore

```python
# Restore specific table
import sqlite3

# Connect to both databases
backup_conn = sqlite3.connect('backups/health_tracking_20260204.db')
current_conn = sqlite3.connect('health_tracking.db')

# Copy specific table
backup_conn.backup(current_conn, pages=1, name='residents')

backup_conn.close()
current_conn.close()
```

---

## Migration Guide

### Migrating from Development to Production

#### Step 1: Export Data

```python
from database import DatabaseManager
import pandas as pd

db = DatabaseManager('dev_health_tracking.db')

# Export all tables
residents_df = db.export_residents_to_df()
visits_df = db.export_visits_to_df()
history_df = db.export_medical_history_to_df()

# Save to CSV
residents_df.to_csv('export_residents.csv', index=False)
visits_df.to_csv('export_visits.csv', index=False)
history_df.to_csv('export_medical_history.csv', index=False)
```

#### Step 2: Import to Production

```python
from database import DatabaseManager, init_database
import pandas as pd

# Initialize production database
init_database('prod_health_tracking.db')
db = DatabaseManager('prod_health_tracking.db')

# Load CSV files
residents_df = pd.read_csv('export_residents.csv')
visits_df = pd.read_csv('export_visits.csv')
history_df = pd.read_csv('export_medical_history.csv')

# Import residents
for _, row in residents_df.iterrows():
    db.add_resident(row.to_dict())

# Import visits
for _, row in visits_df.iterrows():
    db.add_visit(row.to_dict())

# Import medical history
for _, row in history_df.iterrows():
    db.add_or_update_medical_history(row.to_dict())
```

### Database Migration Between Servers

```bash
# On source server
tar -czf health_data_export.tar.gz health_tracking.db uploaded_photos/

# Transfer to destination
scp health_data_export.tar.gz user@destination:/path/

# On destination server
tar -xzf health_data_export.tar.gz
```

---

## Performance Optimization

### Database Maintenance

#### Analyze Database

```bash
# Analyze database for query optimization
sqlite3 health_tracking.db "ANALYZE;"
```

#### Vacuum Database

Reclaim unused space and optimize:

```bash
# Vacuum to optimize
sqlite3 health_tracking.db "VACUUM;"
```

#### Check Integrity

```bash
# Check database integrity
sqlite3 health_tracking.db "PRAGMA integrity_check;"
```

### Performance Tips

1. **Use Indexes** (already implemented in schema.py)
2. **Regular VACUUM** (monthly recommended)
3. **Batch Operations** for bulk inserts
4. **Connection Pooling** for high concurrency

### Monitor Database Size

```bash
# Check database size
du -h health_tracking.db

# Check table sizes
sqlite3 health_tracking.db "
SELECT 
    name,
    SUM(pgsize) as size_bytes,
    ROUND(SUM(pgsize) / 1024.0 / 1024.0, 2) as size_mb
FROM dbstat
GROUP BY name
ORDER BY size_bytes DESC;
"
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Database Locked

**Symptom:** `OperationalError: database is locked`

**Solution:**
```bash
# Close all connections to the database
# Check for processes using the database
lsof health_tracking.db

# Kill the process if needed
kill -9 <PID>

# Or restart the application
```

#### Issue 2: Corrupted Database

**Symptom:** `DatabaseError: database disk image is malformed`

**Solution:**
```bash
# Try to recover
sqlite3 health_tracking.db ".recover" > recovered_data.sql

# Create new database from recovered data
rm health_tracking.db
sqlite3 health_tracking.db < recovered_data.sql

# Or restore from backup
cp backups/latest_backup.db health_tracking.db
```

#### Issue 3: Missing Tables

**Symptom:** `OperationalError: no such table`

**Solution:**
```python
# Reinitialize database
from database import init_database
init_database()
```

#### Issue 4: Foreign Key Constraint Failed

**Symptom:** `IntegrityError: FOREIGN KEY constraint failed`

**Solution:**
- Ensure the referenced resident exists before adding visits
- Check `resident_id` matches `unique_id` in residents table

### Database Recovery Commands

```bash
# Create a new database from existing data
sqlite3 health_tracking.db .dump | sqlite3 new_health_tracking.db

# Export and reimport specific table
sqlite3 health_tracking.db "SELECT * FROM residents;" > residents_backup.txt

# Check for and fix any issues
sqlite3 health_tracking.db "PRAGMA foreign_key_check;"
```

---

## Environment-Specific Configuration

### Development Environment

```python
# dev_config.py
DATABASE_PATH = 'dev_health_tracking.db'
DEBUG = True
BACKUP_ENABLED = False
```

### Production Environment

```python
# prod_config.py
DATABASE_PATH = 'health_tracking.db'
DEBUG = False
BACKUP_ENABLED = True
BACKUP_SCHEDULE = 'daily'
```

### Testing Environment

```python
# test_config.py
DATABASE_PATH = ':memory:'  # In-memory database for testing
DEBUG = True
BACKUP_ENABLED = False
```

---

## Security Best Practices

1. **File Permissions:**
   ```bash
   chmod 600 health_tracking.db  # Owner read/write only
   ```

2. **Regular Backups:**
   - Automated daily backups
   - Off-site backup storage
   - Test restore procedures

3. **Data Encryption:**
   - Consider SQLCipher for encrypted database
   - Encrypt backup files

4. **Access Control:**
   - Limit database file access
   - Use application-level authentication

5. **Audit Trail:**
   - All modifications tracked with `registered_by`/`updated_by`
   - Timestamps on all operations

---

## Additional Resources

- **SQLite Documentation:** https://www.sqlite.org/docs.html
- **Python SQLite3 Module:** https://docs.python.org/3/library/sqlite3.html
- **Database Best Practices:** See README.md section on maintenance

---

## Support

For database-related issues:
1. Check this guide first
2. Review application logs
3. Verify database integrity
4. Restore from backup if needed
5. Create GitHub issue if problem persists

---

**Last Updated:** February 2026  
**Version:** 1.0
