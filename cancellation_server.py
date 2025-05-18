import sqlite3
from mcp.server.fastmcp import FastMCP
from typing import Dict
import os

# Initialize FastMCP
mcp = FastMCP("FlightCancellation")

@mcp.tool()
def cancel_flight_booking(booking_id: int) -> Dict:
    """
    Cancel a flight booking by removing it from the database.
    
    Args:
        booking_id: The ID of the booking to cancel
    
    Returns:
        Dictionary containing cancellation status
    """
    try:
        # Connect to the database
        conn = sqlite3.connect('data/flights.db')
        cursor = conn.cursor()
        
        # Delete the booking
        cursor.execute('DELETE FROM bookings WHERE booking_id = ?', (booking_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return {"error": "Booking not found"}
        
        # Commit and close
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Booking {booking_id} has been cancelled successfully"
        }
    
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.close()
        return {"error": f"Cancellation failed: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport="stdio") 