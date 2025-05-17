from amadeus import Client, ResponseError
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Amadeus client
amadeus = Client(
    client_id=os.getenv('AMADEUS_KEY'),
    client_secret=os.getenv('AMADEUS_SECRET')
)

# Create server
mcp = FastMCP("Hotel Booking Server")

@mcp.tool()
def search_hotels_by_city(city_code: str) -> dict:
    """
    Search for hotels in a given city using Amadeus API.
    
    Args:
        city_code: The IATA city code (e.g., 'MAA' for Chennai, 'NYC' for New York)
    
    Returns:
        Dictionary containing hotel information including name and hotel ID
    """
    try:
        response = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code)
        hotels = response.data
        return {
            "hotels": [
                {
                    "name": hotel["name"],
                    "hotel_id": hotel["hotelId"]
                }
                for hotel in hotels[0:5]
            ]
        }
    except ResponseError as error:
        return {"error": str(error)}

@mcp.tool()
def search_hotel_offers(hotel_id: str, adults: str = "1") -> dict:
    """
    Search for offers in a specific hotel using Amadeus API.
    
    Args:
        hotel_id: The Amadeus hotel ID
        adults: Number of adults (default: "1")
    
    Returns:
        Dictionary containing hotel offers information.
        LLM can format it and provide important details in short and concise manner.
    """
    try:
        response = amadeus.shopping.hotel_offers_search.get(
            hotelIds=hotel_id,
            adults=adults
        )
        return response.data
    except ResponseError as error:
        return {"error": str(error)}

if __name__ == "__main__":
    mcp.run(transport="stdio") 