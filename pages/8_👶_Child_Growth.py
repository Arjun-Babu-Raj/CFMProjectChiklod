"""
Child Growth Monitoring Page
Track growth metrics for children under 5 years with WHO growth charts.
"""

import streamlit as st
from datetime import datetime, date
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
st.title("👶 Child Growth Monitoring")
st.markdown("Track growth metrics for children under 5 years")
st.markdown("---")

# WHO Growth Standards Reference Data (simplified)
# Boys Weight-for-Age (months: kg) - WHO standards
WHO_BOYS_WEIGHT = {
    0: {'p3': 2.5, 'p50': 3.3, 'p97': 4.4},
    6: {'p3': 6.4, 'p50': 7.9, 'p97': 9.8},
    12: {'p3': 7.7, 'p50': 9.6, 'p97': 12.0},
    24: {'p3': 9.7, 'p50': 12.2, 'p97': 15.3},
    36: {'p3': 11.3, 'p50': 14.3, 'p97': 18.3},
    48: {'p3': 12.7, 'p50': 16.3, 'p97': 21.2},
    60: {'p3': 14.1, 'p50': 18.3, 'p97': 24.2}
}

# Girls Weight-for-Age (months: kg)
WHO_GIRLS_WEIGHT = {
    0: {'p3': 2.4, 'p50': 3.2, 'p97': 4.2},
    6: {'p3': 5.7, 'p50': 7.3, 'p97': 9.3},
    12: {'p3': 7.0, 'p50': 9.0, 'p97': 11.5},
    24: {'p3': 9.0, 'p50': 11.5, 'p97': 14.8},
    36: {'p3': 10.8, 'p50': 13.9, 'p97': 18.1},
    48: {'p3': 12.3, 'p50': 16.0, 'p97': 21.5},
    60: {'p3': 13.7, 'p50': 18.2, 'p97': 25.0}
}

# Boys Height-for-Age (months: cm)
WHO_BOYS_HEIGHT = {
    0: {'p3': 46.1, 'p50': 49.9, 'p97': 53.7},
    6: {'p3': 63.3, 'p50': 67.6, 'p97': 72.0},
    12: {'p3': 71.0, 'p50': 75.7, 'p97': 80.5},
    24: {'p3': 81.7, 'p50': 87.1, 'p97': 92.9},
    36: {'p3': 88.7, 'p50': 96.1, 'p97': 103.3},
    48: {'p3': 94.9, 'p50': 103.3, 'p97': 111.7},
    60: {'p3': 100.7, 'p50': 110.0, 'p97': 119.2}
}

# Girls Height-for-Age (months: cm)
WHO_GIRLS_HEIGHT = {
    0: {'p3': 45.4, 'p50': 49.1, 'p97': 52.9},
    6: {'p3': 61.2, 'p50': 65.7, 'p97': 70.3},
    12: {'p3': 68.9, 'p50': 74.0, 'p97': 79.2},
    24: {'p3': 80.0, 'p50': 86.4, 'p97': 92.9},
    36: {'p3': 87.4, 'p50': 95.1, 'p97': 102.7},
    48: {'p3': 94.1, 'p50': 102.7, 'p97': 111.3},
    60: {'p3': 99.9, 'p50': 109.4, 'p97': 118.9}
}


def calculate_z_score_simple(value, age_months, gender, metric='weight'):
    """Simple z-score approximation based on WHO standards."""
    if metric == 'weight':
        ref_data = WHO_BOYS_WEIGHT if gender == 'Male' else WHO_GIRLS_WEIGHT
    else:
        ref_data = WHO_BOYS_HEIGHT if gender == 'Male' else WHO_GIRLS_HEIGHT
    
    # Find closest age in reference
    closest_age = min(ref_data.keys(), key=lambda x: abs(x - age_months))
    ref = ref_data[closest_age]
    
    # Simple z-score: (value - median) / (p97 - p3) * 4
    median = ref['p50']
    sd_approx = (ref['p97'] - ref['p3']) / 4
    
    if sd_approx > 0:
        z_score = (value - median) / sd_approx
        return round(z_score, 2)
    return 0


# Child Selection
st.subheader("Select Child")

# Use the new search-to-select widget for children
selected_child = select_resident_widget(db, key_prefix="child_growth")

