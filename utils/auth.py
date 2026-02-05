"""
Authentication helpers for streamlit-authenticator integration.
"""

import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import shutil
import os
import copy


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Load authentication configuration from Streamlit secrets or YAML file.
    Priority: st.secrets > config.yaml > config.template.yaml
    
    On Streamlit Cloud, config.yaml won't exist (it's in .gitignore), so this function
    will load from st.secrets which is where you add credentials in the Streamlit Cloud dashboard.
    
    Args:
        config_path: Path to config file (used as fallback)
        
    Returns:
        Configuration dictionary
    """
    # Helper function to load YAML config
    def _load_yaml_config(path: str) -> dict:
        with open(path) as file:
            return yaml.load(file, Loader=SafeLoader)
    
    # Try to load from Streamlit secrets first (for Cloud deployment)
    try:
        if "credentials" in st.secrets:
            # st.secrets is a special object that needs deep recursive conversion
            # We need to convert all nested dicts/objects recursively
            def _convert_secrets_to_dict(obj):
                """Recursively convert st.secrets objects to regular dicts"""
                if isinstance(obj, dict):
                    return {k: _convert_secrets_to_dict(v) for k, v in obj.items()}
                elif hasattr(obj, '__getitem__') and hasattr(obj, 'keys'):
                    # It's dict-like (includes Secrets objects)
                    return {k: _convert_secrets_to_dict(obj[k]) for k in obj.keys()}
                else:
                    return obj
            
            credentials = _convert_secrets_to_dict(st.secrets["credentials"])
            cookie = _convert_secrets_to_dict(st.secrets.get("cookie", {
                "name": "cfm_cookie",
                "key": "cfm_key",
                "expiry_days": 30
            }))
            
            # Add preauthorized section if not present
            preauthorized = _convert_secrets_to_dict(st.secrets.get("preauthorized", {
                "emails": list(credentials.get("usernames", {}).keys())
            })) if "preauthorized" in st.secrets else {
                "emails": []
            }
            
            config = {
                "credentials": credentials,
                "cookie": cookie,
                "preauthorized": preauthorized
            }
            return config
    except Exception as e:
        pass
    
    # Fallback to local config.yaml file
    try:
        return _load_yaml_config(config_path)
    except FileNotFoundError:
        # Try to create config.yaml from template
        template_path = "config.template.yaml"
        if os.path.exists(template_path):
            try:
                shutil.copy(template_path, config_path)
                st.success(f"✅ Created '{config_path}' from template.")
                st.warning("⚠️ Using default configuration. Please review and update credentials for production use.")
                return _load_yaml_config(config_path)
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
