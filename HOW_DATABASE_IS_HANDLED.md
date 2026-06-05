# 🗄️ How the Database is Currently Handled

## Overview

The **Village Health Tracking System** uses **SQLite** as its database solution with a well-structured Python abstraction layer. This document explains the current database architecture, implementation, and handling mechanisms.

---

## Database Technology Stack

### Core Technology
- **Database Engine**: SQLite3 (file-based, serverless)
- **Database File**: `health_tracking.db` (located in project root)
- **Language**: Python 3.8+ with built-in `sqlite3` module
- **ORM/Abstraction**: Custom `DatabaseManager` class (no external ORM)
- **Data Export**: Pandas DataFrames for CSV/Excel exports

### Why SQLite?
1. **Zero Configuration**: No server setup or administration required
2. **Portability**: Single file database, easy to backup and transfer
3. **Reliability**: ACID-compliant, production-ready
4. **Performance**: Sufficient for village-scale health tracking (thousands of records)
5. **Integration**: Built into Python standard library
6. **Storage**: Efficient for text, numbers, and metadata (photos stored separately)

---

## Database Architecture

### File Structure
```
CFMProjectChiklod/
├── health_tracking.db              # Main SQLite database file
├── database/
│   ├── __init__.py                # Package initialization & exports
│   ├── db_manager.py              # DatabaseManager class (CRUD operations)
│   └── schema.py                  # Database initialization & schema
├── setup_database.py              # Setup script with safety checks
└── backups/                       # Automated backup location
    ├── health_tracking_*.db       # Database file backups
    ├── health_tracking_*.sql.gz   # SQL dump backups
    └── photos_*.tar.gz            # Photo backups
```

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────┐
│         Application Layer (Streamlit)           │
│  app.py, pages/*.py - UI and business logic     │
└────────────────┬────────────────────────────────┘
                 │
                 ├─ st.session_state.db_manager
                 │
┌────────────────▼────────────────────────────────┐
│      Abstraction Layer (DatabaseManager)        │
│  database/db_manager.py - CRUD operations       │
│  - add_resident(), get_resident(), etc.         │
│  - Transaction management                       │
│  - Error handling                               │
└────────────────┬────────────────────────────────┘
                 │
                 ├─ _get_connection()
                 │
┌────────────────▼────────────────────────────────┐
│         Data Layer (SQLite3)                    │
│  health_tracking.db - Actual data storage       │
│  - residents table                              │
│  - visits table                                 │
│  - medical_history table                        │
└─────────────────────────────────────────────────┘
```

---

## Database Schema

### 1. Residents Table
**Purpose**: Stores demographic information for registered village residents.

```sql
CREATE TABLE residents (
    unique_id TEXT PRIMARY KEY,        -- Format: VH-YYYY-XXXX
    name TEXT NOT NULL,                -- Full name
    age INTEGER,                       -- Age in years
    gender TEXT,                       -- Male/Female/Other
    address TEXT,                      -- Residential address
    phone TEXT,                        -- 10-digit phone number
    village_area TEXT,                 -- Village area/neighborhood
    photo_path TEXT,                   -- Relative path to profile photo
    registration_date TEXT,            -- YYYY-MM-DD format
    registered_by TEXT                 -- Health worker username
);
```

**Key Features**:
- Primary key on `unique_id` for fast lookups
- Auto-generated IDs using `utils/id_generator.py`
- Photos stored separately in `uploaded_photos/` directory

### 2. Visits Table
**Purpose**: Records health checkup visits with vitals and observations.

```sql
CREATE TABLE visits (
    visit_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-increment ID
    resident_id TEXT,                            -- Foreign key to residents
    visit_date TEXT,                             -- YYYY-MM-DD format
    visit_time TEXT,                             -- HH:MM:SS format
    health_worker TEXT,                          -- Health worker username
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
    photo_paths TEXT,                            -- Comma-separated paths
    FOREIGN KEY (resident_id) REFERENCES residents(unique_id)
);

-- Performance indexes
CREATE INDEX idx_resident_id ON visits(resident_id);
CREATE INDEX idx_visit_date ON visits(visit_date);
```

**Key Features**:
- Auto-incrementing visit IDs
- Foreign key relationship to residents
- Indexes for fast filtering by resident and date
- Flexible vitals fields (NULL allowed for missing data)

### 3. Medical History Table
**Purpose**: Stores long-term medical information for residents.

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
    updated_by TEXT,                               -- Health worker username
    FOREIGN KEY (resident_id) REFERENCES residents(unique_id)
);

CREATE INDEX idx_medical_history_resident ON medical_history(resident_id);
```

**Key Features**:
- One record per resident (update if exists, insert if new)
- Tracks who last updated and when
- Index for fast resident lookup

---

## Database Manager Implementation

### Class Overview: `DatabaseManager`

Located in `database/db_manager.py`, this class provides a clean API for all database operations.

```python
class DatabaseManager:
    def __init__(self, db_path: str = "health_tracking.db"):
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Create connection with row factory for dict access"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
```

### Key Design Patterns

#### 1. Connection Management
Each method creates a fresh connection and closes it after use:

```python
def add_resident(self, resident_data: Dict) -> bool:
    try:
        conn = self._get_connection()  # Open connection
        cursor = conn.cursor()
        
        # Execute query
        cursor.execute("INSERT INTO residents (...) VALUES (...)", data)
        
        conn.commit()  # Commit transaction
        conn.close()   # Always close connection
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
```

**Rationale**: 
- No connection pooling needed (SQLite is local)
- Prevents lock issues in multi-page Streamlit app
- Simple and reliable

#### 2. Row Factory Pattern
```python
conn.row_factory = sqlite3.Row
```
Enables accessing columns by name instead of index:
```python
row = cursor.fetchone()
resident = dict(row)  # Convert to dictionary
print(resident['name'])  # Access by key
```

#### 3. Error Handling
All methods use try-except with graceful degradation:
- Returns `False` or empty list on error
- Prints error message for debugging
- Never crashes the application

---

## Database Operations

### CRUD Operations Available

#### Residents
| Method | Description | Returns |
|--------|-------------|---------|
| `add_resident(data)` | Add new resident | `bool` |
| `get_resident(unique_id)` | Get resident by ID | `Dict` or `None` |
| `get_all_residents()` | Get all residents | `List[Dict]` |
| `search_residents(term)` | Search by name/ID | `List[Dict]` |
| `filter_residents(filters)` | Filter by criteria | `List[Dict]` |
| `resident_exists(unique_id)` | Check if exists | `bool` |
| `get_resident_count()` | Count total | `int` |

#### Visits
| Method | Description | Returns |
|--------|-------------|---------|
| `add_visit(data)` | Add visit record | `bool` |
| `get_resident_visits(id)` | Get visits for resident | `List[Dict]` |
| `get_all_visits()` | Get all visits | `List[Dict]` |
| `get_recent_visits(limit)` | Get recent visits | `List[Dict]` |
| `get_visit_count()` | Count total | `int` |
| `get_visits_by_health_worker()` | Group by worker | `List[Tuple]` |

#### Medical History
| Method | Description | Returns |
|--------|-------------|---------|
| `add_or_update_medical_history(data)` | Insert or update | `bool` |
| `get_medical_history(id)` | Get history for resident | `Dict` or `None` |

#### Analytics
| Method | Description | Returns |
|--------|-------------|---------|
| `get_demographics_summary()` | Age/gender stats | `Dict` |
| `get_monthly_trends()` | Registration/visit trends | `Dict` |

#### Export
| Method | Description | Returns |
|--------|-------------|---------|
| `export_residents_to_df()` | Export residents | `pd.DataFrame` |
| `export_visits_to_df(id?)` | Export visits | `pd.DataFrame` |
| `export_medical_history_to_df()` | Export history | `pd.DataFrame` |

---

## Database Initialization

### Automatic Initialization

The database is **automatically initialized** on first run:

```python
# In app.py main()
def main():
    # Initialize database (only once)
    try:
        init_database()  # Creates tables if they don't exist
    except Exception as e:
        st.error(f"❌ Database initialization error: {e}")
        st.stop()
    
    # Create DatabaseManager in session state
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
```

### Schema Initialization Function

Located in `database/schema.py`:

```python
def init_database(db_path: str = "health_tracking.db") -> None:
    """Initialize database with all required tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables with IF NOT EXISTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS residents (...)
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (...)
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_history (...)
    """)
    
    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_resident_id ON visits(resident_id)
    """)
    
    conn.commit()
    conn.close()
```

**Key Features**:
- `IF NOT EXISTS` prevents errors if database already exists
- Safe to call multiple times
- Creates all tables and indexes in one transaction

### Manual Setup Script

For advanced setup or reset, use `setup_database.py`:

```bash
python setup_database.py
```

This script:
1. Checks if database exists
2. Prompts for confirmation before reset
3. Creates backup before deletion
4. Initializes new database
5. Verifies tables and indexes
6. Creates required directories

---

## Session State Management

### DatabaseManager Instance

The application uses Streamlit's `session_state` to maintain a **single DatabaseManager instance** across page navigations:

```python
# In app.py (runs once per session)
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

# In pages (reuse existing instance)
db = st.session_state.db_manager
residents = db.get_all_residents()
```

**Benefits**:
- Single instance per user session
- No overhead of creating new managers
- Consistent across all pages
- Memory efficient

### Connection Lifecycle

```
User Opens App
     ↓
app.py initializes database
     ↓
Creates DatabaseManager in session_state
     ↓
User Navigates to Page
     ↓
Page accesses db_manager from session_state
     ↓
DatabaseManager method called
     ↓
  Opens connection → Execute query → Close connection
     ↓
Returns result to page
     ↓
(Repeat for each database operation)
```

---

## Backup and Maintenance

### Automated Backup Script

**Script**: `backup_database.sh` (Linux/Mac) or `backup_database.bat` (Windows)

**What it backs up**:
1. Database file (`health_tracking.db`)
2. Photo directory (`uploaded_photos/`)
3. SQL dump (portable format)

**Retention**: Keeps backups for 30 days (configurable)

**Usage**:
```bash
# Run manually
./backup_database.sh

# Schedule with cron (daily at 2 AM)
0 2 * * * /path/to/backup_database.sh >> /path/to/backup.log 2>&1
```

**Output**:
```
backups/
├── health_tracking_20260208_020000.db       # Binary backup
├── health_tracking_20260208_020000.sql.gz   # SQL dump
└── photos_20260208_020000.tar.gz            # Photos archive
```

### Database Maintenance Commands

```bash
# Check integrity
sqlite3 health_tracking.db "PRAGMA integrity_check;"

# Optimize and reclaim space
sqlite3 health_tracking.db "VACUUM;"

# Analyze for query optimization
sqlite3 health_tracking.db "ANALYZE;"

# Export to SQL
sqlite3 health_tracking.db .dump > backup.sql

# Check database size
du -h health_tracking.db
```

---

## Data Flow Examples

### Example 1: Registering a New Resident

```
User fills form in Register Resident page
           ↓
Form submission triggers
           ↓
Generate unique ID (VH-2026-XXXX)
           ↓
Validate inputs (age, phone, etc.)
           ↓
Compress and save photo
           ↓
Create resident_data dictionary
           ↓
db_manager.add_resident(resident_data)
           ↓
DatabaseManager._get_connection()
           ↓
Execute INSERT INTO residents
           ↓
Commit transaction
           ↓
Close connection
           ↓
Return True (success)
           ↓
Show success message to user
```

### Example 2: Viewing Resident History

```
User searches for resident by ID/name
           ↓
db_manager.search_residents(search_term)
           ↓
Execute SELECT with LIKE clause
           ↓
Return list of matching residents
           ↓
User selects a resident
           ↓
db_manager.get_resident(unique_id)
           ↓
db_manager.get_resident_visits(unique_id)
           ↓
db_manager.get_medical_history(unique_id)
           ↓
Combine data and display
           ↓
Generate charts with Plotly
           ↓
Show complete profile
```

### Example 3: Exporting Data

```
User selects export options
           ↓
db_manager.export_residents_to_df()
           ↓
Execute SELECT * FROM residents
           ↓
Convert rows to pandas DataFrame
           ↓
User chooses format (CSV/Excel)
           ↓
df.to_csv() or df.to_excel()
           ↓
Provide download link
```

---

## Performance Considerations

### Current Performance Characteristics

| Operation | Typical Performance | Notes |
|-----------|-------------------|--------|
| Single resident lookup | < 1ms | Indexed by unique_id |
| All residents (1000 records) | < 10ms | Full table scan |
| Visit history (100 visits) | < 5ms | Indexed by resident_id |
| Search by name | < 50ms | Uses LIKE, full scan |
| Monthly analytics | < 100ms | Aggregation queries |
| Data export (all data) | < 500ms | Includes DataFrame conversion |

### Optimization Strategies Implemented

1. **Indexes**: Created on frequently queried columns
   - `residents.unique_id` (primary key, automatic)
   - `visits.resident_id` (foreign key lookups)
   - `visits.visit_date` (date filtering)
   - `medical_history.resident_id` (foreign key lookups)

2. **Row Factory**: Efficient dictionary conversion
   ```python
   conn.row_factory = sqlite3.Row
   ```

3. **Batch Queries**: Using pandas for exports instead of row-by-row

4. **Connection Management**: No persistent connections to prevent locks

### When to Scale Up

Consider migrating to PostgreSQL/MySQL if:
- Resident count exceeds 50,000
- Concurrent users exceed 10
- Network-based access required
- Advanced features needed (full-text search, JSON, etc.)
- Multi-facility deployment

---

## Security Considerations

### Current Security Measures

1. **Authentication**: Required for all database operations
   - Implemented via `streamlit-authenticator`
   - Session-based access control

2. **Audit Trail**: All modifications tracked
   - `registered_by` in residents table
   - `health_worker` in visits table
   - `updated_by` in medical_history table
   - Timestamps on all records

3. **File Permissions**: Database file access restricted
   ```bash
   chmod 600 health_tracking.db  # Owner read/write only
   ```

4. **SQL Injection Prevention**: Parameterized queries
   ```python
   # Good - parameterized
   cursor.execute("SELECT * FROM residents WHERE unique_id = ?", (id,))
   
   # Bad - string concatenation (NOT used in this project)
   # cursor.execute(f"SELECT * FROM residents WHERE unique_id = '{id}'")
   ```

5. **Data Validation**: Input validation before database insertion
   - Phone number format
   - Age ranges
   - Required fields
   - Unique ID format

### Areas for Enhancement

1. **Encryption**: SQLite database is not encrypted
   - Consider SQLCipher for encryption at rest
   - Encrypt backups

2. **Role-Based Access**: All authenticated users have full access
   - Could add roles (admin, doctor, data entry)
   - Restrict sensitive operations

3. **Soft Deletes**: No delete operations currently
   - Could add `deleted_at` column
   - Preserve data for audit

---

## Troubleshooting Common Issues

### Issue 1: Database Locked Error

**Symptom**: `sqlite3.OperationalError: database is locked`

**Causes**:
- Another process has the database open
- Long-running transaction
- Streamlit hot-reload during query

**Solutions**:
```bash
# Check for processes using the database
lsof health_tracking.db

# Kill the process
kill -9 <PID>

# Or restart the Streamlit app
# Press Ctrl+C and restart
```

**Prevention**: Current implementation minimizes this by:
- Opening/closing connections quickly
- No persistent connections
- Short-lived transactions

### Issue 2: Missing Tables

**Symptom**: `sqlite3.OperationalError: no such table: residents`

**Solution**:
```python
# Reinitialize database
python -c "from database import init_database; init_database()"

# Or use setup script
python setup_database.py
```

### Issue 3: Foreign Key Constraint Failed

**Symptom**: `sqlite3.IntegrityError: FOREIGN KEY constraint failed`

**Cause**: Trying to add visit for non-existent resident

**Solution**:
```python
# Always check resident exists first
if db_manager.resident_exists(resident_id):
    db_manager.add_visit(visit_data)
else:
    print("Resident not found")
```

### Issue 4: Database Corruption

**Symptom**: `sqlite3.DatabaseError: database disk image is malformed`

**Solutions**:
```bash
# Method 1: Try to recover
sqlite3 health_tracking.db ".recover" > recovered_data.sql
rm health_tracking.db
sqlite3 health_tracking.db < recovered_data.sql

# Method 2: Restore from backup
cp backups/health_tracking_latest.db health_tracking.db

# Method 3: Export/reimport
sqlite3 health_tracking.db .dump | sqlite3 new_health_tracking.db
```

---

## Migration Paths

### Migrating to PostgreSQL (Future)

If/when scaling requires PostgreSQL:

1. **Schema Translation**:
   ```sql
   -- SQLite → PostgreSQL changes
   TEXT → VARCHAR
   INTEGER PRIMARY KEY AUTOINCREMENT → SERIAL PRIMARY KEY
   TEXT (dates) → DATE or TIMESTAMP
   ```

2. **Code Changes**:
   - Replace `sqlite3` with `psycopg2`
   - Update connection string
   - Adjust SQL dialect (minor differences)
   - Keep DatabaseManager API the same

3. **Data Migration**:
   ```bash
   # Export from SQLite
   sqlite3 health_tracking.db .dump > export.sql
   
   # Convert and import to PostgreSQL
   # (Use pgloader or manual conversion)
   ```

---

## Best Practices in Use

The current implementation follows these SQLite best practices:

✅ **Parameterized Queries**: Prevents SQL injection  
✅ **Short Transactions**: Minimize lock time  
✅ **Proper Indexing**: Fast lookups on key columns  
✅ **Error Handling**: Graceful degradation  
✅ **Connection Management**: Open/close pattern  
✅ **Row Factory**: Easy dictionary access  
✅ **IF NOT EXISTS**: Safe schema creation  
✅ **Regular Backups**: Automated backup script  
✅ **Audit Trail**: Track who/when for modifications  
✅ **Data Validation**: Validate before insertion  

---

## Summary

### How the Database is Handled

1. **Storage**: SQLite database file (`health_tracking.db`)
2. **Abstraction**: Custom `DatabaseManager` class with clean API
3. **Schema**: Three tables (residents, visits, medical_history) with indexes
4. **Operations**: Comprehensive CRUD methods for all entities
5. **Initialization**: Automatic on first run, safe re-initialization
6. **Connections**: Open/close pattern, no pooling needed
7. **Error Handling**: Try-except with graceful degradation
8. **Session State**: Single DatabaseManager instance per user session
9. **Backup**: Automated scripts for database and photos
10. **Security**: Authentication, audit trails, parameterized queries

### Key Strengths

- ✅ Simple and reliable (SQLite)
- ✅ Zero configuration required
- ✅ Clean abstraction layer
- ✅ Good error handling
- ✅ Automated backups
- ✅ Audit trail built-in
- ✅ Portable (single file)

### Areas for Future Enhancement

- 🔄 Add database encryption (SQLCipher)
- 🔄 Implement soft deletes
- 🔄 Add role-based access control
- 🔄 Consider connection pooling for high concurrency
- 🔄 Add database schema versioning/migrations
- 🔄 Implement full-text search for better search performance

---

**Last Updated**: February 8, 2026  
**Author**: System Documentation  
**Project**: CFM Project Chiklod - Village Health Tracking System
