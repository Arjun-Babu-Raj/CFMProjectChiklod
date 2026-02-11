# OpenMRS Integration Implementation Guide

## Overview

This guide provides step-by-step instructions for adding OpenMRS integration capabilities to the Village Health Tracking System. This allows you to keep the current simple interface while gaining interoperability with OpenMRS-based health information systems.

## Architecture

```
Current System (Streamlit)
        ↓
    [Data Entry]
        ↓
  Local Database (Supabase/SQLite)
        ↓
  [Export Service] ← You'll add this
        ↓
   FHIR/REST API
        ↓
   OpenMRS System
```

---

## Phase 1: Add FHIR Export Capability

### Step 1: Install Dependencies

Add to `requirements.txt`:
```txt
fhirclient>=4.1.0
python-dateutil>=2.8.2
requests>=2.31.0
```

Install:
```bash
pip install fhirclient requests python-dateutil
```

### Step 2: Create OpenMRS Integration Module

Create `utils/openmrs_integration.py`:

```python
"""
OpenMRS Integration Module
Provides FHIR export and REST API integration with OpenMRS systems.
"""
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class OpenMRSClient:
    """Client for interacting with OpenMRS REST API."""
    
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize OpenMRS client.
        
        Args:
            base_url: OpenMRS base URL (e.g., http://openmrs.example.com:8080/openmrs)
            username: OpenMRS username
            password: OpenMRS password
        """
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        
    def test_connection(self) -> bool:
        """Test connection to OpenMRS."""
        try:
            response = self.session.get(f"{self.base_url}/ws/rest/v1/session")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def create_patient(self, resident_data: Dict) -> Optional[Dict]:
        """
        Create a patient in OpenMRS from resident data.
        
        Args:
            resident_data: Dictionary with resident information
            
        Returns:
            Created patient data or None if failed
        """
        try:
            # Prepare patient data in OpenMRS format
            patient_payload = {
                "person": {
                    "names": [{
                        "givenName": resident_data['name'].split()[0],
                        "familyName": resident_data['name'].split()[-1] if len(resident_data['name'].split()) > 1 else resident_data['name'],
                        "preferred": True
                    }],
                    "gender": self._map_gender(resident_data.get('gender', 'U')),
                    "birthdate": self._calculate_birthdate(resident_data.get('age')),
                    "birthdateEstimated": True if resident_data.get('age') else False,
                    "addresses": [{
                        "address1": resident_data.get('address', ''),
                        "cityVillage": resident_data.get('village_area', ''),
                        "preferred": True
                    }]
                },
                "identifiers": [{
                    "identifier": resident_data['unique_id'],
                    "identifierType": "e2b966d0-1d5f-11e0-b929-000c29ad1d07",  # Default identifier type
                    "location": "8d6c993e-c2cc-11de-8d13-0010c6dffd0f",  # Default location
                    "preferred": True
                }]
            }
            
            # Add phone if available
            if resident_data.get('phone'):
                patient_payload['person']['attributes'] = [{
                    "attributeType": "14d4f066-15f5-102d-96e4-000c29c2a5d7",  # Phone number attribute
                    "value": resident_data['phone']
                }]
            
            response = self.session.post(
                f"{self.base_url}/ws/rest/v1/patient",
                json=patient_payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                logger.info(f"Patient created: {resident_data['unique_id']}")
                return response.json()
            else:
                logger.error(f"Failed to create patient: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating patient: {e}")
            return None
    
    def create_encounter(self, resident_id: str, visit_data: Dict) -> Optional[Dict]:
        """
        Create an encounter (visit) in OpenMRS.
        
        Args:
            resident_id: Patient unique ID
            visit_data: Dictionary with visit information
            
        Returns:
            Created encounter data or None if failed
        """
        try:
            # Find patient UUID by identifier
            patient = self._find_patient_by_identifier(resident_id)
            if not patient:
                logger.error(f"Patient not found: {resident_id}")
                return None
            
            # Prepare encounter
            encounter_payload = {
                "patient": patient['uuid'],
                "encounterType": "e22e39fd-7db2-45e7-80f1-60fa0d5a4378",  # Vitals encounter type
                "encounterDatetime": f"{visit_data['visit_date']}T{visit_data.get('visit_time', '09:00:00')}",
                "location": "8d6c993e-c2cc-11de-8d13-0010c6dffd0f",  # Default location
                "obs": []
            }
            
            # Add observations
            obs_mappings = self._create_observations(visit_data)
            encounter_payload['obs'] = obs_mappings
            
            response = self.session.post(
                f"{self.base_url}/ws/rest/v1/encounter",
                json=encounter_payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                logger.info(f"Encounter created for patient: {resident_id}")
                return response.json()
            else:
                logger.error(f"Failed to create encounter: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating encounter: {e}")
            return None
    
    def _find_patient_by_identifier(self, identifier: str) -> Optional[Dict]:
        """Find patient by identifier."""
        try:
            response = self.session.get(
                f"{self.base_url}/ws/rest/v1/patient",
                params={'identifier': identifier}
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                return results[0] if results else None
            return None
        except Exception as e:
            logger.error(f"Error finding patient: {e}")
            return None
    
    def _create_observations(self, visit_data: Dict) -> List[Dict]:
        """Create observation objects from visit data."""
        observations = []
        
        # OpenMRS concept UUIDs for common vitals (may need to be customized)
        concept_mappings = {
            'bp_systolic': '5085AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'bp_diastolic': '5086AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'temperature': '5088AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'pulse': '5087AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'weight': '5089AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'height': '5090AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'spo2': '5092AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        }
        
        for field, concept_uuid in concept_mappings.items():
            value = visit_data.get(field)
            if value:
                observations.append({
                    "concept": concept_uuid,
                    "value": float(value)
                })
        
        # Add complaints and observations as text
        if visit_data.get('complaints'):
            observations.append({
                "concept": "160531AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # Chief complaint concept
                "value": visit_data['complaints']
            })
        
        if visit_data.get('observations'):
            observations.append({
                "concept": "159395AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # Clinical notes concept
                "value": visit_data['observations']
            })
        
        return observations
    
    def _map_gender(self, gender: str) -> str:
        """Map gender to OpenMRS format."""
        gender_map = {
            'Male': 'M',
            'Female': 'F',
            'Other': 'O',
            'M': 'M',
            'F': 'F',
            'O': 'O'
        }
        return gender_map.get(gender, 'U')
    
    def _calculate_birthdate(self, age: Optional[int]) -> str:
        """Calculate approximate birthdate from age."""
        if age:
            birth_year = datetime.now().year - age
            return f"{birth_year}-01-01"
        return "1970-01-01"  # Default for unknown


class FHIRExporter:
    """Export data to FHIR format for interoperability."""
    
    @staticmethod
    def export_patient(resident_data: Dict) -> Dict:
        """
        Export resident data to FHIR Patient resource.
        
        Args:
            resident_data: Resident information dictionary
            
        Returns:
            FHIR Patient resource
        """
        patient = {
            "resourceType": "Patient",
            "identifier": [{
                "system": "http://chiklod.cfm/resident-id",
                "value": resident_data['unique_id']
            }],
            "name": [{
                "text": resident_data['name'],
                "family": resident_data['name'].split()[-1] if len(resident_data['name'].split()) > 1 else resident_data['name'],
                "given": [resident_data['name'].split()[0]]
            }],
            "gender": resident_data.get('gender', 'unknown').lower(),
            "birthDate": FHIRExporter._calculate_birth_date(resident_data.get('age')),
            "address": [{
                "text": resident_data.get('address', ''),
                "district": resident_data.get('village_area', '')
            }]
        }
        
        if resident_data.get('phone'):
            patient['telecom'] = [{
                "system": "phone",
                "value": resident_data['phone']
            }]
        
        return patient
    
    @staticmethod
    def export_observation(resident_id: str, visit_data: Dict, obs_type: str) -> Dict:
        """
        Export visit data to FHIR Observation resource.
        
        Args:
            resident_id: Patient unique ID
            visit_data: Visit information
            obs_type: Type of observation (bp, weight, etc.)
            
        Returns:
            FHIR Observation resource
        """
        # LOINC codes for common observations
        loinc_codes = {
            'bp': {'code': '85354-9', 'display': 'Blood pressure'},
            'weight': {'code': '29463-7', 'display': 'Body weight'},
            'height': {'code': '8302-2', 'display': 'Body height'},
            'temperature': {'code': '8310-5', 'display': 'Body temperature'},
            'pulse': {'code': '8867-4', 'display': 'Heart rate'},
            'spo2': {'code': '59408-5', 'display': 'Oxygen saturation'}
        }
        
        observation = {
            "resourceType": "Observation",
            "status": "final",
            "subject": {
                "reference": f"Patient/{resident_id}"
            },
            "effectiveDateTime": visit_data.get('visit_date', datetime.now().isoformat())
        }
        
        if obs_type == 'bp' and visit_data.get('bp_systolic') and visit_data.get('bp_diastolic'):
            observation['code'] = {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": loinc_codes['bp']['code'],
                    "display": loinc_codes['bp']['display']
                }]
            }
            observation['component'] = [
                {
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "8480-6",
                            "display": "Systolic blood pressure"
                        }]
                    },
                    "valueQuantity": {
                        "value": visit_data['bp_systolic'],
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]"
                    }
                },
                {
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "8462-4",
                            "display": "Diastolic blood pressure"
                        }]
                    },
                    "valueQuantity": {
                        "value": visit_data['bp_diastolic'],
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]"
                    }
                }
            ]
        elif obs_type in loinc_codes and visit_data.get(obs_type):
            observation['code'] = {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": loinc_codes[obs_type]['code'],
                    "display": loinc_codes[obs_type]['display']
                }]
            }
            
            unit_map = {
                'weight': 'kg',
                'height': 'cm',
                'temperature': '[degF]',
                'pulse': '/min',
                'spo2': '%'
            }
            
            observation['valueQuantity'] = {
                "value": visit_data[obs_type],
                "unit": unit_map.get(obs_type, ''),
                "system": "http://unitsofmeasure.org",
                "code": unit_map.get(obs_type, '')
            }
        
        return observation
    
    @staticmethod
    def export_bundle(resident_data: Dict, visits_data: List[Dict]) -> Dict:
        """
        Export resident and visits to FHIR Bundle.
        
        Args:
            resident_data: Resident information
            visits_data: List of visit records
            
        Returns:
            FHIR Bundle resource
        """
        bundle = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": []
        }
        
        # Add patient
        patient = FHIRExporter.export_patient(resident_data)
        bundle['entry'].append({
            "resource": patient,
            "request": {
                "method": "POST",
                "url": "Patient"
            }
        })
        
        # Add observations from visits
        for visit in visits_data:
            resident_id = resident_data['unique_id']
            
            # Blood pressure
            if visit.get('bp_systolic') and visit.get('bp_diastolic'):
                bp_obs = FHIRExporter.export_observation(resident_id, visit, 'bp')
                bundle['entry'].append({
                    "resource": bp_obs,
                    "request": {
                        "method": "POST",
                        "url": "Observation"
                    }
                })
            
            # Other vitals
            for obs_type in ['weight', 'height', 'temperature', 'pulse', 'spo2']:
                if visit.get(obs_type):
                    obs = FHIRExporter.export_observation(resident_id, visit, obs_type)
                    bundle['entry'].append({
                        "resource": obs,
                        "request": {
                            "method": "POST",
                            "url": "Observation"
                        }
                    })
        
        return bundle
    
    @staticmethod
    def _calculate_birth_date(age: Optional[int]) -> str:
        """Calculate approximate birth date from age."""
        if age:
            birth_year = datetime.now().year - age
            return f"{birth_year}-01-01"
        return None


def export_to_fhir_file(resident_data: Dict, visits_data: List[Dict], output_path: str):
    """
    Export data to FHIR JSON file.
    
    Args:
        resident_data: Resident information
        visits_data: List of visits
        output_path: Path to save FHIR bundle
    """
    bundle = FHIRExporter.export_bundle(resident_data, visits_data)
    
    with open(output_path, 'w') as f:
        json.dump(bundle, f, indent=2)
    
    logger.info(f"FHIR bundle exported to {output_path}")
```

