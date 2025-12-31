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
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from .ics_aggregator import ICSAggregator, logger

try:
    from .google_calendar import GoogleCalendarPublisher

    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False


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
        feed_urls = []
        for feed in feeds:
            if isinstance(feed, str):
                feed_urls.append(feed)
            elif isinstance(feed, dict) and "url" in feed:
                feed_urls.append(feed["url"])
            else:
                logger.warning(f"Formato de feed inválido: {feed}")

        return feed_urls

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
            urls = [
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]
        return urls
    except FileNotFoundError:
        logger.error(f"Archivo no encontrado: {txt_file}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error cargando feeds desde texto: {e}")
        sys.exit(1)


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


def process_city(
    city_slug: str,
    city_config: Dict,
    output_dir: Optional[str],
    args: argparse.Namespace,
) -> bool:
    """
    Procesa los feeds de una ciudad y genera los archivos ICS/JSON.

    Args:
        city_slug: Slug de la ciudad (ej: 'cdmx', 'gdl')
        city_config: Configuración de la ciudad
        output_dir: Directorio de salida (None para usar el directorio actual)
        args: Argumentos del CLI

    Returns:
        True si el procesamiento fue exitoso, False en caso contrario
    """
    # Usar el slug de la configuración, o el key del diccionario como fallback
    actual_slug = city_config.get("slug", city_slug)
    city_name = city_config.get("name", city_slug)
    logger.info(f"\n{'='*60}")
    logger.info(f"Procesando ciudad: {city_name} ({actual_slug})")
    logger.info(f"{'='*60}")

    # Extraer feeds de la ciudad
    feed_urls = get_feeds_for_city(city_config)
    if not feed_urls:
        logger.warning(f"No se encontraron feeds para {city_name}")
        return False

    logger.info(f"Cargados {len(feed_urls)} feeds para {city_name}")

    # Inicializar agregador
    aggregator = ICSAggregator(timeout=args.timeout, max_retries=args.retries)

    # Agregar feeds
    logger.info("Iniciando agregación de feeds...")
    events = aggregator.aggregate_feeds(feed_urls)

    if not events:
        logger.warning(f"No se encontraron eventos en los feeds de {city_name}")
        return True  # No es un error, simplemente no hay eventos

    logger.info(f"Total de eventos procesados: {len(events)}")

    # Determinar nombres de archivos de salida
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        ics_file = str(output_path / f"cronquiles-{actual_slug}.ics")
        json_file = str(output_path / f"cronquiles-{actual_slug}.json")
    else:
        ics_file = f"cronquiles-{actual_slug}.ics"
        json_file = f"cronquiles-{actual_slug}.json"

    # Generar ICS con metadata de la ciudad
    aggregator.generate_ics(events, ics_file, city_name=city_name)
    logger.info(f"✓ Calendario ICS generado: {ics_file}")

    # Generar JSON si se solicita
    if args.json:
        aggregator.generate_json(events, json_file, city_name=city_name, feeds=city_config.get("feeds", []))
        logger.info(f"✓ Archivo JSON generado: {json_file}")

    # Estadísticas
    tags_count = {}
    for event in events:
        for tag in event.tags:
            tags_count[tag] = tags_count.get(tag, 0) + 1

    if tags_count:
        logger.info(f"\nTags detectados para {city_name}:")
        for tag, count in sorted(tags_count.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {tag}: {count} eventos")

    return True


def main():
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description="Cron-Quiles - Agregador de calendarios tech (Meetup, Luma, ICS)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py
  python main.py --feeds feeds.yaml
  python main.py --feeds list_icals.txt --json
  python main.py --output eventos.ics --json
        """,
    )

    parser.add_argument(
        "--feeds",
        type=str,
        default="config/feeds.yaml",
        help="Archivo de configuración de feeds (YAML o TXT). Por defecto: config/feeds.yaml",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="cronquiles.ics",
        help="Nombre del archivo ICS de salida. Por defecto: cronquiles.ics",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Generar también archivo JSON con los eventos",
    )

    parser.add_argument(
        "--json-output",
        type=str,
        default="cronquiles.json",
        help="Nombre del archivo JSON de salida. Por defecto: cronquiles.json",
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
        "--google-calendar",
        action="store_true",
        help="Publicar eventos directamente en Google Calendar",
    )

    parser.add_argument(
        "--google-credentials",
        type=str,
        default="config/credentials.json",
        help="Ruta al archivo de credenciales OAuth2 de Google. Default: config/credentials.json",
    )

    parser.add_argument(
        "--google-token",
        type=str,
        default="config/token.json",
        help="Ruta donde guardar el token de acceso. Default: config/token.json",
    )

    parser.add_argument(
        "--google-calendar-id",
        type=str,
        default="primary",
        help="ID del calendario donde publicar. Default: 'primary' (calendario principal)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simular publicación sin publicar realmente (útil para pruebas)",
    )

    parser.add_argument(
        "--city",
        type=str,
        help="Generar calendario para una ciudad específica (ej: cdmx, gdl). Requiere feeds.yaml con estructura de ciudades.",
    )

    parser.add_argument(
        "--all-cities",
        action="store_true",
        help="Generar calendarios para todas las ciudades definidas en feeds.yaml",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directorio donde guardar los archivos de salida. Si se especifica, los archivos se nombrarán como cronquiles-{ciudad}.ics/json",
    )

    args = parser.parse_args()

    # Configurar nivel de logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Cargar configuración
    feeds_path = Path(args.feeds)

    if not feeds_path.exists():
        logger.error(f"Archivo de feeds no encontrado: {args.feeds}")
        logger.info(
            "Crea un archivo config/feeds.yaml o usa --feeds para especificar otro archivo"
        )
        sys.exit(1)

    # Modo multi-ciudad: procesar ciudades desde YAML
    if args.city or args.all_cities:
        if feeds_path.suffix.lower() not in [".yaml", ".yml"]:
            logger.error("Los modos --city y --all-cities requieren un archivo YAML")
            sys.exit(1)

        cities = load_cities_from_yaml(str(feeds_path))
        if not cities:
            logger.error("No se encontraron ciudades en el archivo YAML")
            sys.exit(1)

        if args.city:
            # Procesar una ciudad específica
            if args.city not in cities:
                logger.error(
                    f"Ciudad '{args.city}' no encontrada. Ciudades disponibles: {', '.join(cities.keys())}"
                )
                sys.exit(1)
            city_config = cities[args.city]
            success = process_city(args.city, city_config, args.output_dir, args)
            if not success:
                sys.exit(1)
        elif args.all_cities:
            # Procesar todas las ciudades (excluyendo categorías especiales)
            # Por el momento, excluimos "otras_ciudades" que agrupa comunidades
            # de otras ciudades pero no genera calendarios separados aún
            excluded_cities = {"otras_ciudades"}
            active_cities = {
                slug: config
                for slug, config in cities.items()
                if slug not in excluded_cities
            }
            
            if not active_cities:
                logger.error("No se encontraron ciudades activas para procesar")
                sys.exit(1)
            
            logger.info(f"Procesando {len(active_cities)} ciudades...")
            success_count = 0
            for city_slug, city_config in active_cities.items():
                if process_city(city_slug, city_config, args.output_dir, args):
                    success_count += 1
            logger.info(f"\n✓ Procesadas {success_count}/{len(active_cities)} ciudades exitosamente")
        else:
            logger.error("Debes especificar --city o --all-cities")
            sys.exit(1)

    else:
        # Modo legacy: procesar feeds directamente (compatibilidad hacia atrás)
        if feeds_path.suffix.lower() in [".yaml", ".yml"]:
            # Intentar cargar como formato legacy primero
            try:
                with open(str(feeds_path), "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                # Si tiene 'cities', sugerir usar --city o --all-cities
                if "cities" in data:
                    logger.warning(
                        "El archivo YAML tiene estructura de ciudades. "
                        "Usa --city <ciudad> o --all-cities para procesar ciudades específicas."
                    )
                    logger.info(f"Ciudades disponibles: {', '.join(data['cities'].keys())}")
                    sys.exit(1)
                # Si no tiene 'cities', usar formato legacy
                feed_urls = load_feeds_from_yaml(str(feeds_path))
            except Exception as e:
                logger.error(f"Error cargando feeds: {e}")
                sys.exit(1)
        else:
            # Asumir formato de texto plano
            feed_urls = load_feeds_from_txt(str(feeds_path))

        if not feed_urls:
            logger.error("No se encontraron feeds para procesar")
            sys.exit(1)

        logger.info(f"Cargados {len(feed_urls)} feeds desde {args.feeds}")

        # Inicializar agregador
        aggregator = ICSAggregator(timeout=args.timeout, max_retries=args.retries)

        # Agregar feeds
        logger.info("Iniciando agregación de feeds...")
        events = aggregator.aggregate_feeds(feed_urls)

        if not events:
            logger.warning("No se encontraron eventos en los feeds")
            sys.exit(0)

        logger.info(f"Total de eventos procesados: {len(events)}")

        # Determinar archivo de salida
        if args.output_dir:
            output_path = Path(args.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            ics_file = str(output_path / args.output)
            json_file = str(output_path / args.json_output) if args.json else None
        else:
            ics_file = args.output
            json_file = args.json_output if args.json else None

        # Generar ICS
        aggregator.generate_ics(events, ics_file)
        logger.info(f"✓ Calendario ICS generado: {ics_file}")

        # Generar JSON si se solicita
        if args.json:
            aggregator.generate_json(events, json_file)
            logger.info(f"✓ Archivo JSON generado: {json_file}")

        # Publicar en Google Calendar si se solicita
        if args.google_calendar:
            if not GOOGLE_CALENDAR_AVAILABLE:
                logger.error(
                    "Google Calendar no está disponible. "
                    "Instala las dependencias: pip install google-auth google-auth-oauthlib google-api-python-client"
                )
            else:
                publisher = GoogleCalendarPublisher(
                    credentials_file=args.google_credentials,
                    token_file=args.google_token,
                    calendar_id=args.google_calendar_id,
                )

                if publisher.authenticate():
                    stats = publisher.publish_events(events, dry_run=args.dry_run)
                    if args.dry_run:
                        logger.info(f"[DRY RUN] Se publicarían {stats['success']} eventos")
                    else:
                        logger.info(
                            f"✓ Publicados {stats['success']} eventos en Google Calendar"
                        )
                        if stats["failed"] > 0:
                            logger.warning(
                                f"⚠ {stats['failed']} eventos fallaron al publicar"
                            )
                else:
                    logger.error("No se pudo autenticar con Google Calendar")

        # Estadísticas
        tags_count = {}
        for event in events:
            for tag in event.tags:
                tags_count[tag] = tags_count.get(tag, 0) + 1

        if tags_count:
            logger.info("\nTags detectados:")
            for tag, count in sorted(tags_count.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {tag}: {count} eventos")

    logger.info("\n✓ Proceso completado exitosamente")


if __name__ == "__main__":
    main()
