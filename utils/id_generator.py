"""
Unique ID generator for residents.
Generates IDs in format: VH-YYYY-XXXX (e.g., VH-2026-0001)
"""

from datetime import datetime
from typing import Optional
from database.db_manager import DatabaseManager


def generate_unique_id(db_manager: Optional[DatabaseManager] = None) -> str:
    """
    Generate a unique resident ID in format VH-YYYY-XXXX.
    
    Args:
        db_manager: DatabaseManager instance for checking existing IDs
        
    Returns:
        Unique ID string
    """
    if db_manager is None:
        db_manager = DatabaseManager()
    
    # Get current year
    current_year = datetime.now().year
    
    # Get all existing IDs for current year
    all_residents = db_manager.get_all_residents()
    
    # Filter IDs for current year
    current_year_ids = [
        r['unique_id'] for r in all_residents 
        if r['unique_id'].startswith(f"VH-{current_year}-")
    ]
    
    if not current_year_ids:
        # First ID of the year
        sequence = 1
    else:
        # Extract sequence numbers and find max
        sequences = []
        for uid in current_year_ids:
            try:
                seq_str = uid.split('-')[-1]
                sequences.append(int(seq_str))
            except (ValueError, IndexError):
                continue
        
        if sequences:
            sequence = max(sequences) + 1
        else:
            sequence = 1
    
    # Format: VH-YYYY-XXXX (4-digit zero-padded sequence)
    unique_id = f"VH-{current_year}-{sequence:04d}"
    
    return unique_id


def validate_unique_id_format(unique_id: str) -> bool:
    """
    Validate that a unique ID follows the correct format.
    
    Args:
        unique_id: ID string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    import re
    pattern = r'^VH-\d{4}-\d{4}$'
    return bool(re.match(pattern, unique_id))
