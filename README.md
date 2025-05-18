# Travel Booking System with AI Agents

This project implements a travel booking system using AI agents powered by OpenAI. The system can help users search for flights, book flights, generate invoices, and search for hotels. It uses a chatbot-like interface where different specialized agents handle specific tasks.

## Features

- **Flight Search**: Search for available flights with specific dates and locations
- **Flight Booking**: Book flights with credit card information and receive invoices
- **Hotel Search**: Search for hotels in different cities and check room offers
- **Email Notifications**: Send booking confirmations and search results via email
- **Smart Routing**: Automatic routing to specialized agents based on user requests

## Prerequisites

- Python 3.12.4
- OpenAI API key
- Amadeus API credentials
- SQLite3
- Required Python packages (install via pip):
  - openai
  - mcp
  - fpdf
  - amadeus
  - python-dotenv

## Setup

1. Clone the repository

2. Create a `.env` file in the root directory with the following variables:
```env
OPENAI_API_KEY=your_openai_api_key
TWILIO_ENDPOINT=your_twilio_endpoint
FLIGHT_SEARCH=./flight_mcp_server.py
INVOICE_GENERATOR=./invoice_server.py
AMADEUS_KEY=your_amadeus_key
AMADEUS_SECRET=your_amadeus_secret
HOTEL_SERVER=./hotel_mcp_server.py
FROM_EMAIL=your_from_email
TO_EMAIL=your_to_email
```

3. Initialize the flight database (only needs to be done once):
```bash
python setup_flight_db.py
```

4. Run the application:
```bash
python main.py
```

## Project Structure

- `main.py`: Main application file that sets up agents and handles user interaction
- `mcp_helpers.py`: Helper functions for MCP server operations
- `prompts.py`: System prompts for different agents
- `flight_mcp_server.py`: Flight search and booking server
- `hotel_mcp_server.py`: Hotel search server
- `invoice_server.py`: Invoice generation server

## Sample Queries

Here are some example queries you can try with the system:

### Flight Search
```
"I want to search for flights from New York to London"
"Find me flights to Tokyo for next week"
"What flights are available from Los Angeles to Miami on 2024-05-20?"
```

### Flight Booking
```
"I want to book flight number FL1234"
"Book a flight with my customer ID CUST123"
"Help me book the flight I just searched for"
```

### Hotel Search
```
"Find hotels in New York City"
"Search for hotels in MAA (Chennai)"
"Show me hotel offers in NYC for 2 adults"
```

### General Queries
```
"What services do you offer?"
"Can you help me plan a trip?"
"I need to modify my booking"
```

## Agent Capabilities

1. **Triage Agent**
   - Routes requests to specialized agents
   - Handles general travel-related queries
   - Provides basic information about services

2. **Flight Search Agent**
   - Searches flights between cities
   - Handles date format conversion
   - Sends search results via email

3. **Flight Booking Agent**
   - Processes flight bookings
   - Collects payment information
   - Generates booking invoices
   - Sends confirmation emails

4. **Hotel Booking Agent**
   - Searches hotels by city
   - Checks hotel offers and availability
   - Provides room and price information

## Error Handling

The system includes error handling for:
- Invalid credit card information
- Unavailable flights
- Invalid date formats
- Missing required information
- Database errors

## Notes

- The flight database is initialized with sample data
- Credit card transactions are simulated
- Email functionality requires proper SMTP configuration
- Hotel search uses the Amadeus API for real hotel data

## Contributing

Feel free to submit issues and enhancement requests! 