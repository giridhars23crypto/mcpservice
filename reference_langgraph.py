from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from dotenv import load_dotenv
import asyncio
import os


async def chat_loop(graph, messages):
    """
    Run an interactive chat loop with the user, maintaining conversation history.
    
    Args:
        graph: The compiled LangGraph to use for processing
        messages: Initial list of messages (typically including a system message)
    """
    print("Welcome to the Chat Assistant! Type 'exit' to quit.")
    
    # Chat loop that maintains conversation history
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Assistant: Goodbye!")
            break
        
        # Add user message to history
        messages.append(HumanMessage(content=user_input))
        
        # Invoke graph with current conversation state
        response = await graph.ainvoke({"messages": messages})
        
        # Update messages with the complete conversation history from response
        messages = response["messages"]
        print(messages)
        
        # Display the assistant's response (last message)
        assistant_message = messages[-1]
        print(f"\nAssistant: {assistant_message.content}")
    
    return messages


# Async main function to contain our async code
async def main():
    load_dotenv()
    os.getenv('OPENAI_API_KEY')

    model = init_chat_model("openai:gpt-4o-mini")

    async with MultiServerMCPClient(
            {
                "twilio_sendgrid": {
                    "url": os.getenv('TWILIO_ENDPOINT'),
                    "transport": "sse",
                },
                "flight_search": {
                    "command": "python",
                    "args": [os.getenv('FLIGHT_SEARCH')],
                    "transport": "stdio",
                },
                "invoice_generator": {
                    "command": "python",
                    "args": [os.getenv('INVOICE_GENERATOR')],
                    "transport": "stdio",
                }
            }
    ) as client:

        tools = client.get_tools()

        def call_model(state: MessagesState):
            response = model.bind_tools(tools).invoke(state["messages"])
            return {"messages": state["messages"] + [response]}

        # Build the graph
        builder = StateGraph(MessagesState)
        builder.add_node(call_model)
        builder.add_node(ToolNode(tools))
        builder.add_edge(START, "call_model")
        builder.add_conditional_edges(
            "call_model",
            tools_condition,
        )
        builder.add_edge("tools", "call_model")
        graph = builder.compile()

        # Initialize conversation with a system message
        messages = [
            SystemMessage(
                content="""You are a helpful assistant with access to email, calendar, flight search, and invoice generation tools. 
                        
                        1. Searching flights flow 
                        {   
                            Steps:
                            Help the user find flights by asking for departure city, arrival city, and travel date. 
                            Always use the YYYY-MM-DD format for dates. Available cities include: New York, Los Angeles, Chicago, 
                            Miami, San Francisco, Seattle, Dallas, Denver, Boston, Atlanta, London, Paris, Tokyo, Dubai, Sydney.
                            Once the user provides the details, use the flight search tool to find flights. 
                            After successfully retrieving, send the results from giridhars1@gmail.com to giridhars1@gmail.com using the email tool.
                            No of Tool Calls: 2
                            Tool Calls Sequence: Sequential
                            Tool Call Order: 1. Find Flights, 2. Send Email
                        }
                        2. Booking a flight flow 
                        {   
                            Steps:
                            When a user wants to book a flight, first ask for their customer ID.
                            Then ask for the flight ID of the flight they want to book (This assumes customer knows the flight ID).
                            Next, ask for their credit card information including: 
                              - Credit card number (must be 16 digits)
                              - Expiry date (in MM/YY format)
                              - CVV (3 digits)
                            Use the book_flight tool to complete the booking process.
                            Once booking is successful, you must simultaneously:
                              - Generate an invoice using the generate_invoice tool with the booking details
                              - Send a booking confirmation email from giridhars1@gmail.com to giridhars1@gmail.com with booking details
                            No of Tool Calls: 3
                            Tool Calls Sequence: Sequential and Parallel
                            Tool Call Order: 1. Book Flight, 2. [Generate Invoice and Send Email] in parallel
                            
                            For invoice generation, you need to pass the following parameters:
                              - customer_id from the user input
                              - flight_id from the user input
                              - booking_id from the book_flight response
                              - payment_amount from the book_flight response
                              - card_last_four: the last 4 digits of the credit card number
                        }
                        
                         
                    """)

        ]

        # Run the chat loop
        await chat_loop(graph, messages)


# Run the async function with asyncio
if __name__ == "__main__":
    asyncio.run(main())