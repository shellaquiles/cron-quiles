---
name: "Gestión de Agregadores"
description: "Metodología y checklist para incorporar o modificar un Agregador en cronquiles"
---

# Gestión de Agregadores

Cuando necesites añadir soporte para un formato o proveedor nuevo (ej: Luma, Eventbrite, Calendar nativo):

## 1. Mapeo Inicial
Los eventos de este repositorio viven bajo una fuente de la verdad: la clase `EventNormalized`. Todo agregador debe traducir su API raw o ICS raw hacia este modelo de Pydantic.

## 2. Dónde implementar
Los agregadores pertenecen a `src/cronquiles/aggregators/`.
- Deben heredar o implementar la firma esperada del agregador base.
- Si es una conexión REST / JSON-LD, incluir soporte opcional de cache o manejar los delays para evitar ban de IP.

## 3. Registro y Ruteo
Recuerda actualizar `.agents/rules/01-architecture-routing.md` de tu conocimiento interno Y la lógica principal en `src/cronquiles/ics_aggregator.py`:
Asegúrate de agregar la instrucción `elif "URL_NUEVA" in url:` en `aggregate_feeds()`.

## 4. Requerimientos de Salida
Tu agregador siempre debe devolver eventos generados con `EventNormalized`. Asegura que:
- `online` bool esté implementado correctamente evaluando descripciones o localizaciones.
- El ID del evento o la URL canoníca sea persistente a futuro para que la lógica de deduplicación pueda engancharla en las ejecuciones incrementales subsiguientes.
