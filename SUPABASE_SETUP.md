# Supabase Migration Guide

This guide will help you migrate the Village Health Tracking System from SQLite to Supabase.

## Prerequisites

1. A Supabase account (free tier available at https://supabase.com)
2. Python 3.8 or higher
3. All required Python packages installed

## Step 1: Create a Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Fill in the project details:
   - Name: `village-health-tracking` (or your preferred name)
   - Database Password: Choose a strong password
   - Region: Select the closest region to your location
4. Wait for the project to be created (takes 1-2 minutes)

## Step 2: Get Your Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Copy the following credentials:
   - **Project URL** (e.g., `https://xxxxxxxxxxxxx.supabase.co`)
   - **Anon/Public Key** (starts with `eyJh...`)

## Step 3: Configure Environment Variables

### Option A: Using Environment Variables (.env file)

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-key-here
   SUPABASE_BUCKET_NAME=resident-photos
   ```

3. **Important:** Never commit the `.env` file to version control!

### Option B: Using Streamlit Secrets (Recommended for Streamlit Cloud)

1. Create `.streamlit/secrets.toml` file:
   ```bash
   mkdir -p .streamlit
   nano .streamlit/secrets.toml
   ```

2. Add your credentials:
   ```toml
   SUPABASE_URL = "https://your-project-id.supabase.co"
   SUPABASE_KEY = "your-anon-key-here"
   SUPABASE_BUCKET_NAME = "resident-photos"
   ```

3. **Important:** Never commit `secrets.toml` to version control!

## Step 4: Set Up Supabase Database

### New installation (no existing tables)

1. In your Supabase project, go to **SQL Editor**

2. Copy the contents of `supabase_migration.sql` and execute it in the SQL Editor

   OR

   Execute the following command to run the migration:
   ```bash
   python database/schema.py
   ```
   (This will display the SQL that needs to be executed)

3. Verify the tables were created:
   - Go to **Table Editor** in Supabase
   - You should see all the tables listed:
     - residents
     - visits
     - medical_history
     - growth_monitoring
     - maternal_health
     - ncd_followup

### Upgrading an existing Supabase database

If you already ran the v1 migration and need to add the newly collected data points
(Samagra ID, Aadhar number, assessment checklists, BP fields in maternal health),
run the **upgrade script** instead of the full migration:

1. **Back up your data first.** Export your tables from the Supabase **Table Editor**
   (or use the Supabase dashboard's database backup feature) before making schema changes
   on a production instance.

2. In your Supabase project, go to **SQL Editor**

3. Copy the contents of `supabase_migration_v2.sql` and execute it

   This script safely adds only the missing columns using `ADD COLUMN IF NOT EXISTS`,
   so it is **idempotent** (safe to run more than once) and will not affect existing data.

4. Newly added columns per table:

   | Table | New columns |
   |---|---|
   | `residents` | `samagra_id`, `aadhar_no` |
   | `growth_monitoring` | `assessment_data` (JSONB) |
   | `maternal_health` | `bp_systolic`, `bp_diastolic`, `assessment_data` (JSONB) |
   | `ncd_followup` | `assessment_data` (JSONB) |

5. Verify the upgrade by inspecting each table in the **Table Editor** – the new columns should now appear.

## Step 5: Create Storage Bucket for Photos

1. In your Supabase project, go to **Storage**

2. Click "New Bucket"

3. Create a bucket with the following settings:
   - **Name:** `resident-photos`
   - **Public bucket:** Toggle ON (so photos are publicly accessible)
   - Click "Create bucket"

4. (Optional) Set up storage policies if you want to restrict access

## Step 6: Configure Row Level Security (RLS)

The migration script includes basic RLS policies. You may want to customize these based on your authentication setup:

1. Go to **Authentication** → **Policies** in Supabase

2. Review and modify policies for each table as needed

3. For development/testing, you can temporarily disable RLS:
   ```sql
   ALTER TABLE residents DISABLE ROW LEVEL SECURITY;
   -- Repeat for other tables
   ```

   **⚠️ Warning:** Disabling RLS makes your data publicly accessible!

## Step 7: Migrate Existing Data (Optional)

If you have existing data in SQLite, you'll need to export and import it:

1. Export data from SQLite:
   ```python
   import sqlite3
   import pandas as pd
   
   conn = sqlite3.connect('health_tracking.db')
   
   # Export each table
   residents = pd.read_sql_query("SELECT * FROM residents", conn)
   visits = pd.read_sql_query("SELECT * FROM visits", conn)
   medical_history = pd.read_sql_query("SELECT * FROM medical_history", conn)
   
   # Save to CSV
   residents.to_csv('residents.csv', index=False)
   visits.to_csv('visits.csv', index=False)
   medical_history.to_csv('medical_history.csv', index=False)
   
   conn.close()
   ```

2. Import to Supabase:
   - Go to **Table Editor** in Supabase
   - Select a table
   - Click "Insert" → "Import data from CSV"
   - Upload the CSV file

   OR use the Supabase Python client:
   ```python
   from supabase import create_client
   import pandas as pd
   
   supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
   
   # Read CSV
   residents = pd.read_csv('residents.csv')
   
   # Insert in batches
   for _, row in residents.iterrows():
       supabase.table('residents').insert(row.to_dict()).execute()
   ```

## Step 8: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 9: Test the Application

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Log in with your credentials

3. Test the following:
   - Register a new resident
   - Upload a photo (verify it goes to Supabase Storage)
   - Record a visit
   - Try the new health modules:
     - Child Growth Monitoring
     - Maternal Health (ANC/PNC)
     - NCD Followup

## Step 10: Deploy to Streamlit Cloud (Optional)

1. Push your code to GitHub (without .env or secrets.toml)

2. Go to https://share.streamlit.io

3. Connect your GitHub repository

4. Add secrets:
   - Click on your app → Settings → Secrets
   - Add your Supabase credentials in TOML format:
     ```toml
     SUPABASE_URL = "https://your-project-id.supabase.co"
     SUPABASE_KEY = "your-anon-key-here"
     SUPABASE_BUCKET_NAME = "resident-photos"
     ```

5. Deploy!

## Troubleshooting

### Connection Issues

If you get connection errors:

1. Check your credentials are correct
2. Verify your Supabase project is active
3. Check your internet connection
4. Ensure you're using the correct Anon key (not the Service Role key for client-side apps)

### Permission Errors

If you get permission denied errors:

1. Check RLS policies in Supabase
2. Temporarily disable RLS for testing (not recommended for production)
3. Verify your API key has the correct permissions

### Storage Upload Failures

If photo uploads fail:

1. Verify the bucket exists and is named correctly
2. Check the bucket is set to public
3. Verify storage policies allow uploads

### Migration Issues

If tables aren't created:

1. Check for SQL syntax errors in the migration script
2. Verify you're using PostgreSQL-compatible SQL (not SQLite)
3. Check Supabase logs for detailed error messages

## Need Help?

- Supabase Documentation: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
- Python Client Docs: https://supabase.com/docs/reference/python/introduction

## Benefits of Supabase

✅ **Cloud-hosted:** No need to manage your own database server
✅ **Scalable:** Automatically scales with your data
✅ **Real-time:** Built-in real-time subscriptions
✅ **Secure:** Row Level Security and built-in authentication
✅ **Storage:** Integrated file storage for photos
✅ **Free tier:** Generous free tier for small projects
✅ **PostgreSQL:** Full power of PostgreSQL database

## Next Steps

- Set up automated backups in Supabase
- Configure custom authentication (if needed)
- Set up proper RLS policies for production
- Monitor usage in Supabase dashboard
- Explore Supabase features like real-time subscriptions
