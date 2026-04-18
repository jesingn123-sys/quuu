"""
Database module for Smile Dental booking system
Handles SQLite database initialization and booking operations
"""

import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DATABASE_PATH = os.getenv('DATABASE_PATH', 'smile_dental_bookings.db')


def get_db_connection():
    """Create and return database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with bookings table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
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
    ''')
    
    # Create index on phone for faster lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_phone ON bookings(phone)
    ''')
    
    # Create index on date for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_date ON bookings(date)
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


def save_booking(booking_data):
    """
    Save a new booking to database
    Args:
        booking_data: Dict with keys: name, phone, service, date, time, message
    Returns:
        booking_id: ID of the saved booking
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO bookings (name, phone, service, date, time, message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            booking_data['name'],
            booking_data['phone'],
            booking_data['service'],
            booking_data['date'],
            booking_data['time'],
            booking_data['message']
        ))
        
        conn.commit()
        booking_id = cursor.lastrowid
        logger.info(f"Booking saved to database: ID {booking_id}")
        return booking_id
    
    except sqlite3.Error as e:
        logger.error(f"Database error while saving booking: {str(e)}")
        raise
    
    finally:
        conn.close()


def get_booking(booking_id):
    """
    Retrieve a booking by ID
    Args:
        booking_id: ID of the booking to retrieve
    Returns:
        Dict with booking details or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    finally:
        conn.close()


def get_bookings_by_phone(phone):
    """
    Retrieve all bookings for a phone number
    Args:
        phone: Phone number to search for
    Returns:
        List of booking dicts
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM bookings WHERE phone = ? ORDER BY created_at DESC', (phone,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    finally:
        conn.close()


def get_all_bookings(limit=100, offset=0):
    """
    Retrieve all bookings with pagination
    Args:
        limit: Maximum number of bookings to retrieve
        offset: Number of bookings to skip
    Returns:
        List of booking dicts
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT * FROM bookings 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    finally:
        conn.close()


def update_booking_status(booking_id, status):
    """
    Update the status of a booking
    Args:
        booking_id: ID of the booking
        status: New status (e.g., 'confirmed', 'cancelled', 'completed')
    Returns:
        True if updated, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE bookings 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, booking_id))
        
        conn.commit()
        return cursor.rowcount > 0
    
    except sqlite3.Error as e:
        logger.error(f"Database error while updating booking: {str(e)}")
        return False
    
    finally:
        conn.close()


def get_bookings_by_date(date_str):
    """
    Retrieve all bookings for a specific date
    Args:
        date_str: Date string in YYYY-MM-DD format
    Returns:
        List of booking dicts for that date
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT * FROM bookings 
            WHERE date = ? 
            ORDER BY time
        ''', (date_str,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    finally:
        conn.close()


def get_booking_stats():
    """
    Get statistics about all bookings
    Returns:
        Dict with stats
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) as total FROM bookings')
        total = cursor.fetchone()['total']
        
        cursor.execute('''
            SELECT service, COUNT(*) as count 
            FROM bookings 
            GROUP BY service 
            ORDER BY count DESC
        ''')
        services = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM bookings 
            GROUP BY status
        ''')
        statuses = [dict(row) for row in cursor.fetchall()]
        
        return {
            'total_bookings': total,
            'by_service': services,
            'by_status': statuses
        }
    
    finally:
        conn.close()
