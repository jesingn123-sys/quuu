g#!/bin/bash
# SMILE DENTAL BOOKING SYSTEM - QUICK SETUP SCRIPT
# Run this script to set up the backend locally

echo "=========================================="
echo "Smile Dental Backend - Setup Script"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Navigate to backend folder
cd backend 2>/dev/null || mkdir -p backend && cd backend

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file from template
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env file and add your Twilio credentials:"
    echo "   - TWILIO_ACCOUNT_SID"
    echo "   - TWILIO_AUTH_TOKEN"
    echo "   - TWILIO_PHONE_NUMBER"
    echo "   - CLINIC_OWNER_PHONE"
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your Twilio credentials"
echo "2. Run: python app.py"
echo "3. Backend will start at http://localhost:5000"
echo ""
echo "If frontend is at http://localhost:3000,"
echo "it will automatically connect to the backend."
echo ""
echo "=========================================="
