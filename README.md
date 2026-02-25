# Weather Pipeline

A daily weather ETL pipeline built in two versions, showing the evolution from a simple scheduled script to a production-style orchestrated pipeline.

## The evolution

### v1 — Task Scheduler
A Python script that extracts weather data from the OpenWeatherMap API, transforms it, and loads it into a SQLite database. Scheduled to run daily using Windows Task Scheduler.

Gets the job done, but has no visibility — if it fails silently you won't know until you check the database manually.

### v2 — Airflow
The same ETL logic rebuilt as an Apache Airflow DAG. Each step (extract, transform, load) is a separate task with its own logs, retry logic, and status tracking. The pipeline is monitored through a web UI and retries automatically if the API call fails.

| Feature | v1 Task Scheduler | v2 Airflow |
|---|---|---|
| Scheduling | ✅ | ✅ |
| Visual pipeline UI | ❌ | ✅ |
| Per-task logs | ❌ | ✅ |
| Automatic retries | ❌ | ✅ |
| Run history | ❌ | ✅ |
| Rerun a single failed task | ❌ | ✅ |

## Pipeline structure

Both versions follow the same ETL pattern:

```
extract → transform → load
```

- **extract** — calls the OpenWeatherMap API and retrieves current weather
- **transform** — pulls out temperature, humidity, feels like, and description, adds a timestamp
- **load** — inserts the cleaned row into SQLite

## Data collected

| Field | Description |
|---|---|
| city | City name |
| temperature | Temperature in °C |
| feels_like | Feels like temperature in °C |
| humidity | Humidity percentage |
| description | Weather description (e.g. "light rain") |
| timestamp | Date and time the data was collected |

## Project structure

```
weather-pipeline/
├── v1_task_scheduler/
│   ├── weather_pipeline.py   # Original ETL script
│   ├── .env.example          # Environment variable template
│   └── requirements.txt      # Python dependencies
├── v2_airflow/
│   ├── weather_dag.py        # Airflow DAG
│   └── .env.example          # Environment variable template
├── .env.example              # Root level template
├── .gitignore
└── README.md
```

## Setup

### Prerequisites

- Python 3.10+
- A free OpenWeatherMap API key from [openweathermap.org](https://openweathermap.org)
- For v2: WSL2 with Ubuntu (Windows users) or any Linux/Mac environment

### 1. Clone the repository

```bash
git clone https://github.com/your-username/weather-pipeline.git
cd weather-pipeline
```

### 2. Create your `.env` file

```bash
cp .env.example .env
```

Fill in your API key and city:

```
API_KEY=your_openweathermap_api_key
CITY=London
```

---

### Running v1 — Task Scheduler

```bash
cd v1_task_scheduler
pip install -r requirements.txt
python weather_pipeline.py
```

To schedule it, open Windows Task Scheduler and point it at `weather_pipeline.py` to run daily.

---

### Running v2 — Airflow

Install Airflow:

```bash
pip install "apache-airflow==2.8.1" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.1/constraints-3.10.txt"
pip install requests python-dotenv
```

Initialize and create an admin user:

```bash
export AIRFLOW_HOME=~/airflow
airflow db init

airflow users create \
    --username admin \
    --firstname admin \
    --lastname admin \
    --role Admin \
    --email admin@example.com \
    --password admin
```

Copy the DAG into Airflow's dags folder:

```bash
cp v2_airflow/weather_dag.py ~/airflow/dags/
```

Start Airflow in two terminal windows:

```bash
# Terminal 1
airflow webserver --port 8080

# Terminal 2
airflow scheduler
```

Open `http://localhost:8080`, log in with `admin` / `admin`, enable the `weather_pipeline` DAG, and trigger a run with the ▶ button.

## Dependencies

- `requests` — calling the OpenWeatherMap API
- `python-dotenv` — loading environment variables
- `apache-airflow` — pipeline orchestration (v2 only)
- `sqlite3` — built into Python, no install needed