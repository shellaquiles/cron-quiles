import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from dateutil import parser, tz
import requests

from ..models import EventNormalized
from .base import BaseAggregator

logger = logging.getLogger(__name__)


class OCGroupsAggregator(BaseAggregator):
    """
    Extractor de eventos para Open Community Groups (ocgroups.dev),
    como comunidades de CNCF u Open Source communities.
    """

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        timeout: int = 20,
        max_retries: int = 2,
    ):
        self.session = session or requests.Session()
        self.timeout = timeout
        self.max_retries = max_retries

    def extract(
        self, source: str | Dict[str, Any], feed_name: Optional[str] = None
    ) -> List[EventNormalized]:
        """
        Extrae eventos desde la página del grupo de ocgroups.dev.

        Args:
            source: URL del grupo o diccionario de configuración
            feed_name: Nombre opcional de la comunidad

        Returns:
            Lista de eventos normalizados
        """
        url = source if isinstance(source, str) else source.get("url")
        name = feed_name or (source.get("name") if isinstance(source, dict) else None)

        if not url:
            return []

        logger.info(f"Fetching ocgroups.dev feed: {url} ({name})")
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Obtener nombre por defecto del grupo si no se proveyó
            if not name:
                h1 = soup.find("h1")
                name = h1.get_text(strip=True) if h1 else "Open Community Groups"

            # Recolectar URLs de eventos (próximos y pasados) presentes en la página del grupo
            event_urls: List[str] = []
            seen: set[str] = set()

            for a in soup.find_all("a", href=re.compile(r"/event/[a-zA-Z0-9]+")):
                href = a.get("href")
                if not href:
                    continue
                full_url = urljoin(url, href)
                clean_url = full_url.split("?")[0].rstrip("/")
                if clean_url not in seen:
                    seen.add(clean_url)
                    event_urls.append(clean_url)

            logger.info(
                f"Found {len(event_urls)} event URLs on ocgroups.dev group page: {url}"
            )

            events: List[EventNormalized] = []
            for ev_url in event_urls:
                try:
                    event_norm = self._extract_event_page(ev_url, url, name)
                    if event_norm:
                        events.append(event_norm)
                except Exception as e:
                    logger.error(
                        f"Error extracting ocgroups.dev event {ev_url} from {url}: {e}"
                    )

            return events

        except Exception as e:
            logger.error(f"Failed to process ocgroups.dev group {url}: {e}")
            return []

    def _extract_event_page(
        self, event_url: str, source_url: str, group_name: Optional[str]
    ) -> Optional[EventNormalized]:
        """Descarga e interpreta la página de detalle de un evento individual."""
        resp = self.session.get(event_url, timeout=self.timeout)
        if resp.status_code != 200:
            logger.warning(
                f"Failed to fetch event page {event_url} (HTTP {resp.status_code})"
            )
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # Título
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else ""
        if not title:
            og_title = soup.find("meta", property="og:title")
            title = (
                og_title.get("content", "").split(" - ")[0].strip() if og_title else ""
            )

        if not title:
            return None

        # Descripción
        about_div = soup.find("div", class_="markdown")
        description = (
            about_div.get_text(separator="\n", strip=True) if about_div else ""
        )

        # Horarios (dtstart / dtend)
        att = soup.find(attrs={"data-attendance-container": True})
        dtstart_str = att.get("data-starts") if att else None

        dtstart: Optional[datetime] = None
        dtend: Optional[datetime] = None

        date_panel = soup.find(attrs={"data-registration-window-date-panel": True})
        panel_texts = (
            [t.strip() for t in date_panel.stripped_strings] if date_panel else []
        )

        date_str = None
        time_range_str = None
        for t in panel_texts:
            if re.search(
                r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
                t,
                re.I,
            ):
                date_str = t
            elif re.search(
                r"\d{1,2}:\d{2}\s*(?:AM|PM)\s*-\s*\d{1,2}:\d{2}\s*(?:AM|PM)", t, re.I
            ):
                time_range_str = t

        tzinfos = {
            "CST": tz.gettz("America/Mexico_City"),
            "CDT": tz.gettz("America/Mexico_City"),
            "UTC": tz.tzutc(),
        }

        if date_str and time_range_str:
            times = re.findall(r"(\d{1,2}:\d{2}\s*(?:AM|PM))", time_range_str, re.I)
            tz_match = re.search(r"([A-Z]{3,4})$", time_range_str.strip())
            tz_str = tz_match.group(1) if tz_match else "CST"
            tz_obj = tzinfos.get(tz_str, tz.gettz("America/Mexico_City"))

            if times:
                try:
                    dtstart = parser.parse(f"{date_str} {times[0]}").replace(
                        tzinfo=tz_obj
                    )
                except Exception:
                    pass
            if len(times) > 1:
                try:
                    dtend = parser.parse(f"{date_str} {times[1]}").replace(
                        tzinfo=tz_obj
                    )
                    if dtstart and dtend < dtstart:
                        dtend += timedelta(days=1)
                except Exception:
                    pass

        if not dtstart and dtstart_str:
            try:
                dtstart = parser.isoparse(dtstart_str)
            except Exception:
                pass

        # Ubicación
        location = None
        badges = soup.find_all(class_="custom-badge")
        if any("virtual" in b.get_text().lower() for b in badges):
            location = "Online"
        elif "virtual event" in soup.text.lower() and not soup.find(
            attrs={"data-lat": True}
        ):
            location = "Online"

        if not location:
            # Buscar texto de ubicación dentro de la tarjeta
            for div in soup.find_all("div"):
                cl = div.get("class", [])
                if any("rounded-full" in c for c in cl) and any(
                    "bg-white" in c for c in cl
                ):
                    txt = div.get_text(strip=True)
                    if txt and txt.lower() != "location":
                        location = txt
                        break

        # Fallback a organizador y país
        mapped_data = {
            "title": title,
            "description": description,
            "dtstart": dtstart.isoformat() if dtstart else None,
            "dtend": dtend.isoformat() if dtend else None,
            "location": location,
            "url": event_url,
            "source": "OpenCommunityGroups",
            "organizer": group_name,
            "country_code": "MX",
        }

        event_norm = EventNormalized.from_dict(mapped_data)
        event_norm.source_url = source_url
        event_norm.feed_name = group_name

        return event_norm
