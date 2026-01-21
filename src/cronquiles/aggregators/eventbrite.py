import json
import logging
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from .base import BaseAggregator
from ..models import EventNormalized

logger = logging.getLogger(__name__)


class EventbriteExtractor:
    """
    Extractor de eventos de Eventbrite que utiliza el structured data (JSON-LD)
    embebido en las páginas de eventos y organizadores.
    """

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        # Headers para parecer un navegador real
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "es-419,es;q=0.9,en;q=0.8",
            }
        )

    def extract_from_url(self, url: str) -> List[Dict]:
        """
        Extrae eventos de una URL de Eventbrite.
        Detecta automáticamente si es una página de evento único o de organizador.

        Args:
            url: URL de Eventbrite

        Returns:
            Lista de diccionarios con datos de eventos
        """
        try:
            logger.info(f"Fetching Eventbrite URL: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            json_ld_scripts = soup.find_all("script", type="application/ld+json")

            if not json_ld_scripts:
                logger.warning(f"No JSON-LD found in {url}")
                return []

            events = []
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    extracted = self._process_json_ld(data, source_url=url)
                    events.extend(extracted)
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    logger.warning(f"Error processing JSON-LD block: {e}")
                    continue

            # Filtro por país (México)
            mx_events = [e for e in events if self._is_in_mexico(e)]

            logger.info(
                f"Extracted {len(mx_events)} events from {url} (Total found: {len(events)})"
            )
            return mx_events

        except Exception as e:
            logger.error(f"Error extracting from Eventbrite {url}: {e}")
            return []

    def _process_json_ld(self, data: Dict, source_url: str) -> List[Dict]:
        """Procesa un objeto JSON-LD y extrae eventos."""
        events = []

        # Caso 1: Array de objetos
        if isinstance(data, list):
            for item in data:
                events.extend(self._process_json_ld(item, source_url))
            return events

        # Caso 2: Objeto único
        node_type = data.get("@type")

        # Si es un evento directo
        if self._is_event_type(node_type):
            event = self._parse_single_event(data)
            if event:
                events.append(event)

        # Si es una lista de items (común en páginas de organizador)
        elif node_type == "ItemList" and "itemListElement" in data:
            for item in data["itemListElement"]:
                # itemListElement puede ser el evento directo o un wrapper
                item_data = item.get("item", item)
                events.extend(self._process_json_ld(item_data, source_url))

        # Si es un grafo (común en Yoast SEO y otros)
        elif "@graph" in data:
            for item in data["@graph"]:
                events.extend(self._process_json_ld(item, source_url))

        return events

    def _is_event_type(self, node_type: str) -> bool:
        """Verifica si el tipo JSON-LD corresponde a un evento."""
        if not node_type:
            return False
        event_types = {
            "Event",
            "BusinessEvent",
            "SocialEvent",
            "EducationEvent",
            "PublicationEvent",
        }
        if isinstance(node_type, list):
            return any(t in event_types for t in node_type)
        return node_type in event_types

    def _parse_single_event(self, data: Dict) -> Optional[Dict]:
        """Parsea un objeto de evento Schema.org a nuestro formato interno."""
        try:
            url = data.get("url", "")
            if not url:
                return None

            # Extraer location details
            location_data = data.get("location", {})
            address_data = {}
            location_name = ""

            if isinstance(location_data, dict):
                location_name = location_data.get("name", "")
                address = location_data.get("address", {})
                if isinstance(address, dict):
                    address_data = address

            # Construir string de ubicación legible
            location_str = location_name
            street = address_data.get("streetAddress", "")
            locality = address_data.get("addressLocality", "")
            region = address_data.get("addressRegion", "")

            addr_parts = [p for p in [location_name, street, locality, region] if p]
            if addr_parts:
                location_str = ", ".join(addr_parts)

            # Si es online
            if (
                data.get("eventAttendanceMode")
                == "https://schema.org/OnlineEventAttendanceMode"
            ):
                location_str = "Online"

            # Fechas
            start_date = data.get("startDate")
            end_date = data.get("endDate")

            # Organizador
            organizer = data.get("organizer", {})
            organizer_name = ""
            if isinstance(organizer, dict):
                organizer_name = organizer.get("name", "")
            elif isinstance(organizer, str):
                organizer_name = organizer

            return {
                "title": data.get("name", ""),
                "description": data.get("description", ""),
                "url": url,
                "dtstart": start_date,
                "dtend": end_date,
                "location": location_str,
                "organizer": organizer_name,
                "source": "Eventbrite",
                "country_code": address_data.get("addressCountry", ""),
                # Guardamos raw data útil para filtros
                "_address_country": address_data.get("addressCountry", ""),
            }
        except Exception as e:
            logger.warning(f"Error parsing event data: {e}")
            return None

    def _is_in_mexico(self, event: Dict) -> bool:
        """Verifica si el evento es en México."""
        # 1. Checar código de país explícito
        country = event.get("_address_country", "")
        if country in ["MX", "MEX", "Mexico", "México"]:
            return True

        # 2. Si es Online, lo incluimos (asumimos que la comunidad es relevante)
        if event.get("location") == "Online":
            return True

        # 3. Fallback: Checar texto de ubicación
        loc_lower = event.get("location", "").lower()
        if "mexico" in loc_lower or "méxico" in loc_lower or "cdmx" in loc_lower:
            return True

        return False


class EventbriteAggregator(BaseAggregator):
    """Aggregator for Eventbrite URLs (Organizers or Single Events)."""

    def __init__(self, session=None):
        super().__init__(session)
        self.extractor = EventbriteExtractor(self.session)

    def extract(
        self, source: str | Dict, feed_name: Optional[str] = None
    ) -> List[EventNormalized]:
        url = source if isinstance(source, str) else source.get("url")
        name = feed_name or (source.get("name") if isinstance(source, dict) else None)

        if not url:
            return []

        logger.info(f"Processing Eventbrite URL: {url}")
        events = []
        try:
            raw_data = self.extractor.extract_from_url(url)
            for data in raw_data:
                try:
                    # Use provided name as organizer if missing
                    if name and not data.get("organizer"):
                        data["organizer"] = name

                    data["source"] = "Eventbrite"
                    event_norm = EventNormalized.from_dict(data)
                    event_norm.feed_name = name
                    events.append(event_norm)
                except Exception as e:
                    logger.error(f"Error converting Eventbrite event from {url}: {e}")
        except Exception as e:
            logger.error(f"Failed to process Eventbrite feed {url}: {e}")

        return events
