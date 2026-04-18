"""
Smile Dental & Implant Clinic - Flask Backend
Handles booking submissions, SMS notifications, and database management
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta

from functools import wraps
import logging

from database import init_db, save_booking
from sms import send_sms_notification


# Initialize Flask app
app = Flask(__name__)

# Configure CORS - allow all origins for local testing
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "max_age": 3600
    }
})

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# ─── RATE LIMITING ───
# Store IP request counts in memory (in production, use Redis)
request_counts = {}

def rate_limit(max_requests=5, window_seconds=3600):
    """Decorator to rate limit requests by IP address"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            now = datetime.now()
            
            # Clean old entries
            if client_ip in request_counts:
                request_counts[client_ip] = [
                    ts for ts in request_counts[client_ip]
                    if (now - ts).total_seconds() < window_seconds
                ]
            else:
                request_counts[client_ip] = []
            
            # Check rate limit
            if len(request_counts[client_ip]) >= max_requests:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return jsonify({
                    'success': False,
                    'error': 'Too many booking attempts. Please try again in an hour.'
                }), 429
            
            # Record this request
            request_counts[client_ip].append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ─── INPUT VALIDATION ───
def validate_booking_data(data):
    """Validate booking form data"""
    errors = []
    
    # Name validation
    name = data.get('name', '').strip()
    if not name or len(name) < 2:
        errors.append('Name must be at least 2 characters')
    if len(name) > 100:
        errors.append('Name is too long')
    
    # Phone validation
    phone = data.get('phone', '').strip()
    phone_digits = ''.join(c for c in phone if c.isdigit())
    if len(phone_digits) < 10:
        errors.append('Phone number must be at least 10 digits')
    if len(phone_digits) > 15:
        errors.append('Phone number is invalid')
    
    # Service validation
    service = data.get('service', '').strip()
    if not service:
        errors.append('Service is required')
    valid_services = [
        'Dental Implants', 'Teeth Whitening', 'Braces Treatment', 'Root Canal',
        'Dental Check-Up', 'Veneers & Crowns', 'Teeth Cleaning', 'Oral Surgery',
        'Cosmetic Procedure', 'Paediatric Dentistry', 'Mouth Guards', 'Ortho Treatment',
        'Dentures & Bridges', 'Extraction', 'Fillings & Sealants', 'Gum Surgery',
        'X-Ray Imaging', 'Wisdom Tooth Removal'
    ]
    if service not in valid_services:
        errors.append('Invalid service selected')
    
    # Date validation
    try:
        date_str = data.get('date', '')
        booking_date = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if booking_date.date() < today.date():
            errors.append('Date cannot be in the past')
    except ValueError:
        errors.append('Invalid date format')
    
    # Time validation
    time_str = data.get('time', '').strip()
    if not time_str:
        errors.append('Time is required')
    valid_times = [
        '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM',
        '2:00 PM', '2:30 PM', '3:00 PM', '3:30 PM', '4:00 PM', '4:30 PM',
        '5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM', '7:30 PM'
    ]
    if time_str not in valid_times:
        errors.append('Invalid time slot')
    
    # Message validation (optional)
    message = data.get('message', '').strip()
    if len(message) > 500:
        errors.append('Message is too long (max 500 characters)')
    
    return errors


# ─── API ENDPOINTS ───
@app.route('/')
def serve_html():
    return send_from_directory('.' , 'smile-dental.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'smile-dental-backend'}), 200


@app.route('/api/booking', methods=['POST', 'OPTIONS'])
@app.route('/api/book', methods=['POST', 'OPTIONS'])
@rate_limit(max_requests=5, window_seconds=3600)
def submit_booking():
    """
    Receive booking form data, validate, save to DB, and send SMS
    Expected JSON payload:
    {
        "name": "Patient Name",
        "phone": "+91 XXXXX XXXXX",
        "service": "Dental Implants",
        "date": "2025-04-20",
        "time": "10:00 AM",
        "message": "Optional message"
    }
    """
    try:
        # Get JSON data
        data = request.get_json(force=True, silent=True)
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'invalid JSON '
            }), 400
        
        # Validate input
        validation_errors = validate_booking_data(data)
        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'details': validation_errors
            }), 422
        
        # Clean phone number
        phone = ''.join(c for c in data.get('phone', '') if c.isdigit())
        
        # Save to database
        booking = {
            'name': data.get('name', '').strip(),
            'phone': phone,
            'service': data.get('service', '').strip(),
            'date': data.get('date', ''),
            'time': data.get('time', '').strip(),
            'message': data.get('message', '').strip()
        }
        
        booking_id = save_booking(booking)
        logger.info(f"Booking saved: ID {booking_id}, Phone: {phone}, Service: {booking['service']}")
        
        # Send SMS to clinic owner (optional - skipped if no Twilio credentials)
        try:
            sms_result = send_sms_notification(booking)
            if not sms_result['success']:
                logger.warning(f"SMS skipped for booking {booking_id}: {sms_result.get('error','no credentials')}")
        except Exception as sms_err:
            logger.warning(f"SMS skipped (Twilio not configured): {sms_err}")
        
        return jsonify({
            'success': True,
            'message': 'Appointment booked successfully',
            'booking_id': booking_id,
            'reminder': 'We will call you within 24 hours to confirm.'
        }), 201
    
    except Exception as e:
        logger.error(f"Booking submission error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Server error. Please try again later.'
        }), 500


# ─── ERROR HANDLERS ───

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500


# ─── RUN APPLICATION ───

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )
