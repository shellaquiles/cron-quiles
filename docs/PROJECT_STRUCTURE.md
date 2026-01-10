# Estructura del Proyecto

```
cron-quiles/
├── .github/
│   ├── workflows/
│   │   ├── update-events.yml      # GitHub Actions workflow
│   │   └── README.md               # Documentación del workflow
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md           # Template para reportar bugs
│   │   └── feature_request.md      # Template para solicitar features
│   ├── PULL_REQUEST_TEMPLATE.md    # Template para PRs
│   └── dependabot.yml              # Configuración de Dependabot
│
├── .gitignore                       # Archivos a ignorar en Git
│
├── LICENSE                          # Licencia MIT
├── README.md                        # Documentación principal
├── CONTRIBUTING.md                  # Guía para contribuidores
├── CHANGELOG.md                     # Historial de cambios
│
├── data/                            # Datos persistentes
│   └── history.json                # Historial de eventos (base de datos)
│
├── src/
│   └── cronquiles/                  # Paquete Python principal
│       ├── __init__.py             # Inicialización del paquete
│       ├── main.py                 # CLI principal
│       ├── main.py                 # CLI principal
│       ├── ics_aggregator.py       # Orchestrador del pipeline
│       ├── aggregators/            # Paquete de lógica de agregación
│       │   ├── base.py
│       │   ├── ics.py
│       │   ├── eventbrite.py
│       │   ├── luma.py
│       │   ├── meetup.py
│       │   ├── manual.py
│       │   └── hievents.py
│       ├── history_manager.py      # Gestor de persistencia y merge
│       └── models.py               # Modelos de datos (EventNormalized)
│
├── config/                          # Archivos de configuración
│   ├── feeds.yaml                  # Configuración de feeds (YAML)
│   └── list_icals.txt              # Lista alternativa de feeds (texto)
│
├── tools/                           # Scripts de mantenimiento y utilidades
│   ├── fix_cache_encoding.py
│   ├── populate_cache_from_history.py
│   ├── scan_feeds_and_cache.py
│   └── scrape_meetup_history.py
│
├── docs/                            # Documentación adicional
│   ├── AGENTS.md                   # Especificaciones del proyecto
│   └── PROJECT_STRUCTURE.md        # Este archivo
│
├── main.py                          # Punto de entrada CLI (raíz)
├── requirements.txt                # Dependencias Python
├── pyproject.toml                   # Configuración del proyecto (PEP 518)
│
├── gh-pages/                        # Archivos para GitHub Pages
│   ├── css/                        # Estilos CSS
│   ├── js/                         # Scripts JavaScript
│   ├── data/                       # Datos generados (JSON/ICS)
│   │   ├── states_metadata.json     # Manifiesto dinámico para el frontend
│   │   ├── cronquiles-mexico.ics    # Calendario nacional unificado
│   │   └── cronquiles-{slug}.ics    # Calendarios por estado (dinámicos)
│   ├── index.html                  # Página principal con calendario embebido
│   ├── serve.py                    # Servidor HTTP para desarrollo local
│   ├── serve.sh                    # Script para iniciar servidor local
│   └── README-LOCAL.md             # Guía para desarrollo local
│
└── [Archivos generados - obsoletos en raíz]
    # Nota: Los archivos ahora se generan en gh-pages/
```

## Descripción de Directorios

### `src/cronquiles/`
Código fuente principal del proyecto. Contiene:
- **`__init__.py`**: Inicialización del paquete Python
- **`main.py`**: CLI principal con argumentos y lógica de ejecución
- **`ics_aggregator.py`**: Orchestrador (EventPipeline). Coordina la agregación delegando a las clases en `aggregators/`.
- **`aggregators/`**: Paquete modular con la lógica de extracción específica:
  - `GenericICSAggregator` (ICS estándar)
  - `EventbriteAggregator` (Adaptador JSON-LD)
  - `LumaAggregator` & `MeetupAggregator` (Enriquecimiento)
  - `ManualAggregator`
  - `HiEventsAggregator` (Soporte para plataformas como Pythonistas GDL)
- **`history_manager.py`**: Maneja la carga, guardado y fusión (merge) inteligente de eventos históricos desde `data/history.json`.
- **`models.py`**: Contiene la clase `EventNormalized` y lógica de limpieza.
  - `EventNormalized`: Clase que representa un evento unificado. Normaliza eventos, detecta online/presencial, extrae grupo/ubicación, formatea títulos e implementa el **enriquecimiento de ubicación desde Meetup y Luma**.

### `config/`
Archivos de configuración:
- **`feeds.yaml`**: Configuración principal de feeds ICS (formato YAML)
- **`list_icals.txt`**: Lista alternativa de feeds (formato texto plano, una URL por línea)

### `tools/`
Scripts de mantenimiento y utilidad:
- **`populate_cache_from_history.py`**: Extrae ubicaciones verificadas de `history.json` y puebla el cache de geocodificación.
- **`scan_feeds_and_cache.py`**: Escanea todos los feeds configurados, extrae ubicaciones y asegura que estén en el cache (geocodificando si es necesario).
- **`scrape_meetup_history.py`**: Scraper para obtener eventos históricos de grupos de Meetup.
- **`deduplicate_events.py`**: Script para limpiar duplicados en `history.json` re-normalizando eventos.
- **`sort_history.py`**: Script para asegurar el ordenamiento cronológico descendente del historial.

### `docs/`
Documentación adicional del proyecto:
- **`AGENTS.md`**: Especificaciones originales y requisitos del proyecto
- **`PROJECT_STRUCTURE.md`**: Este archivo con la estructura del proyecto

### Raíz del Proyecto
- **`main.py`**: Punto de entrada principal que permite ejecutar desde la raíz
- **`requirements.txt`**: Lista de dependencias Python
- **`pyproject.toml`**: Configuración del proyecto según PEP 518
- **`README.md`**: Documentación principal
- **`LICENSE`**: Licencia MIT
- **`CONTRIBUTING.md`**: Guía para contribuidores
- **`CHANGELOG.md`**: Historial de cambios

### `.github/`
Configuración de GitHub:
- **`workflows/`**: Workflows de GitHub Actions
- **`ISSUE_TEMPLATE/`**: Templates para crear issues
- **`PULL_REQUEST_TEMPLATE.md`**: Template para pull requests
- **`dependabot.yml`**: Configuración de Dependabot

## Archivos Generados

Estos archivos se generan al ejecutar `main.py` y se suben al repo automáticamente por GitHub Actions:
- **`gh-pages/data/states_metadata.json`**: Manifiesto JSON con la lista de estados detectados, sus slugs, conteo de eventos y emojis para el frontend.
- **`gh-pages/data/cronquiles-mexico.ics/json`**: Calendario unificado con todos los eventos.
- **`gh-pages/data/cronquiles-{slug}.ics/json`**: Archivos específicos por estado (ej: `cronquiles-mx-cmx.json`).

**Nota:** Los archivos se generan directamente en `gh-pages/data/` para publicación en GitHub Pages.

## GitHub Pages

La carpeta `gh-pages/` contiene todos los archivos necesarios para GitHub Pages:
- **`index.html`**: Página principal con diseño terminal y calendario embebido
- **`data/`**: Subdirectorio con los archivos de datos
  - **`cronquiles-mexico.ics`**: Calendario ICS nacional para descarga y suscripción WebCal
  - **`cronquiles-mx-cmx.json`**: Ejemplo de datos JSON por estado
- **`serve.py`** / **`serve.sh`**: Scripts para probar el sitio localmente
- **`README-LOCAL.md`**: Instrucciones para desarrollo local

## Uso de la Estructura

### Ejecutar desde la raíz
```bash
python main.py
```

### Ejecutar el módulo directamente
```bash
python -m src.cronquiles.main
```

### Importar como paquete
```python
from src.cronquiles import ICSAggregator
```

**Nota:** El paquete Python se llama `cronquiles` (sin guión) para cumplir con las convenciones de nombres de paquetes Python.

## Ventajas de esta Estructura

1. **Organización clara**: Separación entre código, configuración, documentación y ejemplos
2. **Escalabilidad**: Fácil agregar más módulos o subpaquetes
3. **Estándar Python**: Sigue convenciones comunes de proyectos Python
4. **Mantenibilidad**: Fácil encontrar y modificar archivos
5. **Distribución**: Listo para empaquetar con `setuptools` o `pip`
