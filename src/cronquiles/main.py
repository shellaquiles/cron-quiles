#!/usr/bin/env python3
"""
CLI principal para Cron-Quiles - Agregador de calendarios tech.

Uso:
    python main.py                    # Usa feeds.yaml por defecto
    python main.py --feeds feeds.yaml # Especifica archivo de feeds
    python main.py --json             # Genera también JSON
    python main.py --output custom.ics # Nombre personalizado para ICS
    python main.py --city cdmx        # Genera calendario para una ciudad específica
    python main.py --all-cities       # Genera calendarios para todas las ciudades
"""

import argparse
import logging
import sys
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import os

from dotenv import load_dotenv
import yaml
import json

# Cargar variables de entorno desde .env si existe
load_dotenv()

from .ics_aggregator import ICSAggregator, EventNormalized, logger



def load_cities_from_yaml(yaml_file: str) -> Dict[str, Dict]:
    """
    Carga configuración de ciudades desde un archivo YAML.

    Formato esperado:
        cities:
          cdmx:
            name: "Ciudad de México"
            slug: "cdmx"
            timezone: "America/Mexico_City"
            feeds:
              - url: https://example.com/feed.ics
                name: "Comunidad"
                description: "..."

    Args:
        yaml_file: Ruta al archivo YAML

    Returns:
        Diccionario con configuración de ciudades: {city_slug: city_config}
    """
    try:
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        cities = data.get("cities", {})
        if not cities:
            logger.warning("No se encontraron ciudades en el archivo YAML")
            return {}

        return cities

    except FileNotFoundError:
        logger.error(f"Archivo no encontrado: {yaml_file}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parseando YAML: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error cargando ciudades: {e}")
        sys.exit(1)


def load_feeds_from_yaml(yaml_file: str) -> list:
    """
    Carga URLs de feeds desde un archivo YAML.

    Formato esperado:
        feeds:
          - url: https://example.com/feed.ics
          - url: https://another.com/feed.ics

    O formato simple:
        feeds:
          - https://example.com/feed.ics
          - https://another.com/feed.ics

    Args:
        yaml_file: Ruta al archivo YAML

    Returns:
        Lista de URLs de feeds
    """
    try:
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        feeds = data.get("feeds", [])

        # Manejar dos formatos: lista de strings o lista de dicts con 'url'
        feed_config = []
        for feed in feeds:
            if isinstance(feed, str):
                feed_config.append({"url": feed, "name": None})
            elif isinstance(feed, dict) and "url" in feed:
                feed_config.append(feed)
            else:
                logger.warning(f"Formato de feed inválido: {feed}")

        return feed_config

    except FileNotFoundError:
        logger.error(f"Archivo no encontrado: {yaml_file}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parseando YAML: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error cargando feeds: {e}")
        sys.exit(1)


def load_feeds_from_txt(txt_file: str) -> list:
    """
    Carga URLs de feeds desde un archivo de texto (una URL por línea).

    Args:
        txt_file: Ruta al archivo de texto

    Returns:
        Lista de URLs de feeds
    """
    try:
        with open(txt_file, "r", encoding="utf-8") as f:
            return [{"url": line.strip(), "name": None}
                    for line in f
                    if line.strip() and not line.strip().startswith("#")]
    except FileNotFoundError:
        logger.error(f"Archivo no encontrado: {txt_file}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error cargando feeds desde texto: {e}")
        sys.exit(1)


def load_manual_events(json_file: str) -> list:
    """
    Carga eventos manuales desde un archivo JSON.

    Args:
        json_file: Ruta al archivo JSON

    Returns:
        Lista de eventos (diccionarios)
    """
    try:
        if not os.path.exists(json_file):
            return []

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                logger.warning(f"Formato de eventos manuales inválido en {json_file}")
                return []
            return data
    except Exception as e:
        logger.error(f"Error cargando eventos manuales: {e}")
        return []


def normalize_url(url: str) -> str:
    """
    Normaliza una URL para comparación (meetup, luma, etc).
    Quita protocolos, subdominios comunes, sufijos de eventos y slashes.
    """
    if not url:
        return ""

    # Remover protocolo y www
    u = re.sub(r'^https?://(www\.)?', '', url)

    # Remover sufijos comunes de Meetup/Luma/Eventbrite
    u = re.sub(r'/events(/ical)?/?(\?.*)?$', '', u)
    u = u.replace('/?type=past', '')

    # Limpiar trailing slashes
    u = u.rstrip('/')

    return u.lower()