### Step 3: Add Configuration Support

Update `.env.example` to include:
```env
# OpenMRS Integration (Optional)
OPENMRS_ENABLED=false
OPENMRS_BASE_URL=http://localhost:8080/openmrs
OPENMRS_USERNAME=admin
OPENMRS_PASSWORD=Admin123
```

### Step 4: Create Export Page

Create `pages/11_🔗_OpenMRS_Export.py`:

```python
"""
OpenMRS Export Page
Export data to OpenMRS or FHIR format for interoperability.
"""
import streamlit as st
from datetime import datetime
import json
import os
from database import DatabaseManager
from utils import check_authentication, select_resident_widget
from utils.openmrs_integration import OpenMRSClient, FHIRExporter, export_to_fhir_file

# Check authentication
if not check_authentication():
    st.error("Please log in to access this page")
    st.stop()

# Initialize database manager
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

db = st.session_state.db_manager

# Page header
st.title("🔗 OpenMRS Integration")
st.markdown("Export data to OpenMRS or FHIR format for interoperability")
st.markdown("---")

# Configuration section
st.header("⚙️ Configuration")

col1, col2 = st.columns(2)

with col1:
    export_type = st.radio(
        "Export Type",
        ["FHIR JSON File", "Direct to OpenMRS"],
        help="Choose how to export the data"
    )

with col2:
    if export_type == "Direct to OpenMRS":
        st.info("Configure OpenMRS connection settings")

# OpenMRS settings (if direct export)
if export_type == "Direct to OpenMRS":
    with st.expander("🔧 OpenMRS Connection Settings", expanded=True):
        openmrs_url = st.text_input(
            "OpenMRS Base URL",
            value=os.getenv("OPENMRS_BASE_URL", "http://localhost:8080/openmrs"),
            help="Full URL to OpenMRS instance"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            openmrs_username = st.text_input(
                "Username",
                value=os.getenv("OPENMRS_USERNAME", ""),
                help="OpenMRS username with API access"
            )
        with col2:
            openmrs_password = st.text_input(
                "Password",
                type="password",
                help="OpenMRS password"
            )
        
        if st.button("🔌 Test Connection"):
            if openmrs_url and openmrs_username and openmrs_password:
                with st.spinner("Testing connection..."):
                    client = OpenMRSClient(openmrs_url, openmrs_username, openmrs_password)
                    if client.test_connection():
                        st.success("✅ Connection successful!")
                    else:
                        st.error("❌ Connection failed. Please check your settings.")
            else:
                st.warning("Please fill in all connection fields")

st.markdown("---")

# Data selection
st.header("📋 Select Data to Export")

export_scope = st.radio(
    "Export Scope",
    ["Single Resident", "All Residents", "Date Range"],
    help="Choose what data to export"
)

selected_resident = None
date_range = None

if export_scope == "Single Resident":
    st.subheader("Select Resident")
    selected_resident = select_resident_widget(db, key_prefix="openmrs_export")
    
    if selected_resident:
        st.success(f"✅ Selected: {selected_resident['name']} ({selected_resident['unique_id']})")

elif export_scope == "Date Range":
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime(2024, 1, 1))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    if start_date and end_date:
        date_range = (start_date.isoformat(), end_date.isoformat())
        st.info(f"📅 Exporting data from {start_date} to {end_date}")

st.markdown("---")

# Export action
st.header("🚀 Export Data")

if st.button("📤 Export Now", type="primary"):
    try:
        # Gather data based on scope
        if export_scope == "Single Resident" and selected_resident:
            residents = [selected_resident]
        elif export_scope == "All Residents":
            residents = db.get_all_residents()
        elif export_scope == "Date Range" and date_range:
            residents = db.get_residents_by_date_range(date_range[0], date_range[1])
        else:
            st.error("Please select data to export")
            st.stop()
        
        if not residents:
            st.warning("No data found to export")
            st.stop()
        
        # Export based on type
        if export_type == "FHIR JSON File":
            # Export to FHIR files
            export_dir = "exports/fhir"
            os.makedirs(export_dir, exist_ok=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, resident in enumerate(residents):
                status_text.text(f"Exporting {resident['name']}...")
                
                # Get visits for this resident
                visits = db.get_visits_by_resident(resident['unique_id'])
                
                # Export to FHIR
                filename = f"{export_dir}/{resident['unique_id']}_fhir.json"
                export_to_fhir_file(resident, visits, filename)
                
                progress_bar.progress((idx + 1) / len(residents))
            
            st.success(f"✅ Successfully exported {len(residents)} residents to {export_dir}/")
            st.info(f"📁 Files saved in: {os.path.abspath(export_dir)}")
            
        elif export_type == "Direct to OpenMRS":
            if not all([openmrs_url, openmrs_username, openmrs_password]):
                st.error("Please configure OpenMRS connection settings")
                st.stop()
            
            # Export to OpenMRS
            client = OpenMRSClient(openmrs_url, openmrs_username, openmrs_password)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            success_count = 0
            error_count = 0
            
            for idx, resident in enumerate(residents):
                status_text.text(f"Uploading {resident['name']}...")
                
                # Create patient
                patient_result = client.create_patient(resident)
                if patient_result:
                    success_count += 1
                    
                    # Upload visits
                    visits = db.get_visits_by_resident(resident['unique_id'])
                    for visit in visits:
                        client.create_encounter(resident['unique_id'], visit)
                else:
                    error_count += 1
                
                progress_bar.progress((idx + 1) / len(residents))
            
            if error_count == 0:
                st.success(f"✅ Successfully exported {success_count} residents to OpenMRS!")
            else:
                st.warning(f"⚠️ Exported {success_count} residents, {error_count} failed")
    
    except Exception as e:
        st.error(f"❌ Export failed: {str(e)}")
        st.exception(e)

# Documentation
with st.expander("📖 Help & Documentation"):
    st.markdown("""
    ### What is FHIR?
    FHIR (Fast Healthcare Interoperability Resources) is a standard for exchanging healthcare information electronically. 
    Exporting to FHIR format allows your data to be imported into any FHIR-compatible system, including OpenMRS.
    
    ### Direct OpenMRS Export
    This feature directly creates patients and encounters in an OpenMRS instance via its REST API.
    
    **Requirements:**
    - OpenMRS 2.x or higher
    - API user credentials
    - Network access to OpenMRS server
    
    ### FHIR File Export
    Exports data as JSON files that can be:
    - Imported into OpenMRS using FHIR2 module
    - Shared with other health information systems
    - Used for backup and archival
    - Analyzed with FHIR-compatible tools
    
    ### Troubleshooting
    - **Connection Failed**: Check URL format and network connectivity
    - **Authentication Error**: Verify username and password
    - **Concept Not Found**: OpenMRS concepts may need to be mapped
    
    For more information, see: [OPENMRS_INTEGRATION_GUIDE.md](../OPENMRS_INTEGRATION_GUIDE.md)
    """)
```

