"""
Record Visit Page
Allows health workers to record visits with vitals and observations.
"""

import streamlit as st
from datetime import datetime
from database import DatabaseManager
from utils import (
    check_authentication,
    get_current_user_name,
    save_multiple_photos,
    validate_blood_pressure,
    validate_temperature,
    validate_pulse,
    validate_weight,
    validate_height,
    validate_spo2,
    calculate_bmi
)

# Page configuration
st.set_page_config(
    page_title="Record Visit",
    page_icon="🏥",
    layout="wide"
)

# Check authentication
if not check_authentication():
    st.error("Please log in to access this page")
    st.stop()

# Initialize database manager
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

db = st.session_state.db_manager

# Page header
st.title("🏥 Record Visit")
st.markdown("Record health checkup and vitals for a resident")
st.markdown("---")

# Resident selection
st.subheader("1️⃣ Select Resident")

col1, col2 = st.columns([2, 1])

with col1:
    search_term = st.text_input("Search by Name or Unique ID", placeholder="Start typing...")

with col2:
    if st.button("🔍 Search", use_container_width=True):
        pass  # Search on input change

# Search and display residents
if search_term:
    residents = db.search_residents(search_term)
    
    if residents:
        st.write(f"Found {len(residents)} resident(s)")
        
        # Create selection
        resident_options = {f"{r['name']} ({r['unique_id']})": r['unique_id'] for r in residents}
        selected_display = st.selectbox("Select Resident", list(resident_options.keys()))
        selected_id = resident_options[selected_display]
        
        # Get resident details
        resident = db.get_resident(selected_id)
        
        if resident:
            with st.expander("📋 Resident Information", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Name:** {resident['name']}")
                    st.write(f"**ID:** {resident['unique_id']}")
                
                with col2:
                    st.write(f"**Age:** {resident['age'] if resident['age'] else 'N/A'}")
                    st.write(f"**Gender:** {resident['gender'] if resident['gender'] else 'N/A'}")
                
                with col3:
                    # Get visit count
                    visits = db.get_resident_visits(selected_id)
                    st.write(f"**Total Visits:** {len(visits)}")
                    if visits:
                        st.write(f"**Last Visit:** {visits[0]['visit_date']}")
            
            st.markdown("---")
            
            # Visit form
            st.subheader("2️⃣ Record Vitals and Observations")
            
            with st.form("visit_form"):
                # Vitals
                st.write("**Vital Signs**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    bp_col1, bp_col2 = st.columns(2)
                    with bp_col1:
                        bp_systolic = st.number_input("Systolic BP (mmHg)", min_value=0, max_value=300, value=None, placeholder="120")
                    with bp_col2:
                        bp_diastolic = st.number_input("Diastolic BP (mmHg)", min_value=0, max_value=200, value=None, placeholder="80")
                    
                    temperature = st.number_input("Temperature (°F)", min_value=0.0, max_value=120.0, value=None, step=0.1, placeholder="98.6")
                    pulse = st.number_input("Pulse Rate (bpm)", min_value=0, max_value=300, value=None, placeholder="72")
                
                with col2:
                    weight = st.number_input("Weight (kg)", min_value=0.0, max_value=500.0, value=None, step=0.1, placeholder="70.0")
                    height = st.number_input("Height (cm)", min_value=0.0, max_value=300.0, value=None, step=0.1, placeholder="170.0")
                    spo2 = st.number_input("SpO2 (%)", min_value=0, max_value=100, value=None, placeholder="98")
                
                # Calculate BMI
                bmi = calculate_bmi(weight, height)
                if bmi:
                    st.info(f"**Calculated BMI:** {bmi}")
                
                st.markdown("---")
                
                # Complaints and observations
                st.write("**Clinical Information**")
                
                complaints = st.text_area("Chief Complaints", placeholder="Patient's main complaints...", height=100)
                observations = st.text_area("Clinical Observations", placeholder="Health worker's observations...", height=100)
                
                st.markdown("---")
                
                # Photos
                st.write("**Visit Photos (Optional)**")
                visit_photos = st.file_uploader(
                    "Upload photos",
                    type=['jpg', 'jpeg', 'png'],
                    accept_multiple_files=True,
                    help="Maximum 5MB per photo"
                )
                
                if visit_photos:
                    st.write(f"{len(visit_photos)} photo(s) selected")
                
                st.markdown("---")
                
                # Submit button
                submitted = st.form_submit_button("✅ Record Visit", use_container_width=True)
                
                if submitted:
                    # Validate inputs
                    errors = []
                    
                    is_valid, error = validate_blood_pressure(bp_systolic, bp_diastolic)
                    if not is_valid:
                        errors.append(error)
                    
                    is_valid, error = validate_temperature(temperature)
                    if not is_valid:
                        errors.append(error)
                    
                    is_valid, error = validate_pulse(pulse)
                    if not is_valid:
                        errors.append(error)
                    
                    is_valid, error = validate_weight(weight)
                    if not is_valid:
                        errors.append(error)
                    
                    is_valid, error = validate_height(height)
                    if not is_valid:
                        errors.append(error)
                    
                    is_valid, error = validate_spo2(spo2)
                    if not is_valid:
                        errors.append(error)
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        # Save photos
                        photo_paths = []
                        if visit_photos:
                            photo_paths = save_multiple_photos(visit_photos, selected_id, "visit")
                        
                        # Prepare visit data
                        visit_data = {
                            'resident_id': selected_id,
                            'visit_date': datetime.now().strftime("%Y-%m-%d"),
                            'visit_time': datetime.now().strftime("%H:%M:%S"),
                            'health_worker': get_current_user_name(),
                            'bp_systolic': bp_systolic,
                            'bp_diastolic': bp_diastolic,
                            'temperature': temperature,
                            'pulse': pulse,
                            'weight': weight,
                            'height': height,
                            'bmi': bmi,
                            'spo2': spo2,
                            'complaints': complaints if complaints else None,
                            'observations': observations if observations else None,
                            'photo_paths': ','.join(photo_paths) if photo_paths else None
                        }
                        
                        # Add to database
                        success = db.add_visit(visit_data)
                        
                        if success:
                            st.success("✅ Visit recorded successfully!")
                            st.balloons()
                            
                            # Action buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("➕ Record Another Visit", use_container_width=True):
                                    st.rerun()
                            with col2:
                                if st.button("👤 View Resident Profile", use_container_width=True):
                                    st.switch_page("pages/4_👤_View_Resident.py")
                        else:
                            st.error("❌ Failed to record visit. Please try again.")
    else:
        st.warning("No residents found matching your search.")
else:
    st.info("👆 Please search for a resident to start recording a visit")
