-- Supabase Migration Script for Village Health Tracking System
-- Execute this in Supabase SQL Editor

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
    registered_by TEXT
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

-- PHASE 2: New Health Modules Tables

-- Create growth_monitoring table (For Under-5 Children)
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
    notes TEXT
);

-- Create maternal_health table (ANC/PNC)
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
    delivery_outcome TEXT
);

-- Create ncd_followup table (Diabetes/Hypertension)
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
    referral_needed BOOLEAN
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_visits_resident_id ON visits(resident_id);
CREATE INDEX IF NOT EXISTS idx_visits_date ON visits(visit_date);
CREATE INDEX IF NOT EXISTS idx_medical_history_resident ON medical_history(resident_id);
CREATE INDEX IF NOT EXISTS idx_growth_monitoring_resident ON growth_monitoring(resident_id);
CREATE INDEX IF NOT EXISTS idx_maternal_health_resident ON maternal_health(resident_id);
CREATE INDEX IF NOT EXISTS idx_ncd_followup_resident ON ncd_followup(resident_id);
CREATE INDEX IF NOT EXISTS idx_ncd_followup_date ON ncd_followup(checkup_date);

-- Enable Row Level Security (RLS) for all tables (recommended for Supabase)
ALTER TABLE residents ENABLE ROW LEVEL SECURITY;
ALTER TABLE visits ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE growth_monitoring ENABLE ROW LEVEL SECURITY;
ALTER TABLE maternal_health ENABLE ROW LEVEL SECURITY;
ALTER TABLE ncd_followup ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your authentication setup)
-- Example: Allow authenticated users to read/write all data
CREATE POLICY "Allow authenticated access to residents" ON residents FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated access to visits" ON visits FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated access to medical_history" ON medical_history FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated access to growth_monitoring" ON growth_monitoring FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated access to maternal_health" ON maternal_health FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated access to ncd_followup" ON ncd_followup FOR ALL USING (auth.role() = 'authenticated');

-- Create Storage Bucket for resident photos (run in Supabase Storage UI or via API)
-- You'll need to create a bucket named 'resident-photos' in Supabase Storage
-- And set the bucket to be public or configure appropriate policies
