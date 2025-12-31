"""
ICS Aggregator - Agregador de feeds ICS públicos para eventos tech en México.

Este módulo consume múltiples feeds ICS, normaliza eventos, los deduplica
y genera un calendario unificado.
"""

import logging
import re
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import requests
from dateutil import parser, tz
from dateutil.rrule import rrulestr
from icalendar import Calendar, Event, vText

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fix_encoding(text: str) -> str:
    """
    Corrige problemas comunes de codificación (mojibake).

    Detecta y corrige casos donde texto UTF-8 fue interpretado como Latin-1.
    Ejemplo: "CariÃ±o" -> "Cariño"

    Args:
        text: String que puede tener problemas de codificación

    Returns:
        String con codificación corregida
    """
    if not isinstance(text, str):
        return text

    # Detectar si hay caracteres de mojibake comunes
    if "Ã" in text:
        try:
            # Intentar decodificar como latin-1 y recodificar como UTF-8
            # Esto corrige el problema de mojibake
            fixed = text.encode("latin-1").decode("utf-8")
            return fixed
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Si falla, devolver el texto original
            pass

    return text


# Keywords para tags automáticos
TAG_KEYWORDS = {
    "python": ["python", "py", "django", "flask", "fastapi"],
    "ai": [
        "ai",
        "artificial intelligence",
        "machine learning",
        "ml",
        "deep learning",
        "neural",
    ],
    "cloud": ["aws", "azure", "gcp", "cloud", "serverless", "lambda"],
    "devops": [
        "devops",
        "docker",
        "kubernetes",
        "k8s",
        "ci/cd",
        "terraform",
        "ansible",
    ],
    "data": ["data", "big data", "spark", "hadoop", "analytics", "data science"],
    "security": ["security", "sec", "cybersecurity", "pentest", "hacking"],
    "mobile": ["mobile", "android", "ios", "flutter", "react native"],
    "web": ["web", "html", "javascript", "js", "react", "vue", "angular"],
    "backend": ["backend", "api", "rest", "graphql", "microservices"],
    "frontend": ["frontend", "front-end", "ui", "ux", "design"],
}


