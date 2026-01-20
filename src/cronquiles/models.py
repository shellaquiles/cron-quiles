"""
EventNormalized Model - Modelo de datos para eventos normalizados.
"""

import logging
import os
import re
import json
from datetime import datetime
from typing import Dict, Optional, Set
from urllib.parse import urlparse

import pycountry
import requests
from unidecode import unidecode
from geopy.geocoders import Nominatim, GoogleV3
from geopy.exc import GeopyError
from dateutil import parser, tz
from icalendar import Event, vText
from .schemas import EventSchema

logger = logging.getLogger(__name__)

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


def slugify(text: str) -> str:
    """
    Convierte un texto en un slug simple (minúsculas, sin acentos ni caracteres especiales).
    """
    if not text:
        return ""

    # Usar unidecode para remover acentos y normalizar caracteres
    text = unidecode(text).lower().strip()

    # Remover todo lo que no sea alfanumérico y poner en minúsculas
    text = re.sub(r"[^\w\s-]", "", text)
    # Reemplazar espacios por nada (para city_code)
    return re.sub(r"[-\s]+", "", text)


def detect_platform(url: str) -> str:
    """
    Detecta la plataforma a partir del patrón de URL.

    Args:
        url: URL del evento

    Returns:
        Identificador de plataforma: "meetup", "luma", "eventbrite", o "website"
    """
    if not url:
        return "website"
    url_lower = url.lower()
    if "meetup.com" in url_lower:
        return "meetup"
    if "lu.ma" in url_lower or "luma.com" in url_lower:
        return "luma"
    if "eventbrite.com" in url_lower or "eventbrite.com.mx" in url_lower:
        return "eventbrite"
    return "website"


def get_platform_label(platform: str) -> str:
    """
    Obtiene la etiqueta de visualización para la plataforma.

    Args:
        platform: Identificador de plataforma de detect_platform()

    Returns:
        Etiqueta legible para mostrar en la UI
    """
    labels = {
        "meetup": "Ver en Meetup",
        "luma": "Ver en Luma",
        "eventbrite": "Ver en Eventbrite",
        "website": "Ver sitio web"
    }
    return labels.get(platform, "Ver sitio web")


