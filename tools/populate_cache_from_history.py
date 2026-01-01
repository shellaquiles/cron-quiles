#!/usr/bin/env python3
import json
import logging
import re
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HISTORY_FILE = "data/history.json"
CACHE_FILE = "data/geocoding_cache.json"

def generate_query(location_str):
    """
    Replicates the logic in EventNormalized.geocode_location to generate the cache key.
    """
    if not location_str:
        return None

    # Copied from models.py
    # Limpiar la query: quitar comas redundantes y partes vacías
    location_cleaned = re.sub(r",\s*,", ",", location_str)
    query_parts = [p.strip() for p in location_cleaned.split(",") if p.strip()]

    # Quitar URLs si hay comas (suelen ser las últimas partes)
    query_parts = [p for p in query_parts if not p.startswith("http")]

    # Quitar ruidos comunes de Meetup
    query_parts = [
        re.sub(r"^hosted by\s+", "", p, flags=re.IGNORECASE) for p in query_parts
    ]

    current_query = ", ".join(query_parts).strip()
    if not current_query or len(current_query) < 4:
        return None

    return current_query

def main():
    history_path = Path(HISTORY_FILE)
    cache_path = Path(CACHE_FILE)

    if not history_path.exists():
        logger.error(f"History file not found at {history_path}")
        return

    # Load history
    try:
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load history: {e}")
        return

    # Load cache
    cache = {}
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
            logger.info(f"Loaded {len(cache)} existing cache entries.")
        except Exception as e:
            logger.warning(f"Failed to load cache, creating new: {e}")

    added_count = 0
    skipped_count = 0

    # history.json is a list of events
    events_list = history if isinstance(history, list) else list(history.values())

    for event in events_list:
        location = event.get("location")
        city = event.get("city")
        state = event.get("state")
        country = event.get("country")

        # We need at least city, state, country to form a valid geocoding result
        if not (location and city and state and country):
            continue

        query = generate_query(location)
        if not query:
            continue

        if query in cache:
            skipped_count += 1
            continue

        # Construct a synthetic Google Maps API response
        # See models.py _parse_google_address for expectations
        # It looks for "address_components" with "types"

        synthetic_result = {
            "address_components": [
                {
                    "long_name": country,
                    "short_name": event.get("country_code", "MX"), # Default to MX if missing, logic usually implies it
                    "types": ["country"]
                },
                {
                    "long_name": state,
                    "short_name": event.get("state_code", ""),
                    "types": ["administrative_area_level_1"]
                },
                {
                    "long_name": city,
                    "types": ["locality"]
                }
            ],
            "formatted_address": location, # Not strictly used by parser but good for completeness
            "geometry": {} # Not used by current parser logic
        }

        cache[query] = synthetic_result
        added_count += 1
        # logger.info(f"Added to cache: {query} -> {city}, {state}")

    if added_count > 0:
        # Save cache
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully added {added_count} new entries to cache. Total: {len(cache)}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    else:
        logger.info("No new entries added to cache.")

if __name__ == "__main__":
    main()
