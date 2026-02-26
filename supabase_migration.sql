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

-- PHASE 3: Under-5 Child Assessment and NCD Proforma Tables

-- Child Assessment Checklist table (comprehensive Under-5 assessment)
CREATE TABLE IF NOT EXISTS child_assessment (
    id SERIAL PRIMARY KEY,
    resident_id TEXT REFERENCES residents(unique_id),
    assessment_date TEXT NOT NULL,
    -- Section I: Identification
    birth_weight_kg REAL,
    birth_order INTEGER,
    mother_name TEXT,
    mobile TEXT,
    village TEXT,
    anganwadi_registered BOOLEAN,
    mcp_card_available BOOLEAN,
    rch_id_available BOOLEAN,
    -- Section II: Growth & Development status
    weight_for_age_status TEXT,
    stunting_status TEXT,
    wasting_status TEXT,
    pedal_edema_absent BOOLEAN,
    developmental_milestones_normal BOOLEAN,
    -- Section III: Nutrition & Prophylaxis
    early_breastfeeding BOOLEAN,
    exclusive_bf_months REAL,
    complementary_feeding BOOLEAN,
    thr_amount TEXT,
    thr_utilized BOOLEAN,
    thr_preparation TEXT,
    thr_acceptance INTEGER,
    vitamin_a_given BOOLEAN,
    ifa_syrup_given BOOLEAN,
    deworming_given BOOLEAN,
    anganwadi_attendance BOOLEAN,
    -- Section IV: Immunization
    imm_bcg BOOLEAN,
    imm_opv0 BOOLEAN,
    imm_hepb_birth BOOLEAN,
    imm_opv1 BOOLEAN,
    imm_penta1 BOOLEAN,
    imm_rota1 BOOLEAN,
    imm_fipv1 BOOLEAN,
    imm_pcv1 BOOLEAN,
    imm_opv2 BOOLEAN,
    imm_penta2 BOOLEAN,
    imm_rota2 BOOLEAN,
    imm_opv3 BOOLEAN,
    imm_penta3 BOOLEAN,
    imm_rota3 BOOLEAN,
    imm_fipv2 BOOLEAN,
    imm_pcv2 BOOLEAN,
    imm_mr1 BOOLEAN,
    imm_je1 BOOLEAN,
    imm_pcv_booster BOOLEAN,
    imm_mr2 BOOLEAN,
    imm_je2 BOOLEAN,
    imm_dpt_booster1 BOOLEAN,
    imm_opv_booster BOOLEAN,
    imm_dpt_booster2 BOOLEAN,
    -- Section IV: Morbidity
    morbidity_last_month BOOLEAN,
    morbidity_types TEXT,
    treatment_location TEXT,
    -- Section V: Action & Counseling
    referral_done BOOLEAN,
    counseling_provided BOOLEAN,
    danger_sign_convulsions BOOLEAN,
    danger_sign_unable_to_feed BOOLEAN,
    danger_sign_vomits_everything BOOLEAN,
    danger_sign_lethargy BOOLEAN,
    danger_sign_fast_breathing BOOLEAN,
    supervisory_feedback TEXT,
    -- Section VI: Media
    photo_url TEXT,
    audio_notes TEXT
);

-- Household Proforma table (NCD house visit)
CREATE TABLE IF NOT EXISTS household_proforma (
    id SERIAL PRIMARY KEY,
    jr_name TEXT,
    visit_date TEXT NOT NULL,
    house_no TEXT,
    head_of_family TEXT,
    contact_number TEXT,
    total_members INTEGER,
    address TEXT,
    gps_coordinate TEXT,
    asha_worker_name TEXT
);

-- Household Members table (up to 10 per household)
CREATE TABLE IF NOT EXISTS household_members (
    id SERIAL PRIMARY KEY,
    household_id INTEGER REFERENCES household_proforma(id),
    sl_no INTEGER,
    member_name TEXT,
    age INTEGER,
    sex TEXT,
    ncd_status TEXT,
    is_pregnant BOOLEAN,
    is_lactating BOOLEAN,
    is_child_under5 BOOLEAN,
    other_category TEXT
);

-- MCH Screening table (per household member)
CREATE TABLE IF NOT EXISTS mch_screening (
    id SERIAL PRIMARY KEY,
    household_id INTEGER REFERENCES household_proforma(id),
    member_sl INTEGER,
    category TEXT,
    registered_in_anganwadi BOOLEAN,
    aw_sector_name TEXT,
    aww_name TEXT,
    aww_mobile TEXT,
    key_issues TEXT
);

-- Extend ncd_followup with NCD Proforma fields
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS household_id INTEGER;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS height_cm REAL;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS weight_kg REAL;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS bmi REAL;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS waist_circumference REAL;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS cbac_risk_score TEXT;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS known_disease TEXT;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS disease_duration TEXT;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS on_treatment BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS tobacco_use BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS tobacco_counseling BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS alcohol_use BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS alcohol_counseling BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS diet_salt_high BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS diet_salt_counseling BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS diet_sugar_high BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS diet_sugar_counseling BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS physically_inactive BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS activity_counseling BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS flag_persistent_cough BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS flag_mouth_ulcer BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS flag_swallowing_difficulty BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS flag_weight_loss BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS flag_fits_stroke BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS medications_detail TEXT;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS missed_days_category TEXT;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS stock_adequate BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS barrier_reason TEXT;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS foot_exam_status TEXT;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS vision_change BOOLEAN;
ALTER TABLE ncd_followup ADD COLUMN IF NOT EXISTS status_color TEXT;

-- Indexes for new tables
CREATE INDEX IF NOT EXISTS idx_child_assessment_resident ON child_assessment(resident_id);
CREATE INDEX IF NOT EXISTS idx_child_assessment_date ON child_assessment(assessment_date);
CREATE INDEX IF NOT EXISTS idx_household_proforma_date ON household_proforma(visit_date);
CREATE INDEX IF NOT EXISTS idx_household_members_household ON household_members(household_id);
CREATE INDEX IF NOT EXISTS idx_mch_screening_household ON mch_screening(household_id);

-- Enable Row Level Security for new tables
ALTER TABLE child_assessment ENABLE ROW LEVEL SECURITY;
ALTER TABLE household_proforma ENABLE ROW LEVEL SECURITY;
ALTER TABLE household_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE mch_screening ENABLE ROW LEVEL SECURITY;

-- RLS Policies for new tables
CREATE POLICY "Allow authenticated access to child_assessment" ON child_assessment FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated access to household_proforma" ON household_proforma FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated access to household_members" ON household_members FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated access to mch_screening" ON mch_screening FOR ALL USING (auth.role() = 'authenticated');
