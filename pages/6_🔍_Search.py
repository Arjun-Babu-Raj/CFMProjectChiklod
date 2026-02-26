"""
Search and Browse Page
Search residents by various criteria and browse all residents.
"""

import streamlit as st
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
st.title("🔍 Search & Browse Residents")
st.markdown("Search residents by ID, name, or filter by criteria")
st.markdown("---")

# Two top-level tabs: Individual Search and Family Search
search_tab, family_tab = st.tabs(["👤 Individual Search", "👨‍👩‍👧‍👦 Family Search"])

with search_tab:
    # Search section
    st.subheader("🔎 Quick Search")

    col1, col2 = st.columns([3, 1])

    with col1:
        search_term = st.text_input("Search by Name or Unique ID", placeholder="Enter name or ID...")

    with col2:
        search_button = st.button("🔍 Search", use_container_width=True)

    # Advanced filters
    with st.expander("🔧 Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_gender = st.selectbox("Gender", ["All", "Male", "Female", "Other"])
        
        with col2:
            age_min = st.number_input("Min Age", min_value=0, max_value=120, value=0)
        
        with col3:
            age_max = st.number_input("Max Age", min_value=0, max_value=120, value=120)
        
        # Get unique village areas
        all_residents = db.get_all_residents()
        village_areas = sorted(list(set([r['village_area'] for r in all_residents if r['village_area']])))
        
        filter_area = st.selectbox("Village Area", ["All"] + village_areas)
        
        apply_filters = st.button("Apply Filters", use_container_width=True)

    st.markdown("---")

    # Results section
    results = []

    if search_term and search_button:
        # Quick search
        results = db.search_residents(search_term)
        st.subheader(f"Search Results ({len(results)} found)")

    elif apply_filters:
        # Apply advanced filters
        filters = {}
        
        if filter_gender != "All":
            filters['gender'] = filter_gender
        
        if age_min > 0 or age_max < 120:
            filters['age_min'] = age_min
            filters['age_max'] = age_max
        
        if filter_area != "All":
            filters['village_area'] = filter_area
        
        results = db.filter_residents(filters)
        st.subheader(f"Filter Results ({len(results)} found)")

    else:
        # Browse all residents
        results = db.get_all_residents()
        st.subheader(f"All Residents ({len(results)} total)")

    # Display results
    if results:
        # Convert to DataFrame for better display
        df = pd.DataFrame(results)
        
        # Select columns to display
        display_columns = ['unique_id', 'name', 'age', 'gender', 'phone', 'village_area', 'registration_date']
        available_columns = [col for col in display_columns if col in df.columns]
        df_display = df[available_columns].copy()
        
        # Rename columns for better readability
        column_rename = {
            'unique_id': 'ID',
            'name': 'Name',
            'age': 'Age',
            'gender': 'Gender',
            'phone': 'Phone',
            'village_area': 'Area',
            'registration_date': 'Registered'
        }
        df_display = df_display.rename(columns=column_rename)
        
        # Pagination
        st.write("**Results Table:**")
        
        # Items per page
        items_per_page = st.selectbox("Items per page", [10, 25, 50, 100], index=1)
        
        # Calculate total pages
        total_pages = len(df_display) // items_per_page + (1 if len(df_display) % items_per_page > 0 else 0)
        
        if total_pages > 1:
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
        else:
            page = 1
        
        # Get page data
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        df_page = df_display.iloc[start_idx:end_idx]
        
        # Display table
        st.dataframe(df_page, use_container_width=True, hide_index=True)
        
        st.caption(f"Showing {start_idx + 1} to {min(end_idx, len(df_display))} of {len(df_display)} results")
        
        st.markdown("---")
        
        # Detailed view section
        st.subheader("👤 View Detailed Profile")
        
        # Create selection for detailed view
        resident_options = {f"{r['name']} ({r['unique_id']})": r['unique_id'] for r in results}
        
        if resident_options:
            selected_display = st.selectbox("Select a resident to view details", [""] + list(resident_options.keys()))
            
            if selected_display:
                selected_id = resident_options[selected_display]
                resident = db.get_resident(selected_id)
                
                if resident:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Name:** {resident['name']}")
                        st.write(f"**ID:** {resident['unique_id']}")
                        st.write(f"**Age:** {resident['age'] if resident['age'] else 'N/A'}")
                        st.write(f"**Gender:** {resident['gender'] if resident['gender'] else 'N/A'}")
                    
                    with col2:
                        st.write(f"**Phone:** {resident['phone'] if resident['phone'] else 'N/A'}")
                        st.write(f"**Village Area:** {resident['village_area'] if resident['village_area'] else 'N/A'}")
                        st.write(f"**Address:** {resident['address'] if resident['address'] else 'N/A'}")
                    
                    with col3:
                        visits = db.get_resident_visits(selected_id)
                        st.write(f"**Total Visits:** {len(visits)}")
                        if visits:
                            st.write(f"**Last Visit:** {visits[0]['visit_date']}")
                        st.write(f"**Registered:** {resident['registration_date']}")
                        st.write(f"**By:** {resident['registered_by']}")
                    
                    st.markdown("---")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("👤 View Full Profile", use_container_width=True):
                            st.switch_page("pages/4_👤_View_Resident.py")
                    
                    with col2:
                        if st.button("🏥 Record Visit", use_container_width=True):
                            st.switch_page("pages/2_🏥_Record_Visit.py")
                    
                    with col3:
                        if st.button("📋 Medical History", use_container_width=True):
                            st.switch_page("pages/3_📋_Medical_History.py")
        
        st.markdown("---")
        
        # Export search results
        st.subheader("📥 Export Search Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="📄 Download as CSV",
                data=csv,
                file_name=f"residents_search_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # For Excel export
            try:
                from io import BytesIO
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_display.to_excel(writer, index=False, sheet_name='Residents')
                
                st.download_button(
                    label="📊 Download as Excel",
                    data=buffer.getvalue(),
                    file_name=f"residents_search_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Excel export not available: {e}")

    else:
        st.info("No residents found. Try a different search or filter.")

with family_tab:
    st.subheader("👨‍👩‍👧‍👦 Family Search by Samagra ID")
    st.markdown("Enter a Samagra ID to view all family members registered under it.")

    col1, col2 = st.columns([3, 1])
    with col1:
        family_samagra_id = st.text_input(
            "Samagra ID (Family ID)",
            placeholder="Enter 9-digit Samagra ID...",
            max_chars=9,
            key="family_samagra_input"
        )
    with col2:
        family_search_btn = st.button("🔍 Find Family", use_container_width=True)

    if family_search_btn and family_samagra_id:
        family_members = db.get_family_members(family_samagra_id)

        if family_members:
            st.success(f"Found **{len(family_members)}** family member(s) with Samagra ID: `{family_samagra_id}`")

            # Display as table
            family_df = pd.DataFrame(family_members)
            display_cols = ['unique_id', 'name', 'age', 'gender', 'phone']
            available = [c for c in display_cols if c in family_df.columns]
            family_display = family_df[available].rename(columns={
                'unique_id': 'ID', 'name': 'Name', 'age': 'Age',
                'gender': 'Gender', 'phone': 'Phone'
            })
            st.dataframe(family_display, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("Jump to Profile")
            member_options = {f"{m['name']} ({m['unique_id']})": m['unique_id'] for m in family_members}
            selected_member = st.selectbox("Select a family member", [""] + list(member_options.keys()),
                                           key="family_member_select")
            if selected_member:
                selected_member_id = member_options[selected_member]
                st.session_state['selected_resident_id'] = selected_member_id
                if st.button("👤 Go to Profile", use_container_width=True):
                    st.switch_page("pages/4_👤_View_Resident.py")
        else:
            st.warning(f"No residents found with Samagra ID: `{family_samagra_id}`")
    elif family_search_btn:
        st.error("Please enter a Samagra ID to search.")

st.markdown("---")
st.caption("Search & Browse | Village Health Tracking System")
