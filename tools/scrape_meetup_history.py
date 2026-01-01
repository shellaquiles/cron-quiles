#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Herramienta para scrapear eventos pasados de Meetup usando una cookie de sesión.
Uso: python scrape_meetup_history.py
Requiere: MEETUP_COOKIE env var (valor de la cookie 'MEETUP_MEMBER')
"""

import os
import sys
import yaml
import logging
import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path
import re

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuración
# YEAR_TO_SCRAPE = 2025 # Filter removed by user request
HISTORY_FILE = "data/history.json"

def load_feeds(config_file="config/feeds.yaml"):
    with open(config_file, "r") as f:
        data = yaml.safe_load(f)

    urls = []
    # Recorrer estructura de ciudades
    cities = data.get('cities', {})
    for city in cities.values():
        feeds = city.get('feeds') or []
        for feed in feeds:
            url = feed.get('url', '') if isinstance(feed, dict) else feed
            if 'meetup.com' in url:
                urls.append(url)
    return urls

def extract_group_slug(url):
    # https://www.meetup.com/python-mexico/events/ical -> python-mexico
    parts = url.split('/')
    for i, part in enumerate(parts):
        if 'meetup.com' in part:
            if i + 1 < len(parts):
                return parts[i+1]
    return None

def parse_meetup_date(date_str):
    # Format typically: "Fri, Jan 24, 2025, 7:00 PM CST"
    # Simplified parser or using dateutil
    from dateutil import parser
    try:
        # Limpiar str
        return parser.parse(date_str)
    except:
        return None

def scrape_group_history(group_slug, cookie):
    # La URL de "Past Events" suele ser /group-slug/events/past/
    # Pero para iterar por año a veces requiere logica de paginación o buscar en el archivo.
    # Meetup carga dinámicamente, pero la página /past/ a veces renderiza server-side lo básico.
    # Si no, tendremos problemas.

    # Updated URL format based on user finding
    url = f"https://www.meetup.com/{group_slug}/events/?type=past"


    # Parse cookie string to dict for requests
    cookie_dict = {}
    if "=" in cookie:
        # Handle "KEY=VAL; KEY2=VAL2" format
        for item in cookie.split(";"):
            if "=" in item:
                k, v = item.strip().split("=", 1)
                cookie_dict[k] = v
    else:
        # Handle raw value, assuming MEETUP_SESSION
        cookie_dict["MEETUP_SESSION"] = cookie

    session = requests.Session()
    session.cookies.update(cookie_dict)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.meetup.com/"
    })

    logger.info(f"Scraping {url} with cookies: {list(cookie_dict.keys())}...")
    try:
        response = session.get(url, allow_redirects=True)
        if response.status_code != 200:
            logger.error(f"Failed to fetch {url}: {response.status_code}")
            return []

        # Check if redirected to login
        if "/login" in response.url:
             logger.error("Redirected to login page! Cookie might be invalid or insufficient.")

        with open("debug_meetup.html", "w") as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')

        # Selectores pueden cambiar, esto es frágil
        # Buscamos tarjetas de eventos
        events_data = []

        # Estrategia general: buscar links a /events/12345/
        # Y extraer info cercana

        # Try to parse from __NEXT_DATA__ (Apollo State)
        script = soup.find('script', id='__NEXT_DATA__')
        if script:
            try:
                data = json.loads(script.string)
                apollo_state = data.get('props', {}).get('pageProps', {}).get('__APOLLO_STATE__', {})

                logger.info(f"Found {len(apollo_state)} items in Apollo state")

                for key, node in apollo_state.items():
                    # Check if it's an event
                    if node.get('__typename') == 'Event':
                        # Validar fecha
                        dt_str = node.get('dateTime')
                        if not dt_str:
                            continue

                        try:
                            # dateutil parser handles ISO with offsets well
                            from dateutil import parser
                            dt = parser.isoparse(dt_str)

                            # if dt.year == YEAR_TO_SCRAPE: # Filter removed
                            if True:
                                # Extract Location
                                location = "Online"
                                is_physical = False

                                if 'isOnline' in node:
                                    if not node['isOnline']:
                                        is_physical = True
                                elif node.get('eventType') == 'PHYSICAL':
                                    is_physical = True

                                if is_physical:
                                     # It is physical
                                     venue_obj = node.get('venue')
                                     venue_ref = (venue_obj or {}).get('__ref')

                                     if venue_ref and venue_ref in apollo_state:
                                         venue_node = apollo_state[venue_ref]
                                         # logger.info(f"DEBUG VENUE: {json.dumps(venue_node)}")
                                         # Construct full address
                                         parts = [venue_node.get('name')]
                                         if venue_node.get('address'):
                                             parts.append(venue_node.get('address'))
                                         elif venue_node.get('address1'): # Fallback
                                             parts.append(venue_node.get('address1'))
                                         if venue_node.get('city'):
                                             parts.append(venue_node.get('city'))
                                         # country usually is code like 'mx', verify if country or localizedCountryName exists
                                         if venue_node.get('localizedCountryName'):
                                             parts.append(venue_node.get('localizedCountryName'))
                                         elif venue_node.get('country'):
                                             parts.append(venue_node.get('country').upper())

                                         location = ", ".join([p for p in parts if p])
                                     else:
                                         location = "Presencial (Ubicación TBD)"

                                events_data.append({
                                    "title": node.get('title'),
                                    "description": node.get('description', ''),
                                    "url": node.get('eventUrl', '') or f"https://www.meetup.com/{group_slug}/events/{node.get('id')}/",
                                    "location": location,
                                    "dtstart": dt.isoformat(),
                                    "organizer": group_slug,
                                    "source": url
                                })
                        except Exception as e:
                            logger.warning(f"Error parsing date {dt_str}: {e}")

            except Exception as e:
                logger.warning(f"Error parsing NEXT_DATA for {group_slug}: {e}")

        return events_data

    except Exception as e:
        logger.error(f"Error scraping {group_slug}: {e}")
        return []

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scrape Meetup history")
    parser.add_argument("--feeds", default="config/feeds.yaml", help="Path to feeds config file")
    args = parser.parse_args()

    cookie = os.environ.get("MEETUP_COOKIE")
    if not cookie:
        logger.error("Please set MEETUP_COOKIE environment variable.")
        logger.info("Example: export MEETUP_COOKIE='iod=...'")
        sys.exit(1)

    feeds = load_feeds(args.feeds)
    logger.info(f"Found {len(feeds)} Meetup feeds to process.")

    all_events = []

    for feed_url in feeds:
        slug = extract_group_slug(feed_url)
        if slug:
            events = scrape_group_history(slug, cookie)
            logger.info(f"Found {len(events)} events for {slug}")
            all_events.extend(events)
            time.sleep(2) # Respetar rate limits

    # Asegurar que src esta en path
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root / "src"))

    from cronquiles.history_manager import HistoryManager
    hm = HistoryManager()
    hm.load_history()

    # Convertir a formato compatible con HistoryManager (dicts) y mergear
    # El scraper ya devuelve dicts compatibles

    # Necesitamos "normalizar" un poco para que el título coincida con lo que espera el sistema
    # El sistema usa formato "Grupo|Titulo|Loc".
    # Lo ideal seria usar EventNormalized, pero requeriría instanciar objetos complejos.
    # Vamos a guardar raw y dejar que el sistema lo normalice al cargar?
    # No, HistoryManager espera ya el dict "final".

    # Vamos a inyectar logic simple de normalizacion aqui
    for e in all_events:
        # Formatear titulo estilo sistema
        # Grupo|Nombre|Loc
        # Esto es una aproximación, idealmente usariamos EventNormalized logic
        grp = e['organizer'].replace('-', ' ').title()
        loc = "Online" if e['location'] == "Online" else "México" # Simplificado
        e['title'] = f"{grp}|{e['title']}|{loc}"

        # Tags (simple)
        e['tags'] = []

    # Guardar
    count_before = len(hm.events)

    # Mockear objetos EventNormalized simplificados para usar el metodo merge_events?
    # O mejor agregar metodo add_raw_dict a HistoryManager?
    # Usaremos un hack: manipular el dict interno de HM directamente

    logging.info("Merging scraped events...")
    new_scraped = 0
    for e in all_events:
        key = f"{e['title']}_{e['dtstart']}"
        # Always update in case parsing logic improved (like location)
        if key not in hm.events:
            new_scraped += 1
        hm.events[key] = e

    hm.save_history()
    logger.info(f"Done. Added {new_scraped} new historical events.")

if __name__ == "__main__":
    # Asegurar que src esta en path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
