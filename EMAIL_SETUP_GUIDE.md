# Email Alert System Setup Guide

## Overview
The infrastructure damage reporting system now includes automated email alerts for high-risk incidents (Risk Level 4-5). When a report with risk level 4 or higher is submitted, an alert email is automatically sent to the configured admin recipients.

## Email Recipients Configured
The following admin emails are configured to receive alerts:
- `dishitavaswani0909@gmail.com`
- `kuhuvilecha74190@gmail.com`
- `ixaaniketwalaj@gmail.com`

## Configuration Steps

### Step 1: Set Up Gmail App Password
Since the system uses Gmail's SMTP server, you need to create an app-specific password:

1. **Enable 2-Factor Authentication** on the Gmail account that will send alerts
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification if not already enabled

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer" (or your platform)
   - Google will generate a 16-character password
   - Copy this password (you'll use it in Step 2)

### Step 2: Configure Environment Variables
Set the following environment variables on your server/deployment platform:

```bash
EMAIL_SENDER=your-gmail-account@gmail.com
EMAIL_PASSWORD=your-16-character-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Example for Render.yaml:**
```yaml
env:
  - key: EMAIL_SENDER
    value: your-gmail-account@gmail.com
  - key: EMAIL_PASSWORD
    value: your-app-password-here
  - key: SMTP_SERVER
    value: smtp.gmail.com
  - key: SMTP_PORT
    value: 587
```

### Step 3: Email Alert Trigger
- High-risk reports (Risk Level ≥ 4) automatically trigger email alerts
- Each admin email receives an identical formatted HTML email
- Email includes:
  - Risk Level (1-5 scale)
  - Category of damage
  - Location
  - Description
  - Reporter name
  - Risk assessment details
  - Timestamp (IST timezone)

## Testing the Email System

### Test 1: Submit a High-Risk Report
1. Go to the app and fill out a report form
2. Upload an image showing clear damage
3. Add a description indicating urgency
4. Submit the report
5. The system will analyze the image with Gemini AI
6. If Gemini assesses it as Risk Level 4 or higher, emails will be sent

### Test 2: Direct API Test (Optional)
```bash
curl -X POST http://localhost:5000/submit-report \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Road Damage",
    "description": "Large pothole in main street",
    "location": "Main St & 5th Ave",
    "image": "base64-image-data-here",
    "reporter_email": "user@example.com",
    "reporter_name": "John Doe"
  }'
```

## Email Format

The alert email includes:
- **Subject**: `ALERT: Risk Level X - [Category] Infrastructure Incident`
- **From**: The configured EMAIL_SENDER
- **To**: All three admin emails (sent individually)
- **Content**: HTML-formatted with:
  - Red alert header
  - Risk level prominently displayed
  - All incident details
  - Timestamp in IST timezone
  - Footer with system identification

## Troubleshooting

### Emails Not Being Sent
1. **Check EMAIL_PASSWORD**: Ensure it's set correctly
   - Verify it's a 16-character app password (not your Gmail password)
   - Check for any typos or spaces

2. **Check EMAIL_SENDER**: Must be a valid Gmail account
   - Verify the account has 2FA enabled
   - Verify the app password was generated for this account

3. **Check Server Logs**: Look for messages like:
   - `"Alert email sent to: recipient@gmail.com"` (success)
   - `"WARNING: EMAIL_PASSWORD not configured"` (credentials missing)
   - `"Error sending alert email:"` (SMTP connection issue)

4. **Verify Gmail Security Settings**:
   - Go to https://myaccount.google.com/security
   - Check "Less secure app access" isn't blocking (for app passwords, this shouldn't matter)
   - Verify "Recent security events" for any blocks

### Risk Level Not High Enough
- Only reports with Risk Level 4 or 5 trigger emails
- Ensure the image clearly shows infrastructure damage
- The description should indicate urgency/severity

### Admin Emails List
If you need to add or remove admin email recipients, update:
1. **[backend/admin_whitelist.json](backend/admin_whitelist.json)** - For admin dashboard access
2. **ALERT_EMAIL_RECIPIENTS** in [backend/app.py](backend/app.py) (line ~128-132) - For alert emails

## Code Integration Points

### Email Configuration [backend/app.py](backend/app.py)
- Lines 118-132: Email settings and recipient list
- Lines 134-189: `send_alert_email()` function

### Email Trigger [backend/app.py](backend/app.py)
- Lines 556-557: Email alert sent when risk_level >= 4 in `submit_report()`

### Admin Whitelist [backend/admin_whitelist.json](backend/admin_whitelist.json)
- Contains the three admin emails for dashboard access control

## Production Deployment Notes

1. **Use Environment Secrets**: On Render, GitHub, or similar platforms:
   - Never commit EMAIL_PASSWORD to version control
   - Use the platform's secret/environment variable management

2. **Monitor Email Delivery**:
   - Check server logs regularly for email errors
   - Consider setting up log aggregation (e.g., Papertrail)

3. **Email Rate Limits**:
   - Gmail free tier allows ~500 emails/day
   - Monitor if you exceed typical usage

4. **Alternative Email Providers**:
   - Can switch to SendGrid, Mailgun, or AWS SES
   - Requires updating SMTP_SERVER, SMTP_PORT, and authentication method

## Future Enhancements

- [ ] Email digest/batch sending (hourly/daily summary)
- [ ] Per-admin alert threshold preferences
- [ ] Email templates for different damage types
- [ ] Unsubscribe option for alerts
- [ ] SMS alerts for critical incidents (Risk Level 5)

---

**System Status**: ✅ Email infrastructure implemented and configured
**Next Step**: Set EMAIL_PASSWORD and EMAIL_SENDER environment variables and test with a high-risk report submission
