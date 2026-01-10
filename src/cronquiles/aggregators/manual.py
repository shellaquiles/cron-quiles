import logging
from typing import List, Optional, Dict
from .base import BaseAggregator
from ..models import EventNormalized

logger = logging.getLogger(__name__)


class ManualAggregator(BaseAggregator):
    """Aggregator for manually defined events."""

    def extract(self, source: List[Dict], feed_name: Optional[str] = None) -> List[EventNormalized]:
        # Source here is expected to be a list of dicts (the manual events data)
        # or a single dict if we change schema, but currently list.
        if not source:
            return []

        # If source is just one dict (config style), wrap it?
        # But typically we pass the whole list of manual events here.

        manual_events = []
        data_list = source if isinstance(source, list) else [source]

        for data in data_list:
            try:
                if "source" not in data:
                    data["source"] = "Manual"

                event_norm = EventNormalized.from_dict(data)
                manual_events.append(event_norm)
            except Exception as e:
                logger.error(f"Error processing manual event: {e}")
                continue

        logger.info(f"Processed {len(manual_events)} manual events")
        return manual_events
