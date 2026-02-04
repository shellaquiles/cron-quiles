import logging
import time
from typing import List, Optional, Dict
from .ics import GenericICSAggregator
from ..models import EventNormalized

logger = logging.getLogger(__name__)


class MeetupAggregator(GenericICSAggregator):
    """Aggregator for Meetup ICS feeds with location enrichment."""

    def __init__(
        self,
        session=None,
        timeout: int = 30,
        max_retries: int = 2,
        skip_enrich: bool = False,
    ):
        super().__init__(session, timeout, max_retries)
        self.skip_enrich = skip_enrich

    def extract(
        self, source: str | Dict, feed_name: Optional[str] = None
    ) -> List[EventNormalized]:
        events = super().extract(source, feed_name)

        # Enrich events needing location (omitido si skip_enrich)
        to_enrich = [
            e
            for e in events
            if e.url and "meetup.com" in e.url and len(e.location) < 15
        ]

        if to_enrich and not self.skip_enrich:
            logger.info(f"Found {len(to_enrich)} Meetup events to potentially enrich")
            for event in to_enrich:
                try:
                    if event.enrich_location_from_meetup(self.session):
                        time.sleep(1)
                except Exception as e:
                    logger.warning(f"Error enriching Meetup event {event.url}: {e}")

        return events
