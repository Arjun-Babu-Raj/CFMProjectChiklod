"""
Village Health Tracking System - Main Application
Department of Community and Family Medicine, AIIMS Bhopal

Main entry point with authentication and navigation.
"""

import streamlit as st
from datetime import datetime
from database import init_database, DatabaseManager
from utils import (
    load_config,
    init_authenticator,
    check_authentication,
    get_current_user_name
)

# Page configuration must be first Streamlit command
# This runs at module level but only once
try:
    st.set_page_config(
        page_title="Village Health Tracking System",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except st.errors.StreamlitAPIException:
    # Config already set - this is expected in multi-page apps
    pass


def show_login():
    """Display login page."""
    st.title("🏥 Village Health Tracking System")
    st.subheader("Department of Community and Family Medicine, AIIMS Bhopal")
    
    st.markdown("---")
    
    # Load config and create authenticator
    config = load_config()
    
    # Initialize session state for failed login tracking BEFORE authenticator
    # This prevents authenticator from trying to write to read-only st.secrets
    if 'failed_login_attempts' not in st.session_state:
        st.session_state['failed_login_attempts'] = {}
    
    authenticator = init_authenticator(config)
    
    # Show login form
    authenticator.login(location='main')
    
    if st.session_state.get("authentication_status") == False:
        st.error('Username/password is incorrect')
    elif st.session_state.get("authentication_status") == None:
        st.warning('Please enter your username and password')
        
        with st.expander("ℹ️ First Time Setup"):
            st.info("""
            **For first-time setup:**
            1. Copy `config.template.yaml` to `config.yaml`
            2. Update the passwords (default: password123)
            3. Change the cookie key for security
            
            **Default credentials for testing:**
            - Username: worker1
            - Password: password123
            """)


def show_home():
    """Display home page for authenticated users."""
    st.title("PROJECT CHIKLOD")
    st.subheader("Department of Community and Family Medicine, AIIMS Bhopal")
    
    # Welcome message
    user_name = get_current_user_name()
    st.success(f"Welcome, **{user_name}**!")
    
    st.markdown("---")
    
    # Quick stats
    st.subheader("Quick Statistics")
    
    db = st.session_state.db_manager
    
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
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Register New Resident", use_container_width=True):
            st.switch_page("pages/1_📝_Register_Resident.py")
    
    with col2:
        if st.button("Record Visit", use_container_width=True):
            st.switch_page("pages/2_🏥_Record_Visit.py")
    
    with col3:
        if st.button("Search Residents", use_container_width=True):
            st.switch_page("pages/6_🔍_Search.py")
    
    with col4:
        if st.button("View Analytics", use_container_width=True):
            st.switch_page("pages/5_📊_Analytics.py")
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    recent_visits = db.get_recent_visits(limit=10)
    
    if recent_visits:
        for visit in recent_visits:
            with st.container():
                col1, col2, col3 = st.columns([2, 3, 2])
                
                with col1:
                    st.write(f"**{visit['visit_date']}** {visit['visit_time']}")
                
                with col2:
                    resident_name = visit.get('resident_name', 'Unknown')
                    st.write(f"Visit for **{resident_name}** (ID: {visit['resident_id']})")
                
                with col3:
                    st.write(f"By: {visit['health_worker']}")
                
                st.divider()
    else:
        st.info("No recent activity. Start by registering residents and recording visits.")
    
    # Footer
    st.markdown("---")
    st.caption("Village Health Tracking System | CFM Project Chiklod | 2026")


def main():
    """Main application logic."""
    
    # Initialize database (only once)
    try:
        init_database()
    except Exception as e:
        st.error(f"❌ Database initialization error: {e}")
        st.error("The application cannot continue without a database. Please contact support.")
        st.stop()
    
    # Initialize database manager
    if 'db_manager' not in st.session_state:
        try:
            st.session_state.db_manager = DatabaseManager()
        except Exception as e:
            st.error(f"❌ Failed to create database manager: {e}")
            st.error("The application cannot continue. Please contact support.")
            st.stop()
    
    # Sidebar
    with st.sidebar:
        st.image("assets/cfm_chiklod_logo.svg", use_container_width=True)
        st.markdown("---")
        
        # Check authentication
        if check_authentication():
            user_name = get_current_user_name()
            st.write(f"👤 **{user_name}**")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                # Clear authentication state
                st.session_state['authentication_status'] = None
                st.session_state['name'] = None
                st.session_state['username'] = None
                st.rerun()
            
            st.markdown("---")
            st.info("Use the navigation menu above to access different sections.")
        else:
            st.info("Please log in to continue")
    
    # Main content
    if check_authentication():
        show_home()
    else:
        show_login()


if __name__ == "__main__":
    main()
