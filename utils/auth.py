"""
Authentication helpers for streamlit-authenticator integration.
"""

import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import shutil
import os


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Load authentication configuration from YAML file.
    If config.yaml doesn't exist, automatically create it from config.template.yaml.
    
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
        # Try to create config.yaml from template
        template_path = "config.template.yaml"
        if os.path.exists(template_path):
            try:
                shutil.copy(template_path, config_path)
                st.success(f"✅ Created '{config_path}' from template. Using default credentials.")
                st.info("**Default login credentials:**\n- Username: worker1\n- Password: password123")
                with open(config_path) as file:
                    config = yaml.load(file, Loader=SafeLoader)
                return config
            except Exception as e:
                st.error(f"Failed to create config file from template: {e}")
                st.stop()
        else:
            st.error(f"Configuration file '{config_path}' not found and template '{template_path}' is missing.")
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
