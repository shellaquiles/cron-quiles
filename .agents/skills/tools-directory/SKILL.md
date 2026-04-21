---
name: "Mantenimiento con Scripts de Tools"
description: "Directorio de utilidades para depuración y sanitización de datos"
---

# Herramientas del Proyecto (`/tools/`)

El directorio `tools/` contiene scripts de Python de uso manual / ad-hoc para resolver inconsistencias o inicializar estados. El agente puede invocarlos cuando un problema particular lo amerite.

## Directorio de Scripts:

1. **`deduplicate_events.py`**:
   Limpia y purga eventos duplicados que el Agregador no pudo atrapar en la memoria a corto plazo, usualmente invocado vía `make tools-deduplicate` en el workflow de auditoría.

2. **`populate_cache_from_history.py`**:
   Lee los eventos guardados en `data/history.json` y extrae sus ubicaciones ya geolocalizadas para pre-popular `geocoding_cache.json`. Salva las cuotas de API de Google Maps/OpenStreet.

3. **`fix_cache_encoding.py`**:
   Repara errores de codificación UTF-8 que pudieran corromper el caché geográfico.

4. **`scan_feeds_and_cache.py`**:
   Realiza un dry-run extenso por todo `feeds.yaml` validando la sanidad de las URLs y verificando si el caché tiene agujeros que deban llenarse.

5. **`scrape_meetup_history.py`**:
   Recupera eventos pasados específicamente de la plataforma Meetup usando web scraping o su API delegada, para engordar la base de datos histórica.

6. **`sort_history.py`**:
   Aplica un formateo estricto y orden alfabético/cronológico a `history.json` para facilitar la inspección visual en PRs o debugging.

7. **`update_communities_status.py`**:
   Pinguea las comunidades listadas para checar 404s o abandono, útil para purgar grupos inactivos.
