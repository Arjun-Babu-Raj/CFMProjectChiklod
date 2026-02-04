#!/usr/bin/env python3
"""
Test script for Village Health Tracking System
Run this to verify all core functionality works correctly.
"""

import sys
from datetime import datetime

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from database import DatabaseManager, init_database
        from utils import (
            generate_unique_id, validate_phone, calculate_bmi,
            save_uploaded_photo, validate_blood_pressure,
            get_bmi_category, validate_age
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_database():
    """Test database operations."""
    print("\nTesting database operations...")
    try:
        from database import DatabaseManager, init_database
        
        # Initialize database
        init_database("test_health.db")
        db = DatabaseManager("test_health.db")
        
        # Test resident operations
        from utils import generate_unique_id
        unique_id = generate_unique_id(db)
        
        resident_data = {
            'unique_id': unique_id,
            'name': 'Test Resident',
            'age': 30,
            'gender': 'Male',
            'address': 'Test Address',
            'phone': '1234567890',
            'village_area': 'Test Area',
            'photo_path': None,
            'registration_date': datetime.now().strftime('%Y-%m-%d'),
            'registered_by': 'Test Worker'
        }
        
        assert db.add_resident(resident_data), "Failed to add resident"
        resident = db.get_resident(unique_id)
        assert resident is not None, "Failed to retrieve resident"
        assert resident['name'] == 'Test Resident', "Resident data mismatch"
        
        # Test visit operations
        visit_data = {
            'resident_id': unique_id,
            'visit_date': datetime.now().strftime('%Y-%m-%d'),
            'visit_time': datetime.now().strftime('%H:%M:%S'),
            'health_worker': 'Test Worker',
            'bp_systolic': 120,
            'bp_diastolic': 80,
            'temperature': 98.6,
            'pulse': 72,
            'weight': 70.0,
            'height': 175.0,
            'bmi': 22.9,
            'spo2': 98,
            'complaints': 'Test complaint',
            'observations': 'Test observation',
            'photo_paths': None
        }
        
        assert db.add_visit(visit_data), "Failed to add visit"
        visits = db.get_resident_visits(unique_id)
        assert len(visits) == 1, "Failed to retrieve visits"
        
        # Test medical history
        history_data = {
            'resident_id': unique_id,
            'chronic_conditions': 'Test conditions',
            'past_diagnoses': 'Test diagnoses',
            'current_medications': 'Test medications',
            'allergies': 'Test allergies',
            'family_history': 'Test family history',
            'notes': 'Test notes',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_by': 'Test Worker'
        }
        
        assert db.add_or_update_medical_history(history_data), "Failed to add medical history"
        history = db.get_medical_history(unique_id)
        assert history is not None, "Failed to retrieve medical history"
        
        # Test statistics
        count = db.get_resident_count()
        assert count == 1, f"Expected 1 resident, got {count}"
        
        visit_count = db.get_visit_count()
        assert visit_count == 1, f"Expected 1 visit, got {visit_count}"
        
        print("✅ All database operations successful")
        
        # Cleanup
        import os
        os.remove("test_health.db")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validators():
    """Test validation functions."""
    print("\nTesting validators...")
    try:
        from utils import (
            validate_phone, validate_age, validate_blood_pressure,
            validate_temperature, validate_pulse, validate_weight,
            validate_height, validate_spo2, calculate_bmi, get_bmi_category
        )
        
        # Test phone validation
        assert validate_phone("1234567890")[0] == True, "Valid phone failed"
        assert validate_phone("123")[0] == False, "Invalid phone passed"
        
        # Test age validation
        assert validate_age(30)[0] == True, "Valid age failed"
        assert validate_age(150)[0] == False, "Invalid age passed"
        
        # Test blood pressure
        assert validate_blood_pressure(120, 80)[0] == True, "Valid BP failed"
        assert validate_blood_pressure(80, 120)[0] == False, "Invalid BP passed"
        
        # Test temperature
        assert validate_temperature(98.6)[0] == True, "Valid temp failed"
        assert validate_temperature(200)[0] == False, "Invalid temp passed"
        
        # Test pulse
        assert validate_pulse(72)[0] == True, "Valid pulse failed"
        assert validate_pulse(300)[0] == False, "Invalid pulse passed"
        
        # Test weight
        assert validate_weight(70.0)[0] == True, "Valid weight failed"
        assert validate_weight(500.0)[0] == False, "Invalid weight passed"
        
        # Test height
        assert validate_height(175.0)[0] == True, "Valid height failed"
        assert validate_height(300.0)[0] == False, "Invalid height passed"
        
        # Test SpO2
        assert validate_spo2(98)[0] == True, "Valid SpO2 failed"
        assert validate_spo2(150)[0] == False, "Invalid SpO2 passed"
        
        # Test BMI calculation
        bmi = calculate_bmi(70.0, 175.0)
        assert bmi is not None, "BMI calculation failed"
        assert 22.0 < bmi < 23.5, f"BMI value incorrect: {bmi}"
        
        # Test BMI category
        category = get_bmi_category(22.9)
        assert category == "Normal", f"BMI category incorrect: {category}"
        
        print("✅ All validators working correctly")
        return True
    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_id_generator():
    """Test unique ID generation."""
    print("\nTesting ID generator...")
    try:
        from database import DatabaseManager, init_database
        from utils import generate_unique_id, validate_unique_id_format
        
        # Initialize database
        init_database("test_id.db")
        db = DatabaseManager("test_id.db")
        
        # Generate IDs
        id1 = generate_unique_id(db)
        assert validate_unique_id_format(id1), f"Invalid ID format: {id1}"
        assert id1.startswith("VH-"), f"ID doesn't start with VH-: {id1}"
        
        # Add resident and generate next ID
        from datetime import datetime
        resident_data = {
            'unique_id': id1,
            'name': 'Test',
            'age': None,
            'gender': None,
            'address': None,
            'phone': None,
            'village_area': None,
            'photo_path': None,
            'registration_date': datetime.now().strftime('%Y-%m-%d'),
            'registered_by': 'Test'
        }
        db.add_resident(resident_data)
        
        id2 = generate_unique_id(db)
        assert id2 != id1, "IDs should be unique"
        assert validate_unique_id_format(id2), f"Invalid ID format: {id2}"
        
        print(f"✅ ID generation working: {id1}, {id2}")
        
        # Cleanup
        import os
        os.remove("test_id.db")
        
        return True
    except Exception as e:
        print(f"❌ ID generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Village Health Tracking System - Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Database", test_database()))
    results.append(("Validators", test_validators()))
    results.append(("ID Generator", test_id_generator()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")
    
    all_passed = all(result for _, result in results)
    
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("The system is ready for deployment.")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please fix the issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
