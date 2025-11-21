"""
Data Seeding Script for Corporate Travel Management System
Populates 180 days of flight and hotel inventory
Uses PostgreSQL (Neon DB or Supabase)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import *
from datetime import datetime, timedelta, time
import random
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PostgreSQL Connection from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set!")

# Configuration
DAYS_TO_GENERATE = 180
START_DATE = datetime.now().date()

# ============================================================================
# REFERENCE DATA
# ============================================================================

AIRPORTS_DATA = [
    # India
    {"code": "BOM", "city": "Mumbai", "country": "India", "timezone": "Asia/Kolkata"},
    {"code": "DEL", "city": "Delhi", "country": "India", "timezone": "Asia/Kolkata"},
    {"code": "BLR", "city": "Bengaluru", "country": "India", "timezone": "Asia/Kolkata"},
    {"code": "HYD", "city": "Hyderabad", "country": "India", "timezone": "Asia/Kolkata"},
    {"code": "MAA", "city": "Chennai", "country": "India", "timezone": "Asia/Kolkata"},
    {"code": "CCU", "city": "Kolkata", "country": "India", "timezone": "Asia/Kolkata"},
    {"code": "PNQ", "city": "Pune", "country": "India", "timezone": "Asia/Kolkata"},
    {"code": "AMD", "city": "Ahmedabad", "country": "India", "timezone": "Asia/Kolkata"},
    {"code": "GOI", "city": "Goa", "country": "India", "timezone": "Asia/Kolkata"},
    {"code": "COK", "city": "Kochi", "country": "India", "timezone": "Asia/Kolkata"},
    {"code": "JAI", "city": "Jaipur", "country": "India", "timezone": "Asia/Kolkata"},
    
    # Asia & Pacific
    {"code": "SIN", "city": "Singapore", "country": "Singapore", "timezone": "Asia/Singapore"},
    {"code": "KUL", "city": "Kuala Lumpur", "country": "Malaysia", "timezone": "Asia/Kuala_Lumpur"},
    {"code": "BKK", "city": "Bangkok", "country": "Thailand", "timezone": "Asia/Bangkok"},
    {"code": "HKG", "city": "Hong Kong", "country": "China", "timezone": "Asia/Hong_Kong"},
    {"code": "HND", "city": "Tokyo", "country": "Japan", "timezone": "Asia/Tokyo"},
    {"code": "SYD", "city": "Sydney", "country": "Australia", "timezone": "Australia/Sydney"},
    {"code": "MEL", "city": "Melbourne", "country": "Australia", "timezone": "Australia/Melbourne"},
    
    # Middle East
    {"code": "DXB", "city": "Dubai", "country": "United Arab Emirates", "timezone": "Asia/Dubai"},
    {"code": "DOH", "city": "Doha", "country": "Qatar", "timezone": "Asia/Qatar"},
    {"code": "AUH", "city": "Abu Dhabi", "country": "United Arab Emirates", "timezone": "Asia/Dubai"},
    
    # Europe
    {"code": "LHR", "city": "London", "country": "United Kingdom", "timezone": "Europe/London"},
    {"code": "CDG", "city": "Paris", "country": "France", "timezone": "Europe/Paris"},
    {"code": "FRA", "city": "Frankfurt", "country": "Germany", "timezone": "Europe/Berlin"},
    {"code": "AMS", "city": "Amsterdam", "country": "Netherlands", "timezone": "Europe/Amsterdam"},
    {"code": "ZRH", "city": "Zurich", "country": "Switzerland", "timezone": "Europe/Zurich"},
    {"code": "FCO", "city": "Rome", "country": "Italy", "timezone": "Europe/Rome"},
    
    # Americas
    {"code": "JFK", "city": "New York", "country": "United States", "timezone": "America/New_York"},
    {"code": "SFO", "city": "San Francisco", "country": "United States", "timezone": "America/Los_Angeles"},
    {"code": "LAX", "city": "Los Angeles", "country": "United States", "timezone": "America/Los_Angeles"},
    {"code": "ORD", "city": "Chicago", "country": "United States", "timezone": "America/Chicago"},
    {"code": "YYZ", "city": "Toronto", "country": "Canada", "timezone": "America/Toronto"},
]

AIRLINES_DATA = [
    {"code": "YA", "name": "Yash Air", "country": "India", "preferred": True, "discount": 18.0},
    {"code": "AI", "name": "Air India Corporate", "country": "India", "preferred": True, "discount": 12.0},
    {"code": "SG", "name": "Singapore Global", "country": "Singapore", "preferred": True, "discount": 14.0},
    {"code": "EK", "name": "Emirates Connect", "country": "United Arab Emirates", "preferred": False, "discount": 10.0},
    {"code": "QR", "name": "Qatar Connect", "country": "Qatar", "preferred": True, "discount": 11.0},
    {"code": "BA", "name": "Britannia Airways", "country": "United Kingdom", "preferred": False, "discount": 8.0},
    {"code": "LH", "name": "Deutsche Hansa", "country": "Germany", "preferred": False, "discount": 8.0},
    {"code": "AF", "name": "Air Francais", "country": "France", "preferred": False, "discount": 7.0},
    {"code": "UA", "name": "United Atlantic", "country": "United States", "preferred": False, "discount": 6.0},
    {"code": "DL", "name": "Delta Skies", "country": "United States", "preferred": True, "discount": 9.0},
    {"code": "JL", "name": "Japan Global", "country": "Japan", "preferred": False, "discount": 5.0},
    {"code": "CX", "name": "Cathay Pacific", "country": "China", "preferred": False, "discount": 6.0},
]

BASE_ROUTES = [
    # Domestic India High Frequency
    {"origin": "BOM", "destination": "DEL", "base_price": 5800, "duration": 140, "airlines": ["YA", "AI"], "frequencies": 8},
    {"origin": "DEL", "destination": "BLR", "base_price": 6200, "duration": 150, "airlines": ["YA", "AI"], "frequencies": 6},
    {"origin": "BLR", "destination": "HYD", "base_price": 4500, "duration": 80, "airlines": ["YA"], "frequencies": 5},
    {"origin": "MAA", "destination": "BOM", "base_price": 5600, "duration": 115, "airlines": ["YA", "AI"], "frequencies": 4},
    {"origin": "CCU", "destination": "BOM", "base_price": 6100, "duration": 165, "airlines": ["YA", "AI"], "frequencies": 4},
    {"origin": "PNQ", "destination": "DEL", "base_price": 5200, "duration": 125, "airlines": ["YA"], "frequencies": 3},
    {"origin": "AMD", "destination": "BOM", "base_price": 4800, "duration": 110, "airlines": ["YA"], "frequencies": 3},
    {"origin": "GOI", "destination": "BLR", "base_price": 4200, "duration": 70, "airlines": ["YA"], "frequencies": 3},
    {"origin": "COK", "destination": "DEL", "base_price": 7500, "duration": 190, "airlines": ["YA"], "frequencies": 2},
    {"origin": "JAI", "destination": "BOM", "base_price": 4900, "duration": 105, "airlines": ["YA"], "frequencies": 2},

    # International: Asia/Pacific
    {"origin": "BOM", "destination": "SIN", "base_price": 32000, "duration": 330, "airlines": ["YA", "SG", "EK"], "frequencies": 4},
    {"origin": "DEL", "destination": "BKK", "base_price": 24000, "duration": 240, "airlines": ["YA", "AI"], "frequencies": 3},
    {"origin": "BLR", "destination": "SIN", "base_price": 29500, "duration": 320, "airlines": ["YA", "SG"], "frequencies": 2},
    {"origin": "DEL", "destination": "HND", "base_price": 55000, "duration": 450, "airlines": ["JL", "AI"], "frequencies": 2},
    {"origin": "DEL", "destination": "HKG", "base_price": 38000, "duration": 300, "airlines": ["CX", "AI"], "frequencies": 2},
    {"origin": "SIN", "destination": "SYD", "base_price": 65000, "duration": 480, "airlines": ["SG"], "frequencies": 3},
    {"origin": "HND", "destination": "SYD", "base_price": 78000, "duration": 570, "airlines": ["JL"], "frequencies": 2},

    # International: Middle East (Hubs)
    {"origin": "DEL", "destination": "DXB", "base_price": 26000, "duration": 240, "airlines": ["YA", "EK", "AI"], "frequencies": 5},
    {"origin": "BOM", "destination": "DXB", "base_price": 24000, "duration": 210, "airlines": ["YA", "EK"], "frequencies": 5},
    {"origin": "DEL", "destination": "DOH", "base_price": 28000, "duration": 230, "airlines": ["QR", "AI"], "frequencies": 4},
    {"origin": "HYD", "destination": "AUH", "base_price": 22000, "duration": 220, "airlines": ["EK"], "frequencies": 2},

    # International: Europe
    {"origin": "DEL", "destination": "LHR", "base_price": 65000, "duration": 580, "airlines": ["BA", "AI", "YA"], "frequencies": 4},
    {"origin": "BOM", "destination": "LHR", "base_price": 62000, "duration": 590, "airlines": ["BA", "AI"], "frequencies": 3},
    {"origin": "DEL", "destination": "FRA", "base_price": 54000, "duration": 520, "airlines": ["LH", "AI"], "frequencies": 3},
    {"origin": "BLR", "destination": "FRA", "base_price": 56000, "duration": 540, "airlines": ["LH"], "frequencies": 2},
    {"origin": "DEL", "destination": "CDG", "base_price": 58000, "duration": 560, "airlines": ["AF", "AI"], "frequencies": 2},
    {"origin": "BOM", "destination": "AMS", "base_price": 59000, "duration": 570, "airlines": ["YA"], "frequencies": 2},
    {"origin": "DEL", "destination": "ZRH", "base_price": 61000, "duration": 530, "airlines": ["AI"], "frequencies": 2},

    # International: Americas (Long Haul)
    {"origin": "BOM", "destination": "JFK", "base_price": 89000, "duration": 960, "airlines": ["UA", "AI"], "frequencies": 2},
    {"origin": "DEL", "destination": "JFK", "base_price": 85000, "duration": 920, "airlines": ["AI", "UA"], "frequencies": 2},
    {"origin": "DEL", "destination": "SFO", "base_price": 95000, "duration": 990, "airlines": ["AI", "UA"], "frequencies": 2},
    {"origin": "BLR", "destination": "SFO", "base_price": 105000, "duration": 1050, "airlines": ["AI"], "frequencies": 1},
    {"origin": "DXB", "destination": "JFK", "base_price": 110000, "duration": 850, "airlines": ["EK"], "frequencies": 3},
    {"origin": "DOH", "destination": "LAX", "base_price": 115000, "duration": 980, "airlines": ["QR"], "frequencies": 2},
    {"origin": "LHR", "destination": "JFK", "base_price": 75000, "duration": 480, "airlines": ["BA", "UA", "DL"], "frequencies": 6},
    {"origin": "CDG", "destination": "JFK", "base_price": 72000, "duration": 500, "airlines": ["AF", "DL"], "frequencies": 4},
    {"origin": "HND", "destination": "LAX", "base_price": 82000, "duration": 600, "airlines": ["JL", "UA"], "frequencies": 4},
]

CITIES_DATA = [
    {"city": "Mumbai", "country": "India", "currency": "INR", "tier": 0.6},
    {"city": "Delhi", "country": "India", "currency": "INR", "tier": 0.6},
    {"city": "Bengaluru", "country": "India", "currency": "INR", "tier": 0.6},
    {"city": "Hyderabad", "country": "India", "currency": "INR", "tier": 0.5},
    {"city": "Chennai", "country": "India", "currency": "INR", "tier": 0.5},
    {"city": "Kolkata", "country": "India", "currency": "INR", "tier": 0.5},
    {"city": "Pune", "country": "India", "currency": "INR", "tier": 0.5},
    {"city": "Ahmedabad", "country": "India", "currency": "INR", "tier": 0.4},
    {"city": "Goa", "country": "India", "currency": "INR", "tier": 0.8},
    {"city": "Kochi", "country": "India", "currency": "INR", "tier": 0.5},
    {"city": "Jaipur", "country": "India", "currency": "INR", "tier": 0.5},
    {"city": "Singapore", "country": "Singapore", "currency": "SGD", "tier": 1.8},
    {"city": "Kuala Lumpur", "country": "Malaysia", "currency": "MYR", "tier": 0.7},
    {"city": "Bangkok", "country": "Thailand", "currency": "THB", "tier": 0.8},
    {"city": "Hong Kong", "country": "China", "currency": "HKD", "tier": 1.9},
    {"city": "Tokyo", "country": "Japan", "currency": "JPY", "tier": 2.0},
    {"city": "Sydney", "country": "Australia", "currency": "AUD", "tier": 1.8},
    {"city": "Melbourne", "country": "Australia", "currency": "AUD", "tier": 1.6},
    {"city": "Dubai", "country": "United Arab Emirates", "currency": "AED", "tier": 1.7},
    {"city": "Doha", "country": "Qatar", "currency": "QAR", "tier": 1.6},
    {"city": "Abu Dhabi", "country": "United Arab Emirates", "currency": "AED", "tier": 1.6},
    {"city": "London", "country": "United Kingdom", "currency": "GBP", "tier": 2.2},
    {"city": "Paris", "country": "France", "currency": "EUR", "tier": 2.0},
    {"city": "Frankfurt", "country": "Germany", "currency": "EUR", "tier": 1.6},
    {"city": "Amsterdam", "country": "Netherlands", "currency": "EUR", "tier": 1.8},
    {"city": "Zurich", "country": "Switzerland", "currency": "CHF", "tier": 2.5},
    {"city": "Rome", "country": "Italy", "currency": "EUR", "tier": 1.7},
    {"city": "New York", "country": "United States", "currency": "USD", "tier": 2.5},
    {"city": "San Francisco", "country": "United States", "currency": "USD", "tier": 2.4},
    {"city": "Los Angeles", "country": "United States", "currency": "USD", "tier": 2.2},
    {"city": "Chicago", "country": "United States", "currency": "USD", "tier": 1.9},
    {"city": "Toronto", "country": "Canada", "currency": "CAD", "tier": 1.8},
]

HOTEL_CHAINS = [
    {"name": "Grand Hyatt", "rating": 5, "discount": 15.0, "tags": ["Luxury", "Business"]},
    {"name": "Marriott Marquis", "rating": 5, "discount": 18.0, "tags": ["Luxury", "Business"]},
    {"name": "Hilton Garden", "rating": 4, "discount": 12.0, "tags": ["Business", "Comfort"]},
    {"name": "Sheraton", "rating": 4, "discount": 12.0, "tags": ["Business"]},
    {"name": "Holiday Inn", "rating": 3, "discount": 10.0, "tags": ["Budget", "Family"]},
    {"name": "Novotel", "rating": 4, "discount": 10.0, "tags": ["Business", "Modern"]},
    {"name": "Four Seasons", "rating": 5, "discount": 8.0, "tags": ["Ultra-Luxury"]},
    {"name": "Ibis Styles", "rating": 3, "discount": 5.0, "tags": ["Budget", "Modern"]},
    {"name": "Radisson Blu", "rating": 4, "discount": 14.0, "tags": ["Business", "Airport"]},
    {"name": "Taj Palace", "rating": 5, "discount": 15.0, "tags": ["Heritage", "Luxury"]},
]

GENERIC_SUFFIXES = ["Residency", "Plaza", "Suites", "Inn", "Towers", "Boutique Hotel", "Stay"]

AMENITIES_POOL = [
    "Free WiFi", "Swimming Pool", "Gym", "Spa", "Conference Room", 
    "Airport Shuttle", "Breakfast Included", "Rooftop Bar", "Valet Parking"
]

ROOM_TYPES = [
    {"name": "Standard King", "multiplier": 1.0, "occupancy": 2},
    {"name": "Twin Deluxe", "multiplier": 1.2, "occupancy": 2},
    {"name": "Club Room", "multiplier": 1.6, "occupancy": 2, "amenities": ["Lounge Access"]},
    {"name": "Executive Suite", "multiplier": 2.5, "occupancy": 3},
    {"name": "Presidential Suite", "multiplier": 5.0, "occupancy": 4},
]

# Base hotel prices per night by rating
BASE_HOTEL_PRICES = {
    3: 3000,  # Budget hotels
    4: 6000,  # Mid-range
    5: 12000, # Luxury
}


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database, drop all tables, and recreate them"""
    print("Connecting to PostgreSQL NeonDB...")
    engine = create_engine(DATABASE_URL, echo=False)
    
    print("\n⚠️  WARNING: Dropping all existing tables...")
    print("This will delete all data in the database!")
    print()
    
    # Drop all tables
    try:
        Base.metadata.drop_all(engine)
        print("✓ All tables dropped successfully")
    except Exception as e:
        print(f"⚠️  Could not drop tables (might be first run): {str(e)}")
    
    print("\nRecreating all tables...")
    Base.metadata.create_all(engine)
    print("✓ All tables created successfully")
    
    Session = sessionmaker(bind=engine)
    return Session()


# ============================================================================
# SEEDING FUNCTIONS
# ============================================================================

def seed_airports(session):
    """Seed airports data"""
    print("Seeding airports...")
    for airport_data in AIRPORTS_DATA:
        airport = Airport(**airport_data)
        session.add(airport)
    session.commit()
    print(f"✓ Seeded {len(AIRPORTS_DATA)} airports")


def seed_airlines(session):
    """Seed airlines data"""
    print("Seeding airlines...")
    for airline_data in AIRLINES_DATA:
        airline = Airline(
            code=airline_data["code"],
            name=airline_data["name"],
            country=airline_data["country"],
            is_preferred=airline_data["preferred"],
            corporate_discount=airline_data["discount"]
        )
        session.add(airline)
    session.commit()
    print(f"✓ Seeded {len(AIRLINES_DATA)} airlines")


def seed_cities(session):
    """Seed cities data"""
    print("Seeding cities...")
    for city_data in CITIES_DATA:
        city = City(
            city=city_data["city"],
            country=city_data["country"],
            currency=city_data["currency"],
            tier_multiplier=city_data["tier"]
        )
        session.add(city)
    session.commit()
    print(f"✓ Seeded {len(CITIES_DATA)} cities")


def generate_flight_times():
    """Generate realistic flight departure times"""
    times = []
    # Morning flights (6:00 - 11:00)
    times.extend([time(hour=h, minute=m) for h in range(6, 12) for m in [0, 30]])
    # Afternoon flights (12:00 - 17:00)
    times.extend([time(hour=h, minute=m) for h in range(12, 18) for m in [0, 30]])
    # Evening flights (18:00 - 23:00)
    times.extend([time(hour=h, minute=m) for h in range(18, 24) for m in [0, 30]])
    return times


def seed_flight_inventory(session):
    """Seed 180 days of flight inventory"""
    print(f"Seeding {DAYS_TO_GENERATE} days of flight inventory...")
    
    airlines_map = {airline.code: airline for airline in session.query(Airline).all()}
    airports_map = {airport.code: airport for airport in session.query(Airport).all()}
    
    flight_times = generate_flight_times()
    flight_count = 0
    
    for route in BASE_ROUTES:
        origin_airport = airports_map[route["origin"]]
        dest_airport = airports_map[route["destination"]]
        
        for airline_code in route["airlines"]:
            airline = airlines_map[airline_code]
            
            # Generate flights for each day
            for day_offset in range(DAYS_TO_GENERATE):
                current_date = START_DATE + timedelta(days=day_offset)
                
                # Generate multiple frequencies per day
                for freq_idx in range(route["frequencies"]):
                    departure_time = random.choice(flight_times)
                    
                    # Calculate arrival time
                    duration = route["duration"]
                    departure_datetime = datetime.combine(current_date, departure_time)
                    arrival_datetime = departure_datetime + timedelta(minutes=duration)
                    
                    # Generate flight number
                    flight_number = f"{airline_code}{random.randint(100, 999)}"
                    
                    # Calculate prices with some variation
                    base_price = route["base_price"]
                    price_variation = random.uniform(0.9, 1.2)  # ±20% variation
                    
                    economy_price = base_price * price_variation
                    premium_economy_price = economy_price * 1.5 if random.random() > 0.5 else None
                    business_price = economy_price * 3.5 if random.random() > 0.3 else None
                    first_price = economy_price * 6.0 if random.random() > 0.7 else None
                    
                    flight = FlightInventory(
                        airline_id=airline.id,
                        flight_number=flight_number,
                        origin_code=route["origin"],
                        destination_code=route["destination"],
                        origin_city=origin_airport.city,
                        destination_city=dest_airport.city,
                        departure_date=current_date,
                        departure_time=departure_time,
                        arrival_date=arrival_datetime.date(),
                        arrival_time=arrival_datetime.time(),
                        duration_minutes=duration,
                        economy_price=economy_price,
                        premium_economy_price=premium_economy_price,
                        business_price=business_price,
                        first_price=first_price,
                        is_direct=True,
                        is_available=True
                    )
                    session.add(flight)
                    flight_count += 1
                    
                    # Commit in batches
                    if flight_count % 5000 == 0:
                        session.commit()
                        print(f"  Generated {flight_count} flights...")
    
    session.commit()
    print(f"✓ Seeded {flight_count} flight inventory records")


