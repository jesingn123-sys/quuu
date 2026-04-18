# Smile Dental & Implant Clinic - Phase 2: Backend Setup Guide

## Overview
This is the Python Flask backend for the Smile Dental booking system. It handles:
- Receiving booking form submissions from the frontend
- Server-side validation of all form data
- SQLite database storage of bookings
- SMS notifications to clinic owner via Twilio
- Rate limiting (5 requests per IP per hour)
- CORS security configuration

## Project Structure
```
backend/
├── app.py              # Main Flask application with API endpoints
├── database.py         # SQLite database initialization and CRUD operations
├── sms.py              # Twilio SMS notification handler
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Prerequisites
- Python 3.8+
- pip (Python package manager)
- Twilio account (for SMS notifications)
- Frontend (index.html) running locally or deployed

## Installation & Setup

### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

**Step 1:** Copy the example `.env` file:
```bash
cp .env.example .env
```

**Step 2:** Fill in your actual values in `.env`:
```
FLASK_ENV=production
PORT=5000
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
CLINIC_OWNER_PHONE=+919909016082
```

### 3. Get Twilio Credentials

1. **Sign up for Twilio:**
   - Go to https://www.twilio.com/console
   - Create a free trial account

2. **Get Account Credentials:**
   - Copy your **Account SID** from the dashboard
   - Copy your **Auth Token** from the dashboard

3. **Get or Purchase a Phone Number:**
   - In Twilio Console → Phone Numbers → Manage Numbers
   - Purchase a phone number or use your trial number
   - This is your `TWILIO_PHONE_NUMBER` (used as the "from" number for SMS)

4. **Set Clinic Owner Phone:**
   - Set `CLINIC_OWNER_PHONE` to your clinic's phone number
   - Must include country code: `+919909016082` for India

### 4. Run the Flask Backend

**Development Mode:**
```bash
python app.py
```

The server will start at: `http://localhost:5000`

**Production Mode:**
Update `.env`:
```
FLASK_ENV=production
```

Then use a production WSGI server (see "Deployment" section below).

## API Endpoints

### 1. Health Check
```
GET /api/health
```
Response: `{"status": "healthy", "service": "smile-dental-backend"}`

### 2. Submit Booking
```
POST /api/booking
Content-Type: application/json

{
  "name": "John Doe",
  "phone": "+91 99090 16082",
  "service": "Dental Implants",
  "date": "2025-04-20",
  "time": "10:00 AM",
  "message": "I have sensitivity issues"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Appointment booked successfully",
  "booking_id": 1,
  "reminder": "We will call you within 24 hours to confirm."
}
```

**Error Response (422):**
```json
{
  "success": false,
  "error": "Validation failed",
  "details": [
    "Phone number must be at least 10 digits",
    "Date cannot be in the past"
  ]
}
```

**Rate Limit Response (429):**
```json
{
  "success": false,
  "error": "Too many booking attempts. Please try again in an hour."
}
```

## Validation Rules

### Name
- Minimum 2 characters
- Maximum 100 characters
- Required

### Phone
- At least 10 digits
- Maximum 15 digits
- Required

### Service
- Must be one of predefined services (18 options)
- Required

### Date
- Cannot be today or in the past
- Must be valid date format (YYYY-MM-DD)
- Required

### Time
- Must be one of available clinic hours (10 AM - 8 PM, excluding 1-2 PM lunch)
- Required

### Message
- Optional
- Maximum 500 characters

## Security Features

1. **Server-Side Validation:**
   - All inputs are validated on the backend
   - Invalid data is rejected with detailed error messages

2. **Rate Limiting:**
   - Maximum 5 booking attempts per IP per hour
   - Prevents abuse and spam submissions

3. **CORS Configuration:**
   - Only allows requests from specified frontend origins
   - Configured to prevent cross-site request forgery

4. **Input Sanitization:**
   - Phone numbers are cleaned of non-numeric characters
   - Text fields are trimmed of whitespace

5. **Environment Variables:**
   - Sensitive credentials (Twilio keys) are stored in `.env`
   - Never commit `.env` to version control

