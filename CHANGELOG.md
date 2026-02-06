# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Added
- **Documentación del flujo**: Nuevo `docs/FLUJO.md` con el flujo completo del pipeline (entrada → agregación → salida) y actualización de la página (schedule, push, workflow). Actualizados `docs/PROJECT_STRUCTURE.md`, `docs/GITHUB_PAGES_SETUP.md`, `.github/workflows/README.md`, `gh-pages/README.md` y `gh-pages/README-LOCAL.md` para referenciar el flujo actual y corregir URLs/ejemplos.
- **Frontend / UX (gh-pages)**:
  - **Calendario interactivo**: Al hacer clic en un día del mes se desplaza la vista a la lista de eventos de ese día (scroll suave y resaltado breve). La lista de eventos se agrupa por día con anclas `#day-YYYY-MM-DD`.
  - **Fichas de evento**: Fecha visible primero (pill "día mes" + hora), badge de categoría/organizador, título, ubicación única (sin repetir Address ni Hosted by en la descripción). Reducción de redundancia bilingüe en descripciones.
  - **Eventos online**: Si el evento es online (URL como ubicación o `event.online`), se muestra "en línea" solo en la pill de estado (sin repetir en bloque de ubicación). No se muestra el enlace "Ver en mapa".
  - **Ver en mapa**: Para eventos con dirección física, enlace "Ver en mapa" (siguiente línea a la dirección) que abre Google Maps con la dirección. Campo `online` en el JSON de salida (`models.py`, `schemas.py`) para que el frontend distinga online vs presencial.
  - **Calendario en móvil**: Cabecera en una fila (flechas ← →, mes, Hoy), grid a ancho completo, celdas y botones con área de toque ≥44px.
  - **Navegación multipágina**: Páginas `index.html` (inicio), `eventos.html` (calendario + lista), `suscribir.html` (añadir al calendario), `comunidades.html` (lista de comunidades), con header/nav y estilos compartidos.