def get_feeds_for_city(city_config: Dict) -> List[str]:
    """
    Extrae las URLs de feeds de la configuración de una ciudad.

    Args:
        city_config: Configuración de la ciudad (dict con 'feeds')

    Returns:
        Lista de URLs de feeds
    """
    feeds = city_config.get("feeds", [])
    feed_urls = []
    for feed in feeds:
        if isinstance(feed, str):
            feed_urls.append(feed)
        elif isinstance(feed, dict) and "url" in feed:
            feed_urls.append(feed["url"])
        else:
            logger.warning(f"Formato de feed inválido: {feed}")
    return feed_urls


def generate_states_metadata(grouped_events: Dict[str, List[EventNormalized]], output_file: str):
    """
    Genera un archivo JSON con los metadatos de los estados que tienen eventos.
    """
    import json
    import pycountry
    from datetime import datetime, timezone

    metadata = []

    # Obtener fecha actual con timezone info para comparar (usamos UTC como base simple o local)
    # Los eventos tienen timezone, así que comparar con now() aware es mejor.
    # EventNormalized.dtstart es datetime.
    now = datetime.now(timezone.utc)

    def count_future(events_list):
        count = 0
        for e in events_list:
            if not e.dtstart: continue
            # Asegurar que e.dtstart tenga timezone o asumir UTC si no
            dt = e.dtstart
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            if dt >= now:
                count += 1
        return count

    def get_active_months(events_list):
        months = set()
        for e in events_list:
            if not e.dtstart: continue
            months.add(e.dtstart.strftime("%Y-%m"))
        return sorted(list(months))

    # 1. Agregar entrada para México (unificado)
    all_events_flat = [e for evs in grouped_events.values() for e in evs]
    total_events = len(all_events_flat)
    future_events_mex = count_future(all_events_flat)
    active_months_mex = get_active_months(all_events_flat)

    metadata.append({
        "code": "mexico",
        "name": "México",
        "slug": "mexico",
        "event_count": total_events,
        "future_event_count": future_events_mex,
        "active_months": active_months_mex,
        "emoji": "🇲🇽"
    })

    # 2. Agregar estados individuales
    for code, events in grouped_events.items():
        if not events: continue

        name = code
        emoji = "📅"

        if code.startswith("MX-"):
            try:
                sub = pycountry.subdivisions.get(code=code)
                if sub:
                    name = sub.name
                    # Emojis personalizados para estados populares
                    emojis = {
                        "MX-CMX": "🌮",
                        "MX-JAL": "💻",
                        "MX-NLE": "🏔️",
                        "MX-PUE": "🌋",
                        "MX-YUC": "🏖️"
                    }
                    emoji = emojis.get(code, "🌵")
            except:
                pass
        elif code == "ONLINE":
            name = "Online"
            emoji = "🌐"

        metadata.append({
            "code": code,
            "name": name,
            "slug": code.lower(),
            "event_count": len(events),
            "future_event_count": count_future(events),
            "active_months": get_active_months(events),
            "emoji": emoji
        })

    # Ordenar: México primero, luego por nombre
    metadata.sort(key=lambda x: (x["code"] != "mexico", x["name"]))

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Metadatos de estados generados: {output_file} ({len(metadata)} estados)")