if not selected_child:
    st.info("Search for a child (under 5 years) to start tracking growth.")
    st.stop()

# Validate age
if selected_child.get('age') is None or selected_child.get('age') > 5:
    st.warning(f"⚠️ {selected_child['name']} is not in the child age group (under 5 years). Please select a different resident.")
    st.stop()

# Display child info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Name", selected_child['name'])
with col2:
    st.metric("Age", f"{selected_child.get('age', 'N/A')} years")
with col3:
    st.metric("Gender", selected_child.get('gender', 'N/A'))

st.markdown("---")

# Two tabs: Data Entry and Growth Charts
tab1, tab2, tab3 = st.tabs(["📝 Record Growth Data", "📊 Growth Charts & History", "📋 Assessment Checklist"])

with tab1:
    st.subheader("Record New Growth Measurement")
    
    with st.form("growth_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            record_date = st.date_input("Measurement Date", value=date.today(), max_value=date.today())
            age_months = st.number_input("Age (months)", min_value=0, max_value=60, value=0)
            weight_kg = st.number_input("Weight (kg)", min_value=0.0, max_value=50.0, step=0.1, format="%.1f")
            height_cm = st.number_input("Height/Length (cm)", min_value=0.0, max_value=150.0, step=0.1, format="%.1f")
        
        with col2:
            muac_cm = st.number_input("MUAC - Mid-Upper Arm Circumference (cm)", 
                                      min_value=0.0, max_value=30.0, step=0.1, format="%.1f", value=0.0)
            head_circumference_cm = st.number_input("Head Circumference (cm)", 
                                                   min_value=0.0, max_value=60.0, step=0.1, format="%.1f", value=0.0)
            notes = st.text_area("Notes", placeholder="Any observations or concerns...")
        
        submitted = st.form_submit_button("💾 Save Growth Record", use_container_width=True)
        
        if submitted:
            if weight_kg <= 0 or height_cm <= 0:
                st.error("Weight and height must be greater than 0")
            else:
                # Calculate z-score
                z_score = calculate_z_score_simple(
                    weight_kg, age_months, selected_child.get('gender', 'Male'), 'weight'
                )
                
                growth_data = {
                    'resident_id': selected_child['unique_id'],
                    'record_date': record_date.strftime('%Y-%m-%d'),
                    'age_months': age_months,
                    'weight_kg': weight_kg,
                    'height_cm': height_cm,
                    'muac_cm': muac_cm if muac_cm > 0 else None,
                    'head_circumference_cm': head_circumference_cm if head_circumference_cm > 0 else None,
                    'z_score_weight_age': z_score,
                    'notes': notes if notes else None
                }
                
                if db.add_growth_monitoring(growth_data):
                    st.success("✅ Growth record saved successfully!")
                    
                    # Show alerts
                    if z_score < -2:
                        st.error("⚠️ ALERT: Child is Underweight (Z-score < -2)")
                    elif z_score < -1:
                        st.warning("⚠️ Warning: Child is at risk of underweight (Z-score < -1)")
                    else:
                        st.info("✓ Weight is within normal range")
                    
                    # MUAC alert
                    if muac_cm > 0 and muac_cm < 11.5:
                        st.error("⚠️ ALERT: Severe Acute Malnutrition (MUAC < 11.5 cm)")
                    elif muac_cm > 0 and muac_cm < 12.5:
                        st.warning("⚠️ Warning: Moderate Acute Malnutrition (MUAC < 12.5 cm)")
                    
                    st.rerun()
                else:
                    st.error("Failed to save growth record")

with tab2:
    st.subheader("Growth Charts & History")
    
    # Get growth history
    growth_records = db.get_child_growth_records(selected_child['unique_id'])
    
    if not growth_records:
        st.info("No growth records found for this child. Add measurements in the 'Record Growth Data' tab.")
    else:
        # Convert to DataFrame
        df = pd.DataFrame(growth_records)
        df['record_date'] = pd.to_datetime(df['record_date'])
        df = df.sort_values('record_date')
        
        # WHO reference data for plotting
        gender = selected_child.get('gender', 'Male')
        who_weight_ref = WHO_BOYS_WEIGHT if gender == 'Male' else WHO_GIRLS_WEIGHT
        who_height_ref = WHO_BOYS_HEIGHT if gender == 'Male' else WHO_GIRLS_HEIGHT
        
        # Weight-for-Age Chart
        st.markdown("### Weight-for-Age Chart")
        
        fig_weight = go.Figure()
        
        # Add WHO reference lines
        who_ages = sorted(who_weight_ref.keys())
        fig_weight.add_trace(go.Scatter(
            x=who_ages, y=[who_weight_ref[a]['p97'] for a in who_ages],
            mode='lines', name='WHO 97th %ile', line=dict(color='lightgreen', dash='dash')
        ))
        fig_weight.add_trace(go.Scatter(
            x=who_ages, y=[who_weight_ref[a]['p50'] for a in who_ages],
            mode='lines', name='WHO Median', line=dict(color='green', width=2)
        ))
        fig_weight.add_trace(go.Scatter(
            x=who_ages, y=[who_weight_ref[a]['p3'] for a in who_ages],
            mode='lines', name='WHO 3rd %ile', line=dict(color='orange', dash='dash')
        ))
        
        # Add child's actual measurements
        fig_weight.add_trace(go.Scatter(
            x=df['age_months'], y=df['weight_kg'],
            mode='lines+markers', name='Child Weight',
            line=dict(color='blue', width=3), marker=dict(size=10)
        ))
        
        fig_weight.update_layout(
            title=f"Weight-for-Age: {selected_child['name']}",
            xaxis_title="Age (months)",
            yaxis_title="Weight (kg)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_weight, use_container_width=True)
        
        # Height-for-Age Chart
        st.markdown("### Height-for-Age Chart")
        
        fig_height = go.Figure()
        
        # Add WHO reference lines
        fig_height.add_trace(go.Scatter(
            x=who_ages, y=[who_height_ref[a]['p97'] for a in who_ages],
            mode='lines', name='WHO 97th %ile', line=dict(color='lightgreen', dash='dash')
        ))
        fig_height.add_trace(go.Scatter(
            x=who_ages, y=[who_height_ref[a]['p50'] for a in who_ages],
            mode='lines', name='WHO Median', line=dict(color='green', width=2)
        ))
        fig_height.add_trace(go.Scatter(
            x=who_ages, y=[who_height_ref[a]['p3'] for a in who_ages],
            mode='lines', name='WHO 3rd %ile', line=dict(color='orange', dash='dash')
        ))
        
        # Add child's actual measurements
        fig_height.add_trace(go.Scatter(
            x=df['age_months'], y=df['height_cm'],
            mode='lines+markers', name='Child Height',
            line=dict(color='blue', width=3), marker=dict(size=10)
        ))
        
        fig_height.update_layout(
            title=f"Height-for-Age: {selected_child['name']}",
            xaxis_title="Age (months)",
            yaxis_title="Height (cm)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_height, use_container_width=True)
        
        # Growth History Table
        st.markdown("### Measurement History")
        
        display_df = df[['record_date', 'age_months', 'weight_kg', 'height_cm', 
                         'muac_cm', 'z_score_weight_age', 'notes']].copy()
        display_df.columns = ['Date', 'Age (months)', 'Weight (kg)', 'Height (cm)', 
                              'MUAC (cm)', 'Z-score', 'Notes']
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(display_df.sort_values('Date', ascending=False), use_container_width=True, hide_index=True)
        
        # Latest Status Summary
        st.markdown("### Latest Status")
        latest = df.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Weight", f"{latest['weight_kg']:.1f} kg")
        with col2:
            st.metric("Height", f"{latest['height_cm']:.1f} cm")
        with col3:
            if latest['muac_cm']:
                st.metric("MUAC", f"{latest['muac_cm']:.1f} cm")
            else:
                st.metric("MUAC", "N/A")
        with col4:
            z_score_val = latest['z_score_weight_age']
            if z_score_val < -2:
                st.metric("Status", "Underweight ⚠️", delta_color="off")
            elif z_score_val < -1:
                st.metric("Status", "At Risk", delta_color="off")
            else:
                st.metric("Status", "Normal ✓", delta_color="off")

with tab3:
    st.subheader("Under-5 Child Assessment Checklist")
    st.markdown("**Rural Field Practice Area (CRHA) – AIIMS Bhopal**")
    st.markdown("---")

    with st.form("child_assessment_form"):
        # Section I: Identification & Registration
        st.markdown("### I. Identification & Registration")
        col1, col2, col3 = st.columns(3)
        with col1:
            ca_birth_weight = st.number_input("Birth Weight (kg)", min_value=0.0, max_value=10.0, step=0.1, format="%.2f", value=0.0)
            ca_birth_order = st.number_input("Birth Order", min_value=1, max_value=20, value=1)
        with col2:
            ca_mother_name = st.text_input("Mother's Name")
            ca_mobile = st.text_input("Mobile")
        with col3:
            ca_village = st.text_input("Village")
            ca_assessment_date = st.date_input("Assessment Date", value=date.today(), max_value=date.today())

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            ca_anganwadi_reg = st.checkbox("Child registered at Anganwadi")
        with col_r2:
            ca_mcp_card = st.checkbox("MCP Card available")
        with col_r3:
            ca_rch_id = st.checkbox("RCH ID available")

        st.markdown("---")

        # Section II: Growth & Development
        st.markdown("### II. Growth & Development")
        col1, col2, col3 = st.columns(3)
        with col1:
            ca_wfa_status = st.selectbox("Weight for Age", ["Normal", "Underweight", "Severely Underweight"])
        with col2:
            ca_stunting = st.selectbox("Height for Age (Stunting)", ["Normal", "Stunted", "Severely Stunted"])
        with col3:
            ca_wasting = st.selectbox("Weight for Height (Wasting)", ["Normal", "MAM", "SAM"])

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            ca_pedal_edema_absent = st.checkbox("Bilateral Pedal Edema checked (Absent)")
        with col_g2:
            ca_dev_milestones = st.checkbox("Developmental Milestones Normal (Gross Motor, Fine Motor, Language, Social)")

        st.markdown("---")

        # Section III: Nutrition & Prophylaxis
        st.markdown("### III. Nutrition & Prophylaxis")
        st.markdown("**Feeding Practices:**")
        col1, col2 = st.columns(2)
        with col1:
            ca_early_bf = st.checkbox("Early initiation of breastfeeding (<1 hr)")
            ca_excl_bf_months = st.number_input("Exclusive Breastfeeding till (months)", min_value=0.0, max_value=24.0, step=0.5, value=0.0)
        with col2:
            ca_comp_feeding = st.checkbox("6–24 Months: Complementary feeding started (adequate frequency & diversity)")

        st.markdown("**Take-Home Ration (THR) Details:**")
        col1, col2 = st.columns(2)
        with col1:
            ca_thr_amount = st.text_input("Amount of THR received")
            ca_thr_utilized = st.checkbox("THR is actually being utilized by the child")
        with col2:
            ca_thr_preparation = st.text_input("What is being prepared/given from THR?")
            ca_thr_acceptance = st.select_slider(
                "Child's acceptance of THR (Taste)",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: {1: "1 – Strongly Dislikes", 2: "2 – Dislikes", 3: "3 – Neutral", 4: "4 – Likes", 5: "5 – Strongly Likes"}[x],
                value=3
            )

        st.markdown("**Supplements & Services:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ca_vitamin_a = st.checkbox("Vitamin A given")
        with col2:
            ca_ifa_syrup = st.checkbox("IFA syrup given (if applicable)")
        with col3:
            ca_deworming = st.checkbox("Deworming (Albendazole) given")
        with col4:
            ca_anganwadi_attend = st.checkbox("Child attends Anganwadi regularly & Growth chart updated")

        st.markdown("---")

        # Section IV: Health & Immunization
        st.markdown("### IV. Health & Immunization")
        st.markdown("**Immunization Status (As per National Immunization Schedule, India):**")

        st.markdown("*Birth:*")
        col1, col2, col3 = st.columns(3)
        with col1:
            ca_bcg = st.checkbox("BCG")
        with col2:
            ca_opv0 = st.checkbox("OPV-0")
        with col3:
            ca_hepb_birth = st.checkbox("Hep-B (Birth Dose)")

        st.markdown("*6 Weeks:*")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            ca_opv1 = st.checkbox("OPV-1")
        with col2:
            ca_penta1 = st.checkbox("Pentavalent-1")
        with col3:
            ca_rota1 = st.checkbox("Rota-1")
        with col4:
            ca_fipv1 = st.checkbox("fIPV-1")
        with col5:
            ca_pcv1 = st.checkbox("PCV-1")

        st.markdown("*10 Weeks:*")
        col1, col2, col3 = st.columns(3)
        with col1:
            ca_opv2 = st.checkbox("OPV-2")
        with col2:
            ca_penta2 = st.checkbox("Pentavalent-2")
        with col3:
            ca_rota2 = st.checkbox("Rota-2")

        st.markdown("*14 Weeks:*")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            ca_opv3 = st.checkbox("OPV-3")
        with col2:
            ca_penta3 = st.checkbox("Pentavalent-3")
        with col3:
            ca_rota3 = st.checkbox("Rota-3")
        with col4:
            ca_fipv2 = st.checkbox("fIPV-2")
        with col5:
            ca_pcv2 = st.checkbox("PCV-2")

        st.markdown("*9–12 Months:*")
        col1, col2, col3 = st.columns(3)
        with col1:
            ca_mr1 = st.checkbox("MR-1")
        with col2:
            ca_je1 = st.checkbox("JE-1 *(endemic districts only)*")
        with col3:
            ca_pcv_booster = st.checkbox("PCV Booster")

        st.markdown("*16–24 Months:*")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ca_mr2 = st.checkbox("MR-2")
        with col2:
            ca_je2 = st.checkbox("JE-2 *(endemic districts only)*")
        with col3:
            ca_dpt_booster1 = st.checkbox("DPT Booster-1")
        with col4:
            ca_opv_booster = st.checkbox("OPV Booster")

        st.markdown("*5–6 Years:*")
        ca_dpt_booster2 = st.checkbox("DPT Booster-2")

        st.markdown("**Morbidity in last 1 month:**")
        col1, col2 = st.columns(2)
        with col1:
            ca_morbidity = st.checkbox("Any Morbidity in last 1 month? (Fever, Diarrhea, ARI, Hospital admission)")
        with col2:
            ca_treatment_loc = st.selectbox("If yes, treated at:", ["N/A", "Government", "Private", "Not Taken"])

        st.markdown("---")

        # Section V: Action & Counseling
        st.markdown("### V. Action & Counseling")
        col1, col2 = st.columns(2)
        with col1:
            ca_referral = st.checkbox("Referral done if required (PHC / NRC)")
            ca_counseling = st.checkbox("Counseling provided (Complementary feeding, Handwashing, Feeding during illness, ORS/Zinc)")
        with col2:
            st.markdown("**Mother can identify 3+ Danger Signs:**")
            ca_ds_convulsions = st.checkbox("Convulsions / seizures")
            ca_ds_unable_feed = st.checkbox("Unable to drink or breastfeed")
            ca_ds_vomits = st.checkbox("Vomits everything")
            ca_ds_lethargy = st.checkbox("Lethargy or unconsciousness")
            ca_ds_breathing = st.checkbox("Fast or difficult breathing")

        ca_supervisory_feedback = st.text_area("Supervisory Feedback / Remarks")

        st.markdown("---")

        # Section VI: Media Attachments
        st.markdown("### VI. Media Attachments")
        ca_photo = st.file_uploader("📷 Capture / Upload Image (e.g., photo of the child, growth chart, or MCP card)", type=["jpg", "jpeg", "png"])
        ca_audio_notes = st.text_area("🎙️ Audio Observation Notes (e.g., supervisor's observations or mother's response)")

        ca_submitted = st.form_submit_button("💾 Save Assessment", use_container_width=True)

        if ca_submitted:
            # Handle photo upload
            photo_url = None
            if ca_photo:
                from utils.image_handler import save_uploaded_photo
                photo_url = save_uploaded_photo(ca_photo, selected_child['unique_id'], photo_type="child_assessment")

            assessment_data = {
                'resident_id': selected_child['unique_id'],
                'assessment_date': ca_assessment_date.strftime('%Y-%m-%d'),
                'birth_weight_kg': ca_birth_weight if ca_birth_weight > 0 else None,
                'birth_order': ca_birth_order,
                'mother_name': ca_mother_name if ca_mother_name else None,
                'mobile': ca_mobile if ca_mobile else None,
                'village': ca_village if ca_village else None,
                'anganwadi_registered': ca_anganwadi_reg,
                'mcp_card_available': ca_mcp_card,
                'rch_id_available': ca_rch_id,
                'weight_for_age_status': ca_wfa_status,
                'stunting_status': ca_stunting,
                'wasting_status': ca_wasting,
                'pedal_edema_absent': ca_pedal_edema_absent,
                'developmental_milestones_normal': ca_dev_milestones,
                'early_breastfeeding': ca_early_bf,
                'exclusive_bf_months': ca_excl_bf_months if ca_excl_bf_months > 0 else None,
                'complementary_feeding': ca_comp_feeding,
                'thr_amount': ca_thr_amount if ca_thr_amount else None,
                'thr_utilized': ca_thr_utilized,
                'thr_preparation': ca_thr_preparation if ca_thr_preparation else None,
                'thr_acceptance': ca_thr_acceptance,
                'vitamin_a_given': ca_vitamin_a,
                'ifa_syrup_given': ca_ifa_syrup,
                'deworming_given': ca_deworming,
                'anganwadi_attendance': ca_anganwadi_attend,
                'imm_bcg': ca_bcg, 'imm_opv0': ca_opv0, 'imm_hepb_birth': ca_hepb_birth,
                'imm_opv1': ca_opv1, 'imm_penta1': ca_penta1, 'imm_rota1': ca_rota1,
                'imm_fipv1': ca_fipv1, 'imm_pcv1': ca_pcv1,
                'imm_opv2': ca_opv2, 'imm_penta2': ca_penta2, 'imm_rota2': ca_rota2,
                'imm_opv3': ca_opv3, 'imm_penta3': ca_penta3, 'imm_rota3': ca_rota3,
                'imm_fipv2': ca_fipv2, 'imm_pcv2': ca_pcv2,
                'imm_mr1': ca_mr1, 'imm_je1': ca_je1, 'imm_pcv_booster': ca_pcv_booster,
                'imm_mr2': ca_mr2, 'imm_je2': ca_je2, 'imm_dpt_booster1': ca_dpt_booster1,
                'imm_opv_booster': ca_opv_booster, 'imm_dpt_booster2': ca_dpt_booster2,
                'morbidity_last_month': ca_morbidity,
                'treatment_location': ca_treatment_loc if ca_treatment_loc != "N/A" else None,
                'referral_done': ca_referral,
                'counseling_provided': ca_counseling,
                'danger_sign_convulsions': ca_ds_convulsions,
                'danger_sign_unable_to_feed': ca_ds_unable_feed,
                'danger_sign_vomits_everything': ca_ds_vomits,
                'danger_sign_lethargy': ca_ds_lethargy,
                'danger_sign_fast_breathing': ca_ds_breathing,
                'supervisory_feedback': ca_supervisory_feedback if ca_supervisory_feedback else None,
                'photo_url': photo_url,
                'audio_notes': ca_audio_notes if ca_audio_notes else None,
            }

            if db.add_child_assessment(assessment_data):
                st.success("✅ Child assessment saved successfully!")
                # Alert for SAM/MAM
                if ca_wasting == "SAM":
                    st.error("🚨 SAM detected – Refer to NRC immediately.")
                elif ca_wasting == "MAM":
                    st.warning("⚠️ MAM detected – Ensure THR utilization and close follow-up.")
                if ca_morbidity:
                    st.info("ℹ️ Morbidity noted – ensure appropriate follow-up.")
                st.rerun()
            else:
                st.error("Failed to save child assessment record.")

    # Show past assessments
    st.markdown("---")
    st.subheader("Past Assessments")
    past_assessments = db.get_child_assessment_records(selected_child['unique_id'])
    if past_assessments:
        for rec in past_assessments[:3]:
            with st.expander(f"Assessment – {rec.get('assessment_date', 'N/A')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Weight for Age:** {rec.get('weight_for_age_status', 'N/A')}")
                    st.write(f"**Stunting:** {rec.get('stunting_status', 'N/A')}")
                with col2:
                    st.write(f"**Wasting:** {rec.get('wasting_status', 'N/A')}")
                    st.write(f"**Referral Done:** {'Yes' if rec.get('referral_done') else 'No'}")
                with col3:
                    st.write(f"**Village:** {rec.get('village', 'N/A')}")
                    st.write(f"**Mother:** {rec.get('mother_name', 'N/A')}")
    else:
        st.info("No past assessments recorded.")