def seed_hotels(session):
    """Seed hotels in all cities"""
    print("Seeding hotels...")
    
    cities = session.query(City).all()
    hotel_count = 0
    
    for city in cities:
        # Create 3-5 hotels per city
        num_hotels = random.randint(3, 5)
        
        for _ in range(num_hotels):
            chain = random.choice(HOTEL_CHAINS)
            suffix = random.choice(GENERIC_SUFFIXES)
            
            hotel_name = f"{chain['name']} {city.city} {suffix}"
            amenities = random.sample(AMENITIES_POOL, k=random.randint(4, 7))
            
            hotel = Hotel(
                name=hotel_name,
                chain=chain["name"],
                rating=chain["rating"],
                city=city.city,
                country=city.country,
                address=f"{random.randint(1, 999)} Business District, {city.city}",
                city_tier_multiplier=city.tier_multiplier,
                corporate_discount=chain["discount"],
                amenities=amenities,
                tags=chain["tags"],
                is_active=True
            )
            session.add(hotel)
            hotel_count += 1
    
    session.commit()
    print(f"✓ Seeded {hotel_count} hotels")


def seed_hotel_inventory(session):
    """Seed 180 days of hotel room inventory"""
    print(f"Seeding {DAYS_TO_GENERATE} days of hotel room inventory...")
    
    hotels = session.query(Hotel).all()
    room_count = 0
    
    for hotel in hotels:
        base_price = BASE_HOTEL_PRICES[hotel.rating]
        
        # Apply city tier multiplier
        adjusted_price = base_price * hotel.city_tier_multiplier
        
        # Generate inventory for each room type
        for room_type in ROOM_TYPES:
            for day_offset in range(DAYS_TO_GENERATE):
                current_date = START_DATE + timedelta(days=day_offset)
                
                # Calculate room price
                room_base_price = adjusted_price * room_type["multiplier"]
                
                # Apply seasonal variation (weekends slightly more expensive)
                if current_date.weekday() in [4, 5]:  # Friday, Saturday
                    room_base_price *= 1.15
                
                # Apply corporate discount
                discount_amount = room_base_price * (hotel.corporate_discount / 100)
                discounted_price = room_base_price - discount_amount
                
                room_amenities = room_type.get("amenities", [])
                
                room = HotelRoomInventory(
                    hotel_id=hotel.id,
                    room_type=room_type["name"],
                    occupancy=room_type["occupancy"],
                    date=current_date,
                    base_price=room_base_price,
                    discounted_price=discounted_price,
                    is_available=True,
                    room_amenities=room_amenities
                )
                session.add(room)
                room_count += 1
                
                # Commit in batches
                if room_count % 10000 == 0:
                    session.commit()
                    print(f"  Generated {room_count} room inventory records...")
    
    session.commit()
    print(f"✓ Seeded {room_count} hotel room inventory records")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main seeding function"""
    print("=" * 70)
    print("Corporate Travel Management System - Database Seeding")
    print("PostgreSQL NeonDB")
    print("=" * 70)
    print()
    
    try:
        session = init_db()
        print()
        
        # Seed reference data
        seed_airports(session)
        seed_airlines(session)
        seed_cities(session)
        seed_hotels(session)
        
        # Seed inventory (this takes time)
        seed_flight_inventory(session)
        seed_hotel_inventory(session)
        
        print()
        print("=" * 70)
        print("✓ Database seeding completed successfully!")
        print("=" * 70)
        print()
        print("Summary:")
        print(f"  • {len(AIRPORTS_DATA)} airports")
        print(f"  • {len(AIRLINES_DATA)} airlines")
        print(f"  • {len(CITIES_DATA)} cities")
        print(f"  • ~{len(CITIES_DATA) * 4} hotels")
        print(f"  • ~{len(BASE_ROUTES) * DAYS_TO_GENERATE * 3} flight inventory records")
        print(f"  • ~{len(CITIES_DATA) * 4 * len(ROOM_TYPES) * DAYS_TO_GENERATE} hotel room inventory records")
        print()
        
        session.close()
        
    except Exception as e:
        print(f"✗ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
