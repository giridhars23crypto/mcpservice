import sqlite3
from datetime import datetime
import os
import sys
from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Union, Optional
import re

# Initialize FastMCP
mcp = FastMCP("FlightSearch")

@mcp.tool()
def search_flights(departure_location: str, arrival_location: str, departure_date: str) -> Dict:
    """
    Search for available flights based on departure location, arrival location, and date.
    
    Args:
        departure_location: The city of departure
        arrival_location: The destination city
        departure_date: The departure date in YYYY-MM-DD format (e.g., 2024-05-20)
    
    Returns:
        Dictionary containing either a list of matching flights or an error message
    """
    # Input validation
    if not all([departure_location, arrival_location, departure_date]):
        return {"error": "Missing required parameters"}
    
    try:
        # Validate date format
        datetime.strptime(departure_date, '%Y-%m-%d')
    except ValueError:
        return {"error": "Invalid date format. Please use YYYY-MM-DD format."}
    
    try:
        # Check if database exists
        if not os.path.exists('data/flights.db'):
            return {"error": "Flight database not found. Please run setup_flight_db.py first."}
        
        # Connect to the database
        conn = sqlite3.connect('data/flights.db')
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Query for matching flights
        cursor.execute('''
        SELECT * FROM flight_info
        WHERE departure_location = ? 
        AND arrival_location = ?
        AND departure_date = ?
        AND seats_available > 0
        ORDER BY price ASC
        ''', (departure_location, arrival_location, departure_date))
        
        flights = []
        for row in cursor.fetchall():
            flights.append({
                "flight_number": row['flight_number'],
                "airline": row['airline'],
                "departure_location": row['departure_location'],
                "arrival_location": row['arrival_location'],
                "departure_date": row['departure_date'],
                "departure_time": row['departure_time'],
                "arrival_time": row['arrival_time'],
                "price": row['price'],
                "seats_available": row['seats_available'],
                "flight_id": row['id']
            })
        
        conn.close()
        
        if not flights:
            return {"message": "No flights found matching your criteria."}
        
        return {"flights": flights}
    
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

@mcp.tool()
def book_flight(customer_id: str, flight_id: int, credit_card_number: str, credit_card_expiry: str, credit_card_cvv: str) -> Dict:
    """
    Book a flight for a customer using their provided credit card information.
    
    Args:
        customer_id: The unique identifier for the customer
        flight_id: The ID of the flight to book
        credit_card_number: The customer's credit card number
        credit_card_expiry: The expiry date of the credit card in MM/YY format
        credit_card_cvv: The CVV security code of the credit card
    
    Returns:
        Dictionary containing booking confirmation or error message
    """
    # Input validation
    if not all([customer_id, flight_id, credit_card_number, credit_card_expiry, credit_card_cvv]):
        return {"error": "Missing required parameters"}
    
    # Validate credit card number (basic check - should be 16 digits)
    if not re.match(r'^\d{16}$', credit_card_number):
        return {"error": "Invalid credit card number. Must be 16 digits."}
    
    # Validate expiry date (MM/YY format)
    if not re.match(r'^(0[1-9]|1[0-2])/\d{2}$', credit_card_expiry):
        return {"error": "Invalid expiry date. Must be in MM/YY format."}
    
    # Validate CVV (3 digits)
    if not re.match(r'^\d{3}$', credit_card_cvv):
        return {"error": "Invalid CVV. Must be 3 digits."}
    
    try:
        # Check if database exists
        if not os.path.exists('data/flights.db'):
            return {"error": "Flight database not found. Please run setup_flight_db.py first."}
        
        # Connect to the database
        conn = sqlite3.connect('data/flights.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if flight exists and has available seats
        cursor.execute('''
        SELECT * FROM flight_info
        WHERE id = ? AND seats_available > 0
        ''', (flight_id,))
        
        flight = cursor.fetchone()
        if not flight:
            conn.close()
            return {"error": "Flight not found or no seats available."}
        
        # Get the flight price for payment
        flight_price = flight['price']
        
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Update seats available
        cursor.execute('''
        UPDATE flight_info
        SET seats_available = seats_available - 1
        WHERE id = ?
        ''', (flight_id,))
        
        # Record booking
        booking_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        payment_status = "Completed"  # In a real system, this would depend on payment gateway response
        card_last_four = credit_card_number[-4:]  # Store only last 4 digits for security
        
        cursor.execute('''
        INSERT INTO bookings 
        (customer_id, flight_id, booking_date, payment_amount, payment_status, card_last_four)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (customer_id, flight_id, booking_date, flight_price, payment_status, card_last_four))
        
        # Get the booking ID
        booking_id = cursor.lastrowid
        
        # Commit transaction
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "booking_id": booking_id,
            "message": f"Flight booked successfully! Booking ID: {booking_id}",
            "details": {
                "flight_number": flight['flight_number'],
                "airline": flight['airline'],
                "departure": flight['departure_location'],
                "destination": flight['arrival_location'],
                "date": flight['departure_date'],
                "departure_time": flight['departure_time'],
                "payment_amount": flight_price,
                "payment_status": payment_status
            }
        }
    
    except Exception as e:
        # Rollback in case of error
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        return {"error": f"Booking failed: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport="stdio") 