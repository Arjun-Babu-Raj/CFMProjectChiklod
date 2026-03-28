# 🏥 Village Health Tracking System
### Department of Community and Family Medicine 

A complete, production-ready Streamlit-based health data collection and management system for village residents in Chiklod. This system enables health workers to register residents, record health visits, track vitals, manage medical histories, and analyze health trends over time.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red.svg)

---

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
  - [Local Setup](#local-setup)
  - [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
- [Initial Setup](#initial-setup)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Database Schema](#database-schema)
- [Backup and Maintenance](#backup-and-maintenance)
- [Troubleshooting](#troubleshooting)
- [OpenMRS Integration](#openmrs-integration)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### 🔐 Authentication System
- Secure login for up to 20 health workers
- Password hashing with bcrypt
- Session management with streamlit-authenticator
- Configurable user credentials via YAML

### 📝 Resident Registration
- Auto-generated unique IDs (format: VH-YYYY-XXXX)
- Profile photo upload with automatic compression
- Comprehensive demographic information
- Duplicate prevention
- Registration tracking (who registered and when)

### 🏥 Visit Recording
- Search residents by ID or name
- Record complete vital signs:
  - Blood Pressure (Systolic/Diastolic)
  - Temperature (°F)
  - Pulse Rate (bpm)
  - Weight (kg)
  - Height (cm)
  - BMI (auto-calculated)
  - Oxygen Saturation (SpO2 %)
- Chief complaints and clinical observations
- Multiple photo uploads per visit
- Automatic visit timestamp

### 📋 Medical History Management
- Chronic conditions tracking
- Past diagnoses
- Current medications
- Known allergies (highlighted)
- Family health history
- Additional notes
- Update tracking

### 👤 Longitudinal Data View
- Complete resident profile
- Visit history timeline
- Interactive vitals trend charts (Plotly)
- Photo gallery from all visits
- Medical history summary
- Quick statistics

### 📊 Analytics Dashboard
- Total residents and visits metrics
- Demographics (age groups, gender distribution)
- Health worker performance tracking
- Monthly registration and visit trends
- Village area distribution
- Recent activity log

### 🔍 Search & Browse
- Quick search by ID or name
- Advanced filters (age range, gender, village area)
- Paginated results table
- Detailed profile preview
- Quick actions for selected residents

### 📥 Data Export
- Export to CSV or Excel
- Selectable data types (residents, visits, medical history)
- Date range filtering for visits
- Multi-sheet Excel workbooks
- Data preview before export

---

## 🛠️ Technology Stack

- **Frontend**: Streamlit 1.31+
- **Backend**: Python 3.8+
- **Database**: SQLite3
- **Authentication**: streamlit-authenticator
- **Data Processing**: Pandas 2.0+
- **Visualization**: Plotly 5.18+
- **Image Processing**: Pillow 10.0+
- **File Format Support**: openpyxl (Excel), python-dateutil

---

## 📁 Project Structure

```
CFMProjectChiklod/
├── app.py                          # Main entry point with navigation
├── requirements.txt                # Python dependencies
├── config.yaml                     # Authentication credentials (gitignored)
├── config.template.yaml            # Template for config.yaml
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── .streamlit/
│   └── config.toml                # Streamlit theme configuration
├── database/
│   ├── __init__.py
│   ├── db_manager.py              # Database operations (CRUD)
│   └── schema.py                  # Database initialization
├── pages/
│   ├── 1_📝_Register_Resident.py  # Resident registration
│   ├── 2_🏥_Record_Visit.py       # Visit recording
│   ├── 3_📋_Medical_History.py    # Medical history management
│   ├── 4_👤_View_Resident.py      # Longitudinal data view
│   ├── 5_📊_Analytics.py          # Analytics dashboard
│   ├── 6_🔍_Search.py             # Search & browse
│   └── 7_📥_Export_Data.py        # Data export
├── utils/
│   ├── __init__.py
│   ├── auth.py                    # Authentication helpers
│   ├── id_generator.py            # Unique ID generation
│   ├── image_handler.py           # Photo upload & compression
│   └── validators.py              # Input validation
├── assets/
│   └── .gitkeep                   # Assets folder placeholder
└── uploaded_photos/
    └── .gitkeep                   # Photos folder placeholder
```

---

## 🚀 Installation

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Arjun-Babu-Raj/CFMProjectChiklod.git
   cd CFMProjectChiklod
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration:**
   ```bash
   cp config.template.yaml config.yaml
   ```
   
   Edit `config.yaml` to set secure passwords (see [Initial Setup](#initial-setup))

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

6. **Access the application:**
   Open your browser to `http://localhost:8501`

### Streamlit Cloud Deployment

1. **Fork or push this repository to GitHub**

2. **Go to [Streamlit Community Cloud](https://streamlit.io/cloud)**

3. **Click "New app"**

4. **Configure deployment:**
   - Repository: `your-username/CFMProjectChiklod`
   - Branch: `main`
   - Main file path: `app.py`

5. **Add secrets** (optional for secure credential storage):
   - Go to App settings → Secrets
   - Add your config.yaml content as a secret

6. **Deploy!**

Your app will be live at: `https://your-app-name.streamlit.app`

---

## 🔧 Initial Setup

### Creating Authentication Credentials

1. **Copy the template:**
   ```bash
   cp config.template.yaml config.yaml
   ```

2. **Generate hashed passwords:**
   ```python
   import streamlit_authenticator as stauth
   
   # Generate hashed password
   hashed_password = stauth.Hasher(['your_password']).generate()[0]
   print(hashed_password)
   ```

3. **Update config.yaml:**
   - Replace the `password` field with your generated hash
   - Change the `cookie.key` to a random string
   - Update usernames, emails, and names as needed

4. **Add more health workers:**
   ```yaml
   credentials:
     usernames:
       worker4:
         email: worker4@example.com
         name: Health Worker 4
         password: $2b$12$... # your hashed password
   ```

### Default Credentials (For Testing Only)

- **Username:** worker1
- **Password:** password123

**⚠️ Change these immediately in production!**

---

## 📖 Usage Guide

### 1. Logging In

1. Open the application
2. Enter your username and password
3. Click "Login"

### 2. Registering a Resident

1. Navigate to **📝 Register Resident**
2. Fill in required fields (Name is mandatory)
3. Upload a profile photo (optional)
4. Click **✅ Register Resident**
5. Note the generated Unique ID (e.g., VH-2026-0001)

### 3. Recording a Visit

1. Navigate to **🏥 Record Visit**
2. Search for the resident by name or ID
3. Select the resident
4. Enter vitals and observations
5. Upload visit photos (optional)
6. Click **✅ Record Visit**

### 4. Managing Medical History

1. Navigate to **📋 Medical History**
2. Search and select a resident
3. Fill in medical history details
4. Click **💾 Save Medical History**

### 5. Viewing Resident Profile

1. Navigate to **👤 View Resident**
2. Search and select a resident
3. Explore tabs:
   - **Vitals Trends**: Interactive charts
   - **Visit History**: Chronological timeline
   - **Medical History**: Health conditions
   - **Photo Gallery**: All photos

### 6. Viewing Analytics

1. Navigate to **📊 Analytics**
2. Review:
   - Overall statistics
   - Demographics charts
   - Health worker performance
   - Monthly trends

### 7. Searching Residents

1. Navigate to **🔍 Search**
2. Use quick search or advanced filters
3. Browse paginated results
4. View detailed profiles
5. Export search results

### 8. Exporting Data

1. Navigate to **📥 Export Data**
2. Select data types to export
3. Apply date filters (for visits)
4. Choose format (CSV or Excel)
5. Download files

---

## ⚙️ Configuration

### Streamlit Configuration (.streamlit/config.toml)

```toml
[theme]
primaryColor = "#FF6B6B"        # Primary accent color
backgroundColor = "#FFFFFF"      # Background color
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 5               # Max file upload size in MB
enableXsrfProtection = true     # CSRF protection
```

### Environment Variables (Optional)

For Streamlit Cloud deployment, you can use secrets:

```toml
# .streamlit/secrets.toml
[credentials]
# Add your config.yaml content here
```

---

## 🗄️ Database Setup

The application uses SQLite for data storage. The database is automatically initialized on first run.

### Automatic Initialization

The database (`health_tracking.db`) is created automatically when you first run the application:

```bash
streamlit run app.py
# Database is initialized automatically
```

### Manual Database Setup

If you need to manually initialize or reset the database:

```bash
# Option 1: Using the setup script (recommended)
python setup_database.py

# Option 2: Using Python
python -c "from database import init_database; init_database(); print('Database initialized')"

# Option 3: Using the schema module directly
python database/schema.py
```

### Database Location

By default, the database file is created in the application root directory:
- **File:** `health_tracking.db`
- **Format:** SQLite3
- **Size:** Starts at ~8KB, grows with data

### Database Backup

**Automated Backup Scripts:**

```bash
# Linux/Mac
./backup_database.sh

# Windows
backup_database.bat
```

**Manual Backup:**

```bash
# Simple copy
cp health_tracking.db health_tracking_backup_$(date +%Y%m%d).db

# With photos
tar -czf backup.tar.gz health_tracking.db uploaded_photos/
```

### Scheduled Backups

**Linux/Mac (Cron):**
```bash
# Daily at 2 AM
crontab -e
# Add: 0 2 * * * /path/to/backup_database.sh
```

**Windows (Task Scheduler):**
- Use `backup_database.bat` with Task Scheduler
- Schedule daily or weekly

### Database Maintenance

```bash
# Check integrity
sqlite3 health_tracking.db "PRAGMA integrity_check;"

# Optimize database (monthly recommended)
sqlite3 health_tracking.db "VACUUM;"

# View database size
du -h health_tracking.db
```

### Advanced Configuration

For detailed database operations, migration, and troubleshooting, see:
- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - Complete database guide
- Includes: backup/restore, migration, performance optimization
- Covers: troubleshooting, SQL queries, environment-specific setup

---

## 🗄️ Database Schema

### residents table
```sql
CREATE TABLE residents (
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
);
```

### visits table
```sql
CREATE TABLE visits (
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
);
```

### medical_history table
```sql
CREATE TABLE medical_history (
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
);
```

---

## 💾 Backup and Maintenance

### Database Backup

**Manual Backup:**
```bash
# Copy the database file
cp health_tracking.db health_tracking_backup_$(date +%Y%m%d).db
```

**Automated Backup Script:**
```bash
#!/bin/bash
# backup.sh
DB_FILE="health_tracking.db"
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_DIR/health_tracking_$DATE.db
echo "Backup created: $BACKUP_DIR/health_tracking_$DATE.db"
```

### Photo Backup

```bash
# Backup uploaded photos
tar -czf photos_backup_$(date +%Y%m%d).tar.gz uploaded_photos/
```

### Database Maintenance

**Check database integrity:**
```python
import sqlite3
conn = sqlite3.connect('health_tracking.db')
cursor = conn.cursor()
cursor.execute("PRAGMA integrity_check;")
print(cursor.fetchone())
conn.close()
```

**Vacuum database (optimize):**
```python
import sqlite3
conn = sqlite3.connect('health_tracking.db')
conn.execute("VACUUM")
conn.close()
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **Authentication Error: config.yaml not found**
- **Solution:** Copy `config.template.yaml` to `config.yaml`
  ```bash
  cp config.template.yaml config.yaml
  ```

#### 2. **Module not found errors**
- **Solution:** Install all dependencies
  ```bash
  pip install -r requirements.txt
  ```

#### 3. **Database locked error**
- **Solution:** Close other connections to the database
- Check if another instance is running

#### 4. **Photo upload fails**
- **Solution:** Check `uploaded_photos/` directory exists and is writable
  ```bash
  mkdir -p uploaded_photos
  chmod 755 uploaded_photos
  ```

#### 5. **Charts not displaying**
- **Solution:** Ensure Plotly is installed correctly
  ```bash
  pip install --upgrade plotly
  ```

#### 6. **Session state errors**
- **Solution:** Clear browser cache and refresh
- Or restart the Streamlit server

### Performance Optimization

For large datasets (1000+ residents, 10000+ visits):

1. **Enable database indexing** (already implemented in schema.py)
2. **Use pagination** (already implemented in search page)
3. **Cache expensive operations:**
   ```python
   @st.cache_data
   def get_analytics_data():
       # Your expensive query
       pass
   ```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write meaningful commit messages
- Test thoroughly before submitting

---

## 📄 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2026 CFM Project Chiklod

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support

For issues, questions, or suggestions:

- **GitHub Issues**: [Create an issue](https://github.com/Arjun-Babu-Raj/CFMProjectChiklod/issues)
- **Email**: Contact the development team
- **Documentation**: Refer to this README

---

## 🙏 Acknowledgments

- Head of the Department, Department of Community and Family Medicine
- Faculties, Department of Community and Family Medicine
- Senior Residents, Junior Residents, Department of Community and Family Medicine

---

## 📊 Project Status

- ✅ **Version:** 1.0.0
- ✅ **Status:** Production Ready
- ✅ **Last Updated:** February 2026
- ✅ **Tested With:** Python 3.8+, Streamlit 1.31+

---

## 🎯 Roadmap

Future enhancements planned:

- [ ] SMS notifications for visit reminders
- [ ] Offline mode with data sync
- [ ] Multi-language support (local languages)
- [ ] Advanced analytics with ML predictions
- [ ] Mobile app companion
- [ ] Integration with national health records

---

## 🔗 OpenMRS Integration

For information about integrating with OpenMRS (Open Medical Record System):

- **[OpenMRS Comparison](OPENMRS_COMPARISON.md)** - Comprehensive comparison between this system and OpenMRS
  - Feature comparison and analysis
  - When to use each system
  - Cost-benefit analysis
  - Migration recommendations

- **[OpenMRS Integration Guide](OPENMRS_INTEGRATION_GUIDE.md)** - Step-by-step implementation guide
  - Adding FHIR export capability
  - Direct API integration with OpenMRS
  - Automated sync setup
  - Deployment instructions

**Quick Answer:** The current system is optimized for village-level community health work. OpenMRS is better suited for large-scale clinical facilities. See the comparison document for detailed analysis and integration options.

---

**Built For Chiklod, by Department of Community and Family Medicine **