def main():
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description="Cron-Quiles - Agregador de calendarios tech (Meetup, Luma, ICS)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--feeds",
        type=str,
        default="config/feeds.yaml",
        help="Archivo de configuración de feeds (YAML). Por defecto: config/feeds.yaml",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="gh-pages/data",
        help="Directorio de salida para los archivos generados. Por defecto: gh-pages/data",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        default=True,
        help="Generar también archivos JSON (activado por defecto)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout en segundos para requests HTTP. Por defecto: 30",
    )

    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="Número máximo de reintentos por feed. Por defecto: 2",
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Modo verbose (más logging)"
    )

    parser.add_argument(
        "--all-cities",
        action="store_true",
        default=True,
        help="Procesar todos los feeds y generar archivos por estado (activado por defecto)",
    )

    args = parser.parse_args()

    # Configurar nivel de logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    feeds_path = Path(args.feeds)
    if not feeds_path.exists():
        logger.error(f"Archivo de feeds no encontrado: {args.feeds}")
        sys.exit(1)

    # 1. Cargar feeds
    feed_config = load_feeds_from_yaml(str(feeds_path))
    if not feed_config:
        logger.error("No se encontraron feeds para procesar")
        sys.exit(1)

    logger.info(f"Cargados {len(feed_config)} feeds desde {args.feeds}")

    # 1.1 Cargar eventos manuales
    manual_events_path = Path("config/manual_events.json")
    manual_data = load_manual_events(str(manual_events_path))
    if manual_data:
        logger.info(f"Cargados {len(manual_data)} eventos manuales desde {manual_events_path}")

    # 2. Inicializar agregador
    aggregator = ICSAggregator(timeout=args.timeout, max_retries=args.retries)

    # 3. Agregar y unificar eventos
    logger.info("Iniciando agregación de feeds...")
    all_events = aggregator.aggregate_feeds(feed_config, manual_data=manual_data)

    if not all_events:
        logger.warning("No se encontraron eventos en los feeds.")
        sys.exit(0)

    logger.info(f"Total de eventos unificados: {len(all_events)}")

    # 4. Preparar directorio de salida
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 5. Generar archivo unificado de México
    mex_ics = str(output_path / "cronquiles-mexico.ics")
    mex_json = str(output_path / "cronquiles-mexico.json")

    aggregator.generate_ics(all_events, mex_ics, city_name="México")
    if args.json:
        aggregator.generate_json(all_events, mex_json, city_name="México", feeds=feed_config)

    logger.info("✓ Calendario unificado de México generado.")

    # 6. Agrupar por estado y generar archivos dinámicos
    grouped_events = aggregator.group_events_by_state(all_events)

    for state_code, events in grouped_events.items():
        # Normalizar slug para el nombre del archivo
        slug = state_code.lower()
        ics_file = str(output_path / f"cronquiles-{slug}.ics")
        json_file = str(output_path / f"cronquiles-{slug}.json")

        # Intentar obtener nombre legible del estado
        state_name = state_code
        if state_code.startswith("MX-"):
            try:
                import pycountry
                sub = pycountry.subdivisions.get(code=state_code)
                if sub: state_name = sub.name
            except: pass
        elif state_code == "ONLINE":
            state_name = "Online"

        # Identificar qué feeds pertenecen a este estado basándonos en los eventos
        # Obtenemos las URLs de origen de los eventos de este estado (normalizadas)
        state_source_urls = {normalize_url(e.source_url) for e in events if e.source_url}
        # Filtramos los feeds originales comparando versiones normalizadas
        state_feeds = [f for f in feed_config if normalize_url(f.get("url")) in state_source_urls]

        # Incluir organizadores de eventos manuales en la lista de comunidades de este estado
        manual_organizers = {}
        for event in events:
            if event.source_url == "Manual" and event.organizer:
                if event.organizer not in manual_organizers:
                    manual_organizers[event.organizer] = {
                        "name": event.organizer,
                        "description": f"Organizador de eventos manuales (ej: {event.summary})"
                    }

        # Añadir organizadores manuales que no estén ya en state_feeds
        for org_name, org_data in manual_organizers.items():
            if not any(f.get("name") == org_name for f in state_feeds):
                state_feeds.append(org_data)

        aggregator.generate_ics(events, ics_file, city_name=state_name)
        if args.json:
            aggregator.generate_json(events, json_file, city_name=state_name, feeds=state_feeds)

        logger.info(f"✓ Archivos generados para: {state_name} ({len(events)} eventos, {len(state_feeds)} comunidades)")

    # 7. Generar metadatos para el frontend
    generate_states_metadata(grouped_events, str(output_path / "states_metadata.json"))

    # 8. Actualizar estatus de comunidades en docs/COMMUNITIES.md
    try:
        logger.info("Actualizando estatus de comunidades en docs/COMMUNITIES.md...")
        script_path = Path("tools/update_communities_status.py")
        if script_path.exists():
            subprocess.run([sys.executable, str(script_path)], check=True)
            logger.info("Estatus de comunidades actualizado.")
        else:
            logger.warning(f"No se encontró el script de actualización de estatus en {script_path}")
    except Exception as e:
        logger.error(f"Error actualizando estatus de comunidades: {e}")

    logger.info(f"\n✓ Proceso completado exitosamente. Archivos en: {args.output_dir}")


if __name__ == "__main__":
    main()
