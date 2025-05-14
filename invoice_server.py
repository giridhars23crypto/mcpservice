import os
import sys
from mcp.server.fastmcp import FastMCP
from typing import Dict
import uuid
from fpdf import FPDF
from datetime import datetime, timedelta
import random

# Initialize FastMCP
mcp = FastMCP("InvoiceGenerator")

@mcp.tool()
def generate_invoice(customer_id: str, flight_id: int, booking_id: int, payment_amount: float, card_last_four: str) -> Dict:
    """
    Generate a simple invoice PDF for a flight booking.
    
    Args:
        customer_id: The unique identifier for the customer
        flight_id: The ID of the flight booked
        booking_id: The ID of the booking
        payment_amount: The amount paid for the booking
        card_last_four: The last four digits of the credit card used
    
    Returns:
        Dictionary containing invoice information or error message
    """
    try:
        # Create directory for invoices if it doesn't exist
        pdf_path = os.path.join("data", "invoices")
        os.makedirs(pdf_path, exist_ok=True)
        
        # Generate invoice number and date
        invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        invoice_date = datetime.now().strftime('%Y-%m-%d')
        
        # Generate random flight details
        flight_number = f"FL{random.randint(1000, 9999)}"
        airlines = ["American Airlines", "Delta Air Lines", "United Airlines", "British Airways"]
        airline = random.choice(airlines)
        
        cities = ["New York", "Los Angeles", "Chicago", "Miami", "London", "Paris", "Tokyo"]
        departure_city = random.choice(cities)
        arrival_city = random.choice([city for city in cities if city != departure_city])
        
        departure_date = (datetime.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        departure_time = f"{random.randint(6, 22):02d}:{random.randint(0, 59):02d}"
        
        # Create the invoice PDF
        invoice_filename = f"invoice_{booking_id}_{invoice_number}.pdf"
        full_path = os.path.join(pdf_path, invoice_filename)
        
        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "FLIGHT BOOKING INVOICE", 0, 1, "C")
        pdf.ln(10)
        
        # Invoice details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Invoice Number:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, invoice_number, 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Invoice Date:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, invoice_date, 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Booking ID:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, str(booking_id), 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Customer ID:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, customer_id, 0, 1)
        
        pdf.ln(10)
        
        # Flight details
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Flight Details", 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Flight Number:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, flight_number, 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Airline:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, airline, 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "From:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, departure_city, 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "To:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, arrival_city, 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Date:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, departure_date, 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Departure Time:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, departure_time, 0, 1)
        
        pdf.ln(10)
        
        # Payment details
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Payment Details", 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Payment Amount:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, f"${payment_amount:.2f}", 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Payment Method:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, f"Credit Card (ending in {card_last_four})", 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Payment Status:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, "Completed", 0, 1)
        
        # Footer
        pdf.ln(20)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(190, 10, "Thank you for your booking!", 0, 1, "C")
        
        # Save PDF
        pdf.output(full_path)
        
        return {
            "success": True,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "filename": invoice_filename,
            "path": full_path,
            "message": f"Invoice generated successfully: {invoice_number}"
        }
        
    except Exception as e:
        return {"error": f"Invoice generation failed: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport="stdio") 