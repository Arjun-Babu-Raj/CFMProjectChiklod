# 🚀 Deployment Guide - Village Health Tracking System

This guide covers deploying the Village Health Tracking System to Streamlit Community Cloud.

## Prerequisites

- GitHub account
- Streamlit Community Cloud account (free at https://streamlit.io/cloud)
- This repository forked or in your GitHub account

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your repository contains:
- ✅ All application files
- ✅ requirements.txt with dependencies
- ✅ config.template.yaml (template file)
- ✅ .gitignore (to exclude config.yaml)
- ✅ .streamlit/config.toml (theme configuration)

### 2. Set Up Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Create New App:**
   - Click "New app" button
   - Select your repository: `Arjun-Babu-Raj/CFMProjectChiklod`
   - Branch: `main` (or your default branch)
   - Main file path: `app.py`
   - Click "Deploy!"

### 3. Configure Secrets (Authentication)

Since `config.yaml` is gitignored, you need to add it as a Streamlit secret:

1. **Go to App Settings:**
   - Click the "⋮" menu in your deployed app
   - Select "Settings"
   - Go to "Secrets" tab

2. **Add Your Config:**
   - Copy the contents of your `config.yaml` file
   - Paste it into the Secrets text area
   - Save

**Example secrets content:**
```toml
# .streamlit/secrets.toml format
credentials.usernames.worker1.email = "worker1@example.com"
credentials.usernames.worker1.name = "Health Worker 1"
credentials.usernames.worker1.password = "$2b$12$..."

credentials.usernames.worker2.email = "worker2@example.com"
credentials.usernames.worker2.name = "Health Worker 2"
credentials.usernames.worker2.password = "$2b$12$..."

cookie.expiry_days = 30
cookie.key = "your_random_key"
cookie.name = "cfm_chiklod_auth"
```

**Alternative: Use config.yaml directly**

If you want to use the config.yaml approach, modify `utils/auth.py` to check for secrets:

```python
def load_config(config_path: str = "config.yaml") -> dict:
    """Load authentication configuration from YAML file or Streamlit secrets."""
    try:
        # First try Streamlit secrets
        if hasattr(st, 'secrets') and 'credentials' in st.secrets:
            config = {
                'credentials': dict(st.secrets['credentials']),
                'cookie': dict(st.secrets['cookie'])
            }
            return config
        
        # Fall back to config file
        with open(config_path) as file:
            config = yaml.load(file, Loader=SafeLoader)
        return config
    except FileNotFoundError:
        st.error(f"Configuration file '{config_path}' not found.")
        st.stop()
```

### 4. Generate Secure Passwords

To create hashed passwords for your health workers:

```python
import streamlit_authenticator as stauth

# Generate password hash
passwords = ['password1', 'password2', 'password3']
hashed_passwords = stauth.Hasher(passwords).generate()

for i, hashed in enumerate(hashed_passwords):
    print(f"Password {i+1}: {hashed}")
```

### 5. Verify Deployment

1. **Check App Status:**
   - Wait for deployment to complete (usually 2-5 minutes)
   - Check logs for any errors

2. **Test Login:**
   - Visit your app URL: `https://your-app-name.streamlit.app`
   - Try logging in with your credentials

3. **Test Core Features:**
   - Register a test resident
   - Record a test visit
   - View analytics
   - Export data

### 6. Custom Domain (Optional)

For a custom domain:

1. **Streamlit Cloud Pro:**
   - Upgrade to Pro plan
   - Configure custom domain in settings

2. **Or use a reverse proxy:**
   - Set up Cloudflare or similar
   - Point to your Streamlit Cloud URL

## Database Persistence

**Important:** Streamlit Cloud has ephemeral file systems. The SQLite database will be reset on app restarts.

### Solutions:

#### Option 1: Use Streamlit Connection (Recommended for Production)

Migrate to a persistent database:
- **PostgreSQL** (free tier: Supabase, ElephantSQL)
- **MySQL** (free tier: PlanetScale)
- **Cloud Storage** (AWS S3, Google Cloud Storage)

#### Option 2: Regular Backups

Set up automatic backups:
1. Add a backup function in your app
2. Use Streamlit Cloud's GitHub integration
3. Store backups in GitHub repository or cloud storage

#### Option 3: Use Streamlit Session State

For small datasets only:
```python
if 'db_data' not in st.session_state:
    st.session_state.db_data = load_from_cloud_storage()
```

## Environment Variables

Set environment variables in Streamlit Cloud:

1. Go to App Settings → Advanced Settings
2. Add environment variables:
   ```
   TZ=Asia/Kolkata
   PYTHONUNBUFFERED=1
   ```

## Performance Optimization

### 1. Enable Caching

Add caching to expensive operations:

```python
@st.cache_data(ttl=600)
def get_all_residents():
    return db.get_all_residents()
```

### 2. Optimize Image Loading

Use lazy loading for images:

```python
@st.cache_data
def load_image(path):
    return Image.open(path)
```

### 3. Database Indexing

Already implemented in `database/schema.py`:
- Index on `resident_id` in visits table
- Index on `visit_date` in visits table

## Monitoring

### 1. Check App Logs

In Streamlit Cloud:
- Go to your app
- Click "⋮" menu → "Logs"
- Monitor for errors

### 2. Usage Analytics

Streamlit Cloud provides:
- Visitor count
- Resource usage
- Error tracking

### 3. Custom Monitoring

Add logging to your app:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Resident registered: {unique_id}")
```

## Security Checklist

Before going live:

- [ ] Change all default passwords
- [ ] Use strong, unique cookie key
- [ ] Enable XSRF protection (already in config.toml)
- [ ] Review .gitignore (config.yaml excluded)
- [ ] Test authentication thoroughly
- [ ] Set up regular database backups
- [ ] Configure HTTPS (automatic on Streamlit Cloud)
- [ ] Review user permissions
- [ ] Test on mobile devices
- [ ] Verify data export security

## Troubleshooting Deployment

### App Won't Start

**Check:**
1. requirements.txt has all dependencies
2. Python version compatibility (3.8+)
3. No syntax errors in code
4. Check deployment logs

**Solution:**
```bash
# Test locally first
streamlit run app.py
```

### Authentication Not Working

**Check:**
1. Secrets are properly configured
2. Password hashes are correct
3. Cookie key is set

**Solution:**
```python
# Verify secrets
import streamlit as st
st.write(st.secrets)  # Remove after testing!
```

### Database Issues

**Check:**
1. Database file permissions
2. SQLite is installed
3. Schema is initialized

**Solution:**
```python
# Force database initialization
from database import init_database
init_database()
```

### Images Not Loading

**Check:**
1. uploaded_photos directory exists
2. File permissions are correct
3. Image paths are relative

**Solution:**
```bash
mkdir -p uploaded_photos
chmod 755 uploaded_photos
```

## Updating the App

### Via GitHub

1. **Push Changes:**
   ```bash
   git add .
   git commit -m "Update message"
   git push
   ```

2. **Streamlit Cloud Auto-deploys:**
   - Changes are detected automatically
   - App restarts with new code
   - Usually takes 1-2 minutes

### Manual Reboot

In Streamlit Cloud:
- Click "⋮" menu → "Reboot app"

## Cost and Limits

### Streamlit Community Cloud (Free)

- **Cost:** $0/month
- **Apps:** Up to 3 public apps
- **Resources:** 1 GB RAM, 1 CPU per app
- **Bandwidth:** 1 GB/month
- **Storage:** Ephemeral (resets on restart)

**Sufficient for:**
- ✅ 1000 residents
- ✅ 10,000+ visits
- ✅ 20 concurrent users
- ✅ Basic analytics

### If You Need More

**Streamlit Cloud Pro:**
- Cost: ~$250/year
- Unlimited apps
- More resources
- Custom domains
- Priority support

**Self-Hosting:**
- Deploy on your own server
- Full control
- Use persistent database

## Backup Strategy

### Manual Backup

1. **Export All Data:**
   - Use the Export Data page
   - Download CSV/Excel files
   - Save to secure location

2. **Database Backup:**
   ```bash
   # Download database file (if accessible)
   scp user@server:/path/health_tracking.db ./backup/
   ```

### Automated Backup (Advanced)

Set up a scheduled backup script:

```python
# backup_scheduler.py
import schedule
import time
from database import DatabaseManager
import pandas as pd

def backup_data():
    db = DatabaseManager()
    
    # Export to CSV
    residents = db.export_residents_to_df()
    visits = db.export_visits_to_df()
    
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    
    residents.to_csv(f'backups/residents_{timestamp}.csv', index=False)
    visits.to_csv(f'backups/visits_{timestamp}.csv', index=False)
    
    print(f"Backup completed: {timestamp}")

# Run daily at 2 AM
schedule.every().day.at("02:00").do(backup_data)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Support and Maintenance

### Regular Maintenance

**Weekly:**
- Check application logs
- Verify all features working
- Review recent data entries

**Monthly:**
- Export complete database backup
- Review user accounts
- Update dependencies if needed

**Quarterly:**
- Review analytics and usage
- Gather user feedback
- Plan feature improvements

### Getting Help

**Resources:**
- Streamlit Documentation: https://docs.streamlit.io/
- Streamlit Forum: https://discuss.streamlit.io/
- GitHub Issues: Report bugs in your repository

**Community Support:**
- Post questions in Streamlit forum
- Check GitHub issues for similar problems
- Contact development team

## Production Checklist

Before going live:

- [ ] All features tested thoroughly
- [ ] Default passwords changed
- [ ] Secrets configured in Streamlit Cloud
- [ ] Database backup strategy in place
- [ ] User training completed
- [ ] Documentation reviewed
- [ ] Mobile responsiveness verified
- [ ] Error handling tested
- [ ] Export functionality verified
- [ ] Analytics working correctly
- [ ] Photos uploading and displaying
- [ ] All health workers can log in
- [ ] Sample data tested and cleared

## Launch Day

1. **Final Checks:**
   - Verify all systems operational
   - Clear any test data
   - Confirm backup strategy active

2. **Announce Launch:**
   - Inform health workers
   - Provide login credentials
   - Share app URL

3. **Monitor Closely:**
   - Watch for errors
   - Respond to user questions
   - Track initial usage

4. **Gather Feedback:**
   - Collect user feedback
   - Note any issues
   - Plan improvements

---

**Congratulations!** Your Village Health Tracking System is now live! 🎉

For questions or issues, refer to the main README.md or create an issue on GitHub.