class EventNormalized:
    """
    Representa un evento normalizado para comparación y deduplicación.

    Esta clase normaliza eventos de diferentes fuentes ICS y los formatea
    según un estándar consistente. Incluye:
    - Detección automática de eventos online vs presenciales
    - Extracción inteligente del nombre del grupo/organizador
    - Extracción de país y estado para eventos presenciales
    - Formato de título estructurado: Grupo|Nombre evento|Online o Grupo|Nombre evento|País|Estado
    - Normalización de títulos para deduplicación
    - Extracción automática de tags basados en keywords
    """

    def __init__(self, event: Event, source_url: str):
        self.original_event = event
        self.source_url = source_url

        # Extraer y normalizar campos
        self.title = self._normalize_title(event.get("summary", ""))
        self.description = str(event.get("description", ""))
        self.url = str(event.get("url", "")) if event.get("url") else ""
        self.location = str(event.get("location", "")) if event.get("location") else ""
        # Si no hay location en el feed, intentar extraer de la descripción
        if not self.location or not self.location.strip():
            self.location = self._extract_location_from_description()
        self.organizer = self._extract_organizer(event)

        # Manejar fechas con timezone
        self.dtstart = self._extract_datetime(event.get("dtstart"))
        self.dtend = self._extract_datetime(event.get("dtend"))

        # Calcular hash para deduplicación
        self.hash_key = self._compute_hash()

        # Tags automáticos
        self.tags = self._extract_tags()

    def _normalize_title(self, title: str) -> str:
        """Normaliza el título: lowercase, sin emojis, sin puntuación extra."""
        if not title:
            return ""

        # Remover emojis (caracteres Unicode fuera del rango ASCII básico)
        title = re.sub(r"[^\x00-\x7F]+", "", title)

        # Convertir a lowercase
        title = title.lower()

        # Remover puntuación extra pero mantener espacios
        title = re.sub(r"[^\w\s-]", "", title)

        # Normalizar espacios múltiples
        title = re.sub(r"\s+", " ", title).strip()

        return title

    def _extract_organizer(self, event: Event) -> str:
        """Extrae el organizador del evento."""
        organizer = event.get("organizer")
        if organizer:
            if isinstance(organizer, vText):
                return str(organizer)
            elif hasattr(organizer, "params") and "CN" in organizer.params:
                return organizer.params["CN"]
        return ""

    def _extract_location_from_description(self) -> str:
        """Intenta extraer la ubicación de la descripción cuando no está en el feed."""
        if not self.description:
            return ""

        desc_lower = self.description.lower()
        desc_lines = self.description.split("\n")

        # Buscar patrones comunes de ubicación en la descripción
        location_patterns = [
            r"location:\s*(.+?)(?:\n|$)",
            r"ubicación:\s*(.+?)(?:\n|$)",
            r"dirección:\s*(.+?)(?:\n|$)",
            r"address:\s*(.+?)(?:\n|$)",
            r"venue:\s*(.+?)(?:\n|$)",
            r"lugar:\s*(.+?)(?:\n|$)",
        ]

        for pattern in location_patterns:
            match = re.search(pattern, desc_lower, re.IGNORECASE | re.MULTILINE)
            if match:
                location = match.group(1).strip()
                # Limpiar markdown y caracteres especiales
                location = re.sub(r"\*\*", "", location)
                location = re.sub(r"\\", "", location)
                if len(location) > 5:  # Asegurar que tiene contenido válido
                    return location

        # Buscar líneas que parezcan direcciones (contienen números, calles, colonias)
        for line in desc_lines[:20]:  # Revisar primeras 20 líneas
            line = line.strip()
            # Patrones que indican una dirección
            if any(
                keyword in line.lower()
                for keyword in [
                    "col.",
                    "colonia",
                    "calle",
                    "avenida",
                    "av.",
                    "piso",
                    "torre",
                ]
            ):
                if len(line) > 10 and len(line) < 200:
                    # Limpiar markdown
                    line = re.sub(r"\*\*", "", line)
                    line = re.sub(r"\\", "", line)
                    return line

        return ""

    def _extract_datetime(self, dt_value) -> Optional[datetime]:
        """Extrae datetime de un valor de evento, manejando timezones."""
        if not dt_value:
            return None

        if isinstance(dt_value.dt, datetime):
            dt = dt_value.dt
            # Si no tiene timezone, asumir UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz.UTC)
            return dt
        elif hasattr(dt_value, "dt"):
            # Fecha sin hora
            return None

        return None

    def _compute_hash(self) -> str:
        """Calcula un hash para deduplicación basado en título y fecha."""
        if not self.dtstart:
            return f"{self.title}_no_date"

        # Redondear hacia abajo al bloque de 2 horas más cercano
        # para tolerancia de ±2 horas
        # Esto agrupa eventos en ventanas de 2 horas:
        # 0-1, 2-3, 4-5, ..., 18-19, 20-21, 22-23
        hour = self.dtstart.hour
        # Redondear hacia abajo al número par más cercano (0, 2, 4, ..., 22)
        hour_block = (hour // 2) * 2
        hour_rounded = self.dtstart.replace(
            hour=hour_block, minute=0, second=0, microsecond=0
        )
        return f"{self.title}_{hour_rounded.isoformat()}"

    def _extract_tags(self) -> Set[str]:
        """Extrae tags automáticos basados en keywords."""
        tags = set()
        text_to_check = f"{self.title} {self.description}".lower()

        for tag, keywords in TAG_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_to_check:
                    tags.add(tag)
                    break

        return tags

    def _is_online(self) -> bool:
        """
        Detecta si el evento es online basado en location y descripción.

        Prioriza indicadores de eventos presenciales (in-person, direcciones físicas)
        sobre indicadores de eventos online. Si hay indicadores de ambos tipos,
        se considera presencial.

        Returns:
            True si el evento es online, False si es presencial
        """
        location_lower = self.location.lower()
        description_lower = self.description.lower()

        # Palabras clave que indican evento presencial (tienen prioridad)
        in_person_keywords = [
            "in-person",
            "in person",
            "presencial",
            "físico",
            "venue",
            "location:",
            "dirección:",
            "address:",
            "ubicación:",
            "casa",
            "centro",
            "sede",
            "oficina",
            "salón",
            "auditorio",
        ]

        # Si la descripción menciona "in-person" o direcciones, es presencial
        # incluso si también menciona streaming/YouTube
        for keyword in in_person_keywords:
            if keyword in description_lower:
                # Si dice "in-person and live on YouTube", es presencial
                return False

        # Si hay location explícita, probablemente es presencial
        if self.location and self.location.strip():
            # Verificar que no sea solo una URL
            if not self.location.strip().startswith("http"):
                return False

        # Si no hay location ni indicadores de presencial, probablemente es online
        if not self.location or not self.location.strip():
            return True

        # Palabras clave que indican evento online
        online_keywords = [
            "online",
            "virtual",
            "zoom",
            "meet",
            "google meet",
            "teams",
            "webinar",
            "streaming",
            "live stream",
            "youtube",
            "twitch",
            "discord",
            "slack",
            "webex",
        ]

        text_to_check = f"{location_lower} {description_lower}"
        for keyword in online_keywords:
            if keyword in text_to_check:
                return True

        return False

    def _extract_group(self) -> str:
        """
        Extrae el nombre del grupo/organizador del evento.

        Intenta extraer el nombre en este orden:
        1. Del campo organizer del evento
        2. De la descripción (patrones como "Nombre (Descripción)")
        3. De la URL del evento (ej: meetup.com/kong-mexico-city)
        4. De la URL fuente del feed

        Returns:
            Nombre del grupo o "Evento" si no se puede determinar
        """
        # Primero intentar del organizador
        if self.organizer:
            return self.organizer.strip()

        # Intentar extraer de la descripción (buscar patrones como "Grupo (Descripción)")
        if self.description:
            # Buscar patrones comunes: "Nombre (Descripción)" o "Nombre\n" al inicio
            # Ejemplo: "AI/IA CDMX (Ciudad de México Inteligencia Artificial)"
            desc_lines = self.description.split("\n")
            if desc_lines:
                first_line = desc_lines[0].strip()
                # Si la primera línea tiene formato "Nombre (Descripción)", usar todo
                if "(" in first_line and ")" in first_line:
                    # Extraer hasta el paréntesis de cierre
                    end_idx = first_line.find(")")
                    if end_idx > 0:
                        group_name = first_line[: end_idx + 1].strip()
                        if len(group_name) > 3:  # Asegurar que tiene contenido válido
                            return group_name
                # Si no, usar la primera línea si parece un nombre de grupo
                elif len(first_line) > 0 and len(first_line) < 100:
                    # Verificar que no sea solo una URL o texto muy largo
                    if not first_line.startswith("http") and "/" not in first_line:
                        return first_line

        # Intentar extraer de la URL (ej: meetup.com/kong-mexico-city)
        if self.url:
            parsed = urlparse(self.url)
            path_parts = [p for p in parsed.path.split("/") if p]
            if path_parts:
                # Para meetup: /kong-mexico-city/events/...
                if "meetup.com" in parsed.netloc and len(path_parts) > 0:
                    group_name = path_parts[0].replace("-", " ").title()
                    return group_name

        # Intentar extraer del source_url
        if self.source_url:
            parsed = urlparse(self.source_url)
            path_parts = [p for p in parsed.path.split("/") if p]
            if path_parts:
                if "meetup.com" in parsed.netloc and len(path_parts) > 0:
                    group_name = path_parts[0].replace("-", " ").title()
                    return group_name

        return "Evento"

    def _extract_country_state(self) -> Tuple[str, str]:
        """
        Extrae país y estado de la ubicación del evento.

        Tiene conocimiento especial de estados de México y puede inferir
        el estado desde nombres de ciudades comunes (ej: Guadalajara -> Jalisco).

        Returns:
            Tupla (país, estado) o ("", "") si no se puede extraer.
            Para México, retorna estados normalizados (ej: "CDMX", "Jalisco").
        """
        if not self.location or not self.location.strip():
            return ("", "")

        location = self.location.strip()

        # Intentar patrones comunes de ubicación
        # Formato: "Ciudad, Estado, País" o "Ciudad, Estado" o "Estado, País"
        # Para México: "Ciudad, CDMX" o "Ciudad, Estado de México"

        # Estados de México comunes
        estados_mexico = {
            "cdmx": "CDMX",
            "ciudad de méxico": "CDMX",
            "mexico city": "CDMX",
            "jalisco": "Jalisco",
            "nuevo león": "Nuevo León",
            "puebla": "Puebla",
            "quintana roo": "Quintana Roo",
            "yucatán": "Yucatán",
            "yucatan": "Yucatán",
            "estado de méxico": "Estado de México",
            "estado de mexico": "Estado de México",
            "guadalajara": "Jalisco",
            "monterrey": "Nuevo León",
        }

        location_lower = location.lower()

        # Buscar estado de México
        for key, estado in estados_mexico.items():
            if key in location_lower:
                return ("México", estado)

        # Si contiene "méxico" o "mexico" pero no encontramos estado
        if "méxico" in location_lower or "mexico" in location_lower:
            # Intentar extraer estado de la ubicación
            parts = [p.strip() for p in location.split(",")]
            if len(parts) >= 2:
                # Asumir que el penúltimo o último es el estado
                for part in reversed(parts[-2:]):
                    part_lower = part.lower()
                    for key, estado in estados_mexico.items():
                        if key in part_lower:
                            return ("México", estado)
                # Si no encontramos estado específico, usar el último
                return ("México", parts[-1].strip())
            return ("México", "")

        # Si no es México, intentar extraer país y estado
        parts = [p.strip() for p in location.split(",")]
        if len(parts) >= 2:
            # Último es probablemente el país
            country = parts[-1]
            # Penúltimo podría ser el estado
            state = parts[-2] if len(parts) >= 2 else ""
            return (country, state)

        return ("", "")

    def _format_title(self) -> str:
        """
        Formatea el título según el nuevo formato:
        - Físico: Grupo|Nombre evento|País|Estado
        - Online: Grupo|Nombre evento|Online
        """
        grupo = self._extract_group()
        nombre_evento = str(self.original_event.get("summary", "")).strip()

        if not nombre_evento:
            nombre_evento = "Evento sin título"

        if self._is_online():
            return f"{grupo}|{nombre_evento}|Online"
        else:
            pais, estado = self._extract_country_state()
            if pais and estado:
                return f"{grupo}|{nombre_evento}|{pais}|{estado}"
            elif pais:
                return f"{grupo}|{nombre_evento}|{pais}|"
            else:
                # Si es presencial pero no tenemos ubicación, intentar inferir de la descripción/URL
                # Si el grupo menciona CDMX o la URL es de México, usar México|CDMX
                grupo_lower = grupo.lower()
                desc_lower = self.description.lower()
                url_lower = (self.url + " " + self.source_url).lower()

                if any(
                    keyword in grupo_lower + desc_lower + url_lower
                    for keyword in ["cdmx", "ciudad de méxico", "mexico city", "méxico"]
                ):
                    return f"{grupo}|{nombre_evento}|México|CDMX"
                else:
                    # Si no podemos determinar ubicación, usar Online por defecto
                    return f"{grupo}|{nombre_evento}|Online"

    def to_dict(self) -> Dict:
        """Convierte el evento normalizado a diccionario para JSON."""
        return {
            "title": self._format_title(),
            "description": self.description,
            "url": self.url,
            "location": self.location,
            "organizer": self.organizer,
            "dtstart": self.dtstart.isoformat() if self.dtstart else None,
            "dtend": self.dtend.isoformat() if self.dtend else None,
            "tags": list(self.tags),
            "source": self.source_url,
        }

    def to_ical_event(self) -> Event:
        """Convierte el evento normalizado de vuelta a Event de icalendar."""
        event = Event()

        # Usar el nuevo formato de título
        formatted_title = self._format_title()
        event.add("summary", fix_encoding(formatted_title))

        # Copiar otros campos del evento original con manejo correcto de codificación
        for key in [
            "description",
            "url",
            "location",
            "organizer",
            "dtstart",
            "dtend",
            "uid",
            "dtstamp",
            "created",
            "last-modified",
        ]:
            value = self.original_event.get(key)
            if value:
                # Corregir problemas de codificación en strings
                if isinstance(value, str):
                    value = fix_encoding(value)
                elif isinstance(value, vText):
                    # vText también puede tener problemas de codificación
                    fixed_str = fix_encoding(str(value))
                    value = vText(fixed_str)
                event.add(key, value)

        # Agregar tags como categorías si existen
        if self.tags:
            event.add("categories", list(self.tags))

        return event

    def enrich_location_from_meetup(self, session: requests.Session) -> bool:
        """
        Intenta extraer la ubicación detallada de la página de Meetup.

        Args:
            session: Sesión de requests para realizar la petición

        Returns:
            True si se pudo extraer/mejorar la ubicación
        """
        if "meetup.com" not in self.url:
            return False

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            logger.info(f"Enriching location from Meetup: {self.url}")
            response = session.get(self.url, headers=headers, timeout=10)
            if response.status_code != 200:
                return False

            html = response.text

            # 1. Intentar con JSON-LD (application/ld+json)
            # Usamos regex para evitar dependencias de BS4
            json_ld_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
            for jld_text in json_ld_matches:
                try:
                    data = json.loads(jld_text)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if item.get("@type") == "Event" and "location" in item:
                            loc = item["location"]
                            name = loc.get("name", "")
                            address = loc.get("address", {})

                            parts = []
                            if name and name != "Online Event":
                                parts.append(name)

                            if isinstance(address, dict):
                                street = address.get("streetAddress", "")
                                city = address.get("addressLocality", "")
                                if street: parts.append(street)
                                if city: parts.append(city)
                            elif isinstance(address, str):
                                parts.append(address)

                            new_location = ", ".join(parts).strip()
                            if new_location and len(new_location) > len(self.location):
                                self.location = new_location
                                return True
                except:
                    continue

            # 2. Intentar con __NEXT_DATA__
            next_data_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
            if next_data_match:
                try:
                    data = json.loads(next_data_match.group(1))
                    event_data = data.get("props", {}).get("pageProps", {}).get("event", {})
                    venue = event_data.get("venue", {})
                    if venue:
                        name = venue.get("name", "")
                        addr = venue.get("address", "")
                        parts = []
                        if name: parts.append(name)
                        if addr: parts.append(addr)
                        new_location = ", ".join(parts).strip()
                        if new_location and len(new_location) > len(self.location):
                            self.location = new_location
                            return True
                except:
                    pass

        except Exception as e:
            logger.warning(f"Error enriching location from {self.url}: {e}")

        return False


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
        self, calendar: Calendar, source_url: str
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

                    event_norm = EventNormalized(component, source_url)
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
            feed_urls: Lista de URLs de feeds ICS

        Returns:
            Lista de eventos normalizados y deduplicados
        """
        all_events = []

        for url in feed_urls:
            calendar = self.fetch_feed(url)
            if calendar:
                events = self.extract_events(calendar, url)
                all_events.extend(events)

        # Enriquecer locaciones de Meetup (solo si no tienen locación o es muy corta)
        # Hacemos esto antes de deduplicar para mejorar la calidad de los datos
        meetup_events = [e for e in all_events if "meetup.com" in e.url and len(e.location) < 15]
        if meetup_events:
            logger.info(f"Found {len(meetup_events)} Meetup events to potentially enrich")
            for i, event in enumerate(meetup_events):
                # Pequeño delay para ser respetuosos (no scraping agresivo)
                if i > 0:
                    time.sleep(1)
                event.enrich_location_from_meetup(self.session)

        # Deduplicar
        deduplicated = self.deduplicate_events(all_events)

        # Ordenar por fecha
        deduplicated.sort(
            key=lambda e: e.dtstart or datetime.max.replace(tzinfo=tz.UTC)
        )

        return deduplicated

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
                {"name": f["name"], "description": f.get("description", "")}
                for f in (feeds or [])
            ],
            "events": [event.to_dict() for event in events],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(events_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Generated JSON file: {output_file} with {len(events)} events")
        return output_file