---

## Phase 2: Testing the Integration

### Step 1: Setup Test OpenMRS Instance

Option A: Use OpenMRS Demo
```
URL: https://demo.openmrs.org/openmrs
Username: admin
Password: Admin123
```

Option B: Run Local OpenMRS with Docker
```bash
docker run -d \
  --name openmrs \
  -p 8080:8080 \
  -e DB_DATABASE=openmrs \
  -e DB_USERNAME=openmrs \
  -e DB_PASSWORD=openmrs \
  openmrs/openmrs-core:latest
```

### Step 2: Test FHIR Export

```python
# Test script: test_fhir_export.py
from utils.openmrs_integration import FHIRExporter
import json

# Sample resident data
resident = {
    'unique_id': 'VH-2024-0001',
    'name': 'Test Patient',
    'age': 35,
    'gender': 'Female',
    'address': 'Test Village',
    'village_area': 'Chiklod',
    'phone': '1234567890'
}

# Sample visit data
visits = [{
    'visit_date': '2024-01-15',
    'bp_systolic': 120,
    'bp_diastolic': 80,
    'temperature': 98.6,
    'pulse': 72,
    'weight': 65.5,
    'height': 165,
    'spo2': 98
}]

# Export
bundle = FHIRExporter.export_bundle(resident, visits)
print(json.dumps(bundle, indent=2))
```

