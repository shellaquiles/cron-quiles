---
name: "Data Pipeline y Salidas"
description: "Mantenimiento del engine de histórico y salida GH-Pages"
---

# Generación del Pipeline y Data estática

## Entendiendo el Output
Tras una ejecución de agregación, the pipeline no escribe a base de datos externa, sino que genera archivos procesados para el frontend estático ubicado en GitHub Pages:
- `gh-pages/data/cronquiles-mexico.ics` / `.json` (El Master Físico)
- `gh-pages/data/cronquiles-{state-code}.*` (Por Estado)
- `gh-pages/data/cronquiles-online.*` (Filtrado estricto online)
- `gh-pages/data/states_metadata.json` (Indice frontend)

**Nota al Agente**: JAMAS intentes comitear directamente `gh-pages/data/` en un pull request de desarrollo. Se generan en Github Actions de CI/CD.

## Archivos Críticos de Mantenimiento (Data Directory)
La carpeta de configuración interactiva y persistencia (`/data/` global):
- `data/history.json`: Nunca manipular manualmente. El motor depende de esto para resolver colisiones de updates previos.
- `data/geocoding_cache.json`: Almacén valioso. Si la API de geocodificación detona rate-limit, deberás invocar el workflow de purgado o uso parcial de cache para evitar el quiebre de CI.

Si las traducciones de coordenadas fallan en masa, utiliza las herramientas definidas en Makefile (`make tools-populate-cache`) primero antes de auditar logs profundos.
