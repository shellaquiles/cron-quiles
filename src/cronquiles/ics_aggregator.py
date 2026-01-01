"""
ICS Aggregator - Agregador de feeds ICS públicos para eventos tech en México.

Este módulo consume múltiples feeds ICS, normaliza eventos, los deduplica
y genera un calendario unificado.
"""

import logging
import re
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests
from dateutil import tz
from icalendar import Calendar

# Importar modelo normalizado
from .models import EventNormalized

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ICSAggregator:
    """Agregador principal de feeds ICS."""

    def __init__(self, timeout: int = 30, max_retries: int = 2):
        """
        Inicializa el agregador.

        Args:
            timeout: Timeout en segundos para requests HTTP
            max_retries: Número máximo de reintentos por feed
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Cron-Quiles-ICS-Aggregator/1.0"})
        # Initialize HistoryManager
        from .history_manager import HistoryManager
        self.history_manager = HistoryManager()

    def fetch_feed(self, url: str) -> Optional[Calendar]:
        """
        Descarga y parsea un feed ICS.

        Args:
            url: URL del feed ICS

        Returns:
            Calendar object o None si falla
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching feed: {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                # Asegurar codificación UTF-8
                response.encoding = response.apparent_encoding or "utf-8"

                calendar = Calendar.from_ical(response.text)
                logger.info(f"Successfully parsed feed: {url}")
                return calendar

            except requests.exceptions.RequestException as e:
                logger.warning(f"Error fetching {url} (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    logger.error(
                        f"Failed to fetch feed after {self.max_retries} attempts: {url}"
                    )
                    return None
            except Exception as e:
                logger.error(f"Error parsing feed {url}: {e}")
                return None

        return None

    def extract_events(
        self, calendar: Calendar, source_url: str, feed_name: Optional[str] = None
    ) -> List[EventNormalized]:
        """
        Extrae y normaliza eventos de un calendario.

        Args:
            calendar: Calendar object de icalendar
            source_url: URL de origen del feed

        Returns:
            Lista de eventos normalizados
        """
        events = []

        # Si no se proporcionó un nombre de feed manual, intentar extraerlo del calendario
        if not feed_name:
             # X-WR-CALNAME es una propiedad no estándar pero muy común
             cal_name = calendar.get("X-WR-CALNAME")
             if cal_name:
                 # A veces es una lista de vText
                 if isinstance(cal_name, list):
                     cal_name = cal_name[0]

                 # Limpiar vText
                 if hasattr(cal_name, 'params'):
                     feed_name = str(cal_name)
                 else:
                     feed_name = str(cal_name)

                 # Limpiar bytes string representation b'...'
                 if "b'" in feed_name:
                     try:
                         # Intentar limpiar representación de bytes
                         feed_name = eval(feed_name).decode('utf-8', errors='ignore')
                     except:
                         pass

                 logger.info(f"Using X-WR-CALNAME as feed name: {feed_name}")

        for component in calendar.walk():
            if component.name == "VEVENT":
                try:
                    # Ignorar eventos cancelados
                    status = component.get("status", "").upper()
                    if status == "CANCELLED":
                        logger.debug(
                            f"Skipping cancelled event: {component.get('summary', '')}"
                        )
                        continue

                    event_norm = EventNormalized(component, source_url, feed_name)
                    events.append(event_norm)

                except Exception as e:
                    logger.warning(f"Error processing event from {source_url}: {e}")
                    continue

        logger.info(f"Extracted {len(events)} events from {source_url}")
        return events

    def deduplicate_events(
        self, events: List[EventNormalized], time_tolerance_hours: int = 2
    ) -> List[EventNormalized]:
        """
        Deduplica eventos similares.

        Estrategia:
        1. Agrupa por hash_key (título normalizado + hora redondeada)
        2. Para cada grupo, selecciona el mejor evento según:
           - URL válida
           - Descripción más larga

        Args:
            events: Lista de eventos normalizados
            time_tolerance_hours: Tolerancia en horas para considerar eventos duplicados

        Returns:
            Lista de eventos deduplicados
        """
        # Agrupar por hash_key
        events_by_hash: Dict[str, List[EventNormalized]] = {}

        for event in events:
            hash_key = event.hash_key
            if hash_key not in events_by_hash:
                events_by_hash[hash_key] = []
            events_by_hash[hash_key].append(event)

        # Seleccionar el mejor evento de cada grupo
        deduplicated = []

        for hash_key, group in events_by_hash.items():
            if len(group) == 1:
                deduplicated.append(group[0])
            else:
                # Ordenar por prioridad: URL válida > descripción más larga
                group.sort(
                    key=lambda e: (
                        bool(e.url and e.url.startswith("http")),  # URL válida
                        len(e.description),  # Descripción más larga
                    ),
                    reverse=True,
                )

                selected = group[0]

                # Recolectar URLs alternativas de otros eventos en el grupo
                alt_urls = set()
                primary_url = selected.url.strip() if selected.url else ""

                for duplicate in group[1:]:
                    dup_url = duplicate.url.strip() if duplicate.url else ""
                    if dup_url and dup_url.startswith("http") and dup_url != primary_url:
                        alt_urls.add(dup_url)

                # Si hay URLs alternativas, agregarlas a la descripción
                if alt_urls:
                    header = "\n\nOtras fuentes:"
                    # Evitar duplicar el header si ya existe
                    if header not in selected.description:
                         selected.description += header

                    for url in alt_urls:
                        if url not in selected.description:
                            selected.description += f"\n- {url}"

                logger.info(
                    f"Deduplicated: kept '{selected.original_event.get('summary', '')}' "
                    f"from {len(group)} similar events"
                )
                deduplicated.append(selected)

        logger.info(f"Deduplication: {len(events)} -> {len(deduplicated)} events")
        return deduplicated

    def aggregate_feeds(self, feed_urls: List[str]) -> List[EventNormalized]:
        """
        Agrega múltiples feeds ICS.

        Args:
            feed_urls: Lista de dicts [{'url': ..., 'name': ...}] o strings (compatibilidad)

        Returns:
            Lista de eventos normalizados y deduplicados
        """
        all_events = []

        for feed in feed_urls:
            # Manejar compatibilidad con lista de strings (por si acaso o tests)
            if isinstance(feed, str):
                url = feed
                name = None
            else:
                url = feed.get("url")
                name = feed.get("name")

            if not url:
                continue

            calendar = self.fetch_feed(url)
            if calendar:
                events = self.extract_events(calendar, url, name)
                all_events.extend(events)

        # Enriquecer locaciones de Meetup (solo si no tienen locación o es muy corta)
        # Hacemos esto antes de deduplicar para mejorar la calidad de los datos
        meetup_events = [
            e for e in all_events if "meetup.com" in e.url and len(e.location) < 15
        ]
        if meetup_events:
            logger.info(
                f"Found {len(meetup_events)} Meetup events to potentially enrich"
            )
            for i, event in enumerate(meetup_events):
                # Pequeño delay para ser respetuosos (no scraping agresivo)
                if i > 0:
                    time.sleep(1)
                event.enrich_location_from_meetup(self.session)

        # Deduplicar nuevos eventos primero
        deduplicated_new = self.deduplicate_events(all_events)

        # Cargar historia
        self.history_manager.load_history()

        # Merge con historia
        # Esto actualiza la base de datos interna con lo nuevo
        self.history_manager.merge_events(deduplicated_new)

        # Guardar historia actualizada
        self.history_manager.save_history()

        # Obtener lista COMPLETA unificada (historia + nuevos) para generar el calendario
        all_dicts = self.history_manager.get_all_events()

        # Reconstruir objetos EventNormalized desde diccionarios para el resto del pipeline
        final_events = []
        for d in all_dicts:
            try:
                final_events.append(EventNormalized.from_dict(d))
            except Exception as e:
                logger.error(f"Error reconstructing event from history: {e}")

        # Ordenar por fecha
        final_events.sort(
            key=lambda e: e.dtstart or datetime.max.replace(tzinfo=tz.UTC)
        )

        # Filtrar duplicados nuevamente por si la reconstrucción genero traslapes con lógica distinta
        # (Aunque el hash debería encargarse de eso en el manager)
        # IMPORTANTE: HistoryManager usa keys distintas para eventos con título distinto
        # pero EventNormalized puede detectar que son duplicados.
        # Ejecutamos deduplicate_events una vez más sobre la lista final.
        if final_events:
             final_events = self.deduplicate_events(final_events)

        logger.info(f"Final aggregated count (History + Live): {len(final_events)}")

        return final_events

    def generate_ics(
        self,
        events: List[EventNormalized],
        output_file: str = "cronquiles.ics",
        city_name: Optional[str] = None,
    ) -> str:
        """
        Genera un archivo ICS unificado.

        Args:
            events: Lista de eventos normalizados
            output_file: Nombre del archivo de salida
            city_name: Nombre de la ciudad para incluir en los metadatos (opcional)

        Returns:
            Ruta del archivo generado
        """
        calendar = Calendar()
        calendar.add("prodid", "-//Cron-Quiles//ICS Aggregator//EN")
        calendar.add("version", "2.0")
        calendar.add("calscale", "GREGORIAN")

        # Incluir nombre de ciudad en los metadatos si está disponible
        if city_name:
            calendar.add("X-WR-CALNAME", f"Cron-Quiles - Eventos Tech {city_name}")
            calendar.add("X-WR-CALDESC", f"Calendario unificado de eventos tech en {city_name}, México")
        else:
            calendar.add("X-WR-CALNAME", "Cron-Quiles - Eventos Tech México")
            calendar.add("X-WR-CALDESC", "Calendario unificado de eventos tech en México")

        calendar.add("X-WR-TIMEZONE", "America/Mexico_City")

        for event_norm in events:
            event = event_norm.to_ical_event()
            calendar.add_component(event)

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
        """
        Genera un archivo JSON con los eventos.

        Args:
            events: Lista de eventos normalizados
            output_file: Nombre del archivo de salida
            city_name: Nombre de la ciudad para incluir en los metadatos (opcional)
            feeds: Lista de feeds configurados para incluir las comunidades (opcional)

        Returns:
            Ruta del archivo generado
        """
        import json

        events_data = {
            "generated_at": datetime.now(tz.UTC).isoformat(),
            "total_events": len(events),
            "city": city_name,
            "communities": [
                {"name": f.get("name"), "description": f.get("description", "")}
                for f in (feeds or [])
                if isinstance(f, dict) and f.get("name")
            ],
            "events": [event.to_dict() for event in events],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(events_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Generated JSON file: {output_file} with {len(events)} events")
        return output_file
