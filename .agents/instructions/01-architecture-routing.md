# Reglas de Arquitectura y Ruteo (cronquiles)

## Core Pipeline (`src/cronquiles/`)
- **`main.py`**: Punto de entrada CLI. Carga `config/feeds.yaml`, orquesta y genera salidas.
- **`ics_aggregator.py`**: El director de orquesta. Despacha URLs a los agregadores específicos, gestiona la deduplicación, geocodificación y cache históricos.
- **`models.py`**: Define `EventNormalized` para homogeneizar múltiples fuentes. Extrae etiquetas, normaliza títulos, corrige zonas horarias y crea las llaves únicas (hashes).
- **`history_manager.py`**: Mantiene en `data/history.json` eventos y mezclas (merges) inter-sesión.

## Routing Logic 
Cuando se solicita recolección en `ICSAggregator.aggregate_feeds()`, este es el ruteo actual a respetar:
- `eventbrite.com` URLs → **`EventbriteAggregator`** (`src/cronquiles/aggregators/eventbrite.py`)
- `lu.ma` / `luma.com` URLs → **`LumaAggregator`** (`src/cronquiles/aggregators/luma.py`)
- `meetup.com` URLs → **`MeetupAggregator`** (`src/cronquiles/aggregators/meetup.py` - Extracción con JSON-LD)
- Eventos de `config/manual_events.json` → **`ManualAggregator`** (`src/cronquiles/aggregators/manual.py`)
- Resto de URIs → **`GenericICSAggregator`** (`src/cronquiles/aggregators/ics.py`)

## Reglas Críticas del Modelo de Dominio
1. **Deduplicación**: Los eventos se agrupan mediante hashes. Los hashes utilizan `título_normalizado` y un `bloque_de_tiempo` con tolerancia de 2 horas en UTC. Al hacer el merge de duplicados, privilegiar URLs existentes y descripciones extensas.
2. **Filtrado Geográfico**: Solo se permiten eventos que físicamente ocurren en `MX` (México) o que sean marcados estrictamente como `<online: true>`. El resto será descartado en el agregador.
3. **Indicador Online**: `models.py` usa `EventNormalized._is_online()` para asegurar que se omita "Ver en mapa" desde el frontend (`gh-pages`).
