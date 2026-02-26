"""
Maternal Health Tracking Page
Track Antenatal Care (ANC) and Postnatal Care (PNC) visits.
"""

import streamlit as st
from datetime import datetime, date, timedelta
import uuid
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

# Use the new search-to-select widget for mothers
selected_mother = select_resident_widget(db, key_prefix="maternal_health")

if not selected_mother:
    st.info("Search for a female resident (age 15-45) to manage maternal health records.")
    st.stop()

# Validate gender and age
if selected_mother.get('gender') != 'Female':
    st.warning(f"⚠️ {selected_mother['name']} is not female. Please select a female resident.")
    st.stop()

age = selected_mother.get('age')
if age is not None and (age < 15 or age > 45):
    st.warning(f"⚠️ {selected_mother['name']} is not in the typical reproductive age range (15-45 years). You can still proceed, but this is outside the normal range.")


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
tab1, tab2, tab3, tab4 = st.tabs(["🤰 Antenatal Care (ANC)", "👶 Postnatal Care (PNC)", "⚠️ High-Risk Mothers", "📋 MCH Proforma"])

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
                    'resident_id': selected_mother['unique_id'],
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
    
    maternal_records = db.get_maternal_health_records(selected_mother['unique_id'])
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
                    'resident_id': selected_mother['unique_id'],
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
    
    maternal_records = db.get_maternal_health_records(selected_mother['unique_id'])
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

