# Deployment Troubleshooting Guide

## ImportError Issues

If you encounter an `ImportError` in Streamlit Cloud, particularly with the message:
```
ImportError: This app has encountered an error. The original error message is redacted to prevent data leaks.
```

### Common Causes and Solutions

#### 1. **Streamlit Cloud Cache Issue**
Streamlit Cloud may cache an old version of your application.

**Solution:**
- Go to "Manage app" in Streamlit Cloud
- Click "Reboot app" to clear cache and restart
- If that doesn't work, try "Clear cache" then "Reboot app"

#### 2. **Missing Dependencies**
Ensure all dependencies are properly listed in `requirements.txt`.

**Solution:**
- Verify `requirements.txt` is complete and committed
- Run `pip install -r requirements.txt` locally to verify
- Run `python3 check_imports.py` to verify all imports work

#### 3. **Python Path Issues**
In some deployment environments, the Python path may not include the project root.

**Solution:**
- Ensure all packages have `__init__.py` files
- Our `utils/` and `database/` directories already have these

#### 4. **File Not Deployed**
Sometimes git may not track all necessary files.

**Solution:**
- Run `git status` to check for untracked files
- Ensure `utils/ui_components.py` and other utility files are committed
- Check `.gitignore` isn't excluding necessary files

### Verifying Locally

Before deploying, always verify imports work locally:

```bash
# Check all imports
python3 check_imports.py

# Test running the app
streamlit run app.py
```

### For the NCD Followup Page Specifically

The file `pages/10_💊_NCD_Followup.py` imports:
```python
from utils import check_authentication, get_current_user_name, select_resident_widget
```

All these functions are defined and exported correctly:
- `check_authentication` - from `utils/auth.py`
- `get_current_user_name` - from `utils/auth.py`
- `select_resident_widget` - from `utils/ui_components.py`

They are all exported in `utils/__init__.py`.

### Quick Fix Checklist

- [ ] Reboot the Streamlit Cloud app
- [ ] Clear cache in Streamlit Cloud
- [ ] Verify `requirements.txt` is up to date
- [ ] Run `python3 check_imports.py` locally
- [ ] Check git has all files committed
- [ ] Try a forced redeploy (make a minor change and push)

### Still Having Issues?

If the problem persists:
1. Check Streamlit Cloud logs in "Manage app"
2. Look for the specific error message (not redacted)
3. Verify Python version compatibility (3.8+)
4. Ensure no conflicting file names
5. Check that environment variables/secrets are set in Streamlit Cloud

## Environment Variables

The app requires these environment variables (set in Streamlit Cloud Secrets):

```toml
# .streamlit/secrets.toml format
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-key"
SUPABASE_BUCKET_NAME = "resident-photos"
```

See `.env.example` for the complete list.