- **Revisión UI/UX (Laws of UX)**: Documento `docs/UX_REVISION_LAWS_OF_UX.md` con revisión crítica escritorio y móvil aplicando principios de [Laws of UX](https://lawsofux.com/). Mejoras aplicadas: estilo visible para página actual en nav (`.section-nav-link.active`), área táctil ≥44px en lang switcher (ES/EN), `:focus-visible` en nav, tabs de ciudad, botones del calendario y selector de ciudad para accesibilidad por teclado.
- **Feed CHIDAS TECH**: Luma `https://luma.com/nc2fac44` (comunidad tech, eventos sobre redes e infraestructura).
- **Feed Management In Tech**: Luma `https://luma.com/qhszdqs3` (conversaciones sobre liderazgo y gestión de equipos en tech, Ciudad de México).
- **Feed Founder Friends Mexico**: Luma `https://luma.com/FFMexico2026` (comunidad de founders por Hustle Fund, Ciudad de México).
- **Feeds FinTech México y Sudo FCiencias**: Luma `https://luma.com/eofagheq`, `https://luma.com/02t893pf` (FinTech México), `https://luma.com/e17fbtoo` (Sudo FCiencias, evento bases de datos no relacionales).
- **Feed Fvckup Nights**: Luma perfil `https://luma.com/user/usr-OqGmWs21jbaz5fK` (solo eventos en MX; el pipeline ya filtra por país).
- **Feed This Week in Fintech**: Luma `https://luma.com/lkn7cfxz` (AI x Fintech Talks @ Mexico Fintech Week 2026, Ciudad de México).
- **Feed v0 Prompt to Production Mexico City**: Luma `https://luma.com/fdg8riz2` (evento oficial v0/Vercel en México, aibuilders.mx, Ciudad de México).
- **Evento manual**: Coding Sessions – MDC x Linuxeros Zapopan (sábado 7 feb 2026, 10:00–14:00, Hacker Garage, Zapopan).

### Changed
- **Rendimiento**: Los `sleep` de rate-limit solo se aplican cuando hay llamada real a la API (no cuando hay caché). Geocoding: dormir solo si `geocode_location` usó la API; Luma/Meetup: dormir solo después de un enrich que hizo request. El pipeline es más rápido cuando el caché está poblado.
- **Extracción paralela de feeds**: Los feeds se descargan en paralelo (por defecto 10 workers). Reduce mucho el tiempo cuando hay ~76 feeds.
- **Modo `--fast`**: Omite enriquecimiento de ubicación (Luma/Meetup) y la fase 2 de geocoding (healing de historial). Uso: `make run ARGS="--fast"` o `python -m cronquiles.main --fast`.

## [1.9.0] - 2026-01-21

### Added
- **Soporte multi-fuente para eventos**: Los eventos ahora pueden tener múltiples URLs de diferentes plataformas (Meetup, Luma, Eventbrite)
  - Campo `sources` en eventos con información de plataforma y etiquetas
  - Botones estilizados en el frontend con colores por plataforma (rojo para Meetup, morado para Luma, naranja para Eventbrite)
  - Deduplicación mejorada que combina fuentes de eventos duplicados
- **Enlaces de comunidades**: Las tarjetas de comunidades ahora muestran enlaces a todas sus plataformas
  - Campo `links` en comunidades con información de plataforma
  - Renderizado de botones de plataforma en `CommunityList.js`
- **Cache persistente para URLs de Luma**: Nuevo archivo `data/luma_url_cache.json` para evitar requests innecesarios
  - Conversión de URLs vanity a URLs de API
  - Persistencia entre ejecuciones del pipeline
- **Funciones de detección de plataforma**: `detect_platform()` y `get_platform_label()` en `models.py`
- **Nuevos esquemas**: `SourceSchema` y `CommunityLinkSchema` en `schemas.py`
- **Nuevos feeds**: GDG CloudMX y México City AI, Machine Learning and Computer Vision Meetup

### Changed
- **Migración a uv**: El proyecto ahora usa `uv` en lugar de `pip` para gestión de dependencias
  - Build system actualizado de setuptools a hatchling
  - Generación automática de `uv.lock` para reproducibilidad garantizada
  - GitHub Actions (~70% más rápido) con cache nativo de uv
  - `pyproject.toml` ahora es la fuente única de verdad para todas las 12 dependencias de producción

### Added
- **Makefile**: Sistema de comandos simplificados para desarrollo
  - `make install-dev` - Instala todas las dependencias
  - `make test` - Ejecuta tests
  - `make format` - Formatea código
  - `make lint` - Verifica estilo
  - `make run-all` - Ejecuta pipeline completo
  - Y más. Ver `make help` para lista completa
- **Documentación**:
  - `CLAUDE.md`: Guía para Claude Code con nuevos comandos
  - `MIGRATION.md`: Guía para migrar de pip a uv
  - Updated `CONTRIBUTING.md` con instrucciones de setup con uv
- **CI/CD**:
  - `.github/workflows/tests.yml` ahora usa uv con cache
  - `.github/workflows/update-events.yml` actualizado para uv

### Fixed
- **Dependencias Incompletas**: `pyproject.toml` solo declaraba 4 de 12 dependencias de producción
  - Agregadas: google-auth, google-auth-oauthlib, google-api-python-client, beautifulsoup4, pycountry, geopy, unidecode, python-dotenv

### Notes
- `requirements.txt` aún disponible pero generado desde `uv.lock`
- `uv.lock` **debe** ser commiteado en git para reproducibilidad
- Compatibilidad hacia atrás: El proyecto sigue siendo instalable con pip si es necesario

## [1.8.0] - 2026-01-10

### Added
- Nuevo feed de Luma para **Claude Community**.
- Script de mantenimiento `tools/fix_cache_encoding.py` para sanear el cache geográfico.
- **Soporte Hi.Events**: Nuevo agregador modular `HiEventsAggregator` para plataformas especializadas.
- **Integración Pythonistas GDL**: Añadida la comunidad de Guadalajara basada en Hi.Events.

### Changed
- **Filtrado Global por País**: Implementado un filtro en el pipeline de agregación para asegurar que solo se procesen eventos ubicados en México o eventos Online, manteniendo el calendario enfocado en la comunidad local.
- **Mejora en Normalización**: Se robusteció la detección de ubicaciones en México mediante búsqueda de keywords de respaldo.

### Fixed
- **Codificación del Cache**: Corregido problema de "símbolos raros" (mojibake) en `geocoding_cache.json` mediante sanitización automática y mejoras en `models.py`.
- **Detección de País**: Se corrigió el filtrado incorrecto de eventos mexicanos cuyas direcciones no eran reconocidas inicialmente por `pycountry`.

## [1.7.0] - 2026-01-07

### Added
- **Herramientas de Mantenimiento**:
  - `tools/deduplicate_events.py`: Script para limpiar duplicados en el historial basado en lógica de normalización `EventNormalized`.
  - `tools/sort_history.py`: Script para reordenar el historial usando la lógica canónica de `HistoryManager`.

### Changed
- **Rediseño de Pestañas de Ciudad** (cambio)
  - **Filtrado Inteligente**: Las pestañas de ciudades ahora se ocultan automáticamente si no tienen eventos futuros o en el mes actual.
  - **Excepciones de Visibilidad**: "México" y la ciudad seleccionada siempre permanecen visibles para facilitar la navegación.
  - **Metadatos Expandidos**: `states_metadata.json` ahora incluye `active_months` para permitir un filtrado preciso en el frontend.
  - **Limpieza de UI**: Se eliminó el botón de "Mostrar historial" para mantener la interfaz limpia y enfocada en eventos relevantes.

### Fixed
- **Deduplicación de Historial**: Se identificaron y fusionaron 382 eventos duplicados en `data/history.json` causados por discrepancias en la normalización de títulos (Title Case vs slug).
- **Scraper de Meetup**: Corrección en `tools/scrape_meetup_history.py` para utilizar `HistoryManager` al guardar eventos, asegurando consistencia en la generación de llaves y evitando futuros duplicados.
- **Carga de Configuración**: El scraper ahora soporta carga automática de variables de entorno desde `.env` (específicamente `MEETUP_COOKIE`).
- **Ordenamiento de Historial**: Validación estricta para asegurar que `history.json` siempre se guarde ordenado por fecha descendiente (más recientes primero).
- **Cache de Metadatos**: Se implementó "cache busting" en la carga de `states_metadata.json` para asegurar que los usuarios siempre vean la lista de ciudades actualizada.

## [1.6.0] - 2026-01-03

- **Refactorización de Agregadores** (cambio mayor)
  - Split monolítico de `ics_aggregator.py` a paquete modular `src/cronquiles/aggregators/`.
  - Implementación de clases especializadas: `GenericICSAggregator`, `EventbriteAggregator`, `LumaAggregator`, `MeetupAggregator`, `ManualAggregator`.
  - Orchestrador unificado en `EventPipeline` (antes `ICSAggregator`).
- **Nuevos Feeds Soportados** (nuevo)
  - **Eventbrite**: Soporte completo para URLs de organizador y eventos individuales (scrapeo directo JSON-LD).
- **Documentación** (mejora)
  - `docs/COMMUNITIES.md`: Tabla unificada con columna "Estados", generada automáticamente desde el historial de eventos.
  - Actualización de reglas de estatus (12/18 meses).

### Added
- **Soporte para Eventos Manuales** (nuevo)
  - Configuración vía `config/manual_events.json` para eventos sin feed ICS.
  - Integración automática en el calendario unificado.
- **Mejoras en Calendario Web** (nuevo)
  - **Próximos Eventos**: Si el mes actual no tiene eventos, el calendario muestra automáticamente una lista de eventos futuros.
  - **Información de Debug** (temporalmente usada para ver problemas, ya removida).

### Changed
- **Mejoras en Luma** (cambio)
  - **Enriquecimiento de Ubicación**: Ahora se procesan eventos de Luma que solo tienen URL como ubicación.
  - **Limpieza de Direcciones**: Se eliminan coordenadas numéricas al principio de las direcciones de Luma para mejorar la geocodificación.
- **Normalización de Títulos** (cambio)
  - **Manejo de Pipes**: Los caracteres `|` en los títulos originales se reemplazan por ` - ` para evitar conflictos con el separador interno del sistema.


### Fixed
- **Visualización de Eventos Manuales**: Corregido bug donde eventos futuros no se mostraban si el mes actual estaba vacío.
- **Filtro de Zona Horaria**: Corregido el filtrado de eventos en el calendario que ocultaba eventos debido a desfases horarios (ej: eventos al final del mes).
- **Display Móvil**: Reportado y en seguimiento (Issue #9) problemas de diseño en pantallas pequeñas.

## [1.5.0] - 2026-01-01

### Added
- **Generación Dinámica de Estados** (nuevo)
  - **Detección Automática**: El sistema ahora detecta el estado de cada evento y genera calendarios individuales por estado (`mx-cmx`, `mx-jal`, etc.) sin configuración manual.
  - **Normalización ISO**: Se mejoró el reconocimiento de abreviaturas de estados (ej: `MX-N.L.` -> `Nuevo León`) usando estándares ISO.
  - **Mapeo Robusto de Comunidades**: Los archivos JSON de cada ciudad ahora incluyen metadatos de las comunidades asociadas, resueltos mediante normalización de URLs para ignorar variaciones en el historial.
  - **Frontend Reactivo**: Las pestañas de navegación en la web se generan dinámicamente basándose en los metadatos de los estados procesados.
  - **Simplificación de Configuración**: `feeds.yaml` ahora usa una lista plana, desacoplada de la lógica de ciudades/estados.
  - **Pruebas de Normalización**: Implementadas pruebas automatizadas para asegurar la correcta clasificación de eventos por estado.

## [1.4.0] - 2026-01-01

### Added
- **Infraestructura de Datos y CI** (nuevo)
  - **Persistencia de Datos**: CI (GitHub Actions) ahora persiste `data/history.json` y `data/geocoding_cache.json` entre ejecuciones.
  - **Inyección de Secretos**: CI ahora utiliza `GOOGLE_MAPS_API_KEY` para geocodificación precisa en la nube.
  - **Nuevas Herramientas de Mantenimiento**:
    - `populate_cache_from_history.py`: Reconstuye el cache geográfico usando el historial verificado.
    - `scan_feeds_and_cache.py`: Escanea todos los feeds activos y asegura que sus ubicaciones estén en cache.
- **Estructura de Datos** (nuevo)
  - Archivos generados movidos a `gh-pages/data/` para una separación limpia entre aplicación y datos.

### Changed
- **Refactorización de Ubicación** (cambio)
  - **Eliminación de Lógica Hardcoded**: Se eliminaron diccionarios manuales de alias, adivinanza de países por keywords y hacks específicos (ej. Amazon HQ).
  - **Geocodificación 100% API**: El sistema ahora confía plenamente en Google Maps API (con fallback a Nominatim) para la resolución de lugares.
- **Frontend Actualizado** (cambio)
  - `config.js` y `index.html` actualizados para consumir datos desde la nueva ruta `gh-pages/data/`.

## [1.3.0] - 2025-12-31

### Added
- **Soporte multi-ciudad** (nuevo)
  - Estructura de configuración por ciudades en `feeds.yaml`
  - Generación de calendarios separados por ciudad (ej: `cronquiles-cdmx.ics`, `cronquiles-gdl.ics`)
  - Argumentos CLI `--city` y `--all-cities` para procesar ciudades específicas o todas
  - Argumento `--output-dir` para especificar directorio de salida
  - Metadatos de ciudad en archivos ICS y JSON generados
  - Interfaz web con pestañas para cambiar entre ciudades
  - Persistencia de ciudad seleccionada en localStorage
  - Enlaces de descarga dinámicos que se actualizan según la ciudad seleccionada
  - Soporte inicial para Guadalajara (GDL) además de Ciudad de México (CDMX)
  - Compatibilidad hacia atrás con formato legacy de `feeds.yaml`
- **Actualización completa de documentación AGENTS.md** (nuevo)
  - Documentación actualizada con todas las funcionalidades implementadas
  - Sección de estado actual del proyecto con 12 funcionalidades principales
  - Estructura del proyecto documentada
  - Próximas mejoras posibles listadas
  - **Sección sobre archivos generados**: Instrucciones para no commitear manualmente `cronquiles.ics` y `cronquiles.json` (solo GitHub Actions los commitea)

## [1.2.0] - 2025-12-31

### Added
- **Formato de títulos inteligente** (nuevo)
  - Formato automático según tipo de evento: `Grupo|Nombre evento|Online` o `Grupo|Nombre evento|País|Estado`
  - Detección automática de eventos online vs presenciales basada en palabras clave
  - Extracción inteligente del nombre del grupo desde organizador, descripción o URL
  - Extracción de país y estado para eventos presenciales (especialmente estados de México)
  - Inferencia de ubicación por defecto (México|CDMX) cuando no se puede determinar
- **Interfaz web mejorada con diseño terminal** (nuevo)
  - Diseño estilo terminal consistente con shellaquiles-org
  - Calendario mensual visual embebido con eventos del mes
  - Navegación entre meses con botones anterior/siguiente
  - Visualización automática de todos los eventos del mes actual
  - Indicadores visuales de días con eventos
  - Estilo responsive optimizado para móvil y escritorio
  - **Enriquecimiento de ubicación para Meetup** (nuevo)
    - Extracción automática de direcciones físicas desde las páginas de Meetup (JSON-LD/Next.js)
    - Mejora la información de eventos presenciales que el feed iCal de Meetup suele omitir
    - Sistema respetuoso con User-Agent y delays entre peticiones
  - **Visualización mejorada de títulos**: Separación visual del grupo (verde, bold), nombre del evento (blanco) y ubicación (gris, italic)
  - **Descripciones expandibles**: Descripciones largas se muestran colapsadas con opción "Ver más/Ver menos"
  - **Limpieza de descripciones**:
    - Omisión automática de la primera línea de la descripción (que suele repetir el grupo)
    - Truncado de espacios e indentación innecesaria en cada línea para un diseño más compacto
  - **Fecha al final**: La fecha se muestra al final de cada evento con estilo menos prominente
- **Estructura mejorada para GitHub Pages** (nuevo)
  - Archivos movidos a carpeta `gh-pages/` para mejor organización
  - Scripts de desarrollo local (`serve.py`, `serve.sh`)
  - Documentación para desarrollo local (`README-LOCAL.md`)
- **Mejoras en la interfaz web** (nuevo)
  - Detección automática de errores en desarrollo local con mensajes útiles
  - Mejor manejo de errores con instrucciones claras
  - Interfaz más limpia y enfocada
- **Persistencia de Historial y Scraping** (nuevo)
  - Nuevo módulo `HistoryManager` para preservar eventos pasados y realizar "smart merge"
  - Herramienta `scrape_meetup_history.py` para obtener direcciones físicas detalladas (calle, número) de Meetup
  - Sistema de persistencia en `data/history.json`
  - Mejora la calidad de datos combinando lo mejor del feed vivo y el historial

### Changed
- **Formato de eventos** (cambio)
  - Los títulos ahora siguen formato estructurado con separadores `|`
  - Mejora en la detección de eventos online vs presenciales
  - Extracción mejorada de información de ubicación desde descripciones
- **Reorganización de archivos** (cambio)
  - Archivos generados (`cronquiles.ics`, `cronquiles.json`) ahora se generan en `gh-pages/`
  - Workflow de GitHub Actions actualizado para generar archivos directamente en `gh-pages/`
  - `.gitignore` actualizado para reflejar nueva estructura
- **Interfaz web** (cambio)
  - Diseño completamente renovado con tema terminal
  - Calendario visual reemplaza lista de próximos eventos
  - Mejor experiencia de usuario con información más accesible
  - **Espaciado optimizado**: Reducción significativa de espacios en blanco entre elementos
  - **Renderizado de descripciones**: Cambio de `white-space: pre-line` a `pre-wrap` para preservar saltos de línea
  - **Orden de elementos**: Fecha movida al final de cada evento, después del título y detalles
  - **Formato de fecha mejorado**: Muestra solo la fecha (sin hora) y rango de horas separado (ej: "1 de febrero • 18:00 - 20:00")
  - **Mejoras en renderizado**: Mejor manejo de espacios en blanco y saltos de línea múltiples en descripciones
  - **Limpieza de ubicaciones**: Eliminación automática de espacios en blanco innecesarios en ubicaciones

### Fixed
- Corregido problema de codificación de caracteres (acentos) en eventos ICS
  - Los caracteres con acentos ahora se muestran correctamente (ej: "Cariño" en lugar de "CariÃ±o")
  - Implementada función `fix_encoding()` para corregir problemas de mojibake automáticamente
- Corregido renderizado de saltos de línea en descripciones de eventos
  - Las descripciones ahora preservan correctamente los saltos de línea originales
  - Implementado `white-space: pre-wrap` para renderizado correcto
  - Mejorado el manejo de saltos de línea múltiples excesivos (máximo 2 seguidos)
  - Corregido el renderizado de espacios en blanco en descripciones con formato complejo
- Corregida la repetición de nombres de grupo en descripciones de Meetup
- Corregido el espaciado/indentación erróneo en el renderizado de descripciones web (white-space issue)

## [1.1.0] - 2025-12-29

### Added
- Agregador de feeds ICS públicos
- Normalización de eventos (título, fecha, ubicación, etc.)
- Deduplicación inteligente de eventos similares
- Tags automáticos por keywords (Python, AI, Cloud, DevOps, etc.)
- Generación de calendario ICS unificado
- Generación opcional de JSON con eventos
- CLI con múltiples opciones de configuración
- GitHub Actions workflow para actualización automática
- Manejo robusto de timezones
- Tolerancia a feeds caídos sin romper el proceso
- **Publicación directa en Google Calendar** (nuevo)
  - Soporte para autenticación OAuth2
  - Publicación automática de eventos
  - Modo dry-run para pruebas
  - Soporte para calendarios personalizados
- **Publicación automática en GitHub Pages** (nuevo)
  - Los archivos ICS y JSON se publican automáticamente
  - Página web con interfaz para descargar/suscribir
  - Soporte para suscripción WebCal
  - Actualización automática cada 6 horas

### Removed
- **Código y archivos obsoletos**
  - Eliminado soporte para Google Calendar (`src/cronquiles/google_calendar.py`) para simplificar el proyecto.
  - Eliminado directorio `examples/` ya que no se usaba.
  - Limpieza de scripts de debug temporales (`tools/`).
  - Modularización: `EventNormalized` movido a `src/cronquiles/models.py`.

## [1.0.0] - 2025-12-29

### Added
- Versión inicial del proyecto
- Soporte para múltiples feeds ICS (Meetup, Luma)
- Sistema de deduplicación basado en título normalizado + fecha
- Detección automática de tags
- Documentación completa en README.md
- Ejemplos de configuración

[Unreleased]: https://github.com/shellaquiles/cron-quiles/compare/v1.8.0...HEAD
[1.8.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/shellaquiles/cron-quiles/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/shellaquiles/cron-quiles/releases/tag/v1.0.0
