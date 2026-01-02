# Soporte para Eventos Manuales (JSON)

Este documento explica cómo agregar eventos al sistema de forma manual, sin necesidad de un feed iCal (ICS) público. Esto es útil para conferencias aisladas o comunidades que no cuentan con automatización.

## Ubicación del archivo
Los eventos manuales se definen en: `config/manual_events.json`

## Estructura del JSON
El archivo debe contener un arreglo de objetos con el siguiente formato:

```json
[
    {
        "title": "KCD Guadalajara 2026",
        "description": "Kubernetes Community Days Guadalajara, un evento para profesionales de la nube y Kubernetes.",
        "url": "https://community.cncf.io/kcd-guadalajara/",
        "location": "Holiday Inn Guadalajara Expo, an IHG Hotel 2500 Avenida Adolfo López Mateos Sur, Zapopan, 45050",
        "country": "México",
        "country_code": "MX",
        "city": "Guadalajara",
        "city_code": "gdl",
        "state": "Jalisco",
        "state_code": "MX-JAL",
        "organizer": "KCD Guadalajara",
        "dtstart": "2026-02-28T08:00:00-06:00",
        "dtend": "2026-02-28T19:00:00-06:00",
        "tags": [
            "cloud",
            "devops",
            "kubernetes",
            "conferencia"
        ],
        "source": "Manual"
    }
]
```

### Campos Obligatorios
- `title`: Nombre del evento.
- `url`: Enlace principal (sitio web, registro, etc).
- `organizer`: Nombre de la comunidad u organizador.
- `dtstart`: Fecha y hora de inicio en formato ISO 8601 con zona horaria (UTC-6 para CDMX).

### Campos de Ubicación (Recomendados)
Para que el evento aparezca correctamente en las pestañas del frontend, se recomienda usar los siguientes formatos:

- `country_code`: "MX" (ISO 3166-1 alpha-2).
- `state_code`: Código ISO 3166-2 prefixado con "MX-". Ejemplos:
  - `MX-CMX`: Ciudad de México
  - `MX-YUC`: Yucatán
  - `MX-JAL`: Jalisco
  - `MX-NLE`: Nuevo León
  - `ONLINE`: Para eventos virtuales.
- `city_code`: Slug en minúsculas. Ejemplos: `cdmx`, `merida`, `guadalajara`, `monterrey`.

## Proceso de Agregación
1. El script `main.py` lee este archivo JSON al inicio.
2. Los eventos se normalizan y se mezclan con los eventos provenientes de los feeds ICS.
3. El organizador se añade automáticamente a la lista de comunidades en la barra lateral del frontend.
4. Si el evento ya existe (mismo título y hora), el sistema lo tratará como un duplicado y seleccionará la mejor versión.

## Validación
Al ejecutar `python3 main.py`, el sistema validará que las fechas tengan el formato correcto. Si faltan códigos de ubicación, intentará inferirlos (geocodificación), pero es más fiable proporcionarlos manualmente.
