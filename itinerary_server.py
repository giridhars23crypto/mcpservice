from mcp.server.fastmcp import FastMCP
import os
import requests
from typing import Dict, List
from fpdf import FPDF
from datetime import datetime

# Initialize FastMCP
mcp = FastMCP("ItineraryPlanner")

def create_simple_pdf(plan: str) -> str:
    """Create a simple PDF file with the itinerary plan."""
    try:
        # Create directory for itineraries if it doesn't exist
        pdf_path = os.path.join("data", "itineraries")
        os.makedirs(pdf_path, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"itinerary_{timestamp}.pdf"
        full_path = os.path.join(pdf_path, filename)
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "", 12)
        
        # Add the plan text
        lines = plan.split('\n')
        for line in lines:
            if line.strip():  # Skip empty lines
                pdf.multi_cell(190, 10, line)
        
        # Save PDF
        pdf.output(full_path)
        return full_path
    
    except Exception as e:
        raise Exception(f"Failed to create PDF: {str(e)}")

@mcp.tool()
def save_itinerary_plan(plan: str) -> Dict:
    """
    Save the itinerary plan as a PDF.
    
    Args:
        plan: The natural language plan created by the LLM
    
    Returns:
        Dictionary containing PDF file path
    """
    try:
        # Create PDF
        pdf_path = create_simple_pdf(plan)

        return {
            "success": True,
            "pdf_path": pdf_path
        }
    
    except Exception as e:
        return {"error": f"Failed to save plan: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport="stdio") 