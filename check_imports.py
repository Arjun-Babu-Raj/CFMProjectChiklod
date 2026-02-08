#!/usr/bin/env python3
"""
Import Health Check Script
Verifies that all required modules and dependencies are properly installed and importable.
Run this script to diagnose import issues in deployment environments.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_imports():
    """Check all critical imports."""
    print("=" * 60)
    print("Import Health Check")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Check standard library
    print("\n[1/5] Checking standard library imports...")
    try:
        from datetime import datetime, date, timedelta
        import uuid
        print("  ✓ Standard library imports OK")
    except ImportError as e:
        errors.append(f"Standard library: {e}")
        print(f"  ✗ Error: {e}")
    
    # Check third-party dependencies
    print("\n[2/5] Checking third-party dependencies...")
    dependencies = [
        ('streamlit', 'st'),
        ('pandas', 'pd'),
        ('plotly.graph_objects', 'go'),
        ('PIL', 'Image'),
        ('supabase', None),
        ('dotenv', 'load_dotenv'),
    ]
    
    for module, alias in dependencies:
        try:
            if alias:
                exec(f"import {module} as {alias}")
            else:
                exec(f"import {module}")
            print(f"  ✓ {module}")
        except ImportError as e:
            errors.append(f"{module}: {e}")
            print(f"  ✗ {module}: {e}")
    
    # Check database module
    print("\n[3/5] Checking database module...")
    try:
        from database import DatabaseManager, init_database
        print("  ✓ database.DatabaseManager")
        print("  ✓ database.init_database")
    except ImportError as e:
        errors.append(f"database: {e}")
        print(f"  ✗ database: {e}")
    
    # Check utils module
    print("\n[4/5] Checking utils module...")
    utils_imports = [
        'check_authentication',
        'get_current_user_name',
        'get_current_user',
        'logout',
        'load_config',
        'init_authenticator',
        'generate_unique_id',
        'validate_unique_id_format',
        'compress_image',
        'save_uploaded_photo',
        'select_resident_widget',
    ]
    
    try:
        for func_name in utils_imports:
            exec(f"from utils import {func_name}")
            print(f"  ✓ utils.{func_name}")
    except ImportError as e:
        errors.append(f"utils: {e}")
        print(f"  ✗ utils: {e}")
    
    # Check page files
    print("\n[5/5] Checking page files...")
    pages_dir = project_root / "pages"
    if pages_dir.exists():
        page_files = sorted(pages_dir.glob("*.py"))
        for page_file in page_files:
            print(f"  • {page_file.name}")
        print(f"  ✓ Found {len(page_files)} page files")
    else:
        errors.append("pages directory not found")
        print("  ✗ pages directory not found")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if not errors and not warnings:
        print("✅ All checks passed! Application should run correctly.")
        return 0
    else:
        if errors:
            print(f"\n❌ {len(errors)} error(s) found:")
            for error in errors:
                print(f"   - {error}")
        if warnings:
            print(f"\n⚠️  {len(warnings)} warning(s):")
            for warning in warnings:
                print(f"   - {warning}")
        return 1

if __name__ == "__main__":
    sys.exit(check_imports())
