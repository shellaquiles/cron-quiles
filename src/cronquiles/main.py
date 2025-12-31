#!/usr/bin/env python3
"""
CLI principal para Cron-Quiles - Agregador de calendarios tech.

Uso:
    python main.py                    # Usa feeds.yaml por defecto
    python main.py --feeds feeds.yaml # Especifica archivo de feeds
    python main.py --json             # Genera también JSON
    python main.py --output custom.ics # Nombre personalizado para ICS
"""

import argparse
import logging
import sys
from pathlib import Path

import yaml

from .ics_aggregator import ICSAggregator, logger

try:
    from .google_calendar import GoogleCalendarPublisher

    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False


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

    args = parser.parse_args()

    # Configurar nivel de logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Cargar feeds
    feeds_path = Path(args.feeds)

    if not feeds_path.exists():
        logger.error(f"Archivo de feeds no encontrado: {args.feeds}")
        logger.info(
            "Crea un archivo config/feeds.yaml o usa --feeds para especificar otro archivo"
        )
        sys.exit(1)

    if feeds_path.suffix.lower() in [".yaml", ".yml"]:
        feed_urls = load_feeds_from_yaml(str(feeds_path))
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

    # Generar ICS
    ics_file = aggregator.generate_ics(events, args.output)
    logger.info(f"✓ Calendario ICS generado: {ics_file}")

    # Generar JSON si se solicita
    if args.json:
        json_file = aggregator.generate_json(events, args.json_output)
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
