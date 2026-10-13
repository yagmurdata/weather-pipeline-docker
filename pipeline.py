import os
import time

import psycopg2
import requests

LATITUDE = 41.01
LONGITUDE = 28.98


def extract():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto",
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def transform(raw):
    current = raw["current"]
    return {
        "observed_at": current["time"],
        "temperature_c": current["temperature_2m"],
        "humidity_pct": current["relative_humidity_2m"],
        "wind_speed_kmh": current["wind_speed_10m"],
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
    }


def get_connection():

    for attempt in range(10):
        try:
            return psycopg2.connect(
                host=os.environ["DB_HOST"],
                port=os.environ.get("DB_PORT", "5432"),
                dbname=os.environ["DB_NAME"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
            )
        except psycopg2.OperationalError:
            print(f"Database not ready, retrying ({attempt + 1}/10)...")
            time.sleep(2)
    raise RuntimeError("Could not connect to the database")


def load(row):
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS weather (
                    observed_at TIMESTAMP,
                    latitude DOUBLE PRECISION,
                    longitude DOUBLE PRECISION,
                    temperature_c DOUBLE PRECISION,
                    humidity_pct DOUBLE PRECISION,
                    wind_speed_kmh DOUBLE PRECISION,
                    UNIQUE (observed_at, latitude, longitude)
                )
            """)
            cur.execute("""
                INSERT INTO weather
                (observed_at, latitude, longitude, temperature_c, humidity_pct, wind_speed_kmh)
                VALUES (%(observed_at)s, %(latitude)s, %(longitude)s,
                        %(temperature_c)s, %(humidity_pct)s, %(wind_speed_kmh)s)
                ON CONFLICT DO NOTHING
            """, row)
    conn.close()


if __name__ == "__main__":
    raw = extract()
    row = transform(raw)
    load(row)
    print("Saved:", row)