Feat: Add Hi.Events aggregator and integrate Pythonistas GDL

Este release introduce el soporte para la plataforma **Hi.Events**, permitiendo la integración de comunidades que utilizan este sistema, como **Pythonistas GDL**.

### Added
- **Hi.Events Aggregator**: Nuevo componente modular `HiEventsAggregator` que consume la API pública de Hi.Events para una extracción de datos más robusta.
- **Integración Pythonistas GDL**: Adición oficial de la comunidad de Guadalajara al ecosistema de Cron-Quiles.
- **Detección de Ubicación en GDL**: Los eventos de Hi.Events ahora se geolocalizan automáticamente en Jalisco mediante el enriquecimiento de metadatos de la API.

### Changed
- **Documentación del Proyecto**: Actualización de `README.md`, `AGENTS.md` y `PROJECT_STRUCTURE.md` para reflejar la nueva arquitectura modular.
- **Feeds**: Incorporación de `https://reuniones.pythonistas-gdl.org/` en la configuración global.

### Fixed
- **Normalización de Títulos**: Mejoras en el manejo de pipes y caracteres especiales para evitar conflictos en el formato unificado.
- **Sanitización de Cache**: (Incluido en este ciclo) Corrección de problemas de codificación en el cache geográfico detectados anteriormente.
