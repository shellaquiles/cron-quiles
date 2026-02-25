import logging
import re
from typing import Dict, List, Optional

import requests

from ..models import EventNormalized
from .base import BaseAggregator

logger = logging.getLogger(__name__)


class GdgCommunityDev(BaseAggregator):
    """
    Extractor de eventos de GdgCommunityDev que utilizan los GDG. 
    Usa el api publico para recabar los eventos.
    """

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()

    def extract(
        self, source: str | Dict, feed_name: Optional[str] = None
    ) -> List[EventNormalized]:
        """
        Extract events from a source.

        Args:
            source: URL string or dictionary configuration
            feed_name: Optional name of the feed/community

        Returns:
            List of normalized events
        """
        url = source if isinstance(source, str) else source.get("url")
        name = feed_name or (source.get(
            "name") if isinstance(source, dict) else None)

        if not url:
            return []

        logger.info(f"Fetching {name} - GdgCommunityDev from: {url}")
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            data = response.text
            match = re.search(
                r"Globals\.chapter_id\s*=\s*['\"](\d+)['\"]", data)
            if not match:
                logger.warning(f"No chapter_id found in HTML for {name}")
                return []
            chapter_id = match.group(1)
            api_url = f'https://gdg.community.dev/api/event_slim/for_chapter/{chapter_id}?status=Live&include_cohosted_events=true&visible_on_parent_chapter_only=true&order=start_date&fields=title,start_date_iso,end_date_iso,event_type_title,url,description_short,venue_name,venue_address,venue_city,venue_zip_code,chapter_title,audience_type,tags'
            response = self.session.get(api_url, timeout=20)
            response.raise_for_status()
            data = response.json()

            if data['count'] == 0:
                return []
            events = []
            raw_events = data.get("results", [])
            for event in raw_events:
                try:
                    event_norm = self._payload_to_normalized(event, url, name)
                    events.append(event_norm)
                except Exception as e:
                    logger.error(
                        f"Error converting GdgCommunityDev event from {url}: {e}")
            return events
        except Exception as e:
            logger.error(f"Failed to process GdgCommunityDev feed {url}: {e}")
            return []

    def _payload_to_normalized(
        self, raw: Dict, source_url: str, feed_name: Optional[str]
    ) -> Optional[EventNormalized]:
        """Maps GdgCommunityDev API JSON to EventNormalized object."""

        location_str = None
        audience_type = raw.get("audience_type")
        if audience_type and audience_type in ['IN_PERSON', 'HYBRID']:
            loc_parts = []
            if raw.get("venue_name"):
                loc_parts.append(raw["venue_name"])
            if raw.get("venue_address"):
                loc_parts.append(raw["venue_address"])
            if raw.get("venue_city"):
                loc_parts.append(raw["venue_city"])
            if loc_parts:
                location_str = ", ".join(loc_parts) 
        
        if location_str is None and audience_type in ['VIRTUAL', 'HYBRID']:
            location_str = "Online"

        mapped_data = {
            "title": raw.get("title", ""),
            "description": raw.get("description_short", ""),
            "dtstart": raw.get("start_date_iso"),
            "dtend": raw.get("end_date_iso"),
            "location": location_str,
            "url": raw.get('url'),
            "source": "GdgCommunityDev",
            "organizer": raw.get('chapter_title'),
            "tags": raw.get("tags", []),
            # Hay que asegurarnos de solo agregar GDG de México
            "country_code": "MX"
        }

        event_norm = EventNormalized.from_dict(mapped_data)
        event_norm.source_url = source_url
        event_norm.feed_name = feed_name

        return event_norm
