# Changelog

Todos los cambios notables en este proyecto están documentados aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), versionado con [SemVer](https://semver.org/lang/es/).

## [Unreleased]

---

## [1.9.1] - 2026-08-28

### Added
- **Terminal CLI**: navegación mensual (`eventos.next/last/reset`), multi-región (`eventos.region`), filtrado de online, branding Shellaquiles.
- **GdgCommunityDev Aggregator**: extracción de eventos de Google Developer Groups vía Bevy API.
- **Frontend Feeds**: CHIDAS TECH, FinTech México, Founder Friends MX, Fvckup Nights, Management In Tech, This Week in Fintech, v0 Prompt to Production MX.
- **Eventos Manuales**: RustMX, Linuxcabal, ClawCon CDMX/GDL, FLISOL, Mobil3, KCD, Senior Dev, Avalanche Hackathon.
- **Identidad Visual**: logo triple-color en consola y arte ASCII actualizado.
- **Footer Dinámico**: badge `VERSIÓN` en las 4 páginas, leído del JSON generado vía `DataService.getVersion()`.
- **Archivo `VERSION`**: fuente única de verdad para la versión del proyecto.

### Changed
- **Rendimiento**: `sleep` de rate-limit solo cuando hay request real (no en caché). Feeds descargados en paralelo (10 workers).
- **Modo `--fast`**: omite enriquecimiento de ubicación y geocoding de historial.
- **`PRODID` en `.ics`**: incluye número de versión `-//Shellaquiles//CronQuiles vX.Y.Z//ES`.
- **JSON generado**: incluye campo `version` en todos los archivos de salida.
- **`pyproject.toml`**: versión dinámica desde `VERSION` vía hatchling.
- **`SECURITY.md`**: tabla de versiones soportadas actualizada a `1.9.x`.

---

## [1.9.0] - 2026-01-21

### Added
- **Multi-fuente de eventos**: campo `sources` con URLs de múltiples plataformas; botones estilizados por plataforma en el frontend.
- **Hi.Events Aggregator**: soporte para plataformas de boletaje open source (Pythonistas GDL).
- **Cache de URLs Luma**: `data/luma_url_cache.json` para conversiones de URLs vanity entre ejecuciones.
- **Links de comunidades**: tarjetas de comunidades con botones a todas sus plataformas.
- **Nuevos feeds**: GDG CloudMX, México City AI/ML/CV Meetup.

### Changed
- **Migración a `uv`**: gestión de dependencias; build system de setuptools a hatchling; CI ~70% más rápido.
- **`Makefile`**: comandos simplificados (`install-dev`, `test`, `format`, `lint`, `run-all`, `serve`).

### Fixed
- **Dependencias incompletas**: `pyproject.toml` ahora declara las 12 dependencias de producción.

---

## [1.8.0] - 2026-01-10

### Added
- **Claude Community** feed vía Luma.
- **Hi.Events Aggregator** inicial (base para 1.9.0).
- `tools/fix_cache_encoding.py`: saneamiento del cache geográfico.

### Changed
- **Filtrado global por país**: solo eventos en México o en línea.
- **Detección de México**: búsqueda de keywords de respaldo en normalización.

### Fixed
- **Encoding del cache**: corregido mojibake en `geocoding_cache.json`.
- **Detección de país**: eventos mexicanos no reconocidos por `pycountry`.

---

## [1.7.0] - 2026-01-07

### Added
- `tools/deduplicate_events.py` y `tools/sort_history.py` para mantenimiento del historial.

### Changed
- **Pestañas de ciudad**: se ocultan si no tienen eventos futuros; `states_metadata.json` incluye `active_months`.
- Eliminado botón "Mostrar historial" de la UI.

### Fixed
- 382 eventos duplicados en `data/history.json` fusionados.
- Scraper de Meetup usa `HistoryManager` para consistencia de llaves.
- `history.json` siempre ordenado por fecha descendente.

---

## [1.6.0] - 2026-01-03

### Added
- **Refactorización de Agregadores**: split monolítico → paquete modular `src/cronquiles/aggregators/`.
- **Eventbrite**: soporte para URLs de organizador y eventos individuales (JSON-LD scraping).
- **Eventos Manuales**: `config/manual_events.json` para eventos sin feed ICS.
- **`docs/COMMUNITIES.md`**: tabla con columna "Estados" generada desde historial.

### Changed
- **Luma**: enriquecimiento de ubicación para eventos con solo URL; limpieza de coordenadas en direcciones.
- Caracteres `|` en títulos reemplazados por ` - ` para evitar conflictos de formato interno.

### Fixed
- Eventos futuros no mostrados cuando el mes actual estaba vacío.
- Filtro de zona horaria que ocultaba eventos al final del mes.

---

## [1.5.0] - 2026-01-01

### Added
- **Generación dinámica de estados**: detección automática → calendarios por estado (`mx-cmx`, `mx-jal`, etc.) sin configuración manual.
- **Normalización ISO**: abreviaturas de estados a códigos estándar (`MX-N.L.` → Nuevo León).
- **Frontend reactivo**: pestañas de navegación generadas desde `states_metadata.json`.
- **`feeds.yaml`**: lista plana, desacoplada de lógica de ciudades.

---

## [1.4.0] - 2026-01-01

### Added
- **CI persistente**: `data/history.json` y `data/geocoding_cache.json` entre ejecuciones de GitHub Actions.
- **`GOOGLE_MAPS_API_KEY`** en CI para geocodificación precisa.
- `populate_cache_from_history.py` y `scan_feeds_and_cache.py`.
- Archivos generados movidos a `gh-pages/data/`.

### Changed
- Eliminada lógica hardcoded de alias; geocodificación 100% API (Google Maps + Nominatim fallback).

---

## [1.3.0] - 2025-12-31

### Added
- **Multi-ciudad**: calendarios separados por ciudad (`cronquiles-cdmx.ics`, `cronquiles-gdl.ics`).
- CLI `--city` y `--all-cities`; `--output-dir` configurable.
- Frontend con pestañas por ciudad; persistencia en `localStorage`.
- Soporte inicial para Guadalajara además de CDMX.

---

## [1.2.0] - 2025-12-31

### Added
- **Formato de títulos**: `Grupo|Evento|Online` o `Grupo|Evento|País|Estado`; detección automática online/presencial.
- **Diseño terminal**: calendario mensual embebido, navegación entre meses, indicadores de días con eventos.
- **Enriquecimiento Meetup**: extracción de direcciones físicas desde páginas de Meetup (JSON-LD/Next.js).
- **Historial persistente**: `HistoryManager` + `data/history.json` con smart merge.
- **`gh-pages/`**: estructura separada para frontend estático.

### Fixed
- Encoding de caracteres con acentos en eventos ICS (mojibake).
- Renderizado de saltos de línea en descripciones (`white-space: pre-wrap`).

---

## [1.1.0] - 2025-12-29

### Added
- Agregador de feeds ICS; normalización, deduplicación y tags automáticos.
- Generación de `.ics` unificado y `.json` con eventos.
- GitHub Actions para actualización automática cada 6 horas.
- Publicación en GitHub Pages con soporte `webcal://`.

### Removed
- Soporte Google Calendar (`google_calendar.py`) y directorio `examples/`.

---

## [1.0.0] - 2025-12-29

### Added
- Versión inicial: soporte Meetup y Luma, deduplicación por título+fecha, tags automáticos.

---

[Unreleased]: https://github.com/shellaquiles/cron-quiles/compare/v1.9.1...HEAD
[1.9.1]: https://github.com/shellaquiles/cron-quiles/compare/v1.9.0...v1.9.1
[1.9.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/shellaquiles/cron-quiles/releases/tag/v1.0.0
