#!/usr/bin/env python3
import json
import logging
import re
import os
import yaml
import requests
from pathlib import Path
from icalendar import Calendar
from geopy.geocoders import GoogleV3, Nominatim
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CACHE_FILE = "data/geocoding_cache.json"
CONFIG_FILE = "config/feeds.yaml"

def generate_query(location_str):
    """
    Replicates the logic in EventNormalized.geocode_location to generate the cache key.
    """
    if not location_str:
        return None

    # Copied from models.py logic
    location_cleaned = re.sub(r",\s*,", ",", location_str)
    query_parts = [p.strip() for p in location_cleaned.split(",") if p.strip()]

    # Quitar URLs
    query_parts = [p for p in query_parts if not p.startswith("http")]

    # Quitar ruidos comunes de Meetup
    query_parts = [
        re.sub(r"^hosted by\s+", "", p, flags=re.IGNORECASE) for p in query_parts
    ]

    current_query = ", ".join(query_parts).strip()
    if not current_query or len(current_query) < 4:
        return None

    return current_query

def load_feeds_config(yaml_file):
    try:
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("cities", {})
    except Exception as e:
        logger.error(f"Error loading config {yaml_file}: {e}")
        return {}

def geocode_query(query, geolocator):
    try:
        if isinstance(geolocator, GoogleV3):
            location_data = geolocator.geocode(query, language="es", timeout=10)
        else:
            location_data = geolocator.geocode(query, addressdetails=True, language="es", timeout=10)

        return location_data.raw if location_data else {}
    except Exception as e:
        logger.error(f"Geocoding error for '{query}': {e}")
        return {}

def main():
    cache_path = Path(CACHE_FILE)

    # Init geolocator
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key:
        geolocator = GoogleV3(api_key=api_key)
        logger.info("Using Google Maps API")
    else:
        geolocator = Nominatim(user_agent="cron-quiles-cacher")
        logger.info("Using Nominatim (WARNING: Lower rate limits)")

    # Load cache
    cache = {}
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
            logger.info(f"Loaded {len(cache)} existing cache entries.")
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")

    # Load feeds
    cities_config = load_feeds_config(CONFIG_FILE)
    if not cities_config:
        logger.error("No cities found in config.")
        return

    added_count = 0
    skipped_count = 0
    errors_count = 0

    for city_slug, city_data in cities_config.items():
        logger.info(f"Processing city: {city_data.get('name', city_slug)}")
        feeds = city_data.get("feeds", [])
        if not feeds:
            continue

        for feed in feeds:
            url = feed.get("url")
            if not url: continue

            logger.info(f"  Fetching feed: {url}")
            try:
                # Fetch ICS
                headers = {"User-Agent": "CronQuiles-Cacher/1.0"}
                resp = requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()

                cal = Calendar.from_ical(resp.content)

                for component in cal.walk():
                    if component.name == "VEVENT":
                        location = component.get("LOCATION")
                        if not location: continue

                        # Convert to string (vText)
                        location_str = str(location)

                        query = generate_query(location_str)
                        if not query: continue

                        if query in cache:
                            skipped_count += 1
                            continue

                        # Not in cache - Geocode it!
                        logger.info(f"    Geocoding new location: {query}")
                        result = geocode_query(query, geolocator)

                        if result:
                            cache[query] = result
                            added_count += 1
                        else:
                            logger.warning(f"    Could not geocode: {query}")
                            errors_count += 1

            except Exception as e:
                logger.error(f"  Failed to process feed {url}: {e}")

    # Save final cache
    if added_count > 0:
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved cache with {added_count} new entries. Total: {len(cache)}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    else:
        logger.info("No new entries added to cache.")

    logger.info(f"Summary: Added {added_count}, Skipped {skipped_count}, Errors {errors_count}")

if __name__ == "__main__":
    main()
