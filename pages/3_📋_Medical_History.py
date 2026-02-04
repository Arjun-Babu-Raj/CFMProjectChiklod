"""
Medical History Page
Allows health workers to add/update medical history for residents.
"""

import streamlit as st
from datetime import datetime
from database import DatabaseManager
from utils import check_authentication, get_current_user_name

# Check authentication
if not check_authentication():
    st.error("Please log in to access this page")
    st.stop()

# Initialize database manager
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

db = st.session_state.db_manager

# Page header
st.title("📋 Medical History")
st.markdown("Manage medical history for residents")
st.markdown("---")

# Resident selection
st.subheader("Select Resident")

col1, col2 = st.columns([2, 1])

with col1:
    search_term = st.text_input("Search by Name or Unique ID", placeholder="Start typing...")

with col2:
    if st.button("🔍 Search", use_container_width=True):
        pass

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
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Name:** {resident['name']}")
                    st.write(f"**ID:** {resident['unique_id']}")
                
                with col2:
                    st.write(f"**Age:** {resident['age'] if resident['age'] else 'N/A'}")
                    st.write(f"**Gender:** {resident['gender'] if resident['gender'] else 'N/A'}")
            
            st.markdown("---")
            
            # Get existing medical history
            existing_history = db.get_medical_history(selected_id)
            
            # Medical history form
            st.subheader("Medical History Details")
            
            with st.form("medical_history_form"):
                chronic_conditions = st.text_area(
                    "Chronic Conditions",
                    value=existing_history.get('chronic_conditions', '') if existing_history else '',
                    placeholder="List any chronic conditions (e.g., Diabetes, Hypertension, Asthma)",
                    height=100,
                    help="Enter ongoing health conditions"
                )
                
                past_diagnoses = st.text_area(
                    "Past Diagnoses",
                    value=existing_history.get('past_diagnoses', '') if existing_history else '',
                    placeholder="Previous illnesses and diagnoses",
                    height=100,
                    help="Historical medical diagnoses"
                )
                
                current_medications = st.text_area(
                    "Current Medications",
                    value=existing_history.get('current_medications', '') if existing_history else '',
                    placeholder="List current medications with dosage",
                    height=100,
                    help="Medications currently being taken"
                )
                
                allergies = st.text_area(
                    "Allergies",
                    value=existing_history.get('allergies', '') if existing_history else '',
                    placeholder="Drug allergies, food allergies, etc.",
                    height=80,
                    help="Known allergies"
                )
                
                family_history = st.text_area(
                    "Family History",
                    value=existing_history.get('family_history', '') if existing_history else '',
                    placeholder="Relevant family medical history",
                    height=100,
                    help="Health conditions in family members"
                )
                
                notes = st.text_area(
                    "Additional Notes",
                    value=existing_history.get('notes', '') if existing_history else '',
                    placeholder="Any other relevant medical information",
                    height=100,
                    help="Other important medical information"
                )
                
                st.markdown("---")
                
                # Submit button
                submitted = st.form_submit_button(
                    "💾 Save Medical History" if existing_history else "➕ Add Medical History",
                    use_container_width=True
                )
                
                if submitted:
                    # Prepare history data
                    history_data = {
                        'resident_id': selected_id,
                        'chronic_conditions': chronic_conditions if chronic_conditions else None,
                        'past_diagnoses': past_diagnoses if past_diagnoses else None,
                        'current_medications': current_medications if current_medications else None,
                        'allergies': allergies if allergies else None,
                        'family_history': family_history if family_history else None,
                        'notes': notes if notes else None,
                        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'updated_by': get_current_user_name()
                    }
                    
                    # Add or update in database
                    success = db.add_or_update_medical_history(history_data)
                    
                    if success:
                        st.success("✅ Medical history saved successfully!")
                        
                        if existing_history:
                            st.info("Medical history has been updated")
                        else:
                            st.info("Medical history has been created")
                        
                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("👤 View Resident Profile", use_container_width=True):
                                st.switch_page("pages/4_👤_View_Resident.py")
                        with col2:
                            if st.button("🏥 Record Visit", use_container_width=True):
                                st.switch_page("pages/2_🏥_Record_Visit.py")
                    else:
                        st.error("❌ Failed to save medical history. Please try again.")
            
            # Display existing history summary if available
            if existing_history:
                st.markdown("---")
                st.subheader("📝 History Summary")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.caption(f"**Last Updated:** {existing_history.get('last_updated', 'N/A')}")
                
                with col2:
                    st.caption(f"**Updated By:** {existing_history.get('updated_by', 'N/A')}")
    else:
        st.warning("No residents found matching your search.")
else:
    st.info("👆 Please search for a resident to manage medical history")
