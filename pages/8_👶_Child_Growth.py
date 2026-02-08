"""
Child Growth Monitoring Page
Track growth metrics for children under 5 years with WHO growth charts.
"""

import streamlit as st
from datetime import datetime, date
import plotly.graph_objects as go
import pandas as pd
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

# Filter residents under 5 years
filters = {'age_min': 0, 'age_max': 5}
children = db.filter_residents(filters)

if not children:
    st.warning("No children under 5 years found in the database.")
    st.info("Register children first in the 'Register Resident' page.")
    st.stop()

# Create selection dropdown
child_options = {f"{child['name']} ({child['unique_id']}) - Age: {child.get('age', 'N/A')}": child['unique_id'] 
                 for child in children}

selected_display = st.selectbox("Choose a child:", list(child_options.keys()))
selected_child_id = child_options[selected_display]

# Get selected child details
selected_child = db.get_resident(selected_child_id)

if not selected_child:
    st.error("Child not found!")
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
tab1, tab2 = st.tabs(["📝 Record Growth Data", "📊 Growth Charts & History"])

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
                    'resident_id': selected_child_id,
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
    growth_records = db.get_child_growth_records(selected_child_id)
    
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
