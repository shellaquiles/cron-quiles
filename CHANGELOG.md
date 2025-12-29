# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Fixed
- Corregido problema de codificación de caracteres (acentos) en eventos ICS
  - Los caracteres con acentos ahora se muestran correctamente (ej: "Cariño" en lugar de "CariÃ±o")
  - Implementada función `fix_encoding()` para corregir problemas de mojibake automáticamente

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
