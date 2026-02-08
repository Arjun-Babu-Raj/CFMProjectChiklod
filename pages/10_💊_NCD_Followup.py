"""
NCD (Non-Communicable Disease) Followup Page
Track Diabetes and Hypertension patients with trend analysis.
"""

import streamlit as st
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
import pandas as pd
from database import DatabaseManager
from utils import check_authentication, get_current_user_name, select_resident_widget

# Check authentication
if not check_authentication():
    st.error("Please log in to access this page")
    st.stop()

# Initialize database manager
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

db = st.session_state.db_manager

# Page header
st.title("💊 NCD Followup Tracking")
st.markdown("Non-Communicable Disease Management: Diabetes & Hypertension")
st.markdown("---")

# Patient Selection
st.subheader("Select Patient")

# Use the new search-to-select widget for NCD patients
selected_patient = select_resident_widget(db, key_prefix="ncd_followup")

if not selected_patient:
    st.info("Search for an adult resident (18+ years) to manage NCD followup records.")
    st.stop()

# Validate age (typically adults)
age = selected_patient.get('age')
if age is not None and age < 18:
    st.warning(f"⚠️ {selected_patient['name']} is under 18 years old. NCD tracking is typically for adults. You can still proceed if needed.")


# Display patient info
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Name", selected_patient['name'])
with col2:
    st.metric("Age", f"{selected_patient.get('age', 'N/A')} years")
with col3:
    st.metric("Gender", selected_patient.get('gender', 'N/A'))
with col4:
    st.metric("ID", selected_patient['unique_id'])

st.markdown("---")

# Three tabs: Data Entry, Trends, and Due List
tab1, tab2, tab3 = st.tabs(["📝 Record Checkup", "📊 Trend Analysis", "⏰ Due List"])

