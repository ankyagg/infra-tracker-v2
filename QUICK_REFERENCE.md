# Quick Reference: Email Alert System

## 🎯 What Was Done
Added automated email alerts to send high-risk infrastructure incident notifications to three admin users when reports are submitted with Risk Level 4 or 5.

## 📧 Admin Email Recipients (Configured)
- ✅ dishitavaswani0909@gmail.com
- ✅ kuhuvilecha74190@gmail.com  
- ✅ ixaaniketwalaj@gmail.com

Each receives identical alert emails for Risk Level 4-5 incidents.

## ⚙️ Required Setup (Before Testing)

### Step 1: Create Gmail App Password
1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication
3. Go to https://myaccount.google.com/apppasswords
4. Select Mail + your device
5. Copy the 16-character password

### Step 2: Set Environment Variables
Add these to your deployment (Render, GitHub, etc.):

```
EMAIL_SENDER = your-gmail@gmail.com
EMAIL_PASSWORD = xxxx-xxxx-xxxx-xxxx
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
```

## 🧪 How to Test

1. **Start the server:**
   ```bash
   cd backend
   python app.py
   ```

2. **Submit a report:**
   - Go to the web app
   - Fill out report with damage image
   - Submit

3. **Check Gemini analysis:**
   - If Risk Level ≥ 4 → Email should be sent
   - Check server console: `Alert email sent to: ...`

4. **Verify:**
   - Check all 3 admin email inboxes
   - Each should receive the formatted alert

## 📍 Code Locations

| What | File | Lines |
|------|------|-------|
| Email config | backend/app.py | 118-132 |
| Send function | backend/app.py | 134-189 |
| Email trigger | backend/app.py | 556-557 |
| Admin emails | backend/admin_whitelist.json | - |
| Setup guide | EMAIL_SETUP_GUIDE.md | - |

## ✅ Current Status

```
Email Infrastructure:     ✅ Implemented
Admin Recipients:         ✅ Configured (3 emails)
Trigger Logic:           ✅ Integrated (Risk ≥ 4)
Report Capture:          ✅ Working (reporter info stored)
SMTP Configuration:      ✅ Ready (Gmail SMTP)
─────────────────────────────────────────
Gmail Credentials:       ⏳ Needs Setup
Email Password:          ⏳ Needs Configuration
Testing:                 ⏳ Ready When Credentials Set
```

## 🚀 To Enable Emails

1. Get Gmail account ready with 2FA
2. Generate app password at apppasswords
3. Set EMAIL_SENDER and EMAIL_PASSWORD environment variables
4. Restart server
5. Submit high-risk report to test

## 📧 What Gets Sent

When a Risk Level 4-5 report is submitted:

- **To:** All 3 admin emails (individually)
- **Subject:** `ALERT: Risk Level X - [Category] Infrastructure Incident`
- **Format:** HTML with styling
- **Content:** 
  - Risk level (1-5)
  - Category & location
  - Description & reporter
  - Full risk assessment
  - Timestamp (IST)

## ⚡ Key Features

✅ Multiple recipients (all 3 admins get the email)
✅ HTML formatted email with styling
✅ Complete incident details included
✅ Automatic triggering (no manual setup needed)
✅ Error handling (graceful if creds missing)
✅ Extensible (easy to add more recipients)

## 📋 Checklist for Deployment

- [ ] Create Gmail app password
- [ ] Set EMAIL_SENDER environment variable
- [ ] Set EMAIL_PASSWORD environment variable  
- [ ] Verify SMTP_SERVER = smtp.gmail.com
- [ ] Verify SMTP_PORT = 587
- [ ] Restart server/redeploy
- [ ] Test with high-risk report submission
- [ ] Verify emails received by all 3 admins
- [ ] Document in production notes

## 🆘 Troubleshooting

**Emails not received?**
- ✓ Check EMAIL_PASSWORD is set correctly (16 chars)
- ✓ Verify EMAIL_SENDER account has 2FA
- ✓ Check server logs for "Alert email sent to"
- ✓ Check spam/junk folder in admin emails

**Risk Level too low?**
- ✓ Only Level 4-5 trigger emails
- ✓ Ensure image shows clear damage
- ✓ Add urgency keywords to description

**Not triggering at all?**
- ✓ Check Gemini is configured
- ✓ Check risk_assessment is returned (not null)
- ✓ Check server console for errors

---

**Questions?** See [EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md) for detailed documentation.
