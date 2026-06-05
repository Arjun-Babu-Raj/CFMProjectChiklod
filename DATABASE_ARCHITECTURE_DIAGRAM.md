# Database Architecture Diagram

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Streamlit)                   │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Register │  │ Record   │  │ Medical  │  │ View     │      │
│  │ Resident │  │ Visit    │  │ History  │  │ Resident │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │             │              │             │            │
│  ┌────┴─────┐  ┌───┴──────┐  ┌───┴──────┐  ┌───┴──────┐     │
│  │ Analytics│  │ Search   │  │ Export   │  │ Backup   │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │              │             │
        │        Session State (st.session_state.db_manager)
        │             │              │             │
┌───────▼─────────────▼──────────────▼─────────────▼───────────┐
│                DatabaseManager (Abstraction Layer)            │
│                   database/db_manager.py                      │
│                                                               │
│  Residents Operations:                                        │
│  • add_resident()         • get_resident()                    │
│  • get_all_residents()    • search_residents()                │
│  • filter_residents()     • resident_exists()                 │
│                                                               │
│  Visits Operations:                                           │
│  • add_visit()            • get_resident_visits()             │
│  • get_all_visits()       • get_recent_visits()               │
│  • get_visit_count()                                          │
│                                                               │
│  Medical History:                                             │
│  • add_or_update_medical_history()                            │
│  • get_medical_history()                                      │
│                                                               │
│  Analytics:                                                   │
│  • get_demographics_summary()                                 │
│  • get_monthly_trends()                                       │
│                                                               │
│  Export:                                                      │
│  • export_residents_to_df()                                   │
│  • export_visits_to_df()                                      │
│  • export_medical_history_to_df()                             │
│                                                               │
└───────────────────────────┬───────────────────────────────────┘
                            │
                    _get_connection()
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                 SQLite Database (Data Layer)                  │
│                    health_tracking.db                         │
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   residents     │  │     visits      │  │   medical_   │ │
│  │                 │  │                 │  │   history    │ │
│  │ • unique_id (PK)│  │ • visit_id (PK) │  │ • history_id │ │
│  │ • name          │  │ • resident_id   │  │ • resident_id│ │
│  │ • age           │  │ • visit_date    │  │ • chronic_   │ │
│  │ • gender        │  │ • visit_time    │  │   conditions │ │
│  │ • address       │  │ • health_worker │  │ • past_      │ │
│  │ • phone         │  │ • bp_systolic   │  │   diagnoses  │ │
│  │ • village_area  │  │ • bp_diastolic  │  │ • current_   │ │
│  │ • photo_path    │  │ • temperature   │  │   medications│ │
│  │ • registration_ │  │ • pulse         │  │ • allergies  │ │
│  │   date          │  │ • weight        │  │ • family_    │ │
│  │ • registered_by │  │ • height        │  │   history    │ │
│  └─────────────────┘  │ • bmi           │  │ • notes      │ │
│                       │ • spo2          │  │ • last_      │ │
│  Indexes:             │ • complaints    │  │   updated    │ │
│  • PK on unique_id    │ • observations  │  │ • updated_by │ │
│                       │ • photo_paths   │  └──────────────┘ │
│                       └─────────────────┘                    │
│                                                               │
│                       Indexes:                                │
│                       • PK on visit_id                        │
│                       • idx_resident_id                       │
│                       • idx_visit_date                        │
│                       • idx_medical_history_resident          │
│                                                               │
│                       Foreign Keys:                           │
│                       • visits.resident_id → residents        │
│                       • medical_history.resident_id →         │
│                         residents                             │
└───────────────────────────────────────────────────────────────┘
```

## Data Flow: Register New Resident

```
┌─────────────┐
│    User     │
│ Fills Form  │
└──────┬──────┘
       │
       │ Submit Form
       ▼
┌─────────────────────────────┐
│  Register Resident Page     │
│  (pages/1_*.py)             │
└──────┬──────────────────────┘
       │
       │ 1. Generate unique_id (VH-2026-XXXX)
       │ 2. Validate inputs
       │ 3. Save & compress photo
       │ 4. Create resident_data dict
       ▼
┌─────────────────────────────┐
│  DatabaseManager            │
│  add_resident(data)         │
└──────┬──────────────────────┘
       │
       │ 1. _get_connection()
       │ 2. INSERT INTO residents
       │ 3. commit()
       │ 4. close()
       ▼
┌─────────────────────────────┐
│  SQLite Database            │
│  health_tracking.db         │
│  [New row added]            │
└──────┬──────────────────────┘
       │
       │ Return: True (success)
       ▼
┌─────────────────────────────┐
│  User sees success message  │
│  "Resident registered!"     │
└─────────────────────────────┘
```

## Data Flow: View Resident History

```
┌─────────────┐
│    User     │
│ Searches ID │
└──────┬──────┘
       │
       │ Enter: "VH-2026-0001"
       ▼
