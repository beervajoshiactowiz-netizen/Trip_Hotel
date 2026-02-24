import json
import mysql.connector

# Load JSON file
input_file = "trip_hotel_2026-02-23.json"
def load_file(file_name):
    with open(file_name, "rb") as f:
        data = json.loads(f.read().decode())
    return data

data=load_file(input_file)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="actowiz",
    database="flight_db"
)
cursor = conn.cursor()

create_query = """
CREATE TABLE IF NOT EXISTS Trip_Hotel (
    Hotel_ID BIGINT,
    Hotel_Name VARCHAR(255),
    Phone_No BIGINT,
    Description TEXT,
    Open_Year INT,
    Address VARCHAR(255),
    City VARCHAR(100),
    `State` VARCHAR(100),
    Country VARCHAR(100),
    Pincode INT,
    Room_ID BIGINT,
    Room_Name VARCHAR(255),
    Room_Facilities JSON,
    Room_Images JSON,
    NearbyLocations JSON,
    Policy JSON,
    HotelFacilities JSON,
    Reviews JSON,
    Rating_Cleanliness FLOAT,
    Rating_Amenities FLOAT,
    Rating_Location FLOAT,
    Rating_Service FLOAT,
    Recommendation JSON
);
"""
cursor.execute(create_query)

# Hotel-level info
hotel_id = data.get("Hotel_ID")
hotel_name = data.get("Name")
phone_no = data.get("Phone_No")
description = data.get("Description")
open_year = data.get("Open_Year")

location = data.get("location", {})
address = location.get("Address")
city = location.get("City")
state = location.get("State")
country = location.get("Country")
pincode = location.get("Pincode")

nearby_locations = json.dumps(data.get("Nearby_location", []))
policy = json.dumps(data.get("Policy", []))
hotel_facilities = json.dumps(data.get("Hotel_Facilities", {}))
reviews = json.dumps(data.get("Reviews", []))
ratings = json.dumps(data.get("Ratings", []))
recommendation = json.dumps(data.get("Recommendation", {}))

ratings = data.get("Ratings", [])
rating_cleanliness = rating_amenities = rating_location = rating_service = None

for r in ratings:
    category = r.get("Category", "").lower()
    value = float(r.get("Rating", 0))
    if category == "cleanliness":
        rating_cleanliness = value
    elif category == "amenities":
        rating_amenities = value
    elif category == "location":
        rating_location = value
    elif category == "service":
        rating_service = value

# Iterate over rooms
for room in data.get("Room", []):
    room_id = room.get("Room Id")
    room_name = room.get("Name")
    room_facilities = json.dumps(room.get("facilities", []))
    room_images = json.dumps(room.get("url", []))

    insert_query = """
    INSERT INTO Trip_Hotel (
        Hotel_ID, Hotel_Name, Phone_No, Description, Open_Year,
        Address, City, State, Country, Pincode,
        Room_ID, Room_Name, Room_Facilities, Room_Images,
        NearbyLocations, Policy, HotelFacilities, Reviews,
         Rating_Cleanliness, Rating_Amenities, Rating_Location, Rating_Service,Recommendation
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    record = (
        hotel_id, hotel_name, phone_no, description, open_year,
        address, city, state, country, pincode,
        room_id, room_name, room_facilities, room_images,
        nearby_locations, policy, hotel_facilities, reviews,
        rating_cleanliness, rating_amenities, rating_location, rating_service,
         recommendation
    )

    cursor.execute(insert_query, record)

conn.commit()
conn.close()
print("All rooms inserted successfully!")