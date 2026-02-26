-- Supabase Migration v2 – Upgrade Script for Village Health Tracking System
-- Run this in the Supabase SQL Editor ONLY if you have already executed
-- supabase_migration.sql (v1) and need to add the newly collected data points.
-- Safe to run multiple times – each statement uses IF NOT EXISTS / checks first.

-- ============================================================
-- 1. residents: add Samagra ID and Aadhar number fields
-- ============================================================
ALTER TABLE residents
    ADD COLUMN IF NOT EXISTS samagra_id TEXT;

ALTER TABLE residents
    ADD COLUMN IF NOT EXISTS aadhar_no TEXT;

-- Index for fast family-lookup by Samagra ID
CREATE INDEX IF NOT EXISTS idx_residents_samagra_id ON residents(samagra_id);

-- ============================================================
-- 2. growth_monitoring: add JSON assessment checklist column
-- ============================================================
ALTER TABLE growth_monitoring
    ADD COLUMN IF NOT EXISTS assessment_data JSONB;

-- ============================================================
-- 3. maternal_health: add BP columns and JSON proforma column
-- ============================================================
ALTER TABLE maternal_health
    ADD COLUMN IF NOT EXISTS bp_systolic INTEGER;

ALTER TABLE maternal_health
    ADD COLUMN IF NOT EXISTS bp_diastolic INTEGER;

ALTER TABLE maternal_health
    ADD COLUMN IF NOT EXISTS assessment_data JSONB;

-- ============================================================
-- 4. ncd_followup: add JSON assessment column
-- ============================================================
ALTER TABLE ncd_followup
    ADD COLUMN IF NOT EXISTS assessment_data JSONB;
