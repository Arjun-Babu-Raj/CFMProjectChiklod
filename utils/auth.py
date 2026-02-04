"""
Authentication helpers for streamlit-authenticator integration.
"""

import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Load authentication configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path) as file:
            config = yaml.load(file, Loader=SafeLoader)
        return config
    except FileNotFoundError:
        st.error(f"Configuration file '{config_path}' not found. Please create it from config.template.yaml")
        st.stop()
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        st.stop()


def init_authenticator(config: dict):
    """
    Initialize the authenticator with config.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Authenticator instance
    """
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    return authenticator


def check_authentication() -> bool:
    """
    Check if user is authenticated.
    
    Returns:
        True if authenticated, False otherwise
    """
    if 'authentication_status' not in st.session_state:
        return False
    
    return st.session_state.get('authentication_status', False)


def get_current_user() -> str:
    """
    Get the currently logged-in username.
    
    Returns:
        Username or empty string if not logged in
    """
    if check_authentication():
        return st.session_state.get('username', '')
    return ''


def get_current_user_name() -> str:
    """
    Get the full name of currently logged-in user.
    
    Returns:
        Full name or empty string if not logged in
    """
    if check_authentication():
        return st.session_state.get('name', '')
    return ''


def logout():
    """Clear authentication session state."""
    if 'authentication_status' in st.session_state:
        st.session_state['authentication_status'] = None
    if 'username' in st.session_state:
        st.session_state['username'] = None
    if 'name' in st.session_state:
        st.session_state['name'] = None
