import logging
import re
import time
from typing import List, Optional, Dict
from urllib.parse import urlparse, parse_qs
from .ics import GenericICSAggregator
from ..models import EventNormalized

logger = logging.getLogger(__name__)


class LumaAggregator(GenericICSAggregator):
    """Aggregator para feeds ICS de Luma con enriquecimiento de ubicación."""

    def __init__(self, session=None, timeout: int = 30, max_retries: int = 2,
                 url_cache: Optional[Dict] = None):
        super().__init__(session, timeout, max_retries)
        # Cache persistente compartido con ICSAggregator
        self.url_cache = url_cache if url_cache is not None else {"url_conversions": {}, "vanity_urls": {}}
        # Mantener referencia directa para compatibilidad
        self.vanity_url_cache: Dict[str, str] = self.url_cache["vanity_urls"]

    def _get_vanity_url_from_api_url(self, api_url: str) -> Optional[str]:
        """
        Obtiene la URL vanity de un calendario Luma a partir de su URL de API.

        Proceso:
        1. Extrae el calendar ID de la URL de API
        2. Accede a https://lu.ma/{calendar_id}
        3. Extrae la URL canónica o vanity del HTML

        Args:
            api_url: URL de API (ej: https://api2.luma.com/ics/get?entity=calendar&id=cal-xxx)

        Returns:
            URL vanity si se encuentra, None si no
        """
        try:
            parsed = urlparse(api_url)
            if "api2.luma.com" not in parsed.netloc:
                return None

            # Extraer calendar ID
            query_params = parse_qs(parsed.query)
            calendar_id = query_params.get('id', [''])[0]
            if not calendar_id:
                return None

            # Acceder a la página del calendario
            calendar_page_url = f"https://lu.ma/{calendar_id}"
            logger.info(f"Buscando URL vanity para: {calendar_page_url}")

            response = self.session.get(calendar_page_url, timeout=self.timeout, allow_redirects=True)
            if response.status_code != 200:
                return None

            # Verificar si hubo redirect a una URL vanity
            final_url = response.url
            if final_url and "lu.ma/" in final_url and calendar_id not in final_url:
                # Redirigió a una URL vanity diferente
                logger.info(f"URL vanity encontrada via redirect: {final_url}")
                return final_url

            # Buscar URL canónica en el HTML
            html = response.text

            # Buscar <link rel="canonical" href="...">
            canonical_match = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', html)
            if canonical_match:
                canonical_url = canonical_match.group(1)
                if calendar_id not in canonical_url:
                    logger.info(f"URL vanity encontrada via canonical: {canonical_url}")
                    return canonical_url

            # Buscar og:url meta tag
            og_match = re.search(r'<meta[^>]+property=["\']og:url["\'][^>]+content=["\']([^"\']+)["\']', html)
            if og_match:
                og_url = og_match.group(1)
                if calendar_id not in og_url:
                    logger.info(f"URL vanity encontrada via og:url: {og_url}")
                    return og_url

        except Exception as e:
            logger.warning(f"Error buscando URL vanity para {api_url}: {e}")

        return None

    def _convert_luma_url_to_ics(self, url: str) -> str:
        """
        Convierte URLs de luma.com/calendar-name a formato API ICS.
        Verifica cache primero antes de hacer fetch del HTML.
        """
        # Ya es URL de API ICS
        if "api2.luma.com/ics" in url:
            return url

        # Intentar convertir luma.com/calendar-name a ICS URL
        if "luma.com/" in url or "lu.ma/" in url:
            # 1. Verificar cache primero
            conversion_cache = self.url_cache.get("url_conversions", {})
            if url in conversion_cache:
                cached_api_url = conversion_cache[url]
                logger.info(f"URL de Luma encontrada en cache: {url} -> {cached_api_url}")
                return cached_api_url

            # 2. Cache miss: obtener del HTML
            try:
                logger.info(f"Convirtiendo URL de Luma a ICS: {url}")
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    html = response.text
                    # Buscar calendar ID en el HTML
                    # Patrón 1: app-argument=luma://calendar/cal-XXXXX
                    match = re.search(r'app-argument=luma://calendar/(cal-[a-zA-Z0-9]+)', html)
                    if not match:
                        # Patrón 2: cal-XXXXX en el HTML (puede estar en varios lugares)
                        # Buscar todos los calendar IDs y tomar el primero que sea válido
                        all_cal_ids = re.findall(r'\b(cal-[a-zA-Z0-9]{15,})\b', html)
                        if all_cal_ids:
                            # Usar el primer calendar ID encontrado
                            match = type('Match', (), {'group': lambda self, n: all_cal_ids[0]})()
                    if match:
                        calendar_id = match.group(1)
                        ics_url = f"https://api2.luma.com/ics/get?entity=calendar&id={calendar_id}"
                        logger.info(f"Convertido a ICS URL: {ics_url}")

                        # 3. Guardar en cache para próxima vez
                        conversion_cache[url] = ics_url
                        logger.debug(f"Guardado en cache: {url} -> {ics_url}")

                        return ics_url
            except Exception as e:
                logger.warning(f"Error convirtiendo URL de Luma {url}: {e}")

        return url

    def extract(
        self, source: str | Dict, feed_name: Optional[str] = None
    ) -> List[EventNormalized]:
        # Extraer URL original y nombre antes de convertir
        if isinstance(source, str):
            original_url = source
            name = feed_name
        else:
            original_url = source.get("url", "")
            name = feed_name or source.get("name")

        if not original_url:
            return []

        # Determinar la URL de comunidad (vanity URL si está disponible)
        # Si la URL original es una API URL, intentar obtener la vanity URL
        if "api2.luma.com" in original_url:
            # Revisar cache primero
            if original_url in self.vanity_url_cache:
                community_url = self.vanity_url_cache[original_url]
            else:
                community_url = self._get_vanity_url_from_api_url(original_url)
                if community_url:
                    # Limpiar la URL (quitar parámetros de tracking, etc.)
                    community_url = community_url.split("?")[0]
                else:
                    # Fallback: usar lu.ma/{calendar_id}
                    parsed = urlparse(original_url)
                    query_params = parse_qs(parsed.query)
                    calendar_id = query_params.get("id", [""])[0]
                    community_url = (
                        f"https://lu.ma/{calendar_id}" if calendar_id else original_url
                    )
                # Guardar en cache
                self.vanity_url_cache[original_url] = community_url
        else:
            # Ya es una vanity URL (luma.com/slug o lu.ma/slug)
            community_url = original_url

        # Convertir a URL de API para obtener el feed ICS
        fetch_url = self._convert_luma_url_to_ics(original_url)

        # Obtener el calendario usando la URL de API
        calendar = self.fetch_feed(fetch_url)
        if not calendar:
            return []

        # Extraer eventos usando la URL ORIGINAL como source_url
        # (importante para que el matching de comunidades funcione en main.py)
        # La vanity URL está guardada en self.vanity_url_cache para uso en generate_json
        events = self.extract_events_from_calendar(calendar, original_url, name)

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