with tab1:
    st.subheader("Record NCD Checkup")
    
    with st.form("ncd_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Information**")
            checkup_date = st.date_input("Checkup Date", value=date.today(), max_value=date.today())
            
            condition_type = st.selectbox(
                "Condition Type",
                ["Hypertension", "Diabetes", "Hypertension + Diabetes", "Other"]
            )
            
            st.markdown("**Blood Pressure**")
            bp_systolic = st.number_input("Systolic BP (mmHg)", min_value=0, max_value=250, value=120)
            bp_diastolic = st.number_input("Diastolic BP (mmHg)", min_value=0, max_value=150, value=80)
            
            # BP status indicator
            if bp_systolic > 0 and bp_diastolic > 0:
                if bp_systolic >= 140 or bp_diastolic >= 90:
                    st.error("⚠️ High Blood Pressure!")
                elif bp_systolic < 120 and bp_diastolic < 80:
                    st.success("✓ Normal Blood Pressure")
                else:
                    st.warning("⚠️ Pre-Hypertension")
        
        with col2:
            st.markdown("**Blood Sugar**")
            fasting_blood_sugar = st.number_input(
                "Fasting Blood Sugar (mg/dL)", 
                min_value=0.0, max_value=500.0, 
                step=1.0, format="%.0f", value=0.0
            )
            
            random_blood_sugar = st.number_input(
                "Random Blood Sugar (mg/dL)", 
                min_value=0.0, max_value=500.0, 
                step=1.0, format="%.0f", value=0.0
            )
            
            # Blood sugar status indicator
            if fasting_blood_sugar > 0:
                if fasting_blood_sugar >= 126:
                    st.error("⚠️ High Fasting Blood Sugar (Diabetic Range)")
                elif fasting_blood_sugar >= 100:
                    st.warning("⚠️ Pre-Diabetic Range")
                else:
                    st.success("✓ Normal Fasting Blood Sugar")
            
            if random_blood_sugar > 0:
                if random_blood_sugar >= 200:
                    st.error("⚠️ High Random Blood Sugar (Diabetic Range)")
                elif random_blood_sugar >= 140:
                    st.warning("⚠️ Elevated Random Blood Sugar")
                else:
                    st.success("✓ Normal Random Blood Sugar")
        
        st.markdown("**Treatment & Symptoms**")
        col3, col4 = st.columns(2)
        
        with col3:
            medication_adherence = st.radio(
                "Medication Adherence",
                ["Yes", "No", "Partially"],
                horizontal=True
            )
        
        with col4:
            referral_needed = st.checkbox("Referral Needed")
        
        symptoms = st.text_area(
            "Symptoms / Complaints",
            placeholder="Any new symptoms, side effects, or concerns..."
        )
        
        submitted = st.form_submit_button("💾 Save Checkup Record", use_container_width=True)
        
        if submitted:
            ncd_data = {
                'resident_id': selected_patient['unique_id'],
                'checkup_date': checkup_date.strftime('%Y-%m-%d'),
                'condition_type': condition_type,
                'bp_systolic': bp_systolic if bp_systolic > 0 else None,
                'bp_diastolic': bp_diastolic if bp_diastolic > 0 else None,
                'fasting_blood_sugar': fasting_blood_sugar if fasting_blood_sugar > 0 else None,
                'random_blood_sugar': random_blood_sugar if random_blood_sugar > 0 else None,
                'medication_adherence': medication_adherence,
                'symptoms': symptoms if symptoms else None,
                'referral_needed': referral_needed
            }
            
            if db.add_ncd_followup(ncd_data):
                st.success("✅ NCD checkup record saved successfully!")
                
                # Show critical alerts
                if bp_systolic >= 160 or bp_diastolic >= 100:
                    st.error("🚨 CRITICAL: Severe Hypertension! Immediate medical attention required.")
                
                if fasting_blood_sugar >= 200 or random_blood_sugar >= 300:
                    st.error("🚨 CRITICAL: Very High Blood Sugar! Immediate medical attention required.")
                
                if medication_adherence == "No":
                    st.warning("⚠️ Warning: Poor medication adherence noted.")
                
                if referral_needed:
                    st.info("ℹ️ Referral to specialist recommended.")
                
                st.rerun()
            else:
                st.error("Failed to save NCD checkup record")
    
    # Show recent checkup summary
    st.markdown("---")
    st.subheader("Recent Checkup Summary")
    
    ncd_records = db.get_ncd_followup_records(selected_patient['unique_id'])
    
    if ncd_records:
        latest = ncd_records[0]  # Most recent
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            bp_sys = latest.get('bp_systolic', 'N/A')
            bp_dia = latest.get('bp_diastolic', 'N/A')
            st.metric("Blood Pressure", f"{bp_sys}/{bp_dia}")
        
        with col2:
            fbs = latest.get('fasting_blood_sugar')
            if fbs:
                st.metric("Fasting BS", f"{fbs:.0f} mg/dL")
            else:
                st.metric("Fasting BS", "N/A")
        
        with col3:
            rbs = latest.get('random_blood_sugar')
            if rbs:
                st.metric("Random BS", f"{rbs:.0f} mg/dL")
            else:
                st.metric("Random BS", "N/A")
        
        with col4:
            st.metric("Last Visit", latest.get('checkup_date', 'N/A'))
    else:
        st.info("No checkup records found for this patient.")

with tab2:
    st.subheader("Trend Analysis")
    
    ncd_records = db.get_ncd_followup_records(selected_patient['unique_id'])
    
    if not ncd_records:
        st.info("No checkup records found. Add records in the 'Record Checkup' tab to see trends.")
    else:
        # Convert to DataFrame
        df = pd.DataFrame(ncd_records)
        df['checkup_date'] = pd.to_datetime(df['checkup_date'])
        df = df.sort_values('checkup_date')
        
        # Blood Pressure Trend
        st.markdown("### Blood Pressure Trend")
        
        fig_bp = go.Figure()
        
        # Add systolic line
        fig_bp.add_trace(go.Scatter(
            x=df['checkup_date'],
            y=df['bp_systolic'],
            mode='lines+markers',
            name='Systolic',
            line=dict(color='red', width=2),
            marker=dict(size=8)
        ))
        
        # Add diastolic line
        fig_bp.add_trace(go.Scatter(
            x=df['checkup_date'],
            y=df['bp_diastolic'],
            mode='lines+markers',
            name='Diastolic',
            line=dict(color='blue', width=2),
            marker=dict(size=8)
        ))
        
        # Add reference lines
        fig_bp.add_hline(y=140, line_dash="dash", line_color="orange", 
                        annotation_text="Systolic Target (<140)")
        fig_bp.add_hline(y=90, line_dash="dash", line_color="lightblue", 
                        annotation_text="Diastolic Target (<90)")
        
        fig_bp.update_layout(
            title=f"Blood Pressure Trend: {selected_patient['name']}",
            xaxis_title="Date",
            yaxis_title="Blood Pressure (mmHg)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_bp, use_container_width=True)
        
        # Blood Sugar Trend
        st.markdown("### Blood Sugar Trend")
        
        fig_bs = go.Figure()
        
        # Add fasting blood sugar
        df_fbs = df[df['fasting_blood_sugar'].notna()]
        if not df_fbs.empty:
            fig_bs.add_trace(go.Scatter(
                x=df_fbs['checkup_date'],
                y=df_fbs['fasting_blood_sugar'],
                mode='lines+markers',
                name='Fasting BS',
                line=dict(color='green', width=2),
                marker=dict(size=8)
            ))
        
        # Add random blood sugar
        df_rbs = df[df['random_blood_sugar'].notna()]
        if not df_rbs.empty:
            fig_bs.add_trace(go.Scatter(
                x=df_rbs['checkup_date'],
                y=df_rbs['random_blood_sugar'],
                mode='lines+markers',
                name='Random BS',
                line=dict(color='purple', width=2),
                marker=dict(size=8)
            ))
        
        # Add reference lines
        fig_bs.add_hline(y=126, line_dash="dash", line_color="orange", 
                        annotation_text="Fasting Target (<126)")
        fig_bs.add_hline(y=200, line_dash="dash", line_color="red", 
                        annotation_text="Random Target (<200)")
        
        fig_bs.update_layout(
            title=f"Blood Sugar Trend: {selected_patient['name']}",
            xaxis_title="Date",
            yaxis_title="Blood Sugar (mg/dL)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_bs, use_container_width=True)
        
        # Checkup History Table
        st.markdown("### Checkup History")
        
        display_df = df[['checkup_date', 'condition_type', 'bp_systolic', 'bp_diastolic',
                        'fasting_blood_sugar', 'random_blood_sugar', 'medication_adherence']].copy()
        display_df.columns = ['Date', 'Condition', 'BP Sys', 'BP Dia', 'FBS', 'RBS', 'Med Adherence']
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(display_df.sort_values('Date', ascending=False), 
                    use_container_width=True, hide_index=True)

with tab3:
    st.subheader("⏰ Patient Due List")
    st.markdown("Patients who haven't visited in more than 30 days")
    
    # Get due list
    due_list = db.get_ncd_due_list(days_threshold=30)
    
    if not due_list:
        st.success("✓ No overdue patients at this time!")
    else:
        # Create display dataframe
        due_data = []
        for record in due_list:
            due_data.append({
                'Name': record.get('resident_name', 'Unknown'),
                'Resident ID': record.get('resident_id', ''),
                'Condition': record.get('condition_type', 'N/A'),
                'Last Checkup': record.get('checkup_date', ''),
                'Days Overdue': record.get('days_overdue', 0)
            })
        
        df_due = pd.DataFrame(due_data)
        
        # Color code based on days overdue
        st.dataframe(df_due, use_container_width=True, hide_index=True)
        
        st.markdown(f"**Total Overdue Patients: {len(due_list)}**")
        
        # Summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_overdue = sum(r['days_overdue'] for r in due_list) / len(due_list)
            st.metric("Avg Days Overdue", f"{avg_overdue:.0f}")
        
        with col2:
            max_overdue = max(r['days_overdue'] for r in due_list)
            st.metric("Max Days Overdue", f"{max_overdue}")
        
        with col3:
            critical = len([r for r in due_list if r['days_overdue'] > 60])
            st.metric("Critical (>60 days)", critical)
        
        # Action buttons
        st.markdown("---")
        st.info("💡 **Action Required**: Contact these patients for follow-up appointments.")
