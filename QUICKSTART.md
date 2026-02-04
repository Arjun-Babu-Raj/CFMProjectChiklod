# 🚀 Quick Start Guide

Get the Village Health Tracking System up and running in 5 minutes!

## For Local Development

### 1. Clone and Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/Arjun-Babu-Raj/CFMProjectChiklod.git
cd CFMProjectChiklod

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Authentication (1 minute)

```bash
# Copy template
cp config.template.yaml config.yaml

# Edit config.yaml with your credentials
# For testing, use default credentials:
# Username: worker1
# Password: password123
```

### 3. Run the Application (30 seconds)

```bash
# Start the app
streamlit run app.py

# Open browser to http://localhost:8501
```

### 4. First Login (30 seconds)

1. Enter credentials:
   - Username: `worker1`
   - Password: `password123`
2. Click "Login"
3. You're in! 🎉

### 5. Try Core Features (1 minute)

- **Register a Resident**: Click "📝 Register New Resident"
- **Record a Visit**: Click "🏥 Record Visit"
- **View Analytics**: Click "📊 View Analytics"

## For Streamlit Cloud Deployment

### Quick Deploy (5 minutes)

1. **Fork this repository** to your GitHub account

2. **Go to Streamlit Cloud**: https://share.streamlit.io/

3. **Deploy**:
   - Click "New app"
   - Select your forked repository
   - Main file: `app.py`
   - Click "Deploy"

4. **Configure Secrets**:
   - Go to App Settings → Secrets
   - Copy contents from `config.template.yaml`
   - Save

5. **Access Your App**:
   - Visit `https://your-app-name.streamlit.app`
   - Login and start using!

## Test the System

Run the test suite to verify everything works:

```bash
python test_system.py
```

Expected output:
```
✅ ALL TESTS PASSED!
The system is ready for deployment.
```

## Default Credentials

**⚠️ Change these immediately in production!**

- **Username**: worker1, worker2, worker3
- **Password**: password123 (for all)

## Next Steps

1. **Change Passwords**: Generate secure hashed passwords
2. **Add Health Workers**: Edit config.yaml to add more users
3. **Backup Strategy**: Set up regular database backups
4. **Train Users**: Share this guide with health workers
5. **Go Live**: Start registering real residents!

## Need Help?

- **Documentation**: See [README.md](README.md)
- **Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: Create an issue on GitHub

## Common First-Time Issues

### "config.yaml not found"
```bash
cp config.template.yaml config.yaml
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Database locked"
Close other instances of the app and restart.

## Features Overview

- ✅ **Authentication**: Secure login for 20 health workers
- ✅ **Registration**: Auto-generated IDs (VH-2026-0001)
- ✅ **Visit Recording**: Complete vitals tracking
- ✅ **Medical History**: Chronic conditions, medications
- ✅ **Analytics**: Charts and statistics
- ✅ **Search**: Find residents quickly
- ✅ **Export**: Download data as CSV/Excel
- ✅ **Photos**: Upload and compress images
- ✅ **Mobile-Friendly**: Works on phones

## Quick Tips

💡 **IDs are auto-generated**: No need to enter manually
💡 **Photos are compressed**: Saves storage space
💡 **BMI is calculated**: Just enter weight and height
💡 **Search is fuzzy**: Partial names work
💡 **Export anytime**: All data is exportable

---

**Ready to go!** Start helping your community! 🏥💚