┌─────────────────────────────┐
│  Search/View Resident Page  │
│  (pages/6_*.py, 4_*.py)     │
└──────┬──────────────────────┘
       │
       │ ┌─────────────────────────────────┐
       │ │  DatabaseManager                │
       │ │                                 │
       ├─┼─> get_resident(unique_id)      │
       │ │    Returns: resident details    │
       │ │                                 │
       ├─┼─> get_resident_visits(id)      │
       │ │    Returns: list of visits      │
       │ │                                 │
       ├─┼─> get_medical_history(id)      │
       │ │    Returns: medical history     │
       │ └─────────────────────────────────┘
       │
       │ All queries hit SQLite database
       │
       ▼
┌─────────────────────────────┐
│  SQLite Database            │
│                             │
│  SELECT * FROM residents    │
│  WHERE unique_id = ?        │
│                             │
│  SELECT * FROM visits       │
│  WHERE resident_id = ?      │
│  ORDER BY visit_date DESC   │
│                             │
│  SELECT * FROM medical_     │
│  history WHERE resident_id=?│
└──────┬──────────────────────┘
       │
       │ Returns: Combined data
       ▼
┌─────────────────────────────┐
│  Display on Page:           │
│  • Profile info             │
│  • Visit timeline           │
│  • Vitals charts (Plotly)   │
│  • Photo gallery            │
│  • Medical history          │
└─────────────────────────────┘
```

## Database Connection Lifecycle

```
┌───────────────────────────────────────────────────────────────┐
│                      User Session Start                       │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  app.py initializes    │
                    │  init_database()       │
                    │  (creates tables if    │
                    │   they don't exist)    │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  Create DatabaseManager│
                    │  in st.session_state   │
                    │                        │
                    │  st.session_state.     │
                    │    db_manager =        │
                    │    DatabaseManager()   │
                    └───────────┬────────────┘
                                │
                                │ (Persists for entire session)
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Page 1       │    │  Page 2          │    │  Page 3          │
│  (Register)   │    │  (Record Visit)  │    │  (View)          │
└───────┬───────┘    └────────┬─────────┘    └────────┬─────────┘
        │                     │                       │
        │                     │                       │
        ▼                     ▼                       ▼
┌───────────────────────────────────────────────────────────────┐
│           Each DB Operation (e.g., add_resident)              │
│                                                               │
│  1. conn = sqlite3.connect("health_tracking.db")             │
│     [New connection opened]                                   │
│                                                               │
│  2. cursor = conn.cursor()                                    │
│     [Create cursor]                                           │
│                                                               │
│  3. cursor.execute("INSERT INTO ...")                         │
│     [Execute query]                                           │
│                                                               │
│  4. conn.commit()                                             │
│     [Commit transaction]                                      │
│                                                               │
│  5. conn.close()                                              │
│     [Connection closed immediately]                           │
│                                                               │
│  Total connection lifetime: < 100ms                           │
└───────────────────────────────────────────────────────────────┘
```

## Schema Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                     Entity Relationships                        │
└─────────────────────────────────────────────────────────────────┘

                     ┌─────────────────┐
                     │   residents     │
                     │─────────────────│
                     │ unique_id (PK)  │◄──────┐
                     │ name            │       │
                     │ age             │       │
                     │ gender          │       │
                     │ ...             │       │
                     └────────┬────────┘       │
                              │                │
                              │ One-to-Many    │
                              │                │
              ┌───────────────┼────────────────┼───────────┐
              │               │                │           │
              ▼               ▼                │           │
    ┌─────────────────┐  ┌────────────────────┐           │
    │     visits      │  │ medical_history    │           │
    │─────────────────│  │────────────────────│           │
    │ visit_id (PK)   │  │ history_id (PK)    │           │
    │ resident_id (FK)├──┘ resident_id (FK)   ├───────────┘
    │ visit_date      │    │ chronic_conditions│
    │ health_worker   │    │ past_diagnoses    │
    │ bp_systolic     │    │ current_medications│
    │ bp_diastolic    │    │ allergies         │
    │ temperature     │    │ family_history    │
    │ pulse           │    │ notes             │
    │ weight          │    │ last_updated      │
    │ height          │    │ updated_by        │
    │ bmi             │    └───────────────────┘
    │ spo2            │
    │ complaints      │    Relationship: One-to-One
    │ observations    │    (One resident has one medical history)
    │ photo_paths     │
    └─────────────────┘

    Relationship: One-to-Many
    (One resident can have many visits)


┌─────────────────────────────────────────────────────────────────┐
│                         Indexes                                 │
└─────────────────────────────────────────────────────────────────┘

Table: residents
  ├─ PRIMARY KEY: unique_id (automatic index)
  └─ Purpose: Fast lookup by resident ID

Table: visits
  ├─ PRIMARY KEY: visit_id (automatic index)
  ├─ INDEX: idx_resident_id (on resident_id)
  │  └─ Purpose: Fast filtering of visits by resident
  └─ INDEX: idx_visit_date (on visit_date)
     └─ Purpose: Fast date-based queries for analytics

Table: medical_history
  ├─ PRIMARY KEY: history_id (automatic index)
  └─ INDEX: idx_medical_history_resident (on resident_id)
     └─ Purpose: Fast lookup of history by resident
```

## Backup Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                   Backup Architecture                       │
└─────────────────────────────────────────────────────────────┘

           ┌─────────────────────────────────┐
           │   Production Environment        │
           │                                 │
           │  ┌────────────────────┐         │
           │  │ health_tracking.db │         │
           │  │   (Primary Data)   │         │
           │  └──────────┬─────────┘         │
           │             │                   │
           │  ┌──────────▼─────────┐         │
           │  │ uploaded_photos/   │         │
           │  │  (Photo Storage)   │         │
           │  └──────────┬─────────┘         │
           └─────────────┼───────────────────┘
                         │
                         │ backup_database.sh
                         │ (Runs daily at 2 AM)
                         │
                         ▼
           ┌─────────────────────────────────┐
           │   Backup Storage (backups/)     │
           │                                 │
           │  ┌────────────────────┐         │
           │  │ health_tracking_   │         │
           │  │   20260208.db      │         │
           │  │ (Binary backup)    │         │
           │  └────────────────────┘         │
           │                                 │
           │  ┌────────────────────┐         │
           │  │ health_tracking_   │         │
           │  │   20260208.sql.gz  │         │
           │  │ (SQL dump backup)  │         │
           │  └────────────────────┘         │
           │                                 │
           │  ┌────────────────────┐         │
           │  │ photos_20260208    │         │
           │  │   .tar.gz          │         │
           │  │ (Photo archive)    │         │
           │  └────────────────────┘         │
           │                                 │
           │  Retention: 30 days             │
           │  Auto-cleanup of old backups    │
           └─────────────────────────────────┘

Backup Types:
1. Binary DB Copy: Fast restore, exact replica
2. SQL Dump: Portable, can import to other DB systems
3. Photo Archive: Compressed photos directory
```

## Performance & Scalability

```
┌─────────────────────────────────────────────────────────────┐
│               Current Performance Profile                   │
└─────────────────────────────────────────────────────────────┘

┌───────────────────────┬──────────────┬─────────────────────┐
│ Operation             │ Performance  │ Scalability Notes   │
├───────────────────────┼──────────────┼─────────────────────┤
│ Single Resident       │ < 1ms        │ Excellent           │
│ Lookup (by ID)        │              │ (Indexed PK)        │
├───────────────────────┼──────────────┼─────────────────────┤
│ All Residents         │ < 10ms       │ Good up to 50K      │
│ (1,000 records)       │              │ records             │
├───────────────────────┼──────────────┼─────────────────────┤
│ Visit History         │ < 5ms        │ Excellent           │
│ (100 visits)          │              │ (Indexed FK)        │
├───────────────────────┼──────────────┼─────────────────────┤
│ Search by Name        │ < 50ms       │ Moderate            │
│ (LIKE query)          │              │ (Full table scan)   │
├───────────────────────┼──────────────┼─────────────────────┤
│ Analytics Aggregation │ < 100ms      │ Good up to 100K     │
│                       │              │ records             │
├───────────────────────┼──────────────┼─────────────────────┤
│ Export All Data       │ < 500ms      │ Good with pagination│
│ (to CSV/Excel)        │              │                     │
└───────────────────────┴──────────────┴─────────────────────┘

Capacity Limits (SQLite):
• Max Database Size: 281 TB (theoretical)
• Max Row Count: 2^64 (practical limit ~millions)
• Concurrent Users: 1 writer + multiple readers
• Suitable for: < 50,000 residents, < 10 concurrent users

When to Scale:
┌────────────────┐      ┌──────────────────────────────────┐
│ Current:       │      │ Future (if needed):              │
│ SQLite         │ ───► │ PostgreSQL / MySQL               │
│                │      │                                  │
│ • < 50K        │      │ • 50K+ residents                 │
│   residents    │      │ • 10+ concurrent users           │
│ • < 10 users   │      │ • Multi-facility deployment      │
│ • Single file  │      │ • Network-based access           │
│ • Local        │      │ • Advanced features (FTS, etc.)  │
└────────────────┘      └──────────────────────────────────┘
```

---

**Note**: This diagram provides a visual overview of the database architecture. For detailed implementation information, see `HOW_DATABASE_IS_HANDLED.md`.
