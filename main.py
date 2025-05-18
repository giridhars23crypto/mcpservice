import os
import asyncio
from dotenv import load_dotenv
from mcp import StdioServerParameters
from agents import (
    Agent,
    HandoffOutputItem,
    ItemHelpers,
    MessageOutputItem,
    Runner,
)
from mcp_helpers import get_tools_openai_stdio, get_tools_openai_sse
from prompts import (
    get_flight_search_prompt,
    get_flight_booking_prompt,
    get_hotel_booking_prompt,
    get_triage_prompt,
    get_itinerary_planner_prompt,
    get_flight_cancellation_prompt
)

# Load environment variables
load_dotenv()

async def main():
    # Set up MCP server parameters
    flight_server_params = StdioServerParameters(
        command="python",
        args=[os.getenv('FLIGHT_SEARCH')],
        env=None
    )
    
    invoice_server_params = StdioServerParameters(
        command="python",
        args=[os.getenv('INVOICE_GENERATOR')],
        env=None
    )
    
    hotel_server_params = StdioServerParameters(
        command="python",
        args=[os.getenv('HOTEL_SERVER')],
        env=None
    )

    itinerary_server_params = StdioServerParameters(
        command="python",
        args=["itinerary_server.py"],
        env=None
    )

    cancellation_server_params = StdioServerParameters(
        command="python",
        args=["cancellation_server.py"],
        env=None
    )
    
    email_server_url = os.getenv('TWILIO_ENDPOINT')
    email_config = {'from': os.getenv('FROM_EMAIL'), 'to': os.getenv('TO_EMAIL')}

    # Get tools for each server
    flight_tools = await get_tools_openai_stdio(flight_server_params)
    invoice_tools = await get_tools_openai_stdio(invoice_server_params)
    hotel_tools = await get_tools_openai_stdio(hotel_server_params)
    email_tools = await get_tools_openai_sse(email_server_url)
    itinerary_tools = await get_tools_openai_stdio(itinerary_server_params)
    cancellation_tools = await get_tools_openai_stdio(cancellation_server_params)

    # Create Flight Search Agent
    search_agent = Agent(
        name="Flight Search Agent",
        handoff_description="A specialized agent that helps users search for flights and sends results via email.",
        instructions=get_flight_search_prompt(email_config),
        tools=flight_tools + email_tools
    )

    # Create Flight Booking Agent
    booking_agent = Agent(
        name="Flight Booking Agent",
        handoff_description="A specialized agent that helps users book flights, generate invoices, and send confirmations.",
        instructions=get_flight_booking_prompt(email_config),
        tools=flight_tools + invoice_tools + email_tools
    )

    # Create Hotel Booking Agent
    hotel_agent = Agent(
        name="Hotel Booking Agent",
        handoff_description="A specialized agent that helps users search and book hotels.",
        instructions=get_hotel_booking_prompt(),
        tools=hotel_tools + email_tools
    )

    # Create Itinerary Planning Agent
    itinerary_agent = Agent(
        name="Itinerary Planning Agent",
        handoff_description="A specialized agent that helps users plan their daily itinerary with tourist attractions.",
        instructions=get_itinerary_planner_prompt(),
        tools=itinerary_tools + email_tools
    )

    # Create Flight Cancellation Agent
    cancellation_agent = Agent(
        name="Flight Cancellation Agent",
        handoff_description="A specialized agent that helps users cancel their flight bookings and process refunds.",
        instructions=get_flight_cancellation_prompt(email_config),
        tools=cancellation_tools + email_tools
    )

    # Create Triage Agent
    triage_agent = Agent(
        name="Triage Agent",
        handoff_description="A triage agent that routes user requests to specialized travel agents.",
        instructions=get_triage_prompt(),
        tools=flight_tools + invoice_tools + email_tools + hotel_tools + itinerary_tools + cancellation_tools,
        handoffs=[search_agent, booking_agent, hotel_agent, itinerary_agent, cancellation_agent]
    )

    # Set up bidirectional handoffs
    search_agent.handoffs.append(triage_agent)
    booking_agent.handoffs.append(triage_agent)
    hotel_agent.handoffs.append(triage_agent)
    itinerary_agent.handoffs.append(triage_agent)
    cancellation_agent.handoffs.append(triage_agent)
    
    # Initialize conversation history
    input_items = []
    current_agent = triage_agent
    print("Welcome to the Travel Booking System! Type 'exit' to quit.")
    
    # Chat loop
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Assistant: Goodbye!")
            break
        
        # Add user input to conversation history
        input_items.append({"content": user_input, "role": "user"})
        
        # Run the current agent
        result = await Runner.run(current_agent, input_items)
        
        # Process the result
        for new_item in result.new_items:
            agent_name = new_item.agent.name
            if isinstance(new_item, MessageOutputItem):
                print(f"\n{agent_name}: {ItemHelpers.text_message_output(new_item)}")
            elif isinstance(new_item, HandoffOutputItem):
                print(f"\nHanded off from {new_item.source_agent.name} to {new_item.target_agent.name}")
                current_agent = new_item.target_agent
        
        # Update conversation history
        input_items = result.to_input_list()

if __name__ == "__main__":
    asyncio.run(main()) 