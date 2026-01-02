# 🐢 Cron-Quiles - Agregador de Calendarios Tech

Agregador de calendarios tech (Meetup, Luma, ICS) que se actualiza solo, como buen cron.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Herramienta **open source** para centralizar múltiples feeds ICS públicos de eventos tech en México en un solo calendario unificado.

## 🎯 Objetivo

Consumir múltiples feeds ICS (Meetup, Luma, etc.), normalizar eventos, deduplicarlos y generar un calendario unificado para la comunidad tech mexicana.

Puedes ver la lista completa de comunidades integradas en [Comunidades Tech en México](docs/COMMUNITIES.md).

## ✨ Características

- ✅ Consume múltiples feeds ICS públicos (Meetup, Luma, Google Calendar)
- ✅ **Soporte avanzado para Luma**: Soporte de `lu.ma`, enriquecimiento de ubicaciones URL-only y limpieza de coordenadas.
- ✅ Normaliza eventos (título, fecha, hora, ubicación, link, organizador)
- ✅ **Deduplicación inteligente**:
  - Merge de links: Agrupa URLs alternativas en la descripción del evento principal
  - Tolerancia de tiempo y normalización de timezones UTC
- ✅ **Nombres de grupo inteligentes**: Config manual > X-WR-CALNAME > Organizador
- ✅ Manejo robusto de timezones
- ✅ Tolerancia a feeds caídos (no rompe el proceso)
- ✅ Tags automáticos por keywords (Python, AI, Cloud, DevOps, etc.)
- ✅ Genera ICS unificado y JSON opcional
- ✅ CLI simple y fácil de usar
- ✅ **Generación dinámica de estados** (nuevo): Clasifica eventos automáticamente por su `state_code` (MX-CMX, MX-JAL, etc.)
- ✅ **Mapeo robusto de comunidades** (nuevo): Asocia metadatos de comunidades a cada ciudad usando normalización de URLs.
- ✅ **Interfaz web inteligente** (nuevo): Renderiza pestañas de estados dinámicamente basándose en los datos disponibles
- ✅ **Interfaz web moderna** con diseño terminal y calendario embebido
- ✅ **Enriquecimiento de ubicación** automático para eventos de Meetup
- ✅ **Optimización visual**: Limpieza de espacios y descripciones redundantes

## 📋 Requisitos

- Python 3.10 o superior
- Dependencias listadas en `requirements.txt`

## 🚀 Instalación

1. Clona o descarga este repositorio:
```bash
git clone https://github.com/shellaquiles/cron-quiles.git
cd cron-quiles
```

2. Crea un entorno virtual (recomendado):
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

### Instalación como paquete (opcional)

```bash
pip install -e .
```

Esto instalará el paquete en modo desarrollo y podrás usar `cron-quiles` desde cualquier lugar.

## 📖 Uso

### Uso básico

### Uso recomendado

El script ahora procesa todos los feeds y los agrupa automáticamente por estado basándose en la ubicación de los eventos:

```bash
python main.py --json --output-dir gh-pages/data/
```

Esto generará:
- `gh-pages/data/states_metadata.json`: Manifiesto para el frontend.
- `gh-pages/data/cronquiles-mexico.ics/json`: Calendario unificado de todo el país.
- `gh-pages/data/cronquiles-mx-cmx.ics/json`: Calendario específico (ej: CDMX).
- `gh-pages/data/cronquiles-online.ics/json`: Eventos sin ubicación física.

#### Modo legacy (compatibilidad hacia atrás)

Si tu `feeds.yaml` usa el formato antiguo (sin estructura de ciudades):

```bash
python main.py
```

Esto generará `gh-pages/cronquiles.ics` usando los feeds definidos en `config/feeds.yaml`.

**Nota:** Los archivos se generan en `gh-pages/data/` para publicación en GitHub Pages (según la convención del proyecto).

### Opciones avanzadas

```bash
# Generar calendarios para todas las ciudades
python main.py --all-cities --json --output-dir gh-pages/data/

# Generar calendario para una ciudad específica
python main.py --city cdmx --json --output-dir gh-pages/data/

# Especificar archivo de feeds personalizado
python main.py --feeds config/mi_configuracion.yaml

# Generar también archivo JSON
python main.py --json

# Personalizar nombres de archivos de salida (generados en gh-pages/)
python main.py --output gh-pages/eventos.ics --json-output gh-pages/eventos.json

# Usar archivo de texto plano (una URL por línea) - solo modo legacy
python main.py --feeds config/list_icals.txt

# Modo verbose para debugging
python main.py --verbose

# Ajustar timeout y reintentos
python main.py --timeout 60 --retries 3
```

### Opciones completas

```
```
--feeds FEEDS        Archivo de configuración (YAML o TXT). Default: config/feeds.yaml
--output-dir DIR     Directorio de salida (usa nombres cronquiles-{slug}.ics). Default: gh-pages/data
--json               Generar también archivo JSON (Default: True)
--all-cities         Procesar todos los feeds y generar por estado (Default: True)
--verbose            Modo verbose (más logging)
```
```

## 📁 Estructura del Proyecto

```
cron-quiles/
├── main.py                    # Punto de entrada CLI (raíz)
├── src/
│   └── cronquiles/
│       ├── __init__.py        # Paquete Python
│       ├── main.py            # CLI principal
│       ├── ics_aggregator.py  # Lógica de agregación y deduplicación
│       ├── history_manager.py # Gestor de persistencia
│       └── models.py          # Modelos de datos
├── config/
│   ├── feeds.yaml            # Configuración de feeds (YAML)
│   └── list_icals.txt        # Lista alternativa de feeds (texto)
├── docs/
│   ├── AGENTS.md             # Especificaciones del proyecto
│   └── PROJECT_STRUCTURE.md  # Documentación de estructura
├── gh-pages/                  # Archivos para GitHub Pages
│   ├── css/                  # Estilos CSS
│   ├── js/                   # Scripts JavaScript
│   ├── data/                 # Datos generados (ICS/JSON)
│   ├── index.html            # Página principal con calendario embebido
│   ├── serve.py              # Servidor HTTP para desarrollo local
│   ├── serve.sh              # Script para iniciar servidor
│   └── README-LOCAL.md       # Guía para desarrollo local
├── .github/
│   └── workflows/             # GitHub Actions
├── requirements.txt          # Dependencias Python
├── pyproject.toml            # Configuración del proyecto
├── README.md                 # Esta documentación
├── CONTRIBUTING.md           # Guía para contribuidores
├── CHANGELOG.md              # Historial de cambios
└── LICENSE                   # Licencia MIT
```

## 🏛️ Gestión de Datos Históricos (Nuevo)

El proyecto ahora incluye un sistema de persistencia para asegurar que no se pierdan eventos pasados.

1.  **Scraping de Historial**: Se incluye un script `tools/scrape_meetup_history.py` que permite extraer todos los eventos pasados de un grupo de Meetup.
    ```bash
    export MEETUP_COOKIE="tu_cookie_aquí"
    python tools/scrape_meetup_history.py
    ```

2.  **Persistencia Automática**:
    - Cada vez que se corre el agregador, los nuevos eventos se fusionan con `data/history.json`.
    - Los eventos históricos se preservan incluso si desaparecen de los feeds originales (RSS/ICS).
    - Se prioriza la información más completa (ej. ubicaciones scrapeadas de Meetup sobre datos genéricos de ICS).

### Limpieza y Mantenimiento

El proyecto incluye herramientas para mantener la calidad de los datos:
- Normalización automática de títulos y descripciones.
- Deduplicación inteligente basada en título y fecha (tolerancia de 2 horas).
- **Población automática del cache geográfico**: Los scripts `populate_cache_from_history.py` y `scan_feeds_and_cache.py` aseguran que las ubicaciones se resuelvan correctamente usando la API de Google Maps y se guarden para futuras ejecuciones.

## 🏛️ Gestión de Datos Históricos (Nuevo)

El proyecto ahora incluye un sistema de persistencia para mantener un historial de eventos y mejorar la calidad de los datos (especialmente direcciones físicas).

### Scraping de Historial

Para importar eventos pasados de Meetup y obtener direcciones detalladas (que no vienen en el ICS público):

1. Obtén tu cookie de sesión de Meetup (`MEETUP_MEMBER` o similar) desde tu navegador.
2. Ejecuta el scraper:

```bash
export MEETUP_COOKIE="tu_cookie_aqui"
python3 tools/scrape_meetup_history.py
```

Esto creará/actualizará `data/history.json`.

### Ventajas
- **Direcciones exactas**: El scraper obtiene calle y número, mientras que el ICS a veces solo da la ciudad.
- **Persistencia**: Si un evento desaparece del feed RSS/ICS, se mantiene en tu historial local.
- **Deduplicación inteligente**: El sistema fusiona automáticamente la información del feed vivo con la del historial, preservando siempre los mejores datos.

## ⚙️ Configuración de Feeds

### Formato YAML (Plano)

Ahora los feeds se listan de forma plana. El sistema se encarga de clasificar cada evento en su estado correspondiente leyendo su ubicación:

```yaml
feeds:
  - url: https://www.meetup.com/pythonista/events/ical
    name: "Pythonista"
    description: "Comunidad de Python en CDMX"
  - url: https://www.meetup.com/python-jalisco/events/ical
    name: "Python Jalisco"
  - url: https://api2.luma.com/ics/get?entity=calendar&id=cal-xxx
```

### Formato YAML Legacy (compatibilidad hacia atrás)

También puedes usar el formato antiguo sin estructura de ciudades:

```yaml
feeds:
  - url: https://www.meetup.com/pythonista/events/ical
  - url: https://www.meetup.com/ai-cdmx/events/ical
  - url: https://api2.luma.com/ics/get?entity=calendar&id=cal-xxx
    name: "Nombre Opcional del Grupo" # Si se omite, se usa X-WR-CALNAME o Organizador
```

O formato simple:

```yaml
feeds:
  - https://www.meetup.com/pythonista/events/ical
  - https://www.meetup.com/ai-cdmx/events/ical
```

### Formato Texto Plano

Crea un archivo de texto (ej: `list_icals.txt`) con una URL por línea:

```
https://www.meetup.com/pythonista/events/ical
https://www.meetup.com/ai-cdmx/events/ical
https://api2.luma.com/ics/get?entity=calendar&id=cal-xxx
```

## 🔍 Deduplicación

El sistema deduplica eventos similares usando la siguiente estrategia:

1. **Normalización de título**: lowercase, sin emojis, sin puntuación extra
2. **Comparación de fecha/hora**: tolerancia de ±2 horas
3. **Selección del mejor evento**: prioriza eventos con URL válida y descripción más larga
4. **Merge de Links**: Si se detectan duplicados con diferentes URLs (ej: Luma vs Meetup), se agregan todas las URLs alternativas a la descripción del evento principal.

## 📝 Formato de Títulos y Metadatos

Los eventos se formatean automáticamente según su tipo:

- **Eventos online**: `Grupo|Nombre evento|Online`
- **Eventos presenciales**: `Grupo|Nombre evento|País|Estado`

**Extracción del nombre del grupo (Prioridad):**
1. Nombre configurado en `feeds.yaml` (`name: "..."`)
2. Metadato `X-WR-CALNAME` del calendario ICS
3. Organizador del evento
4. Inferencia desde la URL o descripción

## 🏷️ Tags Automáticos

El sistema detecta automáticamente tags basados en keywords en el título y descripción:

- **python**: Python, Py, Django, Flask, FastAPI
- **ai**: AI, Machine Learning, Deep Learning, Neural
- **cloud**: AWS, Azure, GCP, Cloud, Serverless
- **devops**: DevOps, Docker, Kubernetes, CI/CD, Terraform
- **data**: Data, Big Data, Spark, Hadoop, Analytics
- **security**: Security, Cybersecurity, Pentest
- **mobile**: Mobile, Android, iOS, Flutter
- **web**: Web, HTML, JavaScript, React, Vue
- **backend**: Backend, API, REST, GraphQL
- **frontend**: Frontend, UI, UX, Design

Los tags se agregan como categorías en el ICS y están disponibles en el JSON.

## 📤 Output

### Archivo ICS

El archivo `cronquiles.ics` generado por Cron-Quiles es un calendario estándar ICS que puedes importar en:
- Google Calendar
- Apple Calendar
- Outlook
- Cualquier cliente de calendario compatible

### Archivo JSON (opcional)

Si usas `--json`, se genera un archivo JSON con la estructura:

```json
{
  "generated_at": "2024-01-15T10:30:00+00:00",
  "total_events": 150,
  "events": [
    {
      "title": "Python CDMX|Meetup Mensual|México|CDMX",
      "description": "...",
      "url": "https://...",
      "location": "Ciudad de México",
      "organizer": "Pythonista",
      "dtstart": "2024-02-01T18:00:00-06:00",
      "dtend": "2024-02-01T20:00:00-06:00",
      "tags": ["python", "backend"],
      "source": "https://www.meetup.com/pythonista/events/ical"
    }
  ]
}
```

**Nota**: El campo `title` sigue el formato `Grupo|Nombre evento|Online` o `Grupo|Nombre evento|País|Estado`.

## 🛠️ Desarrollo

### Ejecutar Tests

```bash
# Instalar pytest si no está instalado
pip install pytest

# Ejecutar tests
python -m pytest tests/ -v
```

### Estructura del Código

- **`src/cronquiles/ics_aggregator.py`**: Contiene la clase `ICSAggregator` para agregar feeds.
- **`src/cronquiles/models.py`**: Contiene `EventNormalized`, que representa un evento unificado.

- **`src/cronquiles/main.py`**: CLI que orquesta el proceso

### Extender el Sistema

Para agregar nuevos tags automáticos, edita el diccionario `TAG_KEYWORDS` en `src/cronquiles/ics_aggregator.py`:

```python
TAG_KEYWORDS = {
    'nuevo_tag': ['keyword1', 'keyword2', 'keyword3'],
    # ...
}
```

## 🤖 Automatización con GitHub Actions

El proyecto incluye un workflow de GitHub Actions que actualiza automáticamente el calendario.

### Configuración

El workflow está configurado en `.github/workflows/update-events.yml` y:

- ✅ Se ejecuta automáticamente cada 6 horas
- ✅ Se puede ejecutar manualmente desde la pestaña "Actions" en GitHub
- ✅ Se ejecuta cuando cambias `feeds.yaml` o el código
- ✅ Hace commit y push automático de los archivos actualizados

### 🔐 Configuración de Secretos

Para que la geocodificación funcione correctamente en la nube, es necesario configurar un secreto en el repositorio:

1. Ve a **Settings** -> **Secrets and variables** -> **Actions**.
2. Agrega `GOOGLE_MAPS_API_KEY` con tu llave de Google Maps Platform.

Ver la guía completa en [Configuración de GitHub Pages](docs/GITHUB_PAGES_SETUP.md).

### Activar el workflow

1. Haz push del workflow al repositorio:
```bash
git add .github/workflows/update-events.yml
git commit -m "Add GitHub Actions workflow"
git push
```

2. Ve a la pestaña **Actions** en GitHub para ver el workflow en acción

3. Para ejecutar manualmente: **Actions** → **Update Events Calendar** → **Run workflow**

### Verificar que funciona

Después del primer run, deberías ver:
- Un commit automático con los archivos `*.ics` y `*.json` generados
- El workflow ejecutándose cada 6 horas automáticamente
- Los archivos publicados en GitHub Pages (si está habilitado)

### Publicación en GitHub Pages

El workflow también publica automáticamente los archivos en GitHub Pages, permitiendo:
- ✅ Acceso directo a los archivos ICS y JSON desde la web
- ✅ Suscripción WebCal para actualizaciones automáticas
- ✅ **Interfaz web moderna con diseño terminal** estilo shellaquiles-org
- ✅ **Calendario mensual visual embebido** con todos los eventos del mes
- ✅ Navegación entre meses y visualización automática de eventos

**Para habilitar GitHub Pages:**
1. Ve a **Settings** → **Pages** en tu repositorio
2. En "Source", selecciona **GitHub Actions**
3. Los archivos se publicarán automáticamente en cada actualización

- **URL principal**: `https://shellaquiles.github.io/cron-quiles/`
- **Archivos por estado (slugs ISO)**:
  - México (Todo): `.../data/cronquiles-mexico.ics`
  - CDMX: `.../data/cronquiles-mx-cmx.ics`
  - Jalisco: `.../data/cronquiles-mx-jal.ics`
  - Online: `.../data/cronquiles-online.ics`

**Características de la interfaz web:**
- Diseño terminal con colores verde/negro/blanco
- **Pestañas dinámicas**: Las pestañas de los estados se generan automáticamente según los eventos detectados.
- Calendario mensual interactivo con eventos marcados
- Lista automática de todos los eventos del mes actual
- Navegación entre meses con botones anterior/siguiente
- Diseño responsive optimizado para móvil y escritorio
- **Persistencia de selección**: La ciudad/estado se guarda en localStorage

### Personalizar la frecuencia

Edita `.github/workflows/update-events.yml` y cambia el cron:

```yaml
schedule:
  # Cada 6 horas (actual)
  - cron: '0 */6 * * *'

  # Cada 12 horas
  - cron: '0 */12 * * *'

  # Diario a las 3 AM UTC
  - cron: '0 3 * * *'
```

## 🐛 Troubleshooting

### Un feed no se está descargando

- Verifica que la URL sea accesible públicamente
- Usa `--verbose` para ver logs detallados
- Aumenta `--timeout` si el feed es lento
- El proceso continúa aunque algunos feeds fallen

### Eventos duplicados aparecen

- Ajusta la tolerancia de tiempo en `deduplicate_events()` si es necesario
- Revisa los logs con `--verbose` para ver qué eventos se están deduplicando

### Problemas con timezones

- El sistema maneja automáticamente timezones
- Si un evento no tiene timezone, se asume UTC
- El calendario final usa `America/Mexico_City` como timezone por defecto

## 📝 Licencia

Este proyecto está licenciado bajo la [MIT License](LICENSE) - ver el archivo LICENSE para más detalles.

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor lee [CONTRIBUTING.md](CONTRIBUTING.md) para detalles sobre nuestro código de conducta y el proceso para enviar pull requests.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Algunas ideas:

- Agregar más fuentes de feeds
- Mejorar la estrategia de deduplicación
- Agregar más tags automáticos
- Mejorar el manejo de eventos recurrentes
- Agregar filtros por tags o fechas

## 👥 Contribuidores

¡Gracias a las personas que hacen posible este proyecto!

- **Ricardo Lira** ([@richlira](https://github.com/richlira)) - I18n, Gestión de Comunidades.
- **Ivan Galaviz** ([@ivanovishado](https://github.com/ivanovishado)) - Soporte para Guadalajara.
- **AdanGQ** ([@pixelead0](https://github.com/pixelead0)) - Core, Infraestructura CI, UI Estilo Terminal.

> [!TIP]
> Si quieres aparecer aquí, ¡envía tu Pull Request con nuevas comunidades o mejoras!

## 📧 Contacto

Para la comunidad **Shellaquiles** 🐢

---

**Nota**: Esta herramienta solo consume feeds ICS públicos. No requiere APIs privadas ni planes de pago.