with tab4:
    st.subheader("MCH Supportive Supervision Proforma")
    st.markdown("Complete the MCH assessment and save it against the mother's record.")

    with st.form("mch_proforma_form"):
        # --- Early Registration ---
        with st.expander("📋 Early Registration", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                mcp_card_avail = st.radio("MCP Card Available", ["Yes", "No"], horizontal=True)
                issued_1st_trimester = st.radio("Issued in 1st Trimester", ["Yes", "No"], horizontal=True)
                reg_lt12wks = st.radio("Registered <12 Weeks", ["Yes", "No"], horizontal=True)
            with col2:
                lmp_mch = st.date_input("LMP Date", value=None, max_value=date.today(), key="mch_lmp")
                edd_mch = st.date_input("EDD (Expected Delivery Date)", value=None, key="mch_edd")
                mcts_rch_id = st.text_input("MCTS / RCH ID", placeholder="Enter ID")

        # --- ANC Coverage ---
        with st.expander("🏥 ANC Coverage"):
            col1, col2 = st.columns(2)
            with col1:
                min4_anc = st.radio("Minimum 4 ANC Visits Completed", ["Yes", "No"], horizontal=True)
            with col2:
                weight_gain_recorded = st.radio("Trimester-wise Weight Gain Recorded", ["Yes", "No"],
                                                horizontal=True)

        # --- IFA & Calcium ---
        with st.expander("💊 IFA & Calcium"):
            col1, col2 = st.columns(2)
            with col1:
                ifa_start_date = st.date_input("IFA Start Date", value=None, key="ifa_start")
                ifa_total = st.number_input("Total IFA Tablets (>=180 recommended)",
                                            min_value=0, max_value=500, value=0)
                ifa_compliance = st.radio("IFA Compliance", ["Good", "Irregular", "Not taken"],
                                          horizontal=True)
            with col2:
                ifa_side_effects = st.text_input("IFA Side Effects (if any)",
                                                  placeholder="e.g., Nausea, constipation")
                calcium_issued = st.radio("Calcium Issued", ["Yes", "No"], horizontal=True)

        # --- Investigations ---
        with st.expander("🔬 Investigations"):
            col1, col2 = st.columns(2)
            with col1:
                urine_albumin_inv = st.radio("Urine Albumin", ["Done", "Not Done"], horizontal=True)
                urine_sugar_inv = st.radio("Urine Sugar", ["Done", "Not Done"], horizontal=True)
                blood_group_inv = st.radio("Blood Group", ["Done", "Not Done"], horizontal=True)
                hiv_inv = st.radio("HIV Test", ["Done", "Not Done"], horizontal=True)
                syphilis_inv = st.radio("Syphilis Test", ["Done", "Not Done"], horizontal=True)
            with col2:
                usg_inv = st.radio("USG (Ultrasound)", ["Done", "Not Done"], horizontal=True)
                gdm_inv = st.radio("GDM Screening", ["Done", "Not Done"], horizontal=True)
                hbsag_inv = st.radio("HBsAg", ["Done", "Not Done"], horizontal=True)
                tsh_inv = st.radio("TSH", ["Done", "Not Done"], horizontal=True)
                blood_sugar_inv = st.radio("Blood Sugar", ["Done", "Not Done"], horizontal=True)

        # --- Immunization (TT/Td) ---
        with st.expander("💉 Immunization (Td)"):
            col1, col2, col3 = st.columns(3)
            with col1:
                td1 = st.radio("Td-1", ["Given", "Not Given"], horizontal=True)
            with col2:
                td2 = st.radio("Td-2", ["Given", "Not Given"], horizontal=True)
            with col3:
                td_booster = st.radio("Td Booster", ["Given", "Not Given"], horizontal=True)

        # --- Birth Preparedness ---
        with st.expander("🏠 Birth Preparedness"):
            col1, col2 = st.columns(2)
            with col1:
                birth_place = st.radio("Delivery Place Identified", ["Yes", "No"], horizontal=True)
                transport_id = st.radio("Transport Identified", ["Yes", "No"], horizontal=True)
                emergency_contact = st.radio("Emergency Contact Identified", ["Yes", "No"], horizontal=True)
            with col2:
                blood_donor = st.radio("Blood Donor Identified", ["Yes", "No"], horizontal=True)
                danger_signs_gt3 = st.radio("Knows >3 Danger Signs", ["Yes", "No"], horizontal=True)

        # --- Incentives & PNC ---
        with st.expander("🎁 Incentives & PNC"):
            col1, col2 = st.columns(2)
            with col1:
                pmmvy = st.radio("PMMVY Received", ["Yes", "No"], horizontal=True)
                jsy = st.radio("JSY Received", ["Yes", "No"], horizontal=True)
            with col2:
                pnc_day3 = st.radio("PNC Visit Day 3", ["Done", "Not Done"], horizontal=True)
                pnc_day7 = st.radio("PNC Visit Day 7", ["Done", "Not Done"], horizontal=True)
                pnc_day14 = st.radio("PNC Visit Day 14", ["Done", "Not Done"], horizontal=True)
                pnc_day42 = st.radio("PNC Visit Day 42", ["Done", "Not Done"], horizontal=True)
                postnatal_ifa = st.radio("Postnatal IFA", ["Given", "Not Given"], horizontal=True)
                postnatal_calcium = st.radio("Postnatal Calcium", ["Given", "Not Given"], horizontal=True)

        # --- Baby (0-6 months) ---
        with st.expander("👶 Baby (0-6 Months)"):
            col1, col2 = st.columns(2)
            with col1:
                early_bf_init = st.radio("Early Initiation of Breastfeeding", ["Yes", "No"], horizontal=True)
                exclusive_bf = st.radio("Exclusive Breastfeeding (6 months)", ["Yes", "No"], horizontal=True)
            with col2:
                hbnc_visits = st.radio("HBNC Visits Done", ["Yes", "No"], horizontal=True)

        submitted_mch = st.form_submit_button("💾 Save MCH Proforma", use_container_width=True)

        if submitted_mch:
            mch_assessment_data = {
                "early_registration": {
                    "mcp_card_available": mcp_card_avail,
                    "issued_1st_trimester": issued_1st_trimester,
                    "registered_lt12_weeks": reg_lt12wks,
                    "lmp": lmp_mch.strftime('%Y-%m-%d') if lmp_mch else None,
                    "edd": edd_mch.strftime('%Y-%m-%d') if edd_mch else None,
                    "mcts_rch_id": mcts_rch_id if mcts_rch_id else None
                },
                "anc_coverage": {
                    "min_4_visits_completed": min4_anc,
                    "trimester_weight_gain_recorded": weight_gain_recorded
                },
                "ifa_calcium": {
                    "ifa_start_date": ifa_start_date.strftime('%Y-%m-%d') if ifa_start_date else None,
                    "ifa_total_tablets": ifa_total,
                    "ifa_compliance": ifa_compliance,
                    "ifa_side_effects": ifa_side_effects if ifa_side_effects else None,
                    "calcium_issued": calcium_issued
                },
                "investigations": {
                    "urine_albumin": urine_albumin_inv,
                    "urine_sugar": urine_sugar_inv,
                    "blood_group": blood_group_inv,
                    "hiv": hiv_inv,
                    "syphilis": syphilis_inv,
                    "usg": usg_inv,
                    "gdm": gdm_inv,
                    "hbsag": hbsag_inv,
                    "tsh": tsh_inv,
                    "blood_sugar": blood_sugar_inv
                },
                "immunization_td": {
                    "td1": td1,
                    "td2": td2,
                    "td_booster": td_booster
                },
                "birth_preparedness": {
                    "birth_place_identified": birth_place,
                    "transport_identified": transport_id,
                    "emergency_contact": emergency_contact,
                    "blood_donor_identified": blood_donor,
                    "knows_gt3_danger_signs": danger_signs_gt3
                },
                "incentives_pnc": {
                    "pmmvy_received": pmmvy,
                    "jsy_received": jsy,
                    "pnc_day3": pnc_day3,
                    "pnc_day7": pnc_day7,
                    "pnc_day14": pnc_day14,
                    "pnc_day42": pnc_day42,
                    "postnatal_ifa": postnatal_ifa,
                    "postnatal_calcium": postnatal_calcium
                },
                "baby_0_6_months": {
                    "early_bf_initiation": early_bf_init,
                    "exclusive_breastfeeding": exclusive_bf,
                    "hbnc_visits_done": hbnc_visits
                }
            }

            mch_record = {
                'resident_id': selected_mother['unique_id'],
                'visit_type': 'ANC',
                'visit_date': date.today().strftime('%Y-%m-%d'),
                'lmp_date': lmp_mch.strftime('%Y-%m-%d') if lmp_mch else None,
                'edd_date': edd_mch.strftime('%Y-%m-%d') if edd_mch else None,
                'assessment_data': mch_assessment_data
            }

            if db.add_maternal_health_record(mch_record):
                st.success("✅ MCH Supportive Supervision Proforma saved successfully!")
            else:
                st.error("❌ Failed to save MCH proforma. Please try again.")

