"""
View Resident Page
Display complete resident profile with longitudinal data, charts, and photo gallery.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import os
from database import DatabaseManager
from utils import check_authentication, photo_exists

# Page configuration
st.set_page_config(
    page_title="View Resident",
    page_icon="👤",
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
st.title("👤 View Resident Profile")
st.markdown("Complete resident profile with longitudinal data")
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
        # Create selection
        resident_options = {f"{r['name']} ({r['unique_id']})": r['unique_id'] for r in residents}
        selected_display = st.selectbox("Select Resident", list(resident_options.keys()))
        selected_id = resident_options[selected_display]
        
        # Get resident details
        resident = db.get_resident(selected_id)
        
        if resident:
            st.markdown("---")
            
            # Profile header
            col1, col2, col3 = st.columns([1, 2, 2])
            
            with col1:
                # Display profile photo
                if resident['photo_path'] and photo_exists(resident['photo_path']):
                    st.image(resident['photo_path'], width=200)
                else:
                    st.image("https://via.placeholder.com/200x200/CCCCCC/FFFFFF?text=No+Photo", width=200)
            
            with col2:
                st.subheader(resident['name'])
                st.write(f"**Unique ID:** {resident['unique_id']}")
                st.write(f"**Age:** {resident['age'] if resident['age'] else 'N/A'}")
                st.write(f"**Gender:** {resident['gender'] if resident['gender'] else 'N/A'}")
            
            with col3:
                st.write(f"**Phone:** {resident['phone'] if resident['phone'] else 'N/A'}")
                st.write(f"**Village Area:** {resident['village_area'] if resident['village_area'] else 'N/A'}")
                st.write(f"**Registered:** {resident['registration_date']}")
                st.write(f"**By:** {resident['registered_by']}")
            
            # Get visits and medical history
            visits = db.get_resident_visits(selected_id)
            medical_history = db.get_medical_history(selected_id)
            
            st.markdown("---")
            
            # Quick stats
            st.subheader("📊 Quick Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Visits", len(visits))
            
            with col2:
                if visits:
                    st.metric("Last Visit", visits[0]['visit_date'])
                else:
                    st.metric("Last Visit", "None")
            
            with col3:
                if visits:
                    # Count visits with vitals
                    visits_with_vitals = sum(1 for v in visits if v['bp_systolic'] or v['temperature'])
                    st.metric("Visits with Vitals", visits_with_vitals)
                else:
                    st.metric("Visits with Vitals", 0)
            
            with col4:
                st.metric("Medical History", "Yes" if medical_history else "No")
            
            st.markdown("---")
            
            # Tabs for different sections
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Vitals Trends", "🏥 Visit History", "📋 Medical History", "📷 Photo Gallery"])
            
            with tab1:
                st.subheader("Vitals Trends")
                
                if visits:
                    # Prepare data for charts
                    dates = [v['visit_date'] for v in reversed(visits)]
                    
                    # Blood Pressure Chart
                    bp_systolic = [v['bp_systolic'] for v in reversed(visits)]
                    bp_diastolic = [v['bp_diastolic'] for v in reversed(visits)]
                    
                    if any(bp_systolic) or any(bp_diastolic):
                        fig_bp = go.Figure()
                        fig_bp.add_trace(go.Scatter(x=dates, y=bp_systolic, mode='lines+markers', name='Systolic', line=dict(color='red')))
                        fig_bp.add_trace(go.Scatter(x=dates, y=bp_diastolic, mode='lines+markers', name='Diastolic', line=dict(color='blue')))
                        fig_bp.update_layout(title='Blood Pressure Trend', xaxis_title='Date', yaxis_title='BP (mmHg)')
                        st.plotly_chart(fig_bp, use_container_width=True)
                    
                    # Weight Chart
                    weights = [v['weight'] for v in reversed(visits)]
                    if any(weights):
                        fig_weight = go.Figure()
                        fig_weight.add_trace(go.Scatter(x=dates, y=weights, mode='lines+markers', line=dict(color='green')))
                        fig_weight.update_layout(title='Weight Trend', xaxis_title='Date', yaxis_title='Weight (kg)')
                        st.plotly_chart(fig_weight, use_container_width=True)
                    
                    # Temperature Chart
                    temps = [v['temperature'] for v in reversed(visits)]
                    if any(temps):
                        fig_temp = go.Figure()
                        fig_temp.add_trace(go.Scatter(x=dates, y=temps, mode='lines+markers', line=dict(color='orange')))
                        fig_temp.update_layout(title='Temperature Trend', xaxis_title='Date', yaxis_title='Temperature (°F)')
                        st.plotly_chart(fig_temp, use_container_width=True)
                    
                    # BMI Chart
                    bmis = [v['bmi'] for v in reversed(visits)]
                    if any(bmis):
                        fig_bmi = go.Figure()
                        fig_bmi.add_trace(go.Scatter(x=dates, y=bmis, mode='lines+markers', line=dict(color='purple')))
                        fig_bmi.update_layout(title='BMI Trend', xaxis_title='Date', yaxis_title='BMI')
                        st.plotly_chart(fig_bmi, use_container_width=True)
                else:
                    st.info("No visit data available for trends")
            
            with tab2:
                st.subheader("Visit History Timeline")
                
                if visits:
                    for idx, visit in enumerate(visits, 1):
                        with st.expander(f"**Visit {idx}** - {visit['visit_date']} {visit['visit_time']}", expanded=(idx==1)):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Vitals:**")
                                if visit['bp_systolic'] and visit['bp_diastolic']:
                                    st.write(f"• BP: {visit['bp_systolic']}/{visit['bp_diastolic']} mmHg")
                                if visit['temperature']:
                                    st.write(f"• Temperature: {visit['temperature']}°F")
                                if visit['pulse']:
                                    st.write(f"• Pulse: {visit['pulse']} bpm")
                                if visit['weight']:
                                    st.write(f"• Weight: {visit['weight']} kg")
                                if visit['height']:
                                    st.write(f"• Height: {visit['height']} cm")
                                if visit['bmi']:
                                    st.write(f"• BMI: {visit['bmi']}")
                                if visit['spo2']:
                                    st.write(f"• SpO2: {visit['spo2']}%")
                            
                            with col2:
                                st.write(f"**Health Worker:** {visit['health_worker']}")
                                
                                if visit['complaints']:
                                    st.write("**Complaints:**")
                                    st.write(visit['complaints'])
                                
                                if visit['observations']:
                                    st.write("**Observations:**")
                                    st.write(visit['observations'])
                            
                            # Display visit photos
                            if visit['photo_paths']:
                                st.write("**Photos:**")
                                photo_paths = visit['photo_paths'].split(',')
                                cols = st.columns(min(len(photo_paths), 3))
                                for idx, photo_path in enumerate(photo_paths):
                                    if photo_exists(photo_path):
                                        with cols[idx % 3]:
                                            st.image(photo_path, width=200)
                else:
                    st.info("No visits recorded yet")
            
            with tab3:
                st.subheader("Medical History")
                
                if medical_history:
                    if medical_history['chronic_conditions']:
                        st.write("**Chronic Conditions:**")
                        st.write(medical_history['chronic_conditions'])
                        st.divider()
                    
                    if medical_history['past_diagnoses']:
                        st.write("**Past Diagnoses:**")
                        st.write(medical_history['past_diagnoses'])
                        st.divider()
                    
                    if medical_history['current_medications']:
                        st.write("**Current Medications:**")
                        st.write(medical_history['current_medications'])
                        st.divider()
                    
                    if medical_history['allergies']:
                        st.warning(f"**Allergies:** {medical_history['allergies']}")
                        st.divider()
                    
                    if medical_history['family_history']:
                        st.write("**Family History:**")
                        st.write(medical_history['family_history'])
                        st.divider()
                    
                    if medical_history['notes']:
                        st.write("**Additional Notes:**")
                        st.write(medical_history['notes'])
                        st.divider()
                    
                    st.caption(f"Last updated: {medical_history['last_updated']} by {medical_history['updated_by']}")
                    
                    if st.button("✏️ Edit Medical History", use_container_width=True):
                        st.switch_page("pages/3_📋_Medical_History.py")
                else:
                    st.info("No medical history recorded")
                    
                    if st.button("➕ Add Medical History", use_container_width=True):
                        st.switch_page("pages/3_📋_Medical_History.py")
            
            with tab4:
                st.subheader("Photo Gallery")
                
                # Collect all photos
                all_photos = []
                
                # Profile photo
                if resident['photo_path'] and photo_exists(resident['photo_path']):
                    all_photos.append(('Profile', resident['photo_path']))
                
                # Visit photos
                for visit in visits:
                    if visit['photo_paths']:
                        photo_paths = visit['photo_paths'].split(',')
                        for photo_path in photo_paths:
                            if photo_exists(photo_path):
                                all_photos.append((f"Visit {visit['visit_date']}", photo_path))
                
                if all_photos:
                    # Display photos in grid
                    cols = st.columns(3)
                    for idx, (label, photo_path) in enumerate(all_photos):
                        with cols[idx % 3]:
                            st.image(photo_path, caption=label, use_column_width=True)
                else:
                    st.info("No photos available")
            
            st.markdown("---")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🏥 Record New Visit", use_container_width=True):
                    st.switch_page("pages/2_🏥_Record_Visit.py")
            
            with col2:
                if st.button("📋 Update Medical History", use_container_width=True):
                    st.switch_page("pages/3_📋_Medical_History.py")
            
            with col3:
                if st.button("🔍 Search Other Residents", use_container_width=True):
                    st.switch_page("pages/6_🔍_Search.py")
    else:
        st.warning("No residents found matching your search.")
else:
    st.info("👆 Please search for a resident to view their profile")
