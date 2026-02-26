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
tab1, tab2, tab3, tab4 = st.tabs(["📝 Record Checkup", "📊 Trend Analysis", "⏰ Due List", "🏠 Household Proforma"])

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

with tab4:
    st.subheader("🏠 Household Proforma – NCD Field Visit")
    st.markdown("*Fill once per household visit.*")

    with st.form("household_proforma_form"):
        st.markdown("**Visiting Details**")
        col1, col2 = st.columns(2)
        with col1:
            hp_jr_name = st.text_input("Name of JR visiting the house")
        with col2:
            hp_visit_date = st.date_input("Date of visit", value=date.today(), max_value=date.today())

        st.markdown("---")
        st.markdown("### Part 1: Household Identification")
        col1, col2, col3 = st.columns(3)
        with col1:
            hp_house_no = st.text_input("House No.")
            hp_head = st.text_input("Head of Family")
        with col2:
            hp_contact = st.text_input("Contact Number")
            hp_total_members = st.number_input("Total Members", min_value=1, max_value=50, value=1)
        with col3:
            hp_address = st.text_area("Address / Landmark", height=80)

        col1, col2 = st.columns(2)
        with col1:
            hp_gps = st.text_input("GPS Coordinates of the house")
        with col2:
            hp_asha = st.text_input("ASHA Worker's Name")

        st.markdown("---")
        st.markdown("### Part 2: Member Listing & Sorting")
        st.markdown("*Fill one row per member (up to 10). Tick (✓) the applicable categories.*")

        member_data = []
        for i in range(1, 11):
            st.markdown(f"**Member {i}**")
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 1, 1, 2, 1, 1, 1, 2])
            with col1:
                m_name = st.text_input(f"Name", key=f"m_name_{i}", label_visibility="collapsed" if i > 1 else "visible")
            with col2:
                m_age = st.number_input(f"Age", min_value=0, max_value=120, value=0, key=f"m_age_{i}", label_visibility="collapsed" if i > 1 else "visible")
            with col3:
                m_sex = st.selectbox(f"Sex", ["", "M", "F", "Other"], key=f"m_sex_{i}", label_visibility="collapsed" if i > 1 else "visible")
            with col4:
                m_ncd = st.selectbox(f"NCD Status", ["None", "Known", "Suspect"], key=f"m_ncd_{i}", label_visibility="collapsed" if i > 1 else "visible")
            with col5:
                m_preg = st.checkbox(f"Preg", key=f"m_preg_{i}", label_visibility="collapsed" if i > 1 else "visible")
            with col6:
                m_lact = st.checkbox(f"Lact", key=f"m_lact_{i}", label_visibility="collapsed" if i > 1 else "visible")
            with col7:
                m_child = st.checkbox(f"<5", key=f"m_child_{i}", label_visibility="collapsed" if i > 1 else "visible")
            with col8:
                m_other = st.text_input(f"Other", key=f"m_other_{i}", label_visibility="collapsed" if i > 1 else "visible")

            if m_name:
                member_data.append({
                    'sl_no': i, 'member_name': m_name,
                    'age': m_age if m_age > 0 else None,
                    'sex': m_sex if m_sex else None,
                    'ncd_status': m_ncd if m_ncd != "None" else None,
                    'is_pregnant': m_preg, 'is_lactating': m_lact,
                    'is_child_under5': m_child,
                    'other_category': m_other if m_other else None
                })

        st.markdown("---")
        st.markdown("### MCH & Under-5 Brief Screening")
        st.markdown("*Fill for Pregnant, Lactating, or Children <5.*")

        mch_records = []
        for j in range(1, 4):
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 2, 2, 3])
            with col1:
                mch_sl = st.number_input(f"Member Sl.", min_value=0, max_value=10, value=0, key=f"mch_sl_{j}")
            with col2:
                mch_cat = st.selectbox(f"Category", ["", "Pregnant", "Lactating", "Child <5"], key=f"mch_cat_{j}")
            with col3:
                mch_reg = st.selectbox(f"AW Reg?", ["", "Y", "N"], key=f"mch_reg_{j}")
            with col4:
                mch_aw_name = st.text_input(f"AW / Sector Name", key=f"mch_aw_{j}")
            with col5:
                mch_aww = st.text_input(f"AWW Name & Mobile", key=f"mch_aww_{j}")
            with col6:
                mch_issues = st.text_input(f"Key Questions / Issues", key=f"mch_issues_{j}")

            if mch_sl > 0 and mch_cat:
                mch_records.append({
                    'member_sl': int(mch_sl),
                    'category': mch_cat,
                    'registered_in_anganwadi': True if mch_reg == "Y" else (False if mch_reg == "N" else None),
                    'aw_sector_name': mch_aw_name if mch_aw_name else None,
                    'aww_name': mch_aww if mch_aww else None,
                    'key_issues': mch_issues if mch_issues else None
                })

        st.markdown("---")
        st.markdown("### Part 3: Detailed NCD Evaluation")
        st.markdown("*For members marked 'NCD' and >30 years.*")

        col1, col2, col3 = st.columns(3)
        with col1:
            hp_height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, step=0.5, format="%.1f", value=0.0)
            hp_weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.5, format="%.1f", value=0.0)
        with col2:
            hp_bmi = round(hp_weight / ((hp_height / 100) ** 2), 1) if hp_height > 0 and hp_weight > 0 else 0.0
            st.metric("BMI (auto-calculated)", f"{hp_bmi:.1f}" if hp_bmi > 0 else "—")
            hp_waist = st.number_input("Waist Circumference (cm)", min_value=0.0, max_value=200.0, step=0.5, format="%.1f", value=0.0)
        with col3:
            hp_bp_sys = st.number_input("BP Systolic (mmHg)", min_value=0, max_value=300, value=0)
            hp_bp_dia = st.number_input("BP Diastolic (mmHg)", min_value=0, max_value=200, value=0)

        col1, col2 = st.columns(2)
        with col1:
            hp_rbs = st.number_input("RBS (mg/dL)", min_value=0.0, max_value=600.0, step=1.0, format="%.0f", value=0.0)
            hp_cbac = st.text_input("CBAC Risk Score")
        with col2:
            hp_known_disease = st.text_input("Known Disease (HTN/DM/CVD/CKD)")
            hp_duration = st.text_input("Duration of Disease")

        col1, col2 = st.columns(2)
        with col1:
            hp_on_treatment = st.checkbox("On Treatment")
        with col2:
            pass

        st.markdown("**Red Flags (Check if present):**")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            hp_flag_cough = st.checkbox("Persistent Cough (>2 weeks)")
        with col2:
            hp_flag_ulcer = st.checkbox("Non-healing mouth ulcer")
        with col3:
            hp_flag_swallow = st.checkbox("Difficulty in swallowing")
        with col4:
            hp_flag_wtloss = st.checkbox("Weight loss")
        with col5:
            hp_flag_fits = st.checkbox("Fits / Stroke symptoms")

        st.markdown("---")
        st.markdown("### NCD Risk Factor Assessment (Behavioral)")
        st.markdown("*For NCD patients and members above 30 years.*")

        col1, col2, col3 = st.columns(3)
        with col1:
            hp_tobacco = st.radio("Tobacco (Bidi/Cigarette/Khaini)?", ["No", "Yes"], horizontal=True)
            hp_tobacco_counsel = st.checkbox("Quit-line info given", key="hp_tc")
        with col2:
            hp_alcohol = st.radio("Alcohol (Frequent consumption)?", ["No", "Yes"], horizontal=True)
            hp_alcohol_counsel = st.checkbox("Harmful effects explained", key="hp_ac")
        with col3:
            hp_salt = st.radio("Diet – Salt (Pickles/papad/extra salt)?", ["Low", "High"], horizontal=True)
            hp_salt_counsel = st.checkbox("Reduce to 1 tsp/day counseling given", key="hp_sc")

        col1, col2 = st.columns(2)
        with col1:
            hp_sugar = st.radio("Diet – Sugar (High intake of sweets/soda)?", ["Low", "High"], horizontal=True)
            hp_sugar_counsel = st.checkbox("Replace with whole fruit counseling given", key="hp_suc")
        with col2:
            hp_activity = st.radio("Physical Activity (30 mins walk/work per day)?", ["Yes", "No"], horizontal=True)
            hp_activity_counsel = st.checkbox("Daily brisk walk plan given", key="hp_actc")

        st.markdown("---")
        st.markdown("### NCD Clinical & Adherence")
        st.markdown("*For NCD patients.*")

        hp_medications = st.text_area("Current Medications (list all medicines separately: Medicine 1, 2, 3…)", placeholder="e.g., Amlodipine 5mg, Metformin 500mg")

        col1, col2, col3 = st.columns(3)
        with col1:
            hp_missed_days = st.selectbox("7-Day Recall – Missed Days", ["0 days", "1–2 days", "3+ days"])
        with col2:
            hp_stock = st.radio("Stock adequate for next 15 days?", ["Yes", "No"], horizontal=True)
        with col3:
            hp_barrier = st.selectbox("Barrier for skipping (if any)", ["None", "Cost", "Side effects", "Forgot", "Feels fine"])

        col1, col2 = st.columns(2)
        with col1:
            hp_foot_exam = st.selectbox("Foot Exam", ["No Issues", "Redness", "Open Ulcer"])
        with col2:
            hp_vision = st.radio("New blurring of vision?", ["No", "Yes"], horizontal=True)

        # Auto-determine status color
        def _ncd_status_color(missed, bp_sys, rbs_val, foot, vision_chg):
            if missed == "3+ days" or bp_sys > 160 or rbs_val > 250 or foot == "Open Ulcer" or vision_chg == "Yes":
                return "🔴 Red (Referral)"
            elif missed == "1–2 days" or (140 <= bp_sys <= 160) or (180 < rbs_val <= 250):
                return "🟡 Yellow (Caution)"
            return "🟢 Green (Good)"

        computed_status = _ncd_status_color(hp_missed_days, hp_bp_sys, hp_rbs, hp_foot_exam, hp_vision)
        st.info(f"**Status: {computed_status}**")

        hp_submitted = st.form_submit_button("💾 Save Household Proforma", use_container_width=True)

        if hp_submitted:
            if not hp_jr_name:
                st.error("Please enter the name of the JR visiting.")
            else:
                # Save household proforma
                proforma_data = {
                    'jr_name': hp_jr_name,
                    'visit_date': hp_visit_date.strftime('%Y-%m-%d'),
                    'house_no': hp_house_no if hp_house_no else None,
                    'head_of_family': hp_head if hp_head else None,
                    'contact_number': hp_contact if hp_contact else None,
                    'total_members': hp_total_members,
                    'address': hp_address if hp_address else None,
                    'gps_coordinate': hp_gps if hp_gps else None,
                    'asha_worker_name': hp_asha if hp_asha else None,
                }
                household_id = db.add_household_proforma(proforma_data)

                if household_id:
                    # Save members
                    for m in member_data:
                        m['household_id'] = household_id
                    db.add_household_members(member_data)

                    # Save MCH screening
                    for mch in mch_records:
                        mch['household_id'] = household_id
                    db.add_mch_screening(mch_records)

                    # Save NCD detailed record linked to this patient
                    ncd_extended = {
                        'resident_id': selected_patient['unique_id'],
                        'checkup_date': hp_visit_date.strftime('%Y-%m-%d'),
                        'condition_type': hp_known_disease if hp_known_disease else 'NCD Screening',
                        'bp_systolic': hp_bp_sys if hp_bp_sys > 0 else None,
                        'bp_diastolic': hp_bp_dia if hp_bp_dia > 0 else None,
                        'fasting_blood_sugar': None,
                        'random_blood_sugar': hp_rbs if hp_rbs > 0 else None,
                        'medication_adherence': "Yes" if hp_missed_days == "0 days" else ("Partially" if hp_missed_days == "1–2 days" else "No"),
                        'symptoms': None,
                        'referral_needed': computed_status.startswith("🔴"),
                        'household_id': household_id,
                        'height_cm': hp_height if hp_height > 0 else None,
                        'weight_kg': hp_weight if hp_weight > 0 else None,
                        'bmi': hp_bmi if hp_bmi > 0 else None,
                        'waist_circumference': hp_waist if hp_waist > 0 else None,
                        'cbac_risk_score': hp_cbac if hp_cbac else None,
                        'known_disease': hp_known_disease if hp_known_disease else None,
                        'disease_duration': hp_duration if hp_duration else None,
                        'on_treatment': hp_on_treatment,
                        'tobacco_use': hp_tobacco == "Yes",
                        'tobacco_counseling': hp_tobacco_counsel,
                        'alcohol_use': hp_alcohol == "Yes",
                        'alcohol_counseling': hp_alcohol_counsel,
                        'diet_salt_high': hp_salt == "High",
                        'diet_salt_counseling': hp_salt_counsel,
                        'diet_sugar_high': hp_sugar == "High",
                        'diet_sugar_counseling': hp_sugar_counsel,
                        'physically_inactive': hp_activity == "No",
                        'activity_counseling': hp_activity_counsel,
                        'flag_persistent_cough': hp_flag_cough,
                        'flag_mouth_ulcer': hp_flag_ulcer,
                        'flag_swallowing_difficulty': hp_flag_swallow,
                        'flag_weight_loss': hp_flag_wtloss,
                        'flag_fits_stroke': hp_flag_fits,
                        'medications_detail': hp_medications if hp_medications else None,
                        'missed_days_category': hp_missed_days,
                        'stock_adequate': hp_stock == "Yes",
                        'barrier_reason': hp_barrier if hp_barrier != "None" else None,
                        'foot_exam_status': hp_foot_exam,
                        'vision_change': hp_vision == "Yes",
                        'status_color': computed_status,
                    }
                    db.add_ncd_followup(ncd_extended)

                    st.success(f"✅ Household proforma saved! (ID: {household_id})")
                    if computed_status.startswith("🔴"):
                        st.error("🚨 Red Flag – Patient requires immediate referral.")
                    elif computed_status.startswith("🟡"):
                        st.warning("⚠️ Yellow Flag – Patient needs closer monitoring.")
                    st.rerun()
                else:
                    st.error("Failed to save household proforma.")

    # Show recent household visits
    st.markdown("---")
    st.subheader("Recent Household Visits")
    recent_proformas = db.get_household_proforma_records()
    if recent_proformas:
        for p in recent_proformas[:5]:
            with st.expander(f"Visit on {p.get('visit_date', 'N/A')} – House {p.get('house_no', 'N/A')} | JR: {p.get('jr_name', 'N/A')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Head of Family:** {p.get('head_of_family', 'N/A')}")
                    st.write(f"**Total Members:** {p.get('total_members', 'N/A')}")
                with col2:
                    st.write(f"**Address:** {p.get('address', 'N/A')}")
                    st.write(f"**ASHA Worker:** {p.get('asha_worker_name', 'N/A')}")
                with col3:
                    st.write(f"**GPS:** {p.get('gps_coordinate', 'N/A')}")
                    st.write(f"**Contact:** {p.get('contact_number', 'N/A')}")
    else:
        st.info("No household visits recorded yet.")
