"""
Analytics Dashboard Page
Display comprehensive analytics and statistics for the health tracking system.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from database import DatabaseManager
from utils import check_authentication

# Check authentication
if not check_authentication():
    st.error("Please log in to access this page")
    st.stop()

# Initialize database manager
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

db = st.session_state.db_manager

# Page header
st.title("📊 Analytics Dashboard")
st.markdown("Comprehensive analytics and insights")
st.markdown("---")

# Overall statistics
st.subheader("📈 Overall Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_residents = db.get_resident_count()
    st.metric("Total Residents", total_residents)

with col2:
    total_visits = db.get_visit_count()
    st.metric("Total Visits", total_visits)

with col3:
    if total_residents > 0:
        avg_visits = total_visits / total_residents
        st.metric("Avg Visits/Resident", f"{avg_visits:.1f}")
    else:
        st.metric("Avg Visits/Resident", "0")

with col4:
    recent_visits = db.get_recent_visits(limit=1)
    if recent_visits:
        last_visit_date = recent_visits[0]['visit_date']
        st.metric("Last Visit", last_visit_date)
    else:
        st.metric("Last Visit", "None")

st.markdown("---")

# Demographics
st.subheader("👥 Demographics")

demographics = db.get_demographics_summary()

col1, col2 = st.columns(2)

with col1:
    # Gender distribution
    st.write("**Gender Distribution**")
    
    gender_dist = demographics['gender_distribution']
    if gender_dist:
        df_gender = pd.DataFrame(list(gender_dist.items()), columns=['Gender', 'Count'])
        fig_gender = px.pie(df_gender, values='Count', names='Gender', 
                           title='Gender Distribution',
                           color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_gender, use_container_width=True)
    else:
        st.info("No gender data available")

with col2:
    # Age groups
    st.write("**Age Distribution**")
    
    age_groups = demographics['age_groups']
    if age_groups:
        df_age = pd.DataFrame(list(age_groups.items()), columns=['Age Group', 'Count'])
        fig_age = px.bar(df_age, x='Age Group', y='Count',
                        title='Age Group Distribution',
                        color='Count',
                        color_continuous_scale='Blues')
        st.plotly_chart(fig_age, use_container_width=True)
    else:
        st.info("No age data available")

st.markdown("---")

# Health worker performance
st.subheader("👨‍⚕️ Visits by Health Worker")

visits_by_worker = db.get_visits_by_health_worker()

if visits_by_worker:
    df_workers = pd.DataFrame(visits_by_worker, columns=['Health Worker', 'Visit Count'])
    
    fig_workers = px.bar(df_workers, x='Health Worker', y='Visit Count',
                        title='Visits Recorded by Each Health Worker',
                        color='Visit Count',
                        color_continuous_scale='Greens')
    st.plotly_chart(fig_workers, use_container_width=True)
else:
    st.info("No visit data available")

st.markdown("---")

# Monthly trends
st.subheader("📅 Monthly Trends")

trends = db.get_monthly_trends()

col1, col2 = st.columns(2)

with col1:
    # Monthly registrations
    st.write("**Monthly Registrations**")
    
    monthly_reg = trends['monthly_registrations']
    if monthly_reg:
        df_reg = pd.DataFrame(list(monthly_reg.items()), columns=['Month', 'Count'])
        fig_reg = px.line(df_reg, x='Month', y='Count',
                         title='Residents Registered per Month',
                         markers=True)
        st.plotly_chart(fig_reg, use_container_width=True)
    else:
        st.info("No registration data available")

with col2:
    # Monthly visits
    st.write("**Monthly Visits**")
    
    monthly_visits = trends['monthly_visits']
    if monthly_visits:
        df_visits = pd.DataFrame(list(monthly_visits.items()), columns=['Month', 'Count'])
        fig_visits = px.line(df_visits, x='Month', y='Count',
                           title='Visits Recorded per Month',
                           markers=True)
        st.plotly_chart(fig_visits, use_container_width=True)
    else:
        st.info("No visit data available")

st.markdown("---")

# Recent activity
st.subheader("🕐 Recent Activity")

recent_visits = db.get_recent_visits(limit=15)

if recent_visits:
    df_recent = pd.DataFrame(recent_visits)
    
    # Display as table
    display_columns = ['visit_date', 'visit_time', 'resident_name', 'resident_id', 'health_worker']
    available_columns = [col for col in display_columns if col in df_recent.columns]
    
    if available_columns:
        df_display = df_recent[available_columns].copy()
        df_display.columns = ['Date', 'Time', 'Resident', 'ID', 'Health Worker']
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
else:
    st.info("No recent activity")

st.markdown("---")

# Village area distribution
st.subheader("🏘️ Residents by Village Area")

all_residents = db.get_all_residents()

if all_residents:
    # Count by village area
    df_residents = pd.DataFrame(all_residents)
    
    if 'village_area' in df_residents.columns:
        area_counts = df_residents['village_area'].value_counts()
        
        if not area_counts.empty:
            df_areas = pd.DataFrame({
                'Village Area': area_counts.index,
                'Count': area_counts.values
            })
            
            fig_areas = px.bar(df_areas, x='Village Area', y='Count',
                             title='Residents by Village Area',
                             color='Count',
                             color_continuous_scale='Oranges')
            st.plotly_chart(fig_areas, use_container_width=True)
        else:
            st.info("No village area data available")
    else:
        st.info("No village area data available")
else:
    st.info("No resident data available")

st.markdown("---")

# Common health conditions (from medical history)
st.subheader("🏥 Medical History Overview")

medical_histories = db.export_medical_history_to_df()

if not medical_histories.empty and 'chronic_conditions' in medical_histories.columns:
    # Count residents with medical history
    total_with_history = len(medical_histories)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Residents with Medical History", total_with_history)
    
    with col2:
        # Count those with chronic conditions
        with_chronic = medical_histories['chronic_conditions'].notna().sum()
        st.metric("With Chronic Conditions", with_chronic)
    
    with col3:
        # Count those with allergies
        with_allergies = medical_histories['allergies'].notna().sum()
        st.metric("With Known Allergies", with_allergies)
else:
    st.info("No medical history data available")

st.markdown("---")

# Export analytics data
st.subheader("📥 Export Analytics")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Download Analytics Report (CSV)", use_container_width=True):
        # Create summary report
        report_data = {
            'Metric': [
                'Total Residents',
                'Total Visits',
                'Average Visits per Resident',
                'Residents with Medical History'
            ],
            'Value': [
                total_residents,
                total_visits,
                f"{avg_visits:.1f}" if total_residents > 0 else "0",
                len(medical_histories) if not medical_histories.empty else 0
            ]
        }
        
        df_report = pd.DataFrame(report_data)
        csv = df_report.to_csv(index=False)
        
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"analytics_report_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📈 Refresh Dashboard", use_container_width=True):
        st.rerun()

st.markdown("---")
st.caption("Analytics Dashboard | Village Health Tracking System")
