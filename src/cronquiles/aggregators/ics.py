import logging
import requests
from typing import List, Optional, Dict
from icalendar import Calendar
from .base import BaseAggregator
from ..models import EventNormalized

logger = logging.getLogger(__name__)


class GenericICSAggregator(BaseAggregator):
    """Aggregator for standard ICS feeds."""

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        timeout: int = 30,
        max_retries: int = 2,
    ):
        super().__init__(session)
        self.timeout = timeout
        self.max_retries = max_retries
        self.session.headers.update({"User-Agent": "Cron-Quiles-ICS-Aggregator/1.0"})

    def fetch_feed(self, url: str) -> Optional[Calendar]:
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching feed: {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                response.encoding = response.apparent_encoding or "utf-8"

                calendar = Calendar.from_ical(response.text)
                logger.info(f"Successfully parsed feed: {url}")
                return calendar
            except Exception as e:
                logger.warning(f"Error fetching {url} (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    logger.error(
                        f"Failed to fetch feed after {self.max_retries} attempts: {url}"
                    )

        return None

    def extract_events_from_calendar(
        self, calendar: Calendar, source_url: str, feed_name: Optional[str] = None
    ) -> List[EventNormalized]:
        events = []

        # Try to infer feed name from calendar if not provided
        if not feed_name:
            cal_name = calendar.get("X-WR-CALNAME")
            if cal_name:
                if isinstance(cal_name, list):
                    cal_name = cal_name[0]
                feed_name = str(cal_name)
                # Cleanup bytes string repr
                if "b'" in feed_name:
                    try:
                        feed_name = eval(feed_name).decode("utf-8", errors="ignore")
                    except Exception:
                        pass
                logger.info(f"Using X-WR-CALNAME as feed name: {feed_name}")

        for component in calendar.walk():
            if component.name == "VEVENT":
                try:
                    status = component.get("status", "").upper()
                    if status == "CANCELLED":
                        continue

                    event_norm = EventNormalized(component, source_url, feed_name)
                    events.append(event_norm)
                except Exception as e:
                    logger.warning(f"Error processing event from {source_url}: {e}")
                    continue

        logger.info(f"Extracted {len(events)} events from {source_url}")
        return events

    def extract(
        self, source: str | Dict, feed_name: Optional[str] = None
    ) -> List[EventNormalized]:
        url = source if isinstance(source, str) else source.get("url")
        name = feed_name or (source.get("name") if isinstance(source, dict) else None)

        if not url:
            return []

        calendar = self.fetch_feed(url)
        if calendar:
            return self.extract_events_from_calendar(calendar, url, name)
        return []
