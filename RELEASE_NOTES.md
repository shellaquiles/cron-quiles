Fix: Deduplicate history events and enforce sorting

### Fixed
- **Deduplicación de Historial**: Se identificaron y fusionaron 382 eventos duplicados en `data/history.json` causados por discrepancias en la normalización de títulos (Title Case vs slug).
- **Scraper de Meetup**: Corrección en `tools/scrape_meetup_history.py` para utilizar `HistoryManager` al guardar eventos, asegurando consistencia en la generación de llaves y evitando futuros duplicados.
- **Carga de Configuración**: El scraper ahora soporta carga automática de variables de entorno desde `.env` (específicamente `MEETUP_COOKIE`).
- **Ordenamiento de Historial**: Validación estricta para asegurar que `history.json` siempre se guarde ordenado por fecha descendiente (más recientes primero).
- **Cache de Metadatos**: Se implementó "cache busting" en la carga de `states_metadata.json` para asegurar que los usuarios siempre vean la lista de ciudades actualizada.

### Added
- **Herramientas de Mantenimiento**:
  - `tools/deduplicate_events.py`: Script para limpiar duplicados en el historial basado en lógica de normalización `EventNormalized`.
  - `tools/sort_history.py`: Script para reordenar el historial usando la lógica canónica de `HistoryManager`.
