"""
Database schema initialization for Village Health Tracking System.
Creates PostgreSQL/Supabase tables for residents, visits, medical history, and new health modules.
"""

from typing import Optional
from supabase import create_client, Client
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_supabase_client() -> Client:
    """Get Supabase client."""
    try:
        supabase_url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
        supabase_key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
    except (AttributeError, KeyError):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase credentials not found.")
    
    return create_client(supabase_url, supabase_key)


def init_database() -> None:
    """
    Initialize the database with all required tables.
    Note: For Supabase, tables should be created via SQL editor or migrations.
    This function provides the SQL for reference.
    """
    sql_schema = """
    -- Create residents table
    CREATE TABLE IF NOT EXISTS residents (
        unique_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        address TEXT,
        phone TEXT,
        village_area TEXT,
        photo_path TEXT,
        registration_date TEXT,
        registered_by TEXT,
        samagra_id TEXT,
        aadhar_no TEXT
    );
    
    -- Create visits table
    CREATE TABLE IF NOT EXISTS visits (
        visit_id SERIAL PRIMARY KEY,
        resident_id TEXT REFERENCES residents(unique_id),
        visit_date TEXT,
        visit_time TEXT,
        health_worker TEXT,
        bp_systolic INTEGER,
        bp_diastolic INTEGER,
        temperature REAL,
        pulse INTEGER,
        weight REAL,
        height REAL,
        bmi REAL,
        spo2 INTEGER,
        complaints TEXT,
        observations TEXT,
        photo_paths TEXT
    );
    
    -- Create medical_history table
    CREATE TABLE IF NOT EXISTS medical_history (
        history_id SERIAL PRIMARY KEY,
        resident_id TEXT REFERENCES residents(unique_id),
        chronic_conditions TEXT,
        past_diagnoses TEXT,
        current_medications TEXT,
        allergies TEXT,
        family_history TEXT,
        notes TEXT,
        last_updated TEXT,
        updated_by TEXT
    );
    
    -- Create growth_monitoring table (PHASE 2)
    CREATE TABLE IF NOT EXISTS growth_monitoring (
        id SERIAL PRIMARY KEY,
        resident_id TEXT REFERENCES residents(unique_id),
        record_date TEXT NOT NULL,
        age_months INTEGER,
        weight_kg REAL,
        height_cm REAL,
        muac_cm REAL,
        head_circumference_cm REAL,
        z_score_weight_age REAL,
        notes TEXT,
        assessment_data JSONB
    );
    
    -- Create maternal_health table (PHASE 2)
    CREATE TABLE IF NOT EXISTS maternal_health (
        id SERIAL PRIMARY KEY,
        resident_id TEXT REFERENCES residents(unique_id),
        pregnancy_id TEXT,
        visit_type TEXT CHECK (visit_type IN ('ANC', 'PNC')),
        visit_date TEXT NOT NULL,
        lmp_date TEXT,
        edd_date TEXT,
        gestational_week INTEGER,
        fundal_height REAL,
        fetal_heart_rate INTEGER,
        urine_albumin TEXT,
        hemoglobin REAL,
        tt_dose INTEGER,
        calcium_iron_status TEXT,
        danger_signs TEXT,
        delivery_outcome TEXT,
        assessment_data JSONB
    );
    
    -- Create ncd_followup table (PHASE 2)
    CREATE TABLE IF NOT EXISTS ncd_followup (
        id SERIAL PRIMARY KEY,
        resident_id TEXT REFERENCES residents(unique_id),
        checkup_date TEXT NOT NULL,
        condition_type TEXT,
        bp_systolic INTEGER,
        bp_diastolic INTEGER,
        fasting_blood_sugar REAL,
        random_blood_sugar REAL,
        medication_adherence TEXT,
        symptoms TEXT,
        referral_needed BOOLEAN,
        assessment_data JSONB
    );
    
    -- Create indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_visits_resident_id ON visits(resident_id);
    CREATE INDEX IF NOT EXISTS idx_visits_date ON visits(visit_date);
    CREATE INDEX IF NOT EXISTS idx_medical_history_resident ON medical_history(resident_id);
    CREATE INDEX IF NOT EXISTS idx_growth_monitoring_resident ON growth_monitoring(resident_id);
    CREATE INDEX IF NOT EXISTS idx_maternal_health_resident ON maternal_health(resident_id);
    CREATE INDEX IF NOT EXISTS idx_ncd_followup_resident ON ncd_followup(resident_id);
    CREATE INDEX IF NOT EXISTS idx_ncd_followup_date ON ncd_followup(checkup_date);
    CREATE INDEX IF NOT EXISTS idx_residents_samagra_id ON residents(samagra_id);
    """
    
    print("=" * 60)
    print("SUPABASE SQL SCHEMA")
    print("=" * 60)
    print(sql_schema)
    print("=" * 60)
    print("\nPlease execute the above SQL in your Supabase SQL Editor")
    print("or use the migration script: supabase_migration.sql")


if __name__ == "__main__":
    # Display schema when run directly
    init_database()
    print("\nSchema generated successfully!")
