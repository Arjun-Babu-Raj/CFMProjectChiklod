# ✅ Pre-Deployment Checklist

Use this checklist before deploying to production.

## Security

- [ ] All default passwords changed in `config.yaml`
- [ ] Cookie key changed to a random string
- [ ] `config.yaml` is in `.gitignore`
- [ ] No sensitive data committed to repository
- [ ] Test authentication with new credentials
- [ ] XSRF protection enabled (check `.streamlit/config.toml`)

## Configuration

- [ ] `config.yaml` created from `config.template.yaml`
- [ ] All health worker accounts configured
- [ ] Email addresses are correct
- [ ] Names are correct
- [ ] Cookie expiry days set appropriately (default: 30)

## Testing

- [ ] Run `python test_system.py` - all tests pass
- [ ] Test resident registration
- [ ] Test visit recording
- [ ] Test medical history
- [ ] Test data export
- [ ] Test search functionality
- [ ] Test analytics dashboard
- [ ] Test on mobile device
- [ ] Test with multiple users

## Database

- [ ] Database initializes correctly
- [ ] Sample data can be added
- [ ] Queries execute without errors
- [ ] Backup strategy in place
- [ ] Understand data persistence on deployment platform

## Documentation

- [ ] README.md reviewed
- [ ] DEPLOYMENT.md reviewed
- [ ] QUICKSTART.md reviewed
- [ ] All instructions are clear
- [ ] Contact information updated

## Deployment Platform

### For Streamlit Community Cloud:

- [ ] GitHub repository is accessible
- [ ] Branch selected correctly (usually `main`)
- [ ] Main file path is `app.py`
- [ ] Secrets configured (if using secrets approach)
- [ ] App deployed successfully
- [ ] No errors in deployment logs
- [ ] App accessible at public URL

### For Local/Self-Hosted:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] Port 8501 accessible
- [ ] Firewall configured
- [ ] SSL certificate (if needed)
- [ ] Domain configured (if needed)

## User Training

- [ ] Health workers have login credentials
- [ ] Training session scheduled
- [ ] User guide shared (README.md)
- [ ] Quick start guide shared (QUICKSTART.md)
- [ ] Support contact information provided

## Post-Deployment

- [ ] Monitor app for first 24 hours
- [ ] Check for any errors in logs
- [ ] Verify all features work in production
- [ ] Collect initial user feedback
- [ ] First backup created
- [ ] Document any issues encountered

## Maintenance Plan

- [ ] Backup schedule defined
- [ ] Update procedure documented
- [ ] Support contact established
- [ ] Monitoring plan in place
- [ ] Data export schedule (if needed)

## Optional Enhancements

- [ ] Custom logo/branding
- [ ] Custom domain
- [ ] Additional health worker accounts
- [ ] Customized village areas
- [ ] Additional fields (if needed)
- [ ] Integration with other systems

---

**Sign-off:**

- Deployed by: ________________
- Date: ________________
- Deployment URL: ________________
- Health workers notified: ☐ Yes  ☐ No
- Backup strategy active: ☐ Yes  ☐ No

---

**Notes:**

(Add any deployment-specific notes here)
