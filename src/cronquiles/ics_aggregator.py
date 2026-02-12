"""
ICS Aggregator - Agregador de feeds ICS públicos para eventos tech en México.

Este módulo consume múltiples feeds ICS, normaliza eventos, los deduplica
y genera un calendario unificado.
"""

import logging
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import requests
from dateutil import tz
from icalendar import Calendar
from urllib.parse import urlparse, parse_qs
import re

# Import models & history
from .models import EventNormalized
from .history_manager import HistoryManager

# Import Aggregators
from .aggregators.eventbrite import EventbriteAggregator
from .aggregators.luma import LumaAggregator
from .aggregators.meetup import MeetupAggregator
from .aggregators.ics import GenericICSAggregator
from .aggregators.manual import ManualAggregator
from .aggregators.hievents import HiEventsAggregator
from .aggregators.gdgcommunitydev import GdgCommunityDev
from .schemas import JSONOutputSchema, CommunitySchema, CommunityLinkSchema

# Configurations
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def extract_community_url(feed_url: str) -> str:
    """
    Extrae la URL navegable de una comunidad a partir de la URL del feed ICS.

    Transformaciones:
    - meetup.com/{slug}/events/ical → https://www.meetup.com/{slug}
    - luma.com/{slug} o lu.ma/{slug} → mantener como está
    - api2.luma.com/ics/get?entity=calendar&id={id} → https://lu.ma/{id}
    - eventbrite.com/o/{org-id} → mantener como está
    - eventbrite.com/e/{event-id} → mantener como está
    - Otros → usar como está

    Args:
        feed_url: URL del feed de la comunidad

    Returns:
        URL navegable de la comunidad
    """
    if not feed_url:
        return ""

    parsed = urlparse(feed_url)
    host = parsed.netloc.lower()
    path = parsed.path

    # Meetup: extraer slug del grupo
    if "meetup.com" in host:
        # Patrón: /slug/events/ical o /slug/events/
        match = re.match(r'^/([^/]+)/events/?(?:ical)?$', path)
        if match:
            slug = match.group(1)
            return f"https://www.meetup.com/{slug}"
        # Si no coincide, devolver la URL sin /events/ical
        clean_path = re.sub(r'/events/?(?:ical)?$', '', path)
        return f"https://www.meetup.com{clean_path}"

    # Luma API: extraer ID del calendario
    if "api2.luma.com" in host:
        # Patrón: /ics/get?entity=calendar&id={id}
        query_params = parse_qs(parsed.query)
        calendar_id = query_params.get('id', [''])[0]
        if calendar_id:
            return f"https://lu.ma/{calendar_id}"
        return feed_url

    # lu.ma o luma.com directo: mantener como está
    if "lu.ma" in host or "luma.com" in host:
        return feed_url

    # Eventbrite: mantener como está
    if "eventbrite." in host:
        return feed_url

    # Otros (ICS genérico, etc.): mantener como está
    return feed_url


def detect_platform_from_url(url: str) -> str:
    """
    Detecta la plataforma a partir del patrón de URL.

    Args:
        url: URL de la comunidad

    Returns:
        Identificador de plataforma: "meetup", "luma", "eventbrite", o "website"
    """
    if not url:
        return "website"
    url_lower = url.lower()
    if "meetup.com" in url_lower:
        return "meetup"
    if "lu.ma" in url_lower or "luma.com" in url_lower or "api2.luma.com" in url_lower:
        return "luma"
    if "eventbrite.com" in url_lower or "eventbrite.com.mx" in url_lower:
        return "eventbrite"
    return "website"


def get_platform_label_for_community(platform: str) -> str:
    """
    Obtiene la etiqueta de visualización para la plataforma de comunidad.

    Args:
        platform: Identificador de plataforma

    Returns:
        Etiqueta legible para mostrar en la UI
    """
    labels = {
        "meetup": "Meetup",
        "luma": "Luma",
        "eventbrite": "Eventbrite",
        "website": "Sitio web"
    }
    return labels.get(platform, "Sitio web")


def _aggregator_key_for_url(url: str) -> str:
    """Devuelve la clave del agregador para una URL de feed (eventbrite, luma, meetup, hievents, ics)."""
    if not url:
        return "ics"
    if (
        "eventbrite." in url
        and "/e/" not in url
        and "/o/" not in url
        and "ical" not in url
    ):
        return "eventbrite"
    if "eventbrite." in url and (
        "eventbrite.com" in url or "eventbrite.com.mx" in url
    ):
        return "eventbrite"
    if "lu.ma" in url or "luma.com" in url:
        return "luma"
    if "meetup.com" in url:
        return "meetup"
    if "/reuniones." in url or "hi.events" in url:
        return "hievents"
    if "gdg.community.dev" in url:
        return "gdgcommunitydev"
    return "ics"


def _extract_one_feed(
    feed: Any,
    name: Optional[str],
    agg_key: str,
    luma_url_cache: Dict,
    timeout: int = 30,
    max_retries: int = 2,
    skip_enrich: bool = False,
) -> List[EventNormalized]:
    """
    Extrae eventos de un solo feed (para ejecución en paralelo).
    Crea su propia sesión HTTP para ser thread-safe.
    """
    session = requests.Session()
    session.headers.update({"User-Agent": "Cron-Quiles-ICS-Aggregator/1.0"})
    if agg_key == "eventbrite":
        agg = EventbriteAggregator(session)
    elif agg_key == "luma":
        agg = LumaAggregator(
            session, timeout, max_retries, luma_url_cache, skip_enrich=skip_enrich
        )
    elif agg_key == "meetup":
        agg = MeetupAggregator(
            session, timeout, max_retries, skip_enrich=skip_enrich
        )
    elif agg_key == "hievents":
        agg = HiEventsAggregator(session)
    elif agg_key == "gdgcommunitydev":
        agg = GdgCommunityDev(session)
    else:
        agg = GenericICSAggregator(session, timeout, max_retries)
    try:
        return agg.extract(feed, name)
    except Exception as e:
        url = feed if isinstance(feed, str) else (feed.get("url") or "")
        logger.error("Error extracting from %s: %s", url, e)
        return []


class ICSAggregator:
    """
    Orchestrator for event aggregation.
    Delegates fetching and extraction to specific aggregators based on source type.
    Handles deduplication, healing, history management, and output generation.
    """

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 2,
        feed_workers: int = 10,
        fast_mode: bool = False,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.feed_workers = max(1, min(feed_workers, 20))
        self.fast_mode = fast_mode
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Cron-Quiles-ICS-Aggregator/1.0"})

        self.geocoding_cache = {}
        self.cache_file = Path("data/geocoding_cache.json")
        self.load_geocoding_cache()

        # Cache de URLs de Luma (conversiones y vanity URLs)
        self.luma_url_cache_file = Path("data/luma_url_cache.json")
        self.luma_url_cache = {"url_conversions": {}, "vanity_urls": {}}
        self.load_luma_url_cache()

        self.history_manager = HistoryManager()

        # Initialize specific aggregators
        self.aggregators = {
            "eventbrite": EventbriteAggregator(self.session),
            "luma": LumaAggregator(
                self.session, timeout, max_retries, self.luma_url_cache
            ),
            "meetup": MeetupAggregator(self.session, timeout, max_retries),
            "ics": GenericICSAggregator(self.session, timeout, max_retries),
            "manual": ManualAggregator(self.session),
            "hievents": HiEventsAggregator(self.session),
        }

    def load_geocoding_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.geocoding_cache = json.load(f)
                logger.info(
                    f"Loaded {len(self.geocoding_cache)} entries from geocoding cache."
                )
            except Exception as e:
                logger.warning(f"Could not load geocoding cache: {e}")
                self.geocoding_cache = {}

    def save_geocoding_cache(self):
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.geocoding_cache, f, ensure_ascii=False, indent=2)
            logger.info(
                f"Saved {len(self.geocoding_cache)} entries to geocoding cache."
            )
        except Exception as e:
            logger.warning(f"Could not save geocoding cache: {e}")

    def load_luma_url_cache(self):
        """Carga el cache de URLs de Luma desde disco."""
        if self.luma_url_cache_file.exists():
            try:
                with open(self.luma_url_cache_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        self.luma_url_cache = {
                            "url_conversions": loaded.get("url_conversions", {}),
                            "vanity_urls": loaded.get("vanity_urls", {}),
                        }
                        conv_count = len(self.luma_url_cache["url_conversions"])
                        vanity_count = len(self.luma_url_cache["vanity_urls"])
                        logger.info(
                            f"Loaded {conv_count} URL conversions and "
                            f"{vanity_count} vanity URLs from Luma cache."
                        )
            except Exception as e:
                logger.warning(f"Could not load Luma URL cache: {e}")
                self.luma_url_cache = {"url_conversions": {}, "vanity_urls": {}}

    def save_luma_url_cache(self):
        """Guarda el cache de URLs de Luma a disco."""
        try:
            self.luma_url_cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.luma_url_cache_file, "w", encoding="utf-8") as f:
                json.dump(self.luma_url_cache, f, ensure_ascii=False, indent=2)
            conv_count = len(self.luma_url_cache["url_conversions"])
            vanity_count = len(self.luma_url_cache["vanity_urls"])
            logger.info(
                f"Saved {conv_count} URL conversions and "
                f"{vanity_count} vanity URLs to Luma cache."
            )
        except Exception as e:
            logger.warning(f"Could not save Luma URL cache: {e}")

    def deduplicate_events(
        self, events: List[EventNormalized], time_tolerance_hours: int = 2
    ) -> List[EventNormalized]:
        """
        Deduplica eventos agrupándolos por hash_key (título + bloque de tiempo).
        Combina las URLs de eventos duplicados en el campo sources.
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

                # Combinar URLs alternativas en el campo sources
                for duplicate in group[1:]:
                    for dup_url in duplicate.sources:
                        if (
                            dup_url
                            and dup_url.startswith("http")
                            and dup_url not in selected.sources
                        ):
                            selected.sources.append(dup_url)

                logger.info(
                    f"Deduplicado: conservado '{selected.original_event.get('summary', '')}' "
                    f"de {len(group)} eventos similares (fuentes: {len(selected.sources)})"
                )
                deduplicated.append(selected)

        logger.info(f"Deduplicación: {len(events)} -> {len(deduplicated)} eventos")
        return deduplicated

    def aggregate_feeds(
        self, feed_urls: List[str], manual_data: Optional[List[Dict]] = None
    ) -> List[EventNormalized]:
        all_events = []

        # 1. Process config feeds (en paralelo)
        feed_tasks = []
        for feed in feed_urls:
            url = feed if isinstance(feed, str) else feed.get("url")
            name = None if isinstance(feed, str) else feed.get("name")
            if not url:
                continue
            agg_key = _aggregator_key_for_url(url)
            feed_tasks.append((feed, name, agg_key))

        if feed_tasks:
            logger.info(
                "Fetching %d feeds with %d workers...",
                len(feed_tasks),
                self.feed_workers,
            )
            with ThreadPoolExecutor(max_workers=self.feed_workers) as executor:
                futures = {
                    executor.submit(
                        _extract_one_feed,
                        feed,
                        name,
                        agg_key,
                        self.luma_url_cache,
                        self.timeout,
                        self.max_retries,
                        self.fast_mode,
                    ): (feed, name)
                    for feed, name, agg_key in feed_tasks
                }
                for future in as_completed(futures):
                    try:
                        events = future.result()
                        all_events.extend(events)
                    except Exception as e:
                        feed, name = futures[future]
                        url = feed if isinstance(feed, str) else feed.get("url")
                        logger.error("Error extracting from %s: %s", url, e)

        # 2. Process manual events
        if manual_data:
            events = self.aggregators["manual"].extract(manual_data)
            all_events.extend(events)

        # 2.5 Filter events by country (Only Mexico or Online)
        before_filter_count = len(all_events)
        all_events = [e for e in all_events if e.country_code == "MX" or e._is_online()]
        if len(all_events) < before_filter_count:
            logger.info(
                f"Filtered out {before_filter_count - len(all_events)} non-Mexico / non-Online events."
            )

        # 3. Geocoding (Healing) Phase 1 - Live Events
        to_geocode = [
            e
            for e in all_events
            if not e._is_online() and (not e.state_code or not e.city)
        ]
        if to_geocode:
            logger.info(f"Geocoding {len(to_geocode)} new events...")
            for event in to_geocode:
                _, used_api = event.geocode_location(self.geocoding_cache)
                if used_api:
                    time.sleep(1.1)
            self.save_geocoding_cache()
            self.save_luma_url_cache()

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
        # En fast_mode se omite para reducir tiempo (los datos ya vienen de caché/historial).
        to_geocode_final = [
            e
            for e in final_events
            if not e._is_online() and (not e.state_code or not e.city)
        ]
        if to_geocode_final and not self.fast_mode:
            max_to_geocode = 100
            to_process = to_geocode_final[:max_to_geocode]
            logger.info(f"Healing location data: Geocoding {len(to_process)} events...")

            for event in to_process:
                success, used_api = event.geocode_location(self.geocoding_cache)
                if used_api:
                    time.sleep(1.1)
                if success:
                    # Update history immediately for persistence
                    key = event.hash_key
                    self.history_manager.events[key] = event.to_dict()

            self.history_manager.save_history()
            self.save_geocoding_cache()
            self.save_luma_url_cache()

        # 7. Final Sort and Deduplication
        final_events.sort(
            key=lambda e: e.dtstart or datetime.max.replace(tzinfo=tz.UTC)
        )
        if final_events:
            final_events = self.deduplicate_events(final_events)

            # Sync back to history manager to ensure consistency with latest deduplication logic
            self.history_manager.events = {}
            for event in final_events:
                dict_val = event.to_dict()
                key = (
                    dict_val.get("hash_key")
                    or f"{dict_val['title']}_{dict_val['dtstart']}"
                )
                self.history_manager.events[key] = dict_val
            self.history_manager.save_history()

        logger.info(f"Final aggregated count (History + Live): {len(final_events)}")
        return final_events

    def group_events_by_state(
        self, events: List[EventNormalized]
    ) -> Dict[str, List[EventNormalized]]:
        grouped = {}
        for event in events:
            code = event.state_code if event.state_code else "ONLINE"
            if code not in grouped:
                grouped[code] = []
            grouped[code].append(event)
        return grouped

    def generate_ics(
        self,
        events: List[EventNormalized],
        output_file: str = "cronquiles.ics",
        city_name: Optional[str] = None,
    ) -> str:
        calendar = Calendar()
        calendar.add("prodid", "-//Cron-Quiles//ICS Aggregator//EN")
        calendar.add("version", "2.0")
        calendar.add("calscale", "GREGORIAN")

        if city_name:
            calendar.add("X-WR-CALNAME", f"Eventos Tech {city_name} - cronquiles")
            calendar.add(
                "X-WR-CALDESC",
                f"Calendario unificado de eventos tech en {city_name}, México",
            )
        else:
            calendar.add("X-WR-CALNAME", "Eventos Tech México - cronquiles")
            calendar.add(
                "X-WR-CALDESC", "Calendario unificado de eventos tech en México"
            )
        calendar.add("X-WR-TIMEZONE", "America/Mexico_City")

        for event_norm in events:
            calendar.add_component(event_norm.to_ical_event())

        with open(output_file, "wb") as f:
            f.write(calendar.to_ical())

        logger.info(f"Generated ICS file: {output_file} with {len(events)} events")
        return output_file

    def generate_json(
        self,
        events: List[EventNormalized],
        output_file: str = "cronquiles.json",
        city_name: Optional[str] = None,
        feeds: Optional[List[Dict]] = None,
    ) -> str:
        # Obtener cache de URLs vanity de Luma (si está disponible)
        luma_vanity_cache = getattr(
            self.aggregators.get("luma"), "vanity_url_cache", {}
        )

        # Agrupar comunidades por nombre y recolectar todos sus enlaces
        # (misma comunidad puede tener múltiples feeds en diferentes plataformas)
        community_data: Dict[str, Dict] = {}
        for f in feeds or []:
            if isinstance(f, dict) and f.get("name"):
                name = f.get("name", "")
                feed_url = f.get("url", "")

                if name not in community_data:
                    community_data[name] = {
                        "description": f.get("description", ""),
                        "links": []
                    }

                # Extraer URL navegable y detectar plataforma
                if feed_url:
                    # Prioridad: 1) community_url explícita, 2) cache de Luma, 3) extraer de feed_url
                    explicit_community_url = f.get("community_url")
                    if explicit_community_url:
                        community_url = explicit_community_url
                    elif feed_url in luma_vanity_cache:
                        community_url = luma_vanity_cache[feed_url]
                    else:
                        community_url = extract_community_url(feed_url)
                    platform = detect_platform_from_url(explicit_community_url or feed_url)
                    label = get_platform_label_for_community(platform)

                    # No agregar links de Luma con formato cal-xxx (no funcionan como landing pages)
                    if platform == "luma" and "/cal-" in community_url:
                        continue

                    # Agregar link solo si no existe ya (evitar duplicados)
                    existing_urls = [link["url"] for link in community_data[name]["links"]]
                    if community_url and community_url not in existing_urls:
                        community_data[name]["links"].append(
                            CommunityLinkSchema(
                                platform=platform,
                                url=community_url,
                                label=label
                            )
                        )

        # Construir lista de comunidades con sus enlaces
        communities_list = [
            CommunitySchema(
                name=name,
                description=data["description"],
                links=data["links"]
            )
            for name, data in community_data.items()
        ]

        events_data: JSONOutputSchema = {
            "generated_at": datetime.now(tz.UTC).isoformat(),
            "total_events": len(events),
            "city": city_name,
            "communities": communities_list,
            "events": [event.to_dict() for event in events],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(events_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Generated JSON file: {output_file} with {len(events)} events")
        return output_file
