from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv("/mnt/c/data-engineering/weather-pipeline/.env")

API_KEY = os.getenv("API_KEY")
CITY = os.getenv("CITY")
DB_PATH = "/mnt/c/data-engineering/weather-pipeline/weather.db"

# --- ETL functions ---

def extract(**context):
    if not API_KEY:
        raise ValueError("API_KEY is missing. Check your .env file.")

    if not CITY:
        raise ValueError("CITY is missing. Check your .env file.")

    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    data = response.json()

    # Push data to XCom so the next task can access it
    context['ti'].xcom_push(key="raw_weather", value=data)
    print(f"Extracted weather data for {CITY}.")

def transform(**context):
    data = context['ti'].xcom_pull(key="raw_weather", task_ids="extract")

    if not data:
        raise ValueError("No data found in XCom for key 'raw_weather'.")

    transformed = {
        "city": CITY,
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    context['ti'].xcom_push(key="transformed_weather", value=transformed)
    print(f"Transformed weather data: {transformed}")

def load(**context):
    transformed = context['ti'].xcom_pull(key="transformed_weather", task_ids="transform")

    if not transformed:
        raise ValueError("No data found in Xcom for key 'transformed_weather'.")

    conn = sqlite3.connect(DB_PATH)
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
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        transformed["city"],
        transformed["temperature"],
        transformed["feels_like"],
        transformed["humidity"],
        transformed["description"],
        transformed["timestamp"]
    ))

    conn.commit()
    conn.close()
    print("Data loaded into database.")

# --- DAG definition ---

default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

with DAG(
    dag_id = 'weather_pipeline',
    description = "Daily weather ETL pipeline",
    default_args = default_args,
    start_date = datetime(2025, 1, 1),
    schedule_interval = '@daily',
    catchup = False,
) as dag:

    extract_task = PythonOperator(
        task_id = 'extract',
        python_callable = extract,
        provide_context = True
    )

    transform_task = PythonOperator(
        task_id = 'transform',
        python_callable = transform,
        provide_context = True
    )

    load_task = PythonOperator(
        task_id = 'load',
        python_callable = load,
        provide_context = True
    )

    extract_task >> transform_task >> load_task
