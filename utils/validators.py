"""
Input validators for form fields.
Validates phone numbers, age, medical values, etc.
"""

import re
from typing import Optional, Tuple


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number format (10 digits).
    
    Args:
        phone: Phone number string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return True, ""  # Phone is optional
    
    # Remove spaces and dashes
    cleaned = phone.replace(' ', '').replace('-', '')
    
    # Check if 10 digits
    if not re.match(r'^\d{10}$', cleaned):
        return False, "Phone number must be exactly 10 digits"
    
    return True, ""


def validate_age(age: Optional[int]) -> Tuple[bool, str]:
    """
    Validate age is within reasonable range.
    
    Args:
        age: Age value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if age is None:
        return True, ""  # Age is optional
    
    if age < 0 or age > 120:
        return False, "Age must be between 0 and 120"
    
    return True, ""


def validate_blood_pressure(systolic: Optional[int], diastolic: Optional[int]) -> Tuple[bool, str]:
    """
    Validate blood pressure values.
    
    Args:
        systolic: Systolic BP
        diastolic: Diastolic BP
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if systolic is None and diastolic is None:
        return True, ""  # Both optional
    
    if systolic is not None:
        if systolic < 50 or systolic > 250:
            return False, "Systolic BP must be between 50 and 250 mmHg"
    
    if diastolic is not None:
        if diastolic < 30 or diastolic > 150:
            return False, "Diastolic BP must be between 30 and 150 mmHg"
    
    if systolic is not None and diastolic is not None:
        if diastolic >= systolic:
            return False, "Diastolic BP must be less than Systolic BP"
    
    return True, ""


def validate_temperature(temp: Optional[float]) -> Tuple[bool, str]:
    """
    Validate temperature (in Fahrenheit).
    
    Args:
        temp: Temperature value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if temp is None:
        return True, ""  # Optional
    
    if temp < 90.0 or temp > 110.0:
        return False, "Temperature must be between 90°F and 110°F"
    
    return True, ""


def validate_pulse(pulse: Optional[int]) -> Tuple[bool, str]:
    """
    Validate pulse rate.
    
    Args:
        pulse: Pulse rate in bpm
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if pulse is None:
        return True, ""  # Optional
    
    if pulse < 30 or pulse > 200:
        return False, "Pulse rate must be between 30 and 200 bpm"
    
    return True, ""


def validate_weight(weight: Optional[float]) -> Tuple[bool, str]:
    """
    Validate weight (in kg).
    
    Args:
        weight: Weight value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if weight is None:
        return True, ""  # Optional
    
    if weight < 1.0 or weight > 300.0:
        return False, "Weight must be between 1 and 300 kg"
    
    return True, ""


def validate_height(height: Optional[float]) -> Tuple[bool, str]:
    """
    Validate height (in cm).
    
    Args:
        height: Height value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if height is None:
        return True, ""  # Optional
    
    if height < 30.0 or height > 250.0:
        return False, "Height must be between 30 and 250 cm"
    
    return True, ""


def validate_spo2(spo2: Optional[int]) -> Tuple[bool, str]:
    """
    Validate oxygen saturation (SpO2).
    
    Args:
        spo2: SpO2 percentage
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if spo2 is None:
        return True, ""  # Optional
    
    if spo2 < 70 or spo2 > 100:
        return False, "SpO2 must be between 70% and 100%"
    
    return True, ""


def calculate_bmi(weight: Optional[float], height: Optional[float]) -> Optional[float]:
    """
    Calculate BMI from weight and height.
    
    Args:
        weight: Weight in kg
        height: Height in cm
        
    Returns:
        BMI value or None if cannot calculate
    """
    if weight is None or height is None or height == 0:
        return None
    
    # BMI = weight (kg) / (height (m))^2
    height_m = height / 100.0
    bmi = weight / (height_m ** 2)
    
    return round(bmi, 1)


def get_bmi_category(bmi: Optional[float]) -> str:
    """
    Get BMI category.
    
    Args:
        bmi: BMI value
        
    Returns:
        BMI category string
    """
    if bmi is None:
        return "Unknown"
    
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal"
    elif bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"


def validate_required_field(value, field_name: str) -> Tuple[bool, str]:
    """
    Validate that a required field is not empty.
    
    Args:
        value: Field value
        field_name: Name of field for error message
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return False, f"{field_name} is required"
    
    return True, ""
