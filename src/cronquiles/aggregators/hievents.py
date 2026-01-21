import logging
import requests
from typing import List, Optional, Dict
from .base import BaseAggregator
from ..models import EventNormalized

logger = logging.getLogger(__name__)


class HiEventsAggregator(BaseAggregator):
    """
    Aggregator specifically for Hi.Events platform (used by Pythonistas GDL).
    Uses the public API instead of scraping to get reliable data.
    """

    def __init__(self, session: Optional[requests.Session] = None):
        super().__init__(session)
        self.session.headers.update({"Accept": "application/json"})

    def extract(
        self, source: str | Dict, feed_name: Optional[str] = None
    ) -> List[EventNormalized]:
        """
        Extracts events from a Hi.Events public API or organizer URL.
        """
        url = source if isinstance(source, str) else source.get("url")
        name = feed_name or (source.get("name") if isinstance(source, dict) else None)

        if not url:
            return []

        # If it's a browser URL, try to convert to API URL
        # e.g., https://reuniones.pythonistas-gdl.org/events/1/pythonistas-gdl
        # -> https://reuniones.pythonistas-gdl.org/api/public/organizers/1/events
        api_url = url
        if "/events/" in url and "/api/" not in url:
            try:
                parts = url.split("/")
                # Pattern: .../events/{id}/{slug}
                idx = parts.index("events")
                if len(parts) > idx + 1:
                    org_id = parts[idx + 1]
                    base_url = "/".join(parts[:idx])
                    api_url = f"{base_url}/api/public/organizers/{org_id}/events"
            except (ValueError, IndexError):
                pass

        logger.info(f"Fetching Hi.Events from API: {api_url}")
        try:
            response = self.session.get(api_url, timeout=20)
            response.raise_for_status()
            data = response.json()

            events = []
            # Hi.Events returns events in a 'data' array
            raw_events = data.get("data", [])
            for raw in raw_events:
                try:
                    event_norm = self._map_to_normalized(raw, url, name)
                    if event_norm:
                        events.append(event_norm)
                except Exception as e:
                    logger.error(f"Error mapping Hi.Events event: {e}")

            return events
        except Exception as e:
            logger.error(f"Failed to process Hi.Events feed {url}: {e}")
            return []

    def _map_to_normalized(
        self, raw: Dict, source_url: str, feed_name: Optional[str]
    ) -> Optional[EventNormalized]:
        """Maps Hi.Events API JSON to EventNormalized object."""

        # Extract location string
        loc_details = raw.get("settings", {}).get("location_details", {})
        loc_parts = []
        if loc_details.get("venue_name"):
            loc_parts.append(loc_details["venue_name"])
        if loc_details.get("address_line_1"):
            loc_parts.append(loc_details["address_line_1"])
        if loc_details.get("city"):
            loc_parts.append(loc_details["city"])
        if loc_details.get("state_or_region"):
            loc_parts.append(loc_details["state_or_region"])
        if loc_details.get("country"):
            loc_parts.append(loc_details["country"])

        location_str = ", ".join(loc_parts) if loc_parts else "México"
        if raw.get("settings", {}).get("is_online_event"):
            location_str = "Online"

        # Correct date fields for from_dict
        # Hi.Events provides ISO UTC: 2026-01-31T00:30:00.000000Z
        mapped_data = {
            "title": raw.get("title", ""),
            "description": raw.get("description", ""),
            "dtstart": raw.get("start_date"),
            "dtend": raw.get("end_date"),
            "location": location_str,
            "url": f"{source_url.split('/events/')[0]}/event/{raw.get('id')}/{raw.get('slug')}",
            "source": "Hi.Events",
            "organizer": raw.get("organizer", {}).get("name") or feed_name,
        }

        event_norm = EventNormalized.from_dict(mapped_data)
        event_norm.source_url = source_url
        event_norm.feed_name = feed_name

        return event_norm