def fix_encoding(text: str) -> str:
    """
    Corrige problemas comunes de codificación (mojibake).

    Detecta y corrige casos donde texto UTF-8 fue interpretado como Latin-1 o MacRoman.
    Ejemplo: "CariÃ±o" -> "Cariño", "M茅xico" -> "México"

    Args:
        text: String que puede tener problemas de codificación

    Returns:
        String con codificación corregida
    """
    if not isinstance(text, str) or not text:
        return text

    # 1. Corregir Mojibake común de UTF-8 como Latin-1 (ej: Ã© -> é)
    if "Ã" in text:
        try:
            # Intentar decodificar como latin-1 y recodificar como UTF-8
            return text.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    # 2. Corregir Mojibake específico observado en el cache (ej: 茅 -> é, 贸 -> ó)
    # Estos suelen ocurrir cuando UTF-8 se interpreta como una variante de Windows-1252 o similar
    # y luego se re-codifica incorrectamente.
    replacements = {
        "茅": "é",
        "贸": "ó",
        "谩": "á",
        "铆": "í",
        "煤": "ú",
        "帽": "ñ",
        "麓": "í",  # A veces el acento solo
        "√©": "é",  # MacRoman Mojibake
        "√°": "á",
        "√≠": "í",
        "√≥": "ó",
        "√∫": "ú",
        "√±": "ñ",
        "√ì": "Ó",
        "√Å": "Á",
        "¬∫": "º",  # Paseo -> P.º
        "¬": "",  # A veces queda solo el ¬ de un UTF-8 roto
    }

    # Solo aplicar si vemos que hay una mezcla sospechosa o caracteres típicos de mojibake
    # (No queremos romper texto que legítimamente use caracteres chinos si los hubiera,
    # aunque en este contexto de eventos en México es poco probable).
    if any(c in text for c in replacements.keys()):
        # Si contiene 'México' o 'Mexico' mal codificado, es casi seguro que necesita fix
        for corrupted, clean in replacements.items():
            text = text.replace(corrupted, clean)

    # 3. Eliminar caracteres de reemplazo e intentar limpiar basura residual
    if "\ufffd" in text:
        text = text.replace("\ufffd", "")
        # Si después de quitar el  quedaron caracteres chinos aislados en un texto que
        # claramente es español/inglés, es probable que sean ruido de codificación.
        # (Heurística simple para el contexto del proyecto).
        import re

        # Rango CJK: \u4e00-\u9fff
        if re.search(r"[\u4e00-\u9fff]", text):
            # Solo si el resto del texto parece occidental
            occidental = len(re.findall(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ]", text))
            if occidental > 5:
                text = re.sub(r"[\u4e00-\u9fff]", "", text)

    return text.strip()


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

    # Cache para subdivisiones (estados) de México
    _mx_subdivisions_cache: Optional[Dict[str, pycountry.db.Subdivision]] = None

    @classmethod
    def _get_mx_subdivisions_lookup(cls) -> Dict[str, pycountry.db.Subdivision]:
        """
        Construye una tabla de búsqueda dinámica para subdivisiones de México.
        """
        if cls._mx_subdivisions_cache is not None:
            return cls._mx_subdivisions_cache

        lookup = {}
        try:
            subs = pycountry.subdivisions.get(country_code="MX")
            for sub in subs:
                # Normalizar nombre base (ej: "Veracruz de Ignacio de la Llave" -> "veracruz")
                name_clean = cls._normalize_subdivision_name(sub.name)
                lookup[name_clean] = sub

                # También indexar por el código ISO después del guión (ej: "CMX" de "MX-CMX")
                code_part = sub.code.split("-")[1].lower()
                lookup[code_part] = sub

                # Indexar por el código ISO completo (ej: "MX-CMX")
                lookup[sub.code.lower()] = sub

                # Indexar por el nombre completo también por si acaso
                lookup[sub.name.lower()] = sub
        except Exception as e:
            logger.error(f"Error building subdivisions lookup: {e}")

        cls._mx_subdivisions_cache = lookup
        return lookup

    @staticmethod
    def _normalize_subdivision_name(name: str) -> str:
        """
        Limpia nombres de estados quitando acentos y sufijos largos oficiales.
        """
        # Lowercase y remover acentos con unidecode
        n = unidecode(name).lower().strip()

        # Remover sufijos comunes en MX
        suffixes = [
            " de ignacio de la llave",
            " de zaragoza",
            " de ocampo",
            " de juarez",
            " de madero",
        ]
        for s in suffixes:
            n = n.replace(s, "")

        return n.strip()

    @staticmethod
    @staticmethod
    def _clean_ical_property(prop_value) -> str:
        """
        Limpia una propiedad de icalendar que puede ser vText, lista, o bytes.

        Args:
            prop_value: Valor crudo del evento

        Returns:
            String limpio
        """
        if prop_value is None:
            return ""

        # Si es una lista (propiedades duplicadas), tomar la primera
        # Usamos check genérico por si icalendar devuelve un tipo custom list-like
        if not isinstance(prop_value, (str, bytes, vText)) and hasattr(
            prop_value, "__getitem__"
        ):
            try:
                # Intentar tomar el primero, si es válido
                prop_value = prop_value[0]
            except (IndexError, TypeError):
                pass

        # Convertir a string
        text = str(prop_value)

        # Limpiar representación de vText si se coló en el string
        # (Aunque str(vText) debería funcionar bien, a veces queda como representación)
        if "vText(" in text or "b'" in text:
            try:
                # Intentar extraer contenido de vText(b'...')
                # Regex busca: vText(b'CONTENIDO')
                match = re.search(r"vText\(b['\"](.*?)['\"]\)", text)
                if match:
                    bytes_str = match.group(1)
                    try:
                        # Hack seguro para decodificar unicode escapes
                        decoded = (
                            bytes(bytes_str, "utf-8")
                            .decode("unicode_escape")
                            .encode("latin-1")
                            .decode("utf-8")
                        )
                        text = decoded
                    except Exception:
                        text = bytes_str

                # Intentar limpiar si es solo una representación de bytes b'...'
                elif text.startswith("b'") or text.startswith('b"'):
                    text = eval(text).decode("utf-8", errors="ignore")

            except Exception:
                pass

        # Fix encoding general
        return fix_encoding(text)

    def __init__(self, event: Event, source_url: str, feed_name: Optional[str] = None):
        self.original_event = event
        self.source_url = source_url
        self.feed_name = feed_name

        # Extraer y normalizar campos usando el limpiador
        raw_summary = self._clean_ical_property(event.get("summary"))

        # [FIX] Reemplazar pipes por guiones para evitar truncamiento accidental
        # ya que usamos | como separador interno en nuestro formato
        if "|" in raw_summary:
            raw_summary = raw_summary.replace("|", " - ")

        # Guardar summary limpio para uso posterior (display)
        self.summary = raw_summary
        self.title = self._normalize_title(raw_summary)

        self.description = self._clean_ical_property(event.get("description"))
        self.url = str(event.get("url", "")) if event.get("url") else ""

        # Soporte multi-fuente: lista de todas las URLs para este evento
        # Se inicializa con la URL principal, fuentes adicionales se agregan durante la deduplicación
        self.sources: list[str] = []
        if self.url:
            self.sources.append(self.url)

        self.location = self._clean_ical_property(event.get("location"))
        # Si no hay location en el feed, intentar extraer de la descripción
        if not self.location or not self.location.strip():
            self.location = self._extract_location_from_description()

        # Si no hay URL, intentar extraer de la descripción (ej: lu.ma)
        if not self.url:
            self.url = self._extract_url_from_description()
            # Actualizar sources con la URL extraída
            if self.url and self.url not in self.sources:
                self.sources.append(self.url)

        self.organizer = self._extract_group()

        # Manejar fechas con timezone
        self.dtstart = self._extract_datetime(event.get("dtstart"))
        self.dtend = self._extract_datetime(event.get("dtend"))

        # Calcular hash para deduplicación
        self.hash_key = self._compute_hash()

        # Tags automáticos
        self.tags = self._extract_tags()

        # Flag para forzar online (ej: detectado via structured data)
        self.forced_online = False

        # Location metadata extraction
        loc_details = self._extract_location_details()
        self.country = loc_details["country"]
        self.country_code = loc_details["country_code"]
        self.state = loc_details["state"]
        self.state_code = loc_details["state_code"]
        self.city = loc_details["city"]
        self.city_code = loc_details["city_code"]
        self.address = loc_details.get("address_alias", self.location)

        # Homologar resultados
        self._standardize_location()

    @classmethod
    def from_dict(cls, data: Dict) -> "EventNormalized":
        """Reconstruye un objeto EventNormalized desde un diccionario."""
        # Crear un evento dummy de icalendar
        event = Event()
        # Nota: El summary aquí puede ser overwriteable si lo parseamos abajo
        event.add("summary", data.get("title", ""))
        event.add("description", data.get("description", ""))
        event.add("location", data.get("location", ""))
        # organizer es complicado pq es texto en el dict pero objeto en ICS
        # Lo manejaremos seteando atributos directamente despues

        # Datetimes
        dtstart_str = data.get("dtstart")
        if dtstart_str:
            try:
                dtstart = parser.isoparse(dtstart_str)
                event.add("dtstart", dtstart)
            except Exception:
                pass

        # Instanciar (esto ejecutará init y re-normalización, lo cual está bien)
        # Pero queremos preservar valores exactos del historial/manual si ya estaban normalizados
        instance = cls(event, data.get("source", ""), feed_name=data.get("organizer"))

        # Sobreescribir con valores exactos del diccionario para evitar re-normalización destructiva
        # Restaurar título normalizado para hashing consistente
        # El título en JSON es "Grupo|Resumen|Location" o solo el título
        formatted_title = data.get("title", "")
        clean_summary_extracted = ""

        if "|" in formatted_title:
            parts = formatted_title.split("|")
            # Asumimos formato Grupo|Resumen|...
            if len(parts) >= 2:
                raw_summary = parts[1]
                clean_summary_extracted = raw_summary
                instance.title = instance._normalize_title(raw_summary)
                # Restaurar summary en el evento original también
                event.add("summary", parts[1])
            else:
                instance.title = instance._normalize_title(formatted_title)
                clean_summary_extracted = formatted_title
        else:
            instance.title = instance._normalize_title(formatted_title)
            clean_summary_extracted = formatted_title

        # IMPORTANTE: Establecer self.summary con la versión limpia extraída del título
        # para que _format_title funcione correctamente
        instance.summary = clean_summary_extracted

        instance.description = data.get("description", "")
        instance.url = data.get("url", "")
        instance.location = data.get("location", "")
        instance.organizer = data.get("organizer", "")

        # Restaurar fuentes desde el historial
        # Si hay sources guardados, usarlos; si no, inicializar con la URL principal
        if "sources" in data and data["sources"]:
            # sources puede venir como lista de dicts o lista de strings
            sources_data = data["sources"]
            instance.sources = []
            for src in sources_data:
                if isinstance(src, dict):
                    instance.sources.append(src.get("url", ""))
                else:
                    instance.sources.append(src)
            # Filtrar URLs vacías
            instance.sources = [s for s in instance.sources if s]
        else:
            # Migración: si no hay sources, inicializar con la URL principal
            instance.sources = [instance.url] if instance.url else []

        if dtstart_str:
            instance.dtstart = parser.isoparse(dtstart_str)

        dtend_str = data.get("dtend")
        if dtend_str:
            instance.dtend = parser.isoparse(dtend_str)
        else:
            instance.dtend = None

        if "tags" in data:
            # Combinar tags del sistema con los manuales
            manual_tags = set(data["tags"])
            instance.tags = instance.tags.union(manual_tags)

        instance.source_url = data.get("source", "")

        # Restore location metadata if available and valid (has codes)
        # If history has invalid/empty codes, we keep the ones from initial extraction (cls() above)
        if data.get("country_code"):
            instance.country = data.get("country", "")
            instance.country_code = data.get("country_code", "")
            instance.state = data.get("state", "")
            instance.state_code = data.get("state_code", "")
            instance.city = data.get("city", "")
            instance.city_code = data.get("city_code", "")
            instance.address = data.get("address", data.get("location", ""))

            # --- Healing / Migration ---
            # Si el país es "Mexico" (sin acento) o la ciudad parece un lugar (headquarters, etc)
            # re-extraer para usar la nueva lógica mejorada
            if instance.country == "Mexico":
                loc_details = instance._extract_location_details()
                instance.country = loc_details["country"]
                instance.country_code = loc_details["country_code"]
                instance.state = loc_details["state"]
                instance.state_code = loc_details["state_code"]
                instance.city = loc_details["city"]
                instance.city_code = loc_details["city_code"]
                instance.address = loc_details.get("address_alias", instance.location)

            # Homologar siempre al cargar de historia (Healing Dinámico)
            instance._standardize_location()
        elif "country" in data:
            # Migration from previous format (country/state only)
            instance.address = data.get("address", data.get("location", ""))
            loc_details = instance._extract_location_details()
            instance.country = loc_details["country"]
            instance.country_code = loc_details["country_code"]
            instance.state = loc_details["state"]
            instance.state_code = loc_details["state_code"]
            instance.city = loc_details["city"]
            instance.city_code = loc_details["city_code"]
        else:
            # Re-calculate if not in JSON
            loc_details = instance._extract_location_details()
            instance.country = loc_details["country"]
            instance.country_code = loc_details["country_code"]
            instance.state = loc_details["state"]
            instance.state_code = loc_details["state_code"]
            instance.city = loc_details["city"]
            instance.city_code = loc_details["city_code"]
            instance.address = instance.location

        instance.hash_key = instance._compute_hash()

        return instance

    def _extract_url_from_description(self) -> str:
        """
        Intenta extraer una URL del evento de la descripción.
        Útil para feeds que ponen el link en el cuerpo (ej: Luma).
        """
        if not self.description:
            return ""

        # Buscar URLs de Luma
        # Soporta lu.ma y luma.com (común en descriptions generadas)
        luma_pattern = r"(https?://(?:www\.)?(?:luma\.com|lu\.ma)/[\w-]+)"
        match = re.search(luma_pattern, self.description)
        if match:
            return match.group(1)

        # Buscar otras URLs comunes si es necesario en el futuro

        return ""

    def _normalize_title(self, title: str) -> str:
        """Normaliza el título: lowercase, sin emojis, sin puntuación extra."""
        if not title:
            return ""

        # Remover emojis (caracteres Unicode fuera del rango ASCII básico)
        title = re.sub(r"[^\x00-\x7F]+", "", title)

        # Convertir a lowercase
        title = title.lower()

        # Reemplazar puntuación con espacios para mejor deduplicación
        # Esto hace que "Title/Subtitle" y "Title - Subtitle" sean iguales ("Title Subtitle")
        title = re.sub(r"[^\w\s]", " ", title)

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
        # Truncar título a 40 caracteres para evitar problemas con títulos
        # cortados en feeds ICS (ej: Luma trunca títulos largos)
        title_truncated = self.title[:40] if self.title else ""

        if not self.dtstart:
            return f"{title_truncated}_no_date"

        # Redondear hacia abajo al bloque de 2 horas más cercano
        # para tolerancia de ±2 horas
        # Esto agrupa eventos en ventanas de 2 horas:
        # 0-1, 2-3, 4-5, ..., 18-19, 20-21, 22-23
        # Convertir a UTC para asegurar consistencia entre feeds con diferentes timezones
        # (ej: Luma usa UTC, Meetup usa Local)
        dt_utc = self.dtstart.astimezone(tz.UTC)

        hour = dt_utc.hour
        # Redondear hacia abajo al número par más cercano (0, 2, 4, ..., 22)
        hour_block = (hour // 2) * 2
        hour_rounded = dt_utc.replace(
            hour=hour_block, minute=0, second=0, microsecond=0
        )
        return f"{title_truncated}_{hour_rounded.isoformat()}"

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

        # 0. Prioridad máxima: Flag explícito (ej: de structured data)
        if hasattr(self, "forced_online") and self.forced_online:
            logger.debug(f"Event detected as ONLINE (forced flag): '{self.location}'")
            return True

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

        # 1. Prioridad: Verificar si la ubicación es explícitamente online
        if (
            "online" in location_lower
            or "virtual" in location_lower
            or "zoom" in location_lower
            or "meet" in location_lower
        ):
            logger.debug(f"Event detected as ONLINE (from location): '{self.location}'")
            return True

        # 1b. Si la descripción dice explícitamente que es online
        text_to_check = description_lower
        for keyword in online_keywords:
            if keyword in text_to_check:
                # Caso especial: Si dice "streaming" pero tenemos una dirección física real,
                # solemos considerar que es presencial con stream.
                physical_keywords = [
                    "calle",
                    "colonia",
                    "col.",
                    "avenida",
                    "av.",
                    "piso",
                    "nivel",
                    "número",
                    "no.",
                    "n°",
                    "residencial",
                    "roma",
                    "norte",
                    "sur",
                    "zacatecas",
                ]
                if any(k in location_lower for k in physical_keywords):
                    logger.debug(
                        f"Event detected as PHYSICAL (has streaming but physical keyword in location): '{self.location}'"
                    )
                    return False

                # Si la ubicación tiene un número, probablemente sea una dirección física
                if re.search(r"\d+", location_lower) and len(location_lower) > 10:
                    logger.debug(
                        f"Event detected as PHYSICAL (has streaming but number in location): '{self.location}'"
                    )
                    return False

                logger.debug(
                    f"Event detected as ONLINE (keyword '{keyword}' in description): '{self.location}'"
                )
                return True

        # 2. Si hay indicadores de presencial en la descripción
        for keyword in in_person_keywords:
            if keyword in description_lower:
                logger.debug(
                    f"Event detected as PHYSICAL (keyword '{keyword}' in description): '{self.location}'"
                )
                return False

        # 3. Si hay location explícita y no es una URL, probablemente es presencial
        if self.location and self.location.strip():
            if not self.location.strip().startswith("http"):
                # Si llegamos aquí y no detectamos keywords de online arriba, asumimos presencial
                # pero evitamos casos como locación = "..." o locaciones muy cortas
                if len(self.location.strip()) > 3:
                    logger.debug(
                        f"Event detected as PHYSICAL (location string exists and not detected as online): '{self.location}'"
                    )
                    return False

        # 4. Si no hay nada, o es muy corto, asumir online
        logger.debug(
            f"Event detected as ONLINE (fallback): '{self.location}' (len={len(self.location) if self.location else 0})"
        )
        return True

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
        # 0. Si se proporcionó feed_name en config, usarlo (Prioridad más alta)
        if self.feed_name:
            return self.feed_name

        # Primero intentar del organizador del evento
        organizer = self._extract_organizer(self.original_event)
        if organizer:
            return organizer.strip()

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

    def _extract_location_details(self) -> Dict[str, str]:
        """
        Extrae detalles de ubicación (país, estado, ciudad) y sus códigos ISO.
        """
        details = {
            "country": "",
            "country_code": "",
            "state": "",
            "state_code": "",
            "city": "",
            "city_code": "",
        }

        if not self.location or not self.location.strip():
            return details

        location = self.location.strip()
        # Limpiar dobles comas y espacios extra
        location_cleaned = re.sub(r",\s*,", ",", location)
        parts = [p.strip() for p in location_cleaned.split(",") if p.strip()]

        # --- 1. Detectar País ---
        country_obj = None
        # Intentar buscar el último componente en pycountry
        if parts:
            try:
                # Buscar por nombre exacto o código
                country_obj = (
                    pycountry.countries.get(name=parts[-1])
                    or pycountry.countries.get(official_name=parts[-1])
                    or pycountry.countries.get(alpha_2=parts[-1].upper())
                )
            except Exception:
                pass

        # Fallback a México si contiene keywords comunes
        if not country_obj:
            mx_keywords = [
                "méxico",
                "mexico",
                "cdmx",
                "ciudad de méxico",
                "mexico city",
            ]
            if any(any(kw in p.lower() for kw in mx_keywords) for p in parts):
                try:
                    country_obj = pycountry.countries.get(alpha_2="MX")
                except Exception:
                    pass
        if country_obj:
            details["country"] = (
                "México" if country_obj.alpha_2 == "MX" else country_obj.name
            )
            details["country_code"] = country_obj.alpha_2

        # --- 2. Detectar Estado (Subdivision) ---
        state_obj = None
        if country_obj and country_obj.alpha_2 == "MX":
            lookup = self._get_mx_subdivisions_lookup()

            # Buscar coincidencias en los componentes de la dirección
            for part in parts:
                p_low = part.lower().strip()

                # 2. Normalizar y buscar en el lookup dinámico
                norm_name = self._normalize_subdivision_name(p_low)

                if norm_name in lookup:
                    state_obj = lookup[norm_name]
                    break

        # Caso genérico para otros países (si lo necesitáramos)
        elif country_obj:
            try:
                subs = pycountry.subdivisions.get(country_code=country_obj.alpha_2)
                for part in parts:
                    for sub in subs:
                        if sub.name.lower() == part.lower():
                            state_obj = sub
                            break
                    if state_obj:
                        break
            except Exception:
                pass

        if state_obj:
            details["state"] = state_obj.name
            details["state_code"] = state_obj.code

            # Especial: Amazon HQ en CDMX

        # --- 3. Detectar Ciudad ---
        city_name = ""
        # Usualmente la ciudad es el primer componente o el segundo
        if parts:
            # Filtrar componentes que ya identificamos como estado o país
            remaining = [
                p
                for p in parts
                if p != details["state"]
                and p != details["country"]
                and p != details["country_code"]
                and not details["state_code"].endswith(p.upper())
            ]

            if remaining:
                # Si hay más de uno, solemos preferir el que parece nombre de ciudad
                # Por ahora, tomar el primero de los restantes (que no sea el país/estado)

                # FIX: No asumir que el primer componente es la ciudad. Esto causa problemas
                # cuando el primer componente es el nombre del Venue (ej: Velodrome, Telmex Hub).
                # Es mejor dejar city vacío y dejar que el geocodificador (Google/Nominatim)
                # resuelva la ciudad correcta.

                # city_name = remaining[0]
                pass

                # Si el primero parece una calle o número, intentar el siguiente
                # if len(remaining) > 1 and (re.search(r'\d', remaining[0]) or len(remaining[0]) < 3):
                #     city_name = remaining[1]

            # Si el componente de ciudad parece una calle o número, ignorarlo (ser conservador)
            city_keywords = [
                "calle",
                "clle",
                "avenida",
                "av.",
                "piso",
                "nivel",
                "número",
                "no.",
                "n°",
                "residencial",
                "colonia",
                "col.",
            ]
            if any(k in city_name.lower() for k in city_keywords):
                city_name = ""

            # Si el nombre de la ciudad es muy largo, probablemente sea el nombre del lugar
            elif len(city_name) > 30:
                city_name = ""

        if city_name:
            details["city"] = city_name
            details["city_code"] = slugify(city_name)
        return details

    def _standardize_location(self):
        """Homologiza nombres y códigos, especialmente para CDMX."""
        # 1. Corregir país
        if self.country == "Mexico" or self.country_code == "MX":
            self.country = "México"
            self.country_code = "MX"

        # 2. Normalizar state_code
        if self.state_code:
            # Remover puntos y espacios, convertir a uppercase
            sc = self.state_code.replace(".", "").replace(" ", "").upper()

            # Mapeos específicos de abreviaturas comunes en México para ISO pycountry
            mx_mappings = {
                "MX-NL": "MX-NLE",
                "MX-TLAX": "MX-TLA",
            }

            # Asegurar prefijo MX- si es México y el código es corto (ej: JAL -> MX-JAL)
            if self.country_code == "MX" and not sc.startswith("MX-"):
                sc = f"MX-{sc}"

            if self.country_code == "MX":
                sc = mx_mappings.get(sc, sc)

            self.state_code = sc

        # 3. Corregir state_code para CDMX (homologar MX-CMX)
        if self.state_code in ["MX-CDMX", "MX-DF", "MX-DIF", "CDMX", "DF"]:
            self.state_code = "MX-CMX"
            self.state = "Ciudad de México"

        # 4. Homologar CDMX
        if self.state_code == "MX-CMX":
            # city_code standar para CDMX
            if not self.city_code or self.city_code == "ciudaddemexico":
                self.city_code = "cdmx"

    def _parse_google_address(self, raw_data: Dict) -> Dict:
        """
        Extrae detalles de ubicación de la respuesta raw de Google Maps (address_components).

        Returns:
            Dict con keys: country, country_code, state, state_code, city, city_code
        """
        components = raw_data.get("address_components", [])
        details = {
            "country": "",
            "country_code": "",
            "state": "",
            "state_code": "",
            "city": "",
            "city_code": "",
        }

        for comp in components:
            types = comp.get("types", [])
            if "country" in types:
                details["country"] = comp.get("long_name", "")
                details["country_code"] = comp.get("short_name", "").upper()
            elif "administrative_area_level_1" in types:
                details["state"] = comp.get("long_name", "")
                details["state_code"] = comp.get("short_name", "")
            elif "locality" in types:
                details["city"] = comp.get("long_name", "")
            elif "sublocality" in types and not details["city"]:
                details["city"] = comp.get("long_name", "")
            elif "neighborhood" in types and not details["city"]:
                details["city"] = comp.get("long_name", "")

        # Normalizar state_code para México (MX-XXX) si Google devuelve el nombre corto sin prefijo
        if (
            details["country_code"] == "MX"
            and details["state_code"]
            and "-" not in details["state_code"]
        ):
            details["state_code"] = f"MX-{details['state_code']}"

        if details["city"]:
            details["city_code"] = slugify(details["city"])

        return details

    def geocode_location(self, cache: Optional[Dict] = None) -> bool:
        """
        Usa geopy (GoogleV3 o Nominatim) para obtener detalles precisos de la ubicación.
        Actualiza los campos country, state, city y sus respectivos códigos.

        Args:
            cache: Diccionario opcional para cachear resultados {query: result_dict}
        """
        if not self.location or len(self.location.strip()) < 5:
            return False

        # Si ya es Online, no geocodear
        if self._is_online():
            return False

        try:
            # Elegir geocodificador
            api_key = os.getenv("GOOGLE_MAPS_API_KEY")
            if api_key:
                geolocator = GoogleV3(api_key=api_key)
                service_name = "google"
            else:
                geolocator = Nominatim(user_agent="cron-quiles-aggregator")
                service_name = "nominatim"

            # Limpiar la query: quitar comas redundantes y partes vacías
            location_cleaned = re.sub(r",\s*,", ",", self.location)
            query_parts = [p.strip() for p in location_cleaned.split(",") if p.strip()]

            # Quitar URLs si hay comas (suelen ser las últimas partes)
            query_parts = [p for p in query_parts if not p.startswith("http")]

            # Quitar ruidos comunes de Meetup
            query_parts = [
                re.sub(r"^hosted by\s+", "", p, flags=re.IGNORECASE)
                for p in query_parts
            ]

            current_query = ", ".join(query_parts).strip()
            current_query = fix_encoding(current_query)
            if not current_query or len(current_query) < 4:
                return False

            # Verificar cache
            location_data = None
            if cache and current_query in cache:
                logger.debug(f"Geocoding cache hit for: {current_query}")
                raw_data = cache[current_query]
                if raw_data:

                    class MockLocation:
                        def __init__(self, raw):
                            self.raw = raw

                    location_data = MockLocation(raw_data)
            else:
                logger.debug(
                    f"Geocoding query ({geolocator.__class__.__name__}): {current_query}"
                )
                # GoogleV3 no usa 'addressdetails'
                if isinstance(geolocator, GoogleV3):
                    location_data = geolocator.geocode(
                        current_query, language="es", timeout=10
                    )
                else:
                    location_data = geolocator.geocode(
                        current_query, addressdetails=True, language="es", timeout=10
                    )

                # Guardar en cache
                if cache is not None:
                    cache[current_query] = location_data.raw if location_data else {}

            if not location_data and len(query_parts) > 2:
                # Intentar quitando la primera parte
                fallback_query_1 = ", ".join(query_parts[1:])

                if cache and fallback_query_1 in cache:
                    logger.debug(
                        f"Geocoding cache hit (fallback 1): {fallback_query_1}"
                    )
                    raw_data = cache[fallback_query_1]
                    if raw_data:

                        class MockLocation:
                            def __init__(self, raw):
                                self.raw = raw

                        location_data = MockLocation(raw_data)
                else:
                    if isinstance(geolocator, GoogleV3):
                        location_data = geolocator.geocode(
                            fallback_query_1, language="es", timeout=10
                        )
                    else:
                        location_data = geolocator.geocode(
                            fallback_query_1,
                            addressdetails=True,
                            language="es",
                            timeout=10,
                        )

                    if cache is not None:
                        cache[fallback_query_1] = (
                            location_data.raw if location_data else {}
                        )

                if not location_data:
                    # Intentar con la parte final
                    fallback_query_2 = ", ".join(query_parts[-2:])

                    if cache and fallback_query_2 in cache:
                        logger.debug(
                            f"Geocoding cache hit (fallback 2): {fallback_query_2}"
                        )
                        raw_data = cache[fallback_query_2]
                        if raw_data:

                            class MockLocation:
                                def __init__(self, raw):
                                    self.raw = raw

                            location_data = MockLocation(raw_data)
                    else:
                        if isinstance(geolocator, GoogleV3):
                            location_data = geolocator.geocode(
                                fallback_query_2, language="es", timeout=10
                            )
                        else:
                            location_data = geolocator.geocode(
                                fallback_query_2,
                                addressdetails=True,
                                language="es",
                                timeout=10,
                            )

                        if cache is not None:
                            cache[fallback_query_2] = (
                                location_data.raw if location_data else {}
                            )

            if location_data:
                # 1. Caso Google Maps
                if "address_components" in location_data.raw:
                    res = self._parse_google_address(location_data.raw)
                    self.country = res["country"]
                    self.country_code = res["country_code"]
                    self.state = res["state"]
                    self.state_code = res["state_code"]
                    self.city = res["city"]
                    self.city_code = res["city_code"]
                    self.address = location_data.raw.get(
                        "formatted_address", self.location
                    )

                # 2. Caso Nominatim
                elif "address" in location_data.raw:
                    address = location_data.raw.get("address", {})

                    # Extraer País
                    country_name = address.get("country", "")
                    country_code = address.get("country_code", "").upper()
                    if country_code:
                        self.country_code = country_code
                        # Normalizar nombre de país con pycountry si es posible
                        try:
                            c = pycountry.countries.get(alpha_2=country_code)
                            self.country = c.name if c else country_name
                        except (
                            KeyError
                        ):  # More specific exception for pycountry.countries.get
                            self.country = country_name

                    # Extraer Estado / Provincia
                    state_name = address.get(
                        "state", address.get("province", address.get("region", ""))
                    )
                    if state_name and self.country_code:
                        self.state = state_name
                        # Intentar obtener state_code via pycountry
                        try:
                            subs = pycountry.subdivisions.get(
                                country_code=self.country_code
                            )
                            for sub in subs:
                                if sub.name.lower() == state_name.lower():
                                    self.state_code = sub.code
                                    break
                        except Exception:
                            pass

                    # Extraer Ciudad
                    city_name = address.get(
                        "city",
                        address.get(
                            "town",
                            address.get("village", address.get("suburb", "")),
                        ),
                    )
                    if city_name:
                        self.city = city_name
                        self.city_code = slugify(city_name)

                    self.address = location_data.raw.get("display_name", self.location)

                # Homologar resultados después de geocodificar
                self._standardize_location()

                logger.info(
                    f"Geocoded successfully ({service_name if 'service_name' in locals() else 'unknown'}): "
                    f"{self.location} -> {self.country}, {self.state}, {self.city}"
                )
                return True

        except (GeopyError, Exception) as e:
            logger.debug(f"Geocoding error for '{self.location}': {e}")

        return False

    def _format_title(self) -> str:
        """
        Formatea el título según el nuevo formato:
        - Físico: Grupo|Nombre evento|País|Estado
        - Online: Grupo|Nombre evento|Online
        """
        grupo = self._extract_group()
        # USAR self.summary QUE YA ESTÁ LIMPIO en lugar de raw event
        nombre_evento = self.summary
        if not nombre_evento:
            # Fallback
            nombre_evento = str(self.original_event.get("summary", "")).strip()

        if not nombre_evento:
            nombre_evento = "Evento sin título"

        if self._is_online():
            return f"{grupo}|{nombre_evento}|Online"
        else:
            pais = self.country
            estado = self.state
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
                    # Si no podemos determinar ubicación exacta
                    # Evitar duplicar si ya está en el nombre (caso raro)
                    return f"{grupo}|{nombre_evento}|Online"

    def to_dict(self) -> EventSchema:
        """Convierte el evento normalizado a diccionario para JSON."""
        # Construir array de fuentes con info de plataforma
        sources_with_platform = []
        for source_url in self.sources:
            platform = detect_platform(source_url)
            sources_with_platform.append({
                "platform": platform,
                "url": source_url,
                "label": get_platform_label(platform)
            })

        return {
            "title": self._format_title(),
            "description": self.description,
            "url": self.url,  # compatibilidad: URL principal
            "sources": sources_with_platform,  # nuevo: todas las fuentes con info de plataforma
            "location": self.location,
            "organizer": self.organizer,
            "dtstart": self.dtstart.isoformat() if self.dtstart else None,
            "dtend": self.dtend.isoformat() if self.dtend else None,
            "tags": sorted(list(self.tags)),
            "source": self.source_url,
            "country": self.country,
            "country_code": self.country_code,
            "state": self.state,
            "state_code": self.state_code,
            "city": self.city,
            "city_code": self.city_code,
            "address": self.address,
            "hash_key": self.hash_key,
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
            event.add("categories", sorted(list(self.tags)))

        # Add custom properties for location metadata
        if self.country:
            event.add("X-CRONQUILES-COUNTRY", fix_encoding(self.country))
        if self.country_code:
            event.add("X-CRONQUILES-COUNTRY-CODE", fix_encoding(self.country_code))
        if self.state:
            event.add("X-CRONQUILES-STATE", fix_encoding(self.state))
        if self.state_code:
            event.add("X-CRONQUILES-STATE-CODE", fix_encoding(self.state_code))
        if self.city:
            event.add("X-CRONQUILES-CITY", fix_encoding(self.city))
        if self.city_code:
            event.add("X-CRONQUILES-CITY-CODE", fix_encoding(self.city_code))
        if self.address:
            event.add("X-CRONQUILES-ADDRESS", fix_encoding(self.address))

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
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            }
            logger.debug(f"Enriching location from Meetup: {self.url}")
            response = session.get(self.url, headers=headers, timeout=10)
            if response.status_code != 200:
                return False

            html = response.text

            # 1. Intentar con JSON-LD (application/ld+json)
            # Usamos regex para evitar dependencias de BS4
            json_ld_matches = re.findall(
                r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
            )
            for jld_text in json_ld_matches:
                try:
                    data = json.loads(jld_text)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if item.get("@type") == "Event" and "location" in item:
                            loc = item["location"]

                            # Si el tipo de locación es VirtualLocation, forzar online
                            if loc.get("@type") == "VirtualLocation":
                                logger.info(f"Detected VirtualLocation for {self.url}")
                                self.forced_online = True
                                self.location = "Online"
                                self.city = "Online"
                                self.city_code = "online"
                                return True

                            name = loc.get("name", "")
                            address = loc.get("address", {})

                            parts = []
                            if name and name != "Online Event":
                                parts.append(name)

                            if isinstance(address, dict):
                                street = address.get("streetAddress", "")
                                city = address.get("addressLocality", "")
                                if street:
                                    parts.append(street)
                                if city:
                                    parts.append(city)
                            elif isinstance(address, str):
                                parts.append(address)

                            new_location = ", ".join(parts).strip()
                            if new_location and len(new_location) > len(self.location):
                                self.location = new_location

                                # Re-extraer detalles geográficos inmediatamente
                                loc_details = self._extract_location_details()
                                self.country = loc_details["country"]
                                self.country_code = loc_details["country_code"]
                                self.state = loc_details["state"]
                                self.state_code = loc_details["state_code"]
                                self.city = loc_details["city"]
                                self.city_code = loc_details["city_code"]

                                # Homologar de nuevo con la nueva información
                                self._standardize_location()
                                return True
                except Exception:
                    continue

            # 2. Intentar con __NEXT_DATA__
            next_data_match = re.search(
                r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                html,
                re.DOTALL,
            )
            if next_data_match:
                try:
                    data = json.loads(next_data_match.group(1))
                    event_data = (
                        data.get("props", {}).get("pageProps", {}).get("event", {})
                    )
                    venue = event_data.get("venue", {})
                    if venue:
                        name = venue.get("name", "")
                        addr = venue.get("address", {})
                        parts = []
                        if name:
                            parts.append(name)
                        if isinstance(addr, dict):
                            street = addr.get("address_1", "")
                            city = addr.get("city", "")
                            if street:
                                parts.append(street)
                            if city:
                                parts.append(city)
                        elif isinstance(addr, str):
                            parts.append(addr)

                        new_location = ", ".join(parts).strip()
                        if new_location and len(new_location) > len(self.location):
                            self.location = new_location

                            # Re-extraer detalles geográficos inmediatamente
                            loc_details = self._extract_location_details()
                            self.country = loc_details["country"]
                            self.country_code = loc_details["country_code"]
                            self.state = loc_details["state"]
                            self.state_code = loc_details["state_code"]
                            self.city = loc_details["city"]
                            self.city_code = loc_details["city_code"]

                            # Homologar de nuevo con la nueva información
                            self._standardize_location()
                            return True
                except Exception:
                    pass

        except Exception as e:
            logger.warning(f"Error enriching location from {self.url}: {e}")

        return False

    def enrich_location_from_luma(self, session: requests.Session) -> bool:
        """
        Intenta extraer la ubicación detallada de la página de Luma.
        """
        # Soportar lu.ma y luma.com
        if "lu.ma" not in self.url and "luma.com" not in self.url:
            return False

        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            }
            logger.debug(f"Enriching location from Luma: {self.url}")
            response = session.get(self.url, headers=headers, timeout=10)
            if response.status_code != 200:
                return False

            html = response.text

            # Buscar __NEXT_DATA__
            next_data_match = re.search(
                r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                html,
                re.DOTALL,
            )

            if next_data_match:
                try:
                    data = json.loads(next_data_match.group(1))
                    event_data = (
                        data.get("props", {})
                        .get("pageProps", {})
                        .get("initialData", {})
                        .get("data", {})
                        .get("event", {})
                    )

                    if not event_data:
                        return False

                    new_location_parts = []

                    # 0. [NUEVO] Intentar extraer Venue Name del HTML (Google Maps Link)
                    # <a href="https://www.google.com/maps/search/?api=1&query=Pinterest%20M%C3%A9xico...>
                    try:
                        maps_link_match = re.search(
                            r'href="https://www\.google\.com/maps/search/\?api=1&amp;query=([^"&]+)',
                            html,
                        )
                        if not maps_link_match:
                            # Try without &amp;
                            maps_link_match = re.search(
                                r'href="https://www\.google\.com/maps/search/\?api=1&query=([^"&]+)',
                                html,
                            )

                        if maps_link_match:
                            venue_name_encoded = maps_link_match.group(1)
                            # Decode URL (Pinterest%20M%C3%A9xico -> Pinterest México)
                            from urllib.parse import unquote

                            venue_name = unquote(venue_name_encoded).strip()
                            # Replace + with space just in case
                            venue_name = venue_name.replace("+", " ")

                            if venue_name and venue_name.lower() != "google maps":
                                new_location_parts.append(venue_name)
                                logger.debug(
                                    f"Extracted venue name from Luma: {venue_name}"
                                )
                    except Exception as e:
                        logger.warning(f"Error extracting venue name Luma: {e}")

                    # 1. Verificar geo_address_info
                    geo_info = event_data.get("geo_address_info", {})
                    if geo_info:
                        # Extraer campos disponibles
                        # Prioridad: full_address > address + city > city + region

                        full_address = geo_info.get("full_address")
                        address = geo_info.get("address")
                        sublocality = geo_info.get("sublocality")
                        city = geo_info.get("city")
                        city_state = geo_info.get("city_state")
                        region = geo_info.get("region")
                        country = geo_info.get("country")

                        if full_address:
                            new_location_parts.append(full_address)
                        else:
                            # Construir
                            if address:
                                new_location_parts.append(address)
                            if sublocality:
                                new_location_parts.append(sublocality)
                            if city:
                                new_location_parts.append(city)
                            elif city_state:
                                new_location_parts.append(city_state)

                            if region and region != city:
                                new_location_parts.append(region)
                            if country:
                                new_location_parts.append(country)

                    # 2. Verificar location_type para saber si es online
                    loc_type = event_data.get("location_type")
                    if loc_type == "online":
                        self.forced_online = True
                        self.location = "Online"
                        # Extraer link si es posible
                        virtual_info = event_data.get("virtual_info", {})
                        if virtual_info.get("video_call_url"):
                            # Podríamos agregar esto a la descripción si quisiéramos
                            pass
                        return True

                    # 3. Si tenemos location física
                    if new_location_parts:
                        new_location = ", ".join(new_location_parts).strip()

                        # CLEANUP: Remover coordenadas si aparecen al principio (Luma las pone en full_address)
                        # Ej: "19.42,-99.1725, Ciudad de México" -> "Ciudad de México"
                        # Patrón: número(s).número(s), número(s).número(s),
                        new_location = re.sub(
                            r"^-?\d+\.\d+,\s*-?\d+\.\d+,?\s*", "", new_location
                        )

                        # Limpiar duplicados (ej: Ciudad de México, Ciudad de México)
                        # Un set preservando orden sería ideal pero simple string manipulation funciona
                        # para casos obvios

                        if new_location and len(new_location) > 5:
                            self.location = new_location
                            self.address = new_location

                            # Re-extraer detalles geográficos
                            loc_details = self._extract_location_details()
                            self.country = loc_details["country"]
                            self.country_code = loc_details["country_code"]
                            self.state = loc_details["state"]
                            self.state_code = loc_details["state_code"]
                            self.city = loc_details["city"]
                            self.city_code = loc_details["city_code"]

                            self._standardize_location()
                            return True

                except Exception as e:
                    logger.warning(f"Error parsing Luma JSON: {e}")
                    pass

        except Exception as e:
            logger.warning(f"Error enriching location from Luma {self.url}: {e}")

        return False