## Database Schema

**Bookings Table:**
```sql
CREATE TABLE bookings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  phone TEXT NOT NULL,
  service TEXT NOT NULL,
  date TEXT NOT NULL,
  time TEXT NOT NULL,
  message TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status TEXT DEFAULT 'pending'
)
```

### Indexes:
- `idx_phone`: For fast lookups by phone number
- `idx_date`: For fast lookups by booking date

## Deployment

### Option 1: Heroku (Free/Paid)

1. **Install Heroku CLI:**
   ```bash
   # For Windows, download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Procfile:**
   ```
   echo "web: gunicorn app:app" > Procfile
   ```

3. **Deploy:**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

4. **Set Environment Variables:**
   ```bash
   heroku config:set TWILIO_ACCOUNT_SID=your_sid
   heroku config:set TWILIO_AUTH_TOKEN=your_token
   heroku config:set TWILIO_PHONE_NUMBER=+1234567890
   heroku config:set CLINIC_OWNER_PHONE=+919909016082
   heroku config:set ALLOWED_ORIGINS=https://yourdomain.com
   ```

### Option 2: PythonAnywhere (Free)

1. Sign up at https://www.pythonanywhere.com
2. Upload your backend folder
3. Configure a web app with Flask
4. Set environment variables in the web app settings

### Option 3: AWS EC2

1. Launch an Ubuntu EC2 instance
2. Install Python, pip, and dependencies
3. Use Nginx as reverse proxy
4. Use systemd to run Flask as a service
5. Set up SSL with Let's Encrypt

### Option 4: DigitalOcean App Platform

1. Connect your GitHub repository
2. Create a new app
3. Configure the backend folder as the source
4. Set environment variables in the app settings
5. Deploy automatically from main branch

## Testing the Backend

### Test Health Endpoint:
```bash
curl http://localhost:5000/api/health
```

### Test Booking Submission:
```bash
curl -X POST http://localhost:5000/api/booking \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Patient",
    "phone": "+919909016082",
    "service": "Dental Implants",
    "date": "2025-04-20",
    "time": "10:00 AM",
    "message": "Test booking"
  }'
```

### Test SMS (if Twilio configured):
```python
# Add to app.py for testing
from sms import send_test_sms

@app.route('/api/test-sms', methods=['GET'])
def test_sms():
    result = send_test_sms()
    return jsonify(result)
```

## Monitoring & Logs

- Check `smile_dental_bookings.db` file size to monitor database growth
- Application logs are printed to console (in development)
- Use application logging for production debugging

## Frontend Integration

The frontend HTML has been updated with:
1. Form submission handling via AJAX/Fetch API
2. Dynamic backend URL detection (localhost vs production)
3. Error message display
4. Submission button feedback (disabled state)
5. Network error handling with fallback phone number

## Troubleshooting

### Issue: "Connection Refused" Error
- Ensure Flask backend is running on port 5000
- Check if port 5000 is not blocked by firewall

### Issue: SMS Not Sending
- Verify Twilio credentials in `.env`
- Check Twilio account has enough balance (free tier allows SMS)
- Ensure phone numbers include country code

### Issue: CORS Error
- Add frontend URL to `ALLOWED_ORIGINS` in `.env`
- Restart Flask backend after changing environment variables

### Issue: Database Lock
- Stop Flask backend, delete `smile_dental_bookings.db`
- Run Flask again to recreate database

## Next Steps

1. **Deployment:** Choose a hosting platform above and deploy
2. **Monitoring:** Set up logging and error tracking (Sentry recommended)
3. **Admin Dashboard:** Create an admin panel to view/manage bookings
4. **SMS Confirmations:** Add SMS reminders before scheduled appointments
5. **Booking Availability:** Implement logic to prevent double-booking same time slot
6. **Email Notifications:** Add email confirmations in addition to SMS

## Support

For issues or questions:
- Twilio Docs: https://www.twilio.com/docs
- Flask Docs: https://flask.palletsprojects.com
- CORS Documentation: https://flask-cors.readthedocs.io

---

**Backend Status:** Ready for deployment ✓
