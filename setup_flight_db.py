import sqlite3
import os
from datetime import datetime, timedelta
import random

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect('data/flights.db')
cursor = conn.cursor()

# Create flight_info table
cursor.execute('''
CREATE TABLE IF NOT EXISTS flight_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number TEXT NOT NULL,
    airline TEXT NOT NULL,
    departure_location TEXT NOT NULL,
    arrival_location TEXT NOT NULL,
    departure_date TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    price REAL NOT NULL,
    seats_available INTEGER NOT NULL
)
''')

# Create bookings table
cursor.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    flight_id INTEGER NOT NULL,
    booking_date TEXT NOT NULL,
    payment_amount REAL NOT NULL,
    payment_status TEXT NOT NULL,
    card_last_four TEXT NOT NULL,
    FOREIGN KEY (flight_id) REFERENCES flight_info (id)
)
''')

# Create invoices table
cursor.execute('''
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    invoice_number TEXT NOT NULL,
    invoice_date TEXT NOT NULL,
    filename TEXT NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings (id)
)
''')

# Sample data for flights
cities = [
    "New York", "Los Angeles", "Chicago", "Miami", "San Francisco", 
    "Seattle", "Dallas", "Denver", "Boston", "Atlanta", 
    "London", "Paris", "Tokyo", "Dubai", "Sydney"
]

airlines = [
    "American Airlines", "Delta Air Lines", "United Airlines", 
    "Southwest Airlines", "British Airways", "Air France", 
    "Lufthansa", "Emirates", "Qatar Airways", "Singapore Airlines"
]

# Generate sample flight data for the next 30 days
start_date = datetime.now()
for day in range(30):
    current_date = (start_date + timedelta(days=day)).strftime('%Y-%m-%d')
    
    # Generate flights between different city pairs
    for i in range(len(cities)):
        for j in range(len(cities)):
            if i != j:  # Don't create flights from a city to itself
                # Only create some flights, not all possible combinations
                if random.random() < 0.1:  # 10% chance to create this flight
                    departure_city = cities[i]
                    arrival_city = cities[j]
                    
                    # Generate a flight number
                    airline = random.choice(airlines)
                    airline_code = ''.join([word[0] for word in airline.split()]).upper()
                    flight_number = f"{airline_code}{random.randint(1000, 9999)}"
                    
                    # Generate times
                    departure_hour = random.randint(6, 22)
                    flight_duration = random.randint(1, 10)  # hours
                    arrival_hour = (departure_hour + flight_duration) % 24
                    
                    departure_time = f"{departure_hour:02d}:{random.randint(0, 59):02d}"
                    arrival_time = f"{arrival_hour:02d}:{random.randint(0, 59):02d}"
                    
                    # Generate price and seats
                    price = round(random.uniform(150, 2000), 2)
                    seats = random.randint(0, 200)
                    
                    # Insert the flight
                    cursor.execute('''
                    INSERT INTO flight_info (
                        flight_number, airline, departure_location, arrival_location,
                        departure_date, departure_time, arrival_time, price, seats_available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        flight_number, airline, departure_city, arrival_city,
                        current_date, departure_time, arrival_time, price, seats
                    ))

# Commit changes and close connection
conn.commit()
conn.close()

print("Flight database setup complete with sample data!")
print("Database location: data/flights.db")
print(f"Sample cities: {', '.join(cities[:5])}...")
print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {(start_date + timedelta(days=29)).strftime('%Y-%m-%d')}") 