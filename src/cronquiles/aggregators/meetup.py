import logging
import time
from typing import List, Optional, Dict
from .ics import GenericICSAggregator
from ..models import EventNormalized

logger = logging.getLogger(__name__)


class MeetupAggregator(GenericICSAggregator):
    """Aggregator for Meetup ICS feeds with location enrichment."""

    def extract(
        self, source: str | Dict, feed_name: Optional[str] = None
    ) -> List[EventNormalized]:
        events = super().extract(source, feed_name)

        # Enrich events needing location
        to_enrich = [
            e
            for e in events
            if e.url and "meetup.com" in e.url and len(e.location) < 15
        ]

        if to_enrich:
            logger.info(f"Found {len(to_enrich)} Meetup events to potentially enrich")
            for i, event in enumerate(to_enrich):
                if i > 0:
                    time.sleep(1)
                try:
                    event.enrich_location_from_meetup(self.session)
                except Exception as e:
                    logger.warning(f"Error enriching Meetup event {event.url}: {e}")

        return events
