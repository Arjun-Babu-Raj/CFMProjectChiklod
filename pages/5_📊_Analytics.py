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

# Tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["👥 Demographics", "👶 Child Health", "🤰 Maternal Health", "💊 NCD Control"])

with tab1:
    # Demographics
    st.subheader("Demographics")
    
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

with tab2:
    # Child Health Analytics
    st.subheader("👶 Child Health Analytics")
    
    child_analytics = db.get_child_health_analytics()
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Children (<5 years)", child_analytics['total_children'])
    
    with col2:
        st.metric("Children with Growth Records", child_analytics['children_with_records'])
    
    with col3:
        if child_analytics['children_with_records'] > 0:
            malnourished_pct = (child_analytics['nutritional_status'].get('Malnourished', 0) / 
                               child_analytics['children_with_records'] * 100)
            st.metric("Malnourished %", f"{malnourished_pct:.1f}%")
        else:
            st.metric("Malnourished %", "N/A")
    
    st.markdown("---")
    
    # Nutritional Status Pie Chart
    if child_analytics['nutritional_status']:
        st.write("**Nutritional Status Distribution**")
        st.caption("Based on WHO Z-scores from growth monitoring (Z-score < -2 = Malnourished)")
        
        nutritional_data = child_analytics['nutritional_status']
        if sum(nutritional_data.values()) > 0:
            df_nutrition = pd.DataFrame(list(nutritional_data.items()), 
                                       columns=['Status', 'Count'])
            
            fig_nutrition = px.pie(df_nutrition, values='Count', names='Status',
                                  title='Nutritional Status of Children',
                                  color='Status',
                                  color_discrete_map={'Normal': '#2ecc71', 'Malnourished': '#e74c3c'})
            st.plotly_chart(fig_nutrition, use_container_width=True)
        else:
            st.info("No nutritional status data available yet")
    else:
        st.info("No child growth data available. Start tracking children in the Child Growth module.")

with tab3:
    # Maternal Health Analytics
    st.subheader("🤰 Maternal Health Analytics")
    
    maternal_analytics = db.get_maternal_health_analytics()
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Pregnancies", maternal_analytics['active_pregnancies'])
    
    with col2:
        st.metric("High Risk Mothers", maternal_analytics['high_risk_count'],
                 delta="Require Attention" if maternal_analytics['high_risk_count'] > 0 else None,
                 delta_color="inverse")
    
    with col3:
        total_visits = maternal_analytics['anc_visits'] + maternal_analytics['pnc_visits']
        st.metric("Total Maternal Visits", total_visits)
    
    st.markdown("---")
    
    # ANC vs PNC Visits Bar Chart
    if maternal_analytics['anc_visits'] > 0 or maternal_analytics['pnc_visits'] > 0:
        st.write("**ANC vs PNC Visits**")
        
        visit_data = {
            'Visit Type': ['ANC Visits', 'PNC Visits'],
            'Count': [maternal_analytics['anc_visits'], maternal_analytics['pnc_visits']]
        }
        df_maternal_visits = pd.DataFrame(visit_data)
        
        fig_maternal = px.bar(df_maternal_visits, x='Visit Type', y='Count',
                             title='Antenatal vs Postnatal Care Visits',
                             color='Visit Type',
                             color_discrete_map={'ANC Visits': '#e91e63', 'PNC Visits': '#9c27b0'})
        st.plotly_chart(fig_maternal, use_container_width=True)
        
        # Additional insights
        if maternal_analytics['anc_visits'] > 0 and maternal_analytics['pnc_visits'] > 0:
            ratio = maternal_analytics['pnc_visits'] / maternal_analytics['anc_visits']
            st.info(f"**PNC/ANC Ratio:** {ratio:.2f} - "
                   f"{'Good follow-up' if ratio >= 0.8 else 'Need to improve PNC follow-up'}")
    else:
        st.info("No maternal health data available. Start tracking mothers in the Maternal Health module.")

with tab4:
    # NCD Control Analytics
    st.subheader("💊 NCD Control Analytics")
    
    ncd_analytics = db.get_ncd_analytics()
    
    # Metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total NCD Patients Tracking", ncd_analytics['total_ncd_patients'])
    
    with col2:
        # Count recent uncontrolled BP cases
        uncontrolled_trend = ncd_analytics['uncontrolled_bp_trend']
        if uncontrolled_trend:
            recent_uncontrolled = list(uncontrolled_trend.values())[-1] if uncontrolled_trend else 0
            st.metric("Recent Uncontrolled BP Cases", recent_uncontrolled)
        else:
            st.metric("Recent Uncontrolled BP Cases", 0)
    
    st.markdown("---")
    
    # Uncontrolled BP Trend Line Chart
    if uncontrolled_trend:
        st.write("**Uncontrolled Blood Pressure Trend (Last 6 Months)**")
        st.caption("Tracking patients with Systolic BP > 140 mmHg")
        
        df_bp_trend = pd.DataFrame(list(uncontrolled_trend.items()), 
                                   columns=['Month', 'Uncontrolled BP Count'])
        
        fig_bp_trend = px.line(df_bp_trend, x='Month', y='Uncontrolled BP Count',
                              title='Monthly Uncontrolled Blood Pressure Cases',
                              markers=True,
                              line_shape='spline')
        
        # Add threshold line
        fig_bp_trend.add_hline(y=0, line_dash="dash", line_color="green", 
                              annotation_text="Target: 0 Uncontrolled Cases")
        
        st.plotly_chart(fig_bp_trend, use_container_width=True)
        
        # Analysis
        if len(uncontrolled_trend) >= 2:
            values = list(uncontrolled_trend.values())
            if values[-1] < values[0]:
                st.success("📉 **Positive Trend:** Uncontrolled BP cases are decreasing!")
            elif values[-1] > values[0]:
                st.warning("📈 **Alert:** Uncontrolled BP cases are increasing. Enhanced follow-up needed.")
            else:
                st.info("➡️ **Stable:** Uncontrolled BP cases remain stable.")
    else:
        st.info("No NCD data available. Start tracking patients in the NCD Followup module.")

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

# Medical history overview
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
