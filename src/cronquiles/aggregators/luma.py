import logging
import re
import time
from typing import List, Optional, Dict
from .ics import GenericICSAggregator
from ..models import EventNormalized

logger = logging.getLogger(__name__)


class LumaAggregator(GenericICSAggregator):
    """Aggregator para feeds ICS de Luma con enriquecimiento de ubicación."""

    def _convert_luma_url_to_ics(self, url: str) -> str:
        """
        Convierte URLs de luma.com/calendar-name a formato API ICS.

        Si la URL ya es api2.luma.com/ics/..., la devuelve sin cambios.
        Si es luma.com/calendar-name, extrae el calendar ID del HTML.
        """
        # Ya es URL de API ICS
        if "api2.luma.com/ics" in url:
            return url

        # Intentar convertir luma.com/calendar-name a ICS URL
        if "luma.com/" in url or "lu.ma/" in url:
            try:
                logger.info(f"Convirtiendo URL de Luma a ICS: {url}")
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    html = response.text
                    # Buscar calendar ID en el HTML
                    # Patrón: app-argument=luma://calendar/cal-XXXXX
                    match = re.search(r'app-argument=luma://calendar/(cal-[a-zA-Z0-9]+)', html)
                    if match:
                        calendar_id = match.group(1)
                        ics_url = f"https://api2.luma.com/ics/get?entity=calendar&id={calendar_id}"
                        logger.info(f"Convertido a ICS URL: {ics_url}")
                        return ics_url
            except Exception as e:
                logger.warning(f"Error convirtiendo URL de Luma {url}: {e}")

        return url

    def extract(
        self, source: str | Dict, feed_name: Optional[str] = None
    ) -> List[EventNormalized]:
        # Convertir URL si es necesario
        if isinstance(source, str):
            source = self._convert_luma_url_to_ics(source)
        elif isinstance(source, dict) and "url" in source:
            source["url"] = self._convert_luma_url_to_ics(source["url"])

        events = super().extract(source, feed_name)

        # Enrich events needing location
        to_enrich = [
            e
            for e in events
            if e.url
            and ("lu.ma" in e.url or "luma.com" in e.url)
            and (
                not e.location
                or "Check event page" in e.location
                or len(e.location) < 15
                or e.location.strip().startswith("http")
            )
        ]

        if to_enrich:
            logger.info(f"Found {len(to_enrich)} Luma events to potentially enrich")
            for i, event in enumerate(to_enrich):
                if i > 0:
                    time.sleep(1)
                try:
                    event.enrich_location_from_luma(self.session)
                except Exception as e:
                    logger.warning(f"Error enriching Luma event {event.url}: {e}")

        return events
