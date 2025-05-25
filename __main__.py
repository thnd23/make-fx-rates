"""
FX Rate ETL Pipeline

This script implements a data pipeline for fetching, storing, and synchronizing
foreign exchange (FX) rates using Redis as a fast caching layer and JSON for
persistent storage.

Main Features:
- Fetches FX rates from an API with retries and error handling.
- Stores exchange rates in Redis for quick retrieval.
- Persists data in JSON for long-term storage.
- Implements multi-level logging for debugging and monitoring.
- Ensures proper synchronization between Redis and JSON storage.
"""

import json
import logging
import os
import time
import traceback
from datetime import datetime

import redis
import requests

# API and storage setup
API_URL = "https://open.er-api.com/v6/latest/USD"
JSON_FILE = "currency_rates.json"
LOG_DIR = "logs"
LOG_FILE = f"{LOG_DIR}/fx_rates_{datetime.today().date().isoformat()}.log"
TODAY = datetime.today().date().isoformat()
REDIS_CLIENT = None

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging (multi-level)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def initialize_redis_connection():
    """Initialize Redis connection with error handling."""
    try:
        redis_client = redis.StrictRedis(
            host="localhost", port=6379, db=0, decode_responses=True
        )
        redis_client.ping()
        logging.info("Connected to Redis successfully.")
        return redis_client
    except redis.exceptions.ConnectionError:
        logging.warning(
            "WARNING: Failed to connect to Redis. Ensure the Redis server is running."
        )
        return None
    except redis.exceptions.RedisError as e:
        logging.error("ERROR: Redis error occurred: %s", e)
        return None


def check_existing_data_in_json():
    """Check if today's exchange rate data is already stored."""
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                if TODAY in data:
                    logging.info(
                        "Data for %s exists in JSON. No API call needed.", TODAY
                    )
                    return True
        except IOError as e:
            logging.error("Error: %s", e)
    return False


def check_existing_data_in_redis():
    """Check if today's exchange rate data is already stored in Redis."""
    if REDIS_CLIENT is None:
        logging.warning("WARNING: Redis is not available. Skipping Redis check.")
        return False

    stored_data = REDIS_CLIENT.get(TODAY)
    if stored_data:
        logging.info("Data for %s exists in Redis. No API call needed.", TODAY)
        return True
    return False


def sync_data_sources():
    """Ensure Redis and JSON are synchronized in case one or the other is missing."""
    json_data_exists = check_existing_data_in_json()
    redis_data_exists = check_existing_data_in_redis()

    if json_data_exists and redis_data_exists:
        return True

    if json_data_exists and not redis_data_exists:
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        logging.info("Syncing JSON data to Redis for %s.", TODAY)
        save_to_redis({TODAY: data[TODAY]})
        return data[TODAY]

    if redis_data_exists and not json_data_exists:
        stored_data = json.loads(REDIS_CLIENT.get(TODAY))
        logging.info("Syncing Redis data to JSON for %s.", TODAY)
        save_to_json({TODAY: stored_data})
        return stored_data

    return False


def save_to_redis(new_data, expiry_seconds=86400):
    """Store today's exchange rates in Redis with auto-expiry."""
    if REDIS_CLIENT is None:
        logging.warning("WARNING: Redis is not available. Skipping Redis storage.")
        return

    date_key = list(new_data.keys())[0]
    REDIS_CLIENT.set(date_key, json.dumps(new_data[date_key]), ex=expiry_seconds)
    logging.info(
        "FX rates for %s stored in Redis (expires in %s seconds).",
        date_key,
        expiry_seconds,
    )


def extract_rates(max_retries=5, base_delay=60):
    """Fetch currency rates from API with enhanced error logging."""
    for attempt in range(max_retries):
        try:
            response = requests.get(API_URL, timeout=5)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(
                "ERROR: API request failed (%s). Traceback: %s",
                e,
                traceback.format_exc(),
            )

        wait_time = (2**attempt) * base_delay
        logging.info("Waiting %s seconds before next retry...", wait_time)
        time.sleep(wait_time)

    logging.error("ERROR: Max retries reached. API might be down.")
    return None


def transform_data(data):
    """Convert raw API data into structured format."""
    base_currency = data.get("base_code")
    rates = data.get("rates", {})

    if base_currency in rates:
        del rates[base_currency]

    return {TODAY: rates}


def save_to_json(new_data):
    """Store transformed data in a JSON file locally."""
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, "w", encoding="utf-8") as file:
            json.dump({}, file)

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    last_date = list(data.keys())[-1] if data else None
    new_date = list(new_data.keys())[0]

    if last_date != new_date:
        data.update(new_data)
        with open(JSON_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
            logging.info("FX rates for %s stored in JSON.", new_date)
    else:
        logging.info("No new data to update.")


if __name__ == "__main__":
    REDIS_CLIENT = initialize_redis_connection()
    latest_rates = sync_data_sources()

    if not latest_rates:
        raw_data = extract_rates()
        if raw_data:
            transformed_data = transform_data(raw_data)
            save_to_redis(transformed_data)
            save_to_json(transformed_data)
