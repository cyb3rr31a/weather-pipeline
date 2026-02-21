# A script that pulls weather data for your city every day and stores it in a SQLite database.

import requests
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
CITY = os.getenv("CITY")

def extract():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data

def transform(data):
    transformed = {
        "city": CITY,
        "temperature": data['main']['temp'],
        "feels_like": data['main']['feels_like'],
        "humidity": data['main']['humidity'],
        "description": data['weather'][0]['description'],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    return transformed

def load(transformed):
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temperature REAL,
            feels_like REAL,
            humidity INTEGER,
            description TEXT,
            timestamp TEXT
        )
    ''')

    cursor.execute('''
        INSERT INTO weather (city, temperature, feels_like, humidity, description, timestamp)
        VALUES (:city, :temperature, :feels_like, :humidity, :description, :timestamp)
    ''', transformed)

    conn.commit()
    conn.close()
    print("Data loaded successfully.")

def run():
    raw = extract()
    transformed = transform(raw)
    load(transformed)

run()