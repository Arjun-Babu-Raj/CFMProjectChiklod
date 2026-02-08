"""
Maternal Health Tracking Page
Track Antenatal Care (ANC) and Postnatal Care (PNC) visits.
"""

import streamlit as st
from datetime import datetime, date, timedelta
import uuid
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
st.title("🤰 Maternal Health Tracking")
st.markdown("Antenatal Care (ANC) and Postnatal Care (PNC) Management")
st.markdown("---")


def calculate_edd(lmp_date):
    """Calculate Expected Date of Delivery using Naegele's rule (LMP + 280 days)."""
    if lmp_date:
        edd = lmp_date + timedelta(days=280)
        return edd
    return None


def calculate_gestational_age(lmp_date, visit_date):
    """Calculate gestational age in weeks."""
    if lmp_date and visit_date:
        delta = visit_date - lmp_date
        weeks = delta.days // 7
        return weeks
    return None


# Mother Selection
st.subheader("Select Mother")

# Filter female residents (typical age range for pregnancy)
filters = {'gender': 'Female', 'age_min': 15, 'age_max': 45}
mothers = db.filter_residents(filters)

if not mothers:
    st.warning("No female residents in the reproductive age group found.")
    st.info("Register residents first in the 'Register Resident' page.")
    st.stop()

# Create selection dropdown
mother_options = {f"{mother['name']} ({mother['unique_id']}) - Age: {mother.get('age', 'N/A')}": mother['unique_id'] 
                  for mother in mothers}

selected_display = st.selectbox("Choose a mother:", list(mother_options.keys()))
selected_mother_id = mother_options[selected_display]

# Get selected mother details
selected_mother = db.get_resident(selected_mother_id)

if not selected_mother:
    st.error("Mother not found!")
    st.stop()

# Display mother info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Name", selected_mother['name'])
with col2:
    st.metric("Age", f"{selected_mother.get('age', 'N/A')} years")
with col3:
    st.metric("ID", selected_mother['unique_id'])

st.markdown("---")

# Three tabs: ANC, PNC, and High-Risk Dashboard
tab1, tab2, tab3 = st.tabs(["🤰 Antenatal Care (ANC)", "👶 Postnatal Care (PNC)", "⚠️ High-Risk Mothers"])