### Step 3: Test OpenMRS Connection

```python
# Test script: test_openmrs_connection.py
from utils.openmrs_integration import OpenMRSClient

client = OpenMRSClient(
    base_url="https://demo.openmrs.org/openmrs",
    username="admin",
    password="Admin123"
)

if client.test_connection():
    print("✅ Connection successful!")
else:
    print("❌ Connection failed")
```

---

## Phase 3: Production Deployment

### Step 1: Environment Configuration

Create `.env` file:
```env
# Production OpenMRS Settings
OPENMRS_ENABLED=true
OPENMRS_BASE_URL=https://your-openmrs-instance.com/openmrs
OPENMRS_USERNAME=integration_user
OPENMRS_PASSWORD=secure_password_here
OPENMRS_SYNC_INTERVAL=3600  # Sync every hour (in seconds)
```

### Step 2: Setup Automated Sync (Optional)

Create `utils/openmrs_sync.py`:

```python
"""
Automated synchronization service for OpenMRS.
Runs periodically to sync new/updated records.
"""
import schedule
import time
from datetime import datetime, timedelta
import logging
from database import DatabaseManager
from utils.openmrs_integration import OpenMRSClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenMRSSync:
    """Automated sync service for OpenMRS."""
    
    def __init__(self, client: OpenMRSClient, db: DatabaseManager):
        self.client = client
        self.db = db
        self.last_sync = None
    
    def sync_new_residents(self):
        """Sync newly registered residents."""
        logger.info("Starting resident sync...")
        
        try:
            # Get residents registered since last sync
            if self.last_sync:
                residents = self.db.get_residents_since(self.last_sync)
            else:
                # First sync - get all residents
                residents = self.db.get_all_residents()
            
            logger.info(f"Found {len(residents)} residents to sync")
            
            for resident in residents:
                result = self.client.create_patient(resident)
                if result:
                    logger.info(f"Synced resident: {resident['unique_id']}")
                else:
                    logger.error(f"Failed to sync: {resident['unique_id']}")
                
                # Small delay to avoid overwhelming the server
                time.sleep(1)
            
            self.last_sync = datetime.now()
            logger.info("Resident sync completed")
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
    
    def sync_new_visits(self):
        """Sync new visits/encounters."""
        logger.info("Starting visit sync...")
        
        try:
            # Get visits since last sync
            if self.last_sync:
                visits = self.db.get_visits_since(self.last_sync)
            else:
                # First sync - get recent visits (last 30 days)
                cutoff = (datetime.now() - timedelta(days=30)).isoformat()
                visits = self.db.get_visits_since(cutoff)
            
            logger.info(f"Found {len(visits)} visits to sync")
            
            for visit in visits:
                result = self.client.create_encounter(
                    visit['resident_id'],
                    visit
                )
                if result:
                    logger.info(f"Synced visit: {visit['visit_id']}")
                else:
                    logger.error(f"Failed to sync visit: {visit['visit_id']}")
                
                time.sleep(1)
            
            logger.info("Visit sync completed")
            
        except Exception as e:
            logger.error(f"Visit sync failed: {e}")
    
    def run_sync(self):
        """Run full sync cycle."""
        logger.info("=" * 50)
        logger.info(f"Starting sync cycle at {datetime.now()}")
        logger.info("=" * 50)
        
        if not self.client.test_connection():
            logger.error("Cannot connect to OpenMRS. Skipping sync.")
            return
        
        self.sync_new_residents()
        self.sync_new_visits()
        
        logger.info("Sync cycle completed")
        logger.info("=" * 50)


def start_sync_service(interval_minutes=60):
    """
    Start the sync service.
    
    Args:
        interval_minutes: Sync interval in minutes
    """
    import os
    
    # Load configuration
    openmrs_url = os.getenv("OPENMRS_BASE_URL")
    openmrs_username = os.getenv("OPENMRS_USERNAME")
    openmrs_password = os.getenv("OPENMRS_PASSWORD")
    
    if not all([openmrs_url, openmrs_username, openmrs_password]):
        logger.error("OpenMRS credentials not configured. Sync service disabled.")
        return
    
    # Initialize
    client = OpenMRSClient(openmrs_url, openmrs_username, openmrs_password)
    db = DatabaseManager()
    sync_service = OpenMRSSync(client, db)
    
    # Schedule sync
    schedule.every(interval_minutes).minutes.do(sync_service.run_sync)
    
    logger.info(f"Sync service started. Running every {interval_minutes} minutes.")
    logger.info("Press Ctrl+C to stop.")
    
    # Run immediately on start
    sync_service.run_sync()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    start_sync_service(interval_minutes=60)
```

