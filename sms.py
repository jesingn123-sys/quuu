
import os
from dotenv import load_dotenv

import logging
from twilio.rest import Client

# Set up logging to see what's happening in the terminal
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
CLINIC_OWNER_PHONE = os.getenv("CLINIC_OWNER_PHONE")

def send_sms_notification(booking_details):
    """
    Sends an SMS alert to the clinic owner about a new booking.
    Returns a dictionary for app.py to process.
    """
    # 1. Validation check
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return {"success": False, "error": "Twilio credentials missing"}

    try:
        # 2. Initialize the Twilio Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # 3. Create and send the message
        # We format the body clearly for the clinic owner
        message_body = (
            f"SMILE DENTAL ALERT\n"
            f"New Appointment!\n"
            f"Patient: {booking_details.get('name')}\n"
            f"Phone: {booking_details.get('phone')}\n"
            f"Service: {booking_details.get('service')}\n"
            f"Date: {booking_details.get('date')}"
        )

        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=CLINIC_OWNER_PHONE
        )

        # 4. Success Return (This matches what your app.py expects)
        logger.info(f"SMS sent successfully. SID: {message.sid}")
        return {"success": True, "sid": message.sid}

    except Exception as e:
        # 5. Error Return
        logger.error(f"Twilio error: {str(e)}")
        return {"success": False, "error": str(e)}    
