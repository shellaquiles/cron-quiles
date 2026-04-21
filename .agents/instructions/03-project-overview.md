# Resumen del Proyecto y Operación Core

**Cron-Quiles** es una herramienta en Python que actúa como un agregador de eventos tecnológicos. Consume diferentes fuentes de calendarios (Meetup, Luma, Eventbrite, ICS nativo), los estandariza, los deduplica, y finalmente emite calendarios unificados enfocados en México.

## Automatización y CI/CD (GitHub Actions)
El motor no opera como un demonio en vivo, sino como un trabajo programado y disparado por CI/CD.
- **Frecuencia Cron**: Ejecución agendada cada 6 horas (`schedule` en Github Actions).
- **Triggers adiciones**: También corre tras un `push` a la rama `main` o `master`.
- El flujo de CI se encarga de publicar el resultado compilado estáticamente en la rama `gh-pages`.

## Archivos Clave del Repositorio (Key Files)
Cualquier Agente que opere en este código debe respetar el propósito único de estos archivos:
- `config/feeds.yaml`: El inventario central de todas las comunidades y URLs.
- `config/manual_events.json`: JSON donde se pueden inyectar eventos manuales que no tienen ICS.
- `data/history.json`: Base de datos de persistencia. (NUNCA editar a mano).
- `data/geocoding_cache.json`: Memoria caché para las respuestas de la API de Geocoding.
- `gh-pages/`: Contiene el frontend estático. La data final unificada se deposita en `gh-pages/data/` (Tampoco debe alterarse manualmente).