### Step 3: Run Sync as Background Service

Create `openmrs_sync.service` (Linux):
```ini
[Unit]
Description=OpenMRS Sync Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/CFMProjectChiklod
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python utils/openmrs_sync.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo cp openmrs_sync.service /etc/systemd/system/
sudo systemctl enable openmrs_sync
sudo systemctl start openmrs_sync
sudo systemctl status openmrs_sync
```

---

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check OpenMRS is running: `curl http://your-openmrs-url/openmrs`
   - Verify firewall allows connections
   - Check URL includes `/openmrs` path

2. **Authentication Failed**
   - Verify username/password in OpenMRS
   - Ensure user has API privileges
   - Check for special characters in password

3. **Concept Not Found**
   - OpenMRS concepts vary by installation
   - Update concept UUIDs in `openmrs_integration.py`
   - Use OpenMRS admin to find correct concept IDs

4. **Patient Already Exists**
   - OpenMRS rejects duplicate identifiers
   - Add duplicate checking before creating patients
   - Consider using `GET` to check existence first

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Create integration module
3. ✅ Add export page to UI
4. ✅ Test with demo OpenMRS
5. ✅ Configure production settings
6. ⬜ Deploy to production
7. ⬜ Monitor sync logs
8. ⬜ Train users on export features

---

## Support

For issues with this integration:
1. Check the [OPENMRS_COMPARISON.md](./OPENMRS_COMPARISON.md) document
2. Review OpenMRS documentation: https://wiki.openmrs.org/
3. Post on OpenMRS Talk: https://talk.openmrs.org/
4. Create GitHub issue in this repository

---

## License

This integration code is provided under the same MIT license as the main project.
