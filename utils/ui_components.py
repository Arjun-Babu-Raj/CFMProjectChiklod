"""
UI Components Module
Provides reusable UI components for Streamlit pages.
"""

import streamlit as st
from typing import Optional, Dict


def select_resident_widget(db_manager, key_prefix: str = "") -> Optional[Dict]:
    """
    Display a search-to-select resident widget.
    
    This widget implements a scalability-friendly approach by only loading
    residents after the user performs a search, instead of loading all
    residents at once.
    
    Args:
        db_manager: DatabaseManager instance to use for search
        key_prefix: Optional prefix for widget keys to avoid conflicts
        
    Returns:
        Selected resident dictionary or None if no resident selected
    """
    # Search input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input(
            "Search by Name or ID",
            placeholder="Start typing to search...",
            key=f"{key_prefix}_search_input",
            help="Enter at least 2 characters to search"
        )
    
    with col2:
        # Visual feedback button (optional - search happens on input)
        st.button("🔍 Search", key=f"{key_prefix}_search_btn", use_container_width=True)
    
    # Only search if user has typed something
    if search_term and len(search_term) >= 2:
        residents = db_manager.search_residents(search_term)
        
        if residents:
            st.write(f"Found {len(residents)} resident(s)")
            
            # Create selection options
            resident_options = {
                f"{r['name']} ({r['unique_id']})": r['unique_id'] 
                for r in residents
            }
            
            selected_display = st.selectbox(
                "Select Resident",
                list(resident_options.keys()),
                key=f"{key_prefix}_resident_select"
            )
            
            selected_id = resident_options[selected_display]
            
            # Get and return the full resident object
            resident = db_manager.get_resident(selected_id)
            return resident
        else:
            st.warning("No residents found matching your search.")
            return None
    elif search_term and len(search_term) < 2:
        st.info("👆 Please enter at least 2 characters to search")
        return None
    else:
        st.info("👆 Please search for a resident to continue")
        return None
