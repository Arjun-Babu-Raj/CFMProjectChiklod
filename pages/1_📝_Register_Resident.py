"""
Resident Registration Page
Allows health workers to register new residents with profile photos.
"""

import streamlit as st
from datetime import datetime
from database import DatabaseManager
from utils import (
    check_authentication,
    get_current_user_name,
    generate_unique_id,
    save_uploaded_photo,
    validate_phone,
    validate_age,
    validate_required_field
)

# Page configuration
st.set_page_config(
    page_title="Register Resident",
    page_icon="📝",
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
st.title("📝 Register New Resident")
st.markdown("Fill in the details to register a new village resident")
st.markdown("---")

# Registration form
with st.form("registration_form"):
    st.subheader("Personal Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name *", placeholder="Enter full name")
        age = st.number_input("Age", min_value=0, max_value=120, value=None, placeholder="Enter age")
        gender = st.selectbox("Gender", ["", "Male", "Female", "Other"])
        phone = st.text_input("Phone Number", placeholder="10-digit phone number")
    
    with col2:
        village_area = st.text_input("Village Area", placeholder="Area or neighborhood")
        address = st.text_area("Address", placeholder="Full residential address", height=100)
    
    st.markdown("---")
    st.subheader("Profile Photo")
    
    photo = st.file_uploader(
        "Upload Profile Photo (Optional)",
        type=['jpg', 'jpeg', 'png'],
        help="Maximum size: 5MB. Image will be compressed automatically."
    )
    
    if photo:
        st.image(photo, caption="Preview", width=200)
    
    st.markdown("---")
    
    # Submit button
    submitted = st.form_submit_button("✅ Register Resident", use_container_width=True)
    
    if submitted:
        # Validate required fields
        errors = []
        
        is_valid, error = validate_required_field(name, "Name")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_age(age)
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_phone(phone)
        if not is_valid:
            errors.append(error)
        
        # Show errors if any
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Generate unique ID
            unique_id = generate_unique_id(db)
            
            # Save photo if uploaded
            photo_path = None
            if photo:
                photo_path = save_uploaded_photo(photo, unique_id, "profile")
                if not photo_path:
                    st.error("Failed to save photo. Continuing without photo.")
            
            # Prepare resident data
            resident_data = {
                'unique_id': unique_id,
                'name': name,
                'age': age if age is not None else None,
                'gender': gender if gender else None,
                'address': address if address else None,
                'phone': phone if phone else None,
                'village_area': village_area if village_area else None,
                'photo_path': photo_path,
                'registration_date': datetime.now().strftime("%Y-%m-%d"),
                'registered_by': get_current_user_name()
            }
            
            # Add to database
            success = db.add_resident(resident_data)
            
            if success:
                st.success(f"✅ Resident registered successfully!")
                st.info(f"**Unique ID:** {unique_id}")
                st.balloons()
                
                # Display summary
                with st.expander("📋 Registration Summary", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Unique ID:** {unique_id}")
                        st.write(f"**Name:** {name}")
                        st.write(f"**Age:** {age if age else 'Not provided'}")
                        st.write(f"**Gender:** {gender if gender else 'Not provided'}")
                    
                    with col2:
                        st.write(f"**Phone:** {phone if phone else 'Not provided'}")
                        st.write(f"**Village Area:** {village_area if village_area else 'Not provided'}")
                        st.write(f"**Registered by:** {get_current_user_name()}")
                        st.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
                
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("➕ Register Another Resident", use_container_width=True):
                        st.rerun()
                with col2:
                    if st.button("👤 View Resident Profile", use_container_width=True):
                        st.switch_page("pages/4_👤_View_Resident.py")
            else:
                st.error("❌ Failed to register resident. Please try again.")

# Display recent registrations
st.markdown("---")
st.subheader("📋 Recent Registrations")

recent_residents = db.get_all_residents()[:10]  # Get last 10

if recent_residents:
    for resident in recent_residents:
        with st.expander(f"**{resident['name']}** - {resident['unique_id']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Age:** {resident['age'] if resident['age'] else 'N/A'}")
                st.write(f"**Gender:** {resident['gender'] if resident['gender'] else 'N/A'}")
                st.write(f"**Phone:** {resident['phone'] if resident['phone'] else 'N/A'}")
            
            with col2:
                st.write(f"**Village Area:** {resident['village_area'] if resident['village_area'] else 'N/A'}")
                st.write(f"**Registered:** {resident['registration_date']}")
                st.write(f"**By:** {resident['registered_by']}")
else:
    st.info("No residents registered yet.")
