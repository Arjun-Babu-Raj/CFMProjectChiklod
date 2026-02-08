"""
Export Data Page
Export residents, visits, and medical history data to CSV or Excel.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
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
st.title("📥 Export Data")
st.markdown("Export residents, visits, and medical history data")
st.markdown("---")

# Export options
st.subheader("Select Data to Export")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    export_residents = st.checkbox("Residents", value=True)

with col2:
    export_visits = st.checkbox("Visits", value=True)

with col3:
    export_medical_history = st.checkbox("Medical History", value=False)

with col4:
    export_growth = st.checkbox("Child Growth", value=False)

with col5:
    export_maternal = st.checkbox("Maternal Health", value=False)

with col6:
    export_ncd = st.checkbox("NCD Followup", value=False)

st.markdown("---")

# Date range filter for visits
if export_visits:
    st.subheader("📅 Visit Date Range Filter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        use_date_filter = st.checkbox("Apply date filter", value=False)
    
    with col2:
        if use_date_filter:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
        else:
            start_date = None
    
    with col3:
        if use_date_filter:
            end_date = st.date_input("End Date", value=datetime.now())
        else:
            end_date = None
    
    st.markdown("---")

# Export format
st.subheader("📊 Export Format")

export_format = st.radio("Select format", ["CSV", "Excel"], horizontal=True)

st.markdown("---")

# Preview section
st.subheader("👁️ Data Preview")

if export_residents:
    with st.expander("Residents Data Preview", expanded=True):
        df_residents = db.export_residents_to_df()
        
        if not df_residents.empty:
            st.write(f"**Total Residents:** {len(df_residents)}")
            st.dataframe(df_residents.head(10), use_container_width=True)
            st.caption(f"Showing first 10 of {len(df_residents)} residents")
        else:
            st.info("No resident data available")

if export_visits:
    with st.expander("Visits Data Preview", expanded=True):
        df_visits = db.export_visits_to_df()
        
        # Apply date filter if selected
        if use_date_filter and not df_visits.empty and start_date and end_date:
            df_visits['visit_date'] = pd.to_datetime(df_visits['visit_date'])
            df_visits = df_visits[
                (df_visits['visit_date'] >= pd.Timestamp(start_date)) &
                (df_visits['visit_date'] <= pd.Timestamp(end_date))
            ]
        
        if not df_visits.empty:
            st.write(f"**Total Visits:** {len(df_visits)}")
            st.dataframe(df_visits.head(10), use_container_width=True)
            st.caption(f"Showing first 10 of {len(df_visits)} visits")
        else:
            st.info("No visit data available for selected date range")

if export_medical_history:
    with st.expander("Medical History Data Preview", expanded=True):
        df_history = db.export_medical_history_to_df()
        
        if not df_history.empty:
            st.write(f"**Total Records:** {len(df_history)}")
            st.dataframe(df_history.head(10), use_container_width=True)
            st.caption(f"Showing first 10 of {len(df_history)} medical history records")
        else:
            st.info("No medical history data available")

if export_growth:
    with st.expander("Child Growth Data Preview", expanded=False):
        df_growth = db.export_growth_data()
        
        if not df_growth.empty:
            st.write(f"**Total Records:** {len(df_growth)}")
            st.dataframe(df_growth.head(10), use_container_width=True)
            st.caption(f"Showing first 10 of {len(df_growth)} growth monitoring records")
        else:
            st.info("No child growth data available")

if export_maternal:
    with st.expander("Maternal Health Data Preview", expanded=False):
        df_maternal = db.export_maternal_data()
        
        if not df_maternal.empty:
            st.write(f"**Total Records:** {len(df_maternal)}")
            st.dataframe(df_maternal.head(10), use_container_width=True)
            st.caption(f"Showing first 10 of {len(df_maternal)} maternal health records")
        else:
            st.info("No maternal health data available")

if export_ncd:
    with st.expander("NCD Followup Data Preview", expanded=False):
        df_ncd = db.export_ncd_data()
        
        if not df_ncd.empty:
            st.write(f"**Total Records:** {len(df_ncd)}")
            st.dataframe(df_ncd.head(10), use_container_width=True)
            st.caption(f"Showing first 10 of {len(df_ncd)} NCD followup records")
        else:
            st.info("No NCD followup data available")

st.markdown("---")

# Export buttons
st.subheader("⬇️ Download Data")

if export_format == "CSV":
    # CSV Export
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        if export_residents:
            df_residents = db.export_residents_to_df()
            if not df_residents.empty:
                csv_residents = df_residents.to_csv(index=False)
                st.download_button(
                    label="📄 Residents CSV",
                    data=csv_residents,
                    file_name=f"residents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No data")
    
    with col2:
        if export_visits:
            df_visits = db.export_visits_to_df()
            
            # Apply date filter
            if use_date_filter and not df_visits.empty and start_date and end_date:
                df_visits['visit_date'] = pd.to_datetime(df_visits['visit_date'])
                df_visits = df_visits[
                    (df_visits['visit_date'] >= pd.Timestamp(start_date)) &
                    (df_visits['visit_date'] <= pd.Timestamp(end_date))
                ]
            
            if not df_visits.empty:
                csv_visits = df_visits.to_csv(index=False)
                st.download_button(
                    label="📄 Visits CSV",
                    data=csv_visits,
                    file_name=f"visits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No data")
    
    with col3:
        if export_medical_history:
            df_history = db.export_medical_history_to_df()
            if not df_history.empty:
                csv_history = df_history.to_csv(index=False)
                st.download_button(
                    label="📄 Med History CSV",
                    data=csv_history,
                    file_name=f"medical_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No data")
    
    with col4:
        if export_growth:
            df_growth = db.export_growth_data()
            if not df_growth.empty:
                csv_growth = df_growth.to_csv(index=False)
                st.download_button(
                    label="📄 Child Growth CSV",
                    data=csv_growth,
                    file_name=f"child_growth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No data")
    
    with col5:
        if export_maternal:
            df_maternal = db.export_maternal_data()
            if not df_maternal.empty:
                csv_maternal = df_maternal.to_csv(index=False)
                st.download_button(
                    label="📄 Maternal CSV",
                    data=csv_maternal,
                    file_name=f"maternal_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No data")
    
    with col6:
        if export_ncd:
            df_ncd = db.export_ncd_data()
            if not df_ncd.empty:
                csv_ncd = df_ncd.to_csv(index=False)
                st.download_button(
                    label="📄 NCD Followup CSV",
                    data=csv_ncd,
                    file_name=f"ncd_followup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No data")

else:
    # Excel Export
    try:
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            if export_residents:
                df_residents = db.export_residents_to_df()
                if not df_residents.empty:
                    df_residents.to_excel(writer, sheet_name='Residents', index=False)
            
            if export_visits:
                df_visits = db.export_visits_to_df()
                
                # Apply date filter
                if use_date_filter and not df_visits.empty and start_date and end_date:
                    df_visits['visit_date'] = pd.to_datetime(df_visits['visit_date'])
                    df_visits = df_visits[
                        (df_visits['visit_date'] >= pd.Timestamp(start_date)) &
                        (df_visits['visit_date'] <= pd.Timestamp(end_date))
                    ]
                
                if not df_visits.empty:
                    df_visits.to_excel(writer, sheet_name='Visits', index=False)
            
            if export_medical_history:
                df_history = db.export_medical_history_to_df()
                if not df_history.empty:
                    df_history.to_excel(writer, sheet_name='Medical History', index=False)
            
            if export_growth:
                df_growth = db.export_growth_data()
                if not df_growth.empty:
                    df_growth.to_excel(writer, sheet_name='Child Growth', index=False)
            
            if export_maternal:
                df_maternal = db.export_maternal_data()
                if not df_maternal.empty:
                    df_maternal.to_excel(writer, sheet_name='Maternal Health', index=False)
            
            if export_ncd:
                df_ncd = db.export_ncd_data()
                if not df_ncd.empty:
                    df_ncd.to_excel(writer, sheet_name='NCD Followup', index=False)
        
        buffer.seek(0)
        
        st.download_button(
            label="📊 Download Excel Workbook (All Selected Data)",
            data=buffer.getvalue(),
            file_name=f"health_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    except Exception as e:
        st.error(f"Error creating Excel file: {e}")
        st.info("Try CSV format instead")

st.markdown("---")

# Export statistics
st.subheader("📊 Export Statistics")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if export_residents:
        df_residents = db.export_residents_to_df()
        st.metric("Residents", len(df_residents) if not df_residents.empty else 0)

with col2:
    if export_visits:
        df_visits = db.export_visits_to_df()
        
        # Apply date filter
        if use_date_filter and not df_visits.empty and start_date and end_date:
            df_visits['visit_date'] = pd.to_datetime(df_visits['visit_date'])
            df_visits = df_visits[
                (df_visits['visit_date'] >= pd.Timestamp(start_date)) &
                (df_visits['visit_date'] <= pd.Timestamp(end_date))
            ]
        
        st.metric("Visits", len(df_visits) if not df_visits.empty else 0)

with col3:
    if export_medical_history:
        df_history = db.export_medical_history_to_df()
        st.metric("Med History", len(df_history) if not df_history.empty else 0)

with col4:
    if export_growth:
        df_growth = db.export_growth_data()
        st.metric("Growth", len(df_growth) if not df_growth.empty else 0)

with col5:
    if export_maternal:
        df_maternal = db.export_maternal_data()
        st.metric("Maternal", len(df_maternal) if not df_maternal.empty else 0)

with col6:
    if export_ncd:
        df_ncd = db.export_ncd_data()
        st.metric("NCD", len(df_ncd) if not df_ncd.empty else 0)

st.markdown("---")

# Information box
st.info("""
**ℹ️ Export Information:**
- CSV files are compatible with Excel, Google Sheets, and most data analysis tools
- Excel format includes all selected data in separate sheets
- Date filters apply only to visits data
- Photo paths are included in exports but photos themselves are not
- All exports use UTF-8 encoding
- New modules (Child Growth, Maternal Health, NCD Followup) include resident_id for joining with residents table
""")

st.markdown("---")
st.caption("Data Export | Village Health Tracking System")
