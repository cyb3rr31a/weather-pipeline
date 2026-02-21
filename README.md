# Weather Data Pipeline

A simple ETL pipeline that collects weather data from the OpenWeatherMap API and stores it in a local SQLite database. Designed to run daily on a schedule.

## What it does

- **Extracts** current weather data from the OpenWeatherMap API
- **Transforms** the raw response into a clean, structured format
- **Loads** the data into a local SQLite database

Each day a new row is added, building up a historical record of weather data over time.

## Data collected

| Field | Description |
|---|---|
| city | City name |
| temperature | Temperature in °C |
| feels_like | Feels like temperature in °C |
| humidity | Humidity percentage |
| description | Weather description (e.g. "light rain") |
| timestamp | Date and time the data was collected |

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/weather-pipeline.git
cd weather-pipeline
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get a free API key

Sign up at [openweathermap.org](https://openweathermap.org) and copy your API key from the **API Keys** section of your account.

### 4. Create your `.env` file

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Then open `.env` and add your API key and city:

```
API_KEY=your_api_key_here
CITY=your_city_here
```

### 5. Run the pipeline

```bash
python weather_pipeline.py
```

You should see:
```
Data extracted for London.
Data transformed.
Data loaded into database.
Pipeline completed successfully.
```

A `weather.db` file will be created in your project folder containing your data.

## Scheduling (Windows)

To run the pipeline automatically every day using Task Scheduler:

1. Open **Task Scheduler** and click **Create Basic Task**
2. Set the trigger to **Daily** at your preferred time
3. Set the action to **Start a program**
   - Program: path to your Python executable (run `where python` to find it)
   - Arguments: `weather_pipeline.py`
   - Start in: path to your project folder
4. Save and right-click the task to **Run** it immediately as a test

## Project structure

```
weather-pipeline/
├── weather_pipeline.py  # Main ETL script
├── .env                 # Your API key and city (not tracked by Git)
├── .env.example         # Template for .env
├── .gitignore           # Tells Git to ignore .env and weather.db
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Dependencies

- `requests` — for calling the API
- `python-dotenv` — for loading environment variables from `.env`
- `sqlite3` — built into Python, no install needed