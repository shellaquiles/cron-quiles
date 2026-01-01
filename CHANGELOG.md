# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

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

### Added (versiones anteriores)
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

### Changed
- (Ningún cambio aún)

### Fixed
- (Ningún fix aún)

### Removed
- (Nada removido aún)

---

## [1.0.0] - 2024-01-XX

### Added
- Versión inicial del proyecto
- Soporte para múltiples feeds ICS (Meetup, Luma)
- Sistema de deduplicación basado en título normalizado + fecha
- Detección automática de tags
- Documentación completa en README.md
- Ejemplos de configuración

[Unreleased]: https://github.com/shellaquiles/cron-quiles/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/shellaquiles/cron-quiles/releases/tag/v1.0.0
