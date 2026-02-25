import requests
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
CITY = os.getenv("CITY")

def extract():
    if not API_KEY:
        raise ValueError("API_KEY is missing. Check your .env file.")
    if not CITY:
        raise ValueError("CITY is missing. Check your .env file.")

    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Could not connect to the API. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise TimeoutError("The API request timed out. Try again later.")
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            raise ValueError("Invalid API key. Check your .env file.")
        elif response.status_code == 404:
            raise ValueError(f"City '{CITY}' not found. Check your .env file.")
        else:
            raise Exception(f"API returned an error: {e}")

    data = response.json()
    print(f"Data extracted for {CITY}.")
    return data

def transform(data):
    transformed = {
        "city": CITY,
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    print("Data transformed.")
    return transformed

def load(transformed):
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temperature REAL,
            feels_like REAL,
            humidity INTEGER,
            description TEXT,
            timestamp TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO weather (city, temperature, feels_like, humidity, description, timestamp)
        VALUES (:city, :temperature, :feels_like, :humidity, :description, :timestamp)
    """, transformed)

    conn.commit()
    conn.close()
    print("Data loaded into database.")

def run():
    try:
        raw = extract()
        transformed = transform(raw)
        load(transformed)
        print("Pipeline completed successfully.")
    except Exception as e:
        print(f"Pipeline failed: {e}")

run()