"""
ICS Aggregator - Agregador de feeds ICS públicos para eventos tech en México.

Este módulo consume múltiples feeds ICS, normaliza eventos, los deduplica
y genera un calendario unificado.
"""

import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests
from dateutil import tz
from icalendar import Calendar

# Import models & history
from .models import EventNormalized
from .history_manager import HistoryManager

# Import Aggregators
from .aggregators.eventbrite import EventbriteAggregator
from .aggregators.luma import LumaAggregator
from .aggregators.meetup import MeetupAggregator
from .aggregators.ics import GenericICSAggregator
from .aggregators.manual import ManualAggregator
from .schemas import JSONOutputSchema, CommunitySchema

# Configurations
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ICSAggregator:
    """
    Orchestrator for event aggregation.
    Delegates fetching and extraction to specific aggregators based on source type.
    Handles deduplication, healing, history management, and output generation.
    """

    def __init__(self, timeout: int = 30, max_retries: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Cron-Quiles-ICS-Aggregator/1.0"})

        self.geocoding_cache = {}
        self.cache_file = Path("data/geocoding_cache.json")
        self.load_geocoding_cache()

        self.history_manager = HistoryManager()

        # Initialize specific aggregators
        self.aggregators = {
            'eventbrite': EventbriteAggregator(self.session),
            'luma': LumaAggregator(self.session, timeout, max_retries),
            'meetup': MeetupAggregator(self.session, timeout, max_retries),
            'ics': GenericICSAggregator(self.session, timeout, max_retries),
            'manual': ManualAggregator(self.session)
        }

    def load_geocoding_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.geocoding_cache = json.load(f)
                logger.info(f"Loaded {len(self.geocoding_cache)} entries from geocoding cache.")
            except Exception as e:
                logger.warning(f"Could not load geocoding cache: {e}")
                self.geocoding_cache = {}

    def save_geocoding_cache(self):
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.geocoding_cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.geocoding_cache)} entries to geocoding cache.")
        except Exception as e:
            logger.warning(f"Could not save geocoding cache: {e}")

    def deduplicate_events(self, events: List[EventNormalized], time_tolerance_hours: int = 2) -> List[EventNormalized]:
        """
        Deduplicates events similar to original implementation.
        """
        events_by_hash: Dict[str, List[EventNormalized]] = {}

        for event in events:
            hash_key = event.hash_key
            if hash_key not in events_by_hash:
                events_by_hash[hash_key] = []
            events_by_hash[hash_key].append(event)

        deduplicated = []

        for hash_key, group in events_by_hash.items():
            if len(group) == 1:
                deduplicated.append(group[0])
            else:
                group.sort(
                    key=lambda e: (
                        bool(e.url and e.url.startswith("http")),
                        len(e.description),
                    ),
                    reverse=True,
                )
                selected = group[0]

                # Merge alternative URLs
                alt_urls = set()
                primary_url = selected.url.strip() if selected.url else ""
                for duplicate in group[1:]:
                    dup_url = duplicate.url.strip() if duplicate.url else ""
                    if dup_url and dup_url.startswith("http") and dup_url != primary_url:
                        alt_urls.add(dup_url)

                if alt_urls:
                    header = "\n\nOtras fuentes:"
                    if header not in selected.description:
                        selected.description += header
                    for url in alt_urls:
                        if url not in selected.description:
                            selected.description += f"\n- {url}"

                logger.info(f"Deduplicated: kept '{selected.original_event.get('summary', '')}' from {len(group)} similar events")
                deduplicated.append(selected)

        logger.info(f"Deduplication: {len(events)} -> {len(deduplicated)} events")
        return deduplicated

    def aggregate_feeds(self, feed_urls: List[str], manual_data: Optional[List[Dict]] = None) -> List[EventNormalized]:
        all_events = []

        # 1. Process config feeds
        for feed in feed_urls:
            url = feed if isinstance(feed, str) else feed.get("url")
            name = None if isinstance(feed, str) else feed.get("name")

            if not url: continue

            # Dispatch logic
            if "eventbrite." in url and "/e/" not in url and "/o/" not in url and "ical" not in url:
                 # Check if likely direct Eventbrite URL vs ICS proxy
                 # Actually our code handles this logic. If it looks like eventbrite, use EB aggregator
                 # Assuming direct EB urls:
                 agg = self.aggregators['eventbrite']
            elif "eventbrite." in url and ("eventbrite.com" in url or "eventbrite.com.mx" in url):
                 # Stronger check for Eventbrite domains
                 agg = self.aggregators['eventbrite']
            elif "lu.ma" in url or "luma.com" in url:
                 agg = self.aggregators['luma']
            elif "meetup.com" in url:
                 agg = self.aggregators['meetup']
            else:
                 agg = self.aggregators['ics']

            try:
                events = agg.extract(feed, name)
                all_events.extend(events)
            except Exception as e:
                logger.error(f"Error extracting from {url}: {e}")

        # 2. Process manual events
        if manual_data:
            events = self.aggregators['manual'].extract(manual_data)
            all_events.extend(events)

        # 2.5 Filter events by country (Only Mexico or Online)
        before_filter_count = len(all_events)
        all_events = [
            e for e in all_events
            if e.country_code == "MX" or e._is_online()
        ]
        if len(all_events) < before_filter_count:
            logger.info(f"Filtered out {before_filter_count - len(all_events)} non-Mexico / non-Online events.")

        # 3. Geocoding (Healing) Phase 1 - Live Events
        to_geocode = [e for e in all_events if not e._is_online() and (not e.state_code or not e.city)]
        if to_geocode:
            logger.info(f"Geocoding {len(to_geocode)} new events...")
            for i, event in enumerate(to_geocode):
                if i > 0 and (not self.geocoding_cache or event.location not in self.geocoding_cache):
                    time.sleep(1.1)
                event.geocode_location(self.geocoding_cache)
            self.save_geocoding_cache()

        # 4. Integrate with History
        deduplicated_new = self.deduplicate_events(all_events)
        self.history_manager.load_history()
        self.history_manager.merge_events(deduplicated_new)
        self.history_manager.save_history()

        # 5. Get Complete List
        all_dicts = self.history_manager.get_all_events()
        final_events = []
        for d in all_dicts:
            try:
                final_events.append(EventNormalized.from_dict(d))
            except Exception as e:
                logger.error(f"Error reconstructing event: {e}")

        # 6. Geocoding (Healing) Phase 2 - Full List (including historic)
        to_geocode_final = [e for e in final_events if not e._is_online() and (not e.state_code or not e.city)]
        if to_geocode_final:
            max_to_geocode = 100
            to_process = to_geocode_final[:max_to_geocode]
            logger.info(f"Healing location data: Geocoding {len(to_process)} events...")

            for i, event in enumerate(to_process):
                if i > 0 and (not self.geocoding_cache or event.location not in self.geocoding_cache):
                     time.sleep(1.1)
                if event.geocode_location(self.geocoding_cache):
                     # Update history immediately for persistence
                     key = event.hash_key
                     self.history_manager.events[key] = event.to_dict()

            self.history_manager.save_history()
            self.save_geocoding_cache()

        # 7. Final Sort and Deduplication
        final_events.sort(key=lambda e: e.dtstart or datetime.max.replace(tzinfo=tz.UTC))
        if final_events:
            final_events = self.deduplicate_events(final_events)

            # Sync back to history manager to ensure consistency with latest deduplication logic
            self.history_manager.events = {}
            for event in final_events:
                dict_val = event.to_dict()
                key = dict_val.get('hash_key') or f"{dict_val['title']}_{dict_val['dtstart']}"
                self.history_manager.events[key] = dict_val
            self.history_manager.save_history()

        logger.info(f"Final aggregated count (History + Live): {len(final_events)}")
        return final_events

    def group_events_by_state(self, events: List[EventNormalized]) -> Dict[str, List[EventNormalized]]:
        grouped = {}
        for event in events:
            code = event.state_code if event.state_code else "ONLINE"
            if code not in grouped: grouped[code] = []
            grouped[code].append(event)
        return grouped

    def generate_ics(self, events: List[EventNormalized], output_file: str = "cronquiles.ics", city_name: Optional[str] = None) -> str:
        calendar = Calendar()
        calendar.add("prodid", "-//Cron-Quiles//ICS Aggregator//EN")
        calendar.add("version", "2.0")
        calendar.add("calscale", "GREGORIAN")

        if city_name:
            calendar.add("X-WR-CALNAME", f"Eventos Tech {city_name} - cronquiles")
            calendar.add("X-WR-CALDESC", f"Calendario unificado de eventos tech en {city_name}, México")
        else:
            calendar.add("X-WR-CALNAME", "Eventos Tech México - cronquiles")
            calendar.add("X-WR-CALDESC", "Calendario unificado de eventos tech en México")
        calendar.add("X-WR-TIMEZONE", "America/Mexico_City")

        for event_norm in events:
            calendar.add_component(event_norm.to_ical_event())

        with open(output_file, "wb") as f:
            f.write(calendar.to_ical())

        logger.info(f"Generated ICS file: {output_file} with {len(events)} events")
        return output_file

    def generate_json(self, events: List[EventNormalized], output_file: str = "cronquiles.json", city_name: Optional[str] = None, feeds: Optional[List[Dict]] = None) -> str:
        events_data: JSONOutputSchema = {
            "generated_at": datetime.now(tz.UTC).isoformat(),
            "total_events": len(events),
            "city": city_name,
            "communities": [
                CommunitySchema(name=f.get("name", ""), description=f.get("description", ""))
                for f in (feeds or [])
                if isinstance(f, dict) and f.get("name")
            ],
            "events": [event.to_dict() for event in events],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(events_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Generated JSON file: {output_file} with {len(events)} events")
        return output_file