with tab1:
    st.subheader("Antenatal Care (ANC) Visit")
    
    with st.form("anc_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Information**")
            visit_date = st.date_input("Visit Date", value=date.today(), max_value=date.today())
            
            # Generate or input pregnancy ID
            pregnancy_id = st.text_input("Pregnancy ID", value=f"PREG-{uuid.uuid4().hex[:8].upper()}", 
                                        help="Unique ID for this pregnancy")
            
            lmp_date = st.date_input("Last Menstrual Period (LMP)", 
                                    value=None, 
                                    max_value=date.today())
            
            # Calculate EDD automatically
            if lmp_date:
                edd = calculate_edd(lmp_date)
                gestational_week = calculate_gestational_age(lmp_date, visit_date)
                st.info(f"📅 Calculated EDD: **{edd.strftime('%Y-%m-%d')}**")
                st.info(f"📊 Gestational Age: **{gestational_week} weeks**")
            else:
                edd = None
                gestational_week = None
        
        with col2:
            st.markdown("**Vitals & Measurements**")
            fundal_height = st.number_input("Fundal Height (cm)", min_value=0.0, max_value=50.0, 
                                           step=0.5, format="%.1f", value=0.0)
            fetal_heart_rate = st.number_input("Fetal Heart Rate (bpm)", min_value=0, max_value=200, 
                                              value=0)
            bp_systolic = st.number_input("BP Systolic (mmHg)", min_value=0, max_value=250, value=120)
            bp_diastolic = st.number_input("BP Diastolic (mmHg)", min_value=0, max_value=150, value=80)
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("**Laboratory Tests**")
            urine_albumin = st.selectbox("Urine Albumin", ["", "Nil", "Trace", "+", "++", "+++"])
            hemoglobin = st.number_input("Hemoglobin (g/dL)", min_value=0.0, max_value=20.0, 
                                        step=0.1, format="%.1f", value=0.0)
        
        with col4:
            st.markdown("**Supplements & Immunization**")
            tt_dose = st.number_input("TT Dose Number", min_value=0, max_value=5, value=0, 
                                     help="Tetanus Toxoid dose number")
            calcium_iron_status = st.selectbox("Calcium & Iron Supplementation", 
                                              ["", "Regular", "Irregular", "Not Started"])
        
        st.markdown("**Danger Signs & Notes**")
        danger_signs = st.text_area("Danger Signs (if any)", 
                                    placeholder="e.g., Bleeding, severe headache, blurred vision, reduced fetal movements...")
        
        submitted = st.form_submit_button("💾 Save ANC Record", use_container_width=True)
        
        if submitted:
            if not lmp_date:
                st.error("LMP date is required for ANC records")
            else:
                anc_data = {
                    'resident_id': selected_mother_id,
                    'pregnancy_id': pregnancy_id,
                    'visit_type': 'ANC',
                    'visit_date': visit_date.strftime('%Y-%m-%d'),
                    'lmp_date': lmp_date.strftime('%Y-%m-%d'),
                    'edd_date': edd.strftime('%Y-%m-%d') if edd else None,
                    'gestational_week': gestational_week,
                    'fundal_height': fundal_height if fundal_height > 0 else None,
                    'fetal_heart_rate': fetal_heart_rate if fetal_heart_rate > 0 else None,
                    'urine_albumin': urine_albumin if urine_albumin else None,
                    'hemoglobin': hemoglobin if hemoglobin > 0 else None,
                    'tt_dose': tt_dose if tt_dose > 0 else None,
                    'calcium_iron_status': calcium_iron_status if calcium_iron_status else None,
                    'danger_signs': danger_signs if danger_signs else None,
                    'bp_systolic': bp_systolic if bp_systolic > 0 else None,
                    'delivery_outcome': None
                }
                
                if db.add_maternal_health_record(anc_data):
                    st.success("✅ ANC record saved successfully!")
                    
                    # Show alerts for high-risk factors
                    if bp_systolic >= 140 or bp_diastolic >= 90:
                        st.error("⚠️ ALERT: High Blood Pressure detected! Immediate referral recommended.")
                    
                    if hemoglobin > 0 and hemoglobin < 11:
                        st.error("⚠️ ALERT: Anemia detected! (Hb < 11 g/dL)")
                    
                    if danger_signs:
                        st.error("⚠️ ALERT: Danger signs reported! Immediate attention required.")
                    
                    st.rerun()
                else:
                    st.error("Failed to save ANC record")
    
    # Show ANC history
    st.markdown("---")
    st.subheader("ANC Visit History")
    
    maternal_records = db.get_maternal_health_records(selected_mother_id)
    anc_records = [r for r in maternal_records if r.get('visit_type') == 'ANC']
    
    if anc_records:
        import pandas as pd
        df = pd.DataFrame(anc_records)
        df = df.sort_values('visit_date', ascending=False)
        
        display_cols = ['visit_date', 'gestational_week', 'bp_systolic', 'hemoglobin', 
                       'fetal_heart_rate', 'tt_dose', 'danger_signs']
        display_df = df[display_cols].copy()
        display_df.columns = ['Visit Date', 'Gestational Week', 'BP Systolic', 'Hb (g/dL)', 
                             'FHR (bpm)', 'TT Dose', 'Danger Signs']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No ANC records found for this mother.")

with tab2:
    st.subheader("Postnatal Care (PNC) Visit")
    
    with st.form("pnc_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Information**")
            visit_date_pnc = st.date_input("PNC Visit Date", value=date.today(), max_value=date.today(), key="pnc_date")
            
            pregnancy_id_pnc = st.text_input("Pregnancy ID (from ANC)", 
                                            help="Link to the pregnancy from ANC records", 
                                            key="pnc_preg_id")
            
            delivery_date = st.date_input("Delivery Date", value=None, max_value=date.today(), key="delivery_date")
            
            # Calculate days postpartum
            if delivery_date:
                days_postpartum = (visit_date_pnc - delivery_date).days
                st.info(f"📊 Days Postpartum: **{days_postpartum}**")
        
        with col2:
            st.markdown("**Mother's Vitals**")
            bp_systolic_pnc = st.number_input("BP Systolic (mmHg)", min_value=0, max_value=250, 
                                             value=120, key="pnc_bp_sys")
            bp_diastolic_pnc = st.number_input("BP Diastolic (mmHg)", min_value=0, max_value=150, 
                                              value=80, key="pnc_bp_dia")
            hemoglobin_pnc = st.number_input("Hemoglobin (g/dL)", min_value=0.0, max_value=20.0, 
                                            step=0.1, format="%.1f", value=0.0, key="pnc_hb")
        
        st.markdown("**Delivery Outcome**")
        delivery_outcome = st.text_area("Delivery Details", 
                                       placeholder="Type of delivery, baby's weight, complications, etc.", 
                                       key="delivery_outcome")
        
        st.markdown("**Danger Signs & Notes**")
        danger_signs_pnc = st.text_area("Danger Signs (if any)", 
                                       placeholder="e.g., Heavy bleeding, fever, foul discharge...", 
                                       key="pnc_danger")
        
        submitted_pnc = st.form_submit_button("💾 Save PNC Record", use_container_width=True)
        
        if submitted_pnc:
            if not delivery_date:
                st.error("Delivery date is required for PNC records")
            else:
                pnc_data = {
                    'resident_id': selected_mother_id,
                    'pregnancy_id': pregnancy_id_pnc if pregnancy_id_pnc else f"PNC-{uuid.uuid4().hex[:8].upper()}",
                    'visit_type': 'PNC',
                    'visit_date': visit_date_pnc.strftime('%Y-%m-%d'),
                    'lmp_date': None,
                    'edd_date': None,
                    'gestational_week': None,
                    'fundal_height': None,
                    'fetal_heart_rate': None,
                    'urine_albumin': None,
                    'hemoglobin': hemoglobin_pnc if hemoglobin_pnc > 0 else None,
                    'tt_dose': None,
                    'calcium_iron_status': None,
                    'danger_signs': danger_signs_pnc if danger_signs_pnc else None,
                    'bp_systolic': bp_systolic_pnc if bp_systolic_pnc > 0 else None,
                    'delivery_outcome': delivery_outcome if delivery_outcome else None
                }
                
                if db.add_maternal_health_record(pnc_data):
                    st.success("✅ PNC record saved successfully!")
                    
                    # Alerts
                    if bp_systolic_pnc >= 140:
                        st.error("⚠️ ALERT: High Blood Pressure postpartum!")
                    
                    if hemoglobin_pnc > 0 and hemoglobin_pnc < 10:
                        st.error("⚠️ ALERT: Severe Anemia postpartum! (Hb < 10 g/dL)")
                    
                    if danger_signs_pnc:
                        st.error("⚠️ ALERT: Danger signs reported! Immediate attention required.")
                    
                    st.rerun()
                else:
                    st.error("Failed to save PNC record")
    
    # Show PNC history
    st.markdown("---")
    st.subheader("PNC Visit History")
    
    maternal_records = db.get_maternal_health_records(selected_mother_id)
    pnc_records = [r for r in maternal_records if r.get('visit_type') == 'PNC']
    
    if pnc_records:
        import pandas as pd
        df_pnc = pd.DataFrame(pnc_records)
        df_pnc = df_pnc.sort_values('visit_date', ascending=False)
        
        display_cols = ['visit_date', 'bp_systolic', 'hemoglobin', 'delivery_outcome', 'danger_signs']
        display_df_pnc = df_pnc[display_cols].copy()
        display_df_pnc.columns = ['Visit Date', 'BP Systolic', 'Hb (g/dL)', 'Delivery Outcome', 'Danger Signs']
        
        st.dataframe(display_df_pnc, use_container_width=True, hide_index=True)
    else:
        st.info("No PNC records found for this mother.")

with tab3:
    st.subheader("⚠️ High-Risk Mothers Dashboard")
    st.markdown("List of mothers requiring immediate attention based on ANC records")
    
    # Get high-risk mothers
    high_risk = db.get_high_risk_mothers()
    
    if not high_risk:
        st.success("✓ No high-risk mothers identified at this time.")
    else:
        import pandas as pd
        
        # Create display dataframe
        risk_data = []
        for record in high_risk:
            risk_factors = []
            
            bp_sys = record.get('bp_systolic', 0) or 0
            hb = record.get('hemoglobin', 100) or 100
            danger = record.get('danger_signs', '')
            
            if bp_sys >= 140:
                risk_factors.append("High BP")
            if hb < 11:
                risk_factors.append("Anemia")
            if danger:
                risk_factors.append("Danger Signs")
            
            risk_data.append({
                'Name': record.get('resident_name', 'Unknown'),
                'ID': record.get('resident_id', ''),
                'Last Visit': record.get('visit_date', ''),
                'Gestational Week': record.get('gestational_week', 'N/A'),
                'BP': f"{bp_sys}/{record.get('bp_diastolic', 0) or 0}" if bp_sys > 0 else 'N/A',
                'Hb': f"{hb:.1f}" if hb < 100 else 'N/A',
                'Risk Factors': ', '.join(risk_factors)
            })
        
        df_risk = pd.DataFrame(risk_data)
        st.dataframe(df_risk, use_container_width=True, hide_index=True)
        
        st.markdown(f"**Total High-Risk Mothers: {len(high_risk)}**")
