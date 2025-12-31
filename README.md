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

- ✅ Consume múltiples feeds ICS públicos
- ✅ Normaliza eventos (título, fecha, hora, ubicación, link, organizador)
- ✅ Deduplicación inteligente de eventos similares
- ✅ Manejo robusto de timezones
- ✅ Tolerancia a feeds caídos (no rompe el proceso)
- ✅ Tags automáticos por keywords (Python, AI, Cloud, DevOps, etc.)
- ✅ Genera ICS unificado y JSON opcional
- ✅ CLI simple y fácil de usar
- ✅ **Soporte multi-ciudad** (nuevo): Genera calendarios separados por ciudad (CDMX, Guadalajara, etc.)
- ✅ **Interfaz web con pestañas de ciudades** (nuevo): Cambia entre ciudades fácilmente
- ✅ **Publicación directa en Google Calendar** (opcional, requiere OAuth2)
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

#### Modo multi-ciudad (recomendado)

El proyecto ahora soporta múltiples ciudades. Para generar calendarios para todas las ciudades:

```bash
python main.py --all-cities --json --output-dir gh-pages/
```

Esto generará archivos separados por ciudad:
- `gh-pages/cronquiles-cdmx.ics` y `cronquiles-cdmx.json`
- `gh-pages/cronquiles-gdl.ics` y `cronquiles-gdl.json`

Para generar el calendario de una ciudad específica:

```bash
python main.py --city cdmx --json --output-dir gh-pages/
```

#### Modo legacy (compatibilidad hacia atrás)

Si tu `feeds.yaml` usa el formato antiguo (sin estructura de ciudades):

```bash
python main.py
```

Esto generará `gh-pages/cronquiles.ics` usando los feeds definidos en `config/feeds.yaml`.

**Nota:** Los archivos se generan en `gh-pages/` para publicación en GitHub Pages.

### Opciones avanzadas

```bash
# Generar calendarios para todas las ciudades
python main.py --all-cities --json --output-dir gh-pages/

# Generar calendario para una ciudad específica
python main.py --city cdmx --json --output-dir gh-pages/

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

# Publicar eventos directamente en Google Calendar
python main.py --google-calendar

# Simular publicación sin publicar realmente (dry run)
python main.py --google-calendar --dry-run
```

### Opciones completas

```
--feeds FEEDS        Archivo de configuración (YAML o TXT). Default: config/feeds.yaml
--city CITY          Generar calendario para una ciudad específica (ej: cdmx, gdl)
--all-cities         Generar calendarios para todas las ciudades definidas
--output OUTPUT      Nombre del archivo ICS de salida. Default: cronquiles.ics
--output-dir DIR     Directorio donde guardar archivos (usa nombres cronquiles-{ciudad}.ics)
--json               Generar también archivo JSON
--json-output FILE   Nombre del archivo JSON. Default: cronquiles.json
--timeout SECONDS    Timeout para requests HTTP. Default: 30
--retries N          Número máximo de reintentos. Default: 2
--verbose            Modo verbose (más logging)
```

## 📁 Estructura del Proyecto

```
cron-quiles/
├── main.py                    # Punto de entrada CLI (raíz)
├── src/
│   └── cronquiles/
│       ├── __init__.py        # Paquete Python
│       ├── main.py            # CLI principal
│       └── ics_aggregator.py  # Lógica de agregación y deduplicación
├── config/
│   ├── feeds.yaml            # Configuración de feeds (YAML)
│   └── list_icals.txt        # Lista alternativa de feeds (texto)
├── docs/
│   ├── AGENTS.md             # Especificaciones del proyecto
│   └── PROJECT_STRUCTURE.md  # Documentación de estructura
├── examples/
│   └── example_event.py       # Ejemplo de formato de eventos
├── gh-pages/                  # Archivos para GitHub Pages
│   ├── index.html            # Página principal con calendario embebido
│   ├── cronquiles.ics        # Calendario ICS (generado)
│   ├── cronquiles.json       # JSON con eventos (generado)
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

## ⚙️ Configuración de Feeds

### Formato YAML Multi-Ciudad (recomendado)

El proyecto ahora soporta múltiples ciudades. Crea un archivo `feeds.yaml` con estructura de ciudades:

```yaml
cities:
  cdmx:
    name: "Ciudad de México"
    slug: "cdmx"
    timezone: "America/Mexico_City"
    feeds:
      - url: https://www.meetup.com/pythonista/events/ical
        name: "Pythonista"
        description: "Comunidad de Python en CDMX"
      - url: https://www.meetup.com/ai-cdmx/events/ical
        name: "AI/IA CDMX"
        description: "Comunidad de IA en CDMX"
  
  guadalajara:
    name: "Guadalajara"
    slug: "gdl"
    timezone: "America/Mexico_City"
    feeds:
      - url: https://www.meetup.com/python-jalisco/events/ical
        name: "Python Jalisco"
        description: "Comunidad de Python en Jalisco"
```

### Formato YAML Legacy (compatibilidad hacia atrás)

También puedes usar el formato antiguo sin estructura de ciudades:

```yaml
feeds:
  - url: https://www.meetup.com/pythonista/events/ical
  - url: https://www.meetup.com/ai-cdmx/events/ical
  - url: https://api2.luma.com/ics/get?entity=calendar&id=cal-xxx
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
3. **Selección del mejor evento**: prioriza eventos con:
   - URL válida
   - Descripción más larga

## 📝 Formato de Títulos

Los eventos se formatean automáticamente según su tipo:

- **Eventos online**: `Grupo|Nombre evento|Online`
- **Eventos presenciales**: `Grupo|Nombre evento|País|Estado`

El sistema detecta automáticamente si un evento es online o presencial basándose en:
- Palabras clave en la ubicación y descripción (online: "zoom", "virtual", "streaming", etc.)
- Presencia de direcciones físicas o indicadores de eventos presenciales
- Extracción inteligente de país y estado para eventos presenciales (especialmente México)

El nombre del grupo se extrae de:
- El organizador del evento
- La descripción del evento (patrones como "Nombre (Descripción)")
- La URL del evento (ej: meetup.com/kong-mexico-city)

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

- **`src/cronquiles/ics_aggregator.py`**: Contiene las clases principales:
  - `EventNormalized`: Representa un evento normalizado
  - `ICSAggregator`: Clase principal para agregar feeds

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

**URL de acceso:**
- Página principal: `https://shellaquiles.github.io/cron-quiles/`
- Archivos ICS por ciudad:
  - CDMX: `https://shellaquiles.github.io/cron-quiles/cronquiles-cdmx.ics`
  - Guadalajara: `https://shellaquiles.github.io/cron-quiles/cronquiles-gdl.ics`
- Archivos JSON por ciudad:
  - CDMX: `https://shellaquiles.github.io/cron-quiles/cronquiles-cdmx.json`
  - Guadalajara: `https://shellaquiles.github.io/cron-quiles/cronquiles-gdl.json`
- WebCal (suscripción):
  - CDMX: `webcal://shellaquiles.github.io/cron-quiles/cronquiles-cdmx.ics`
  - Guadalajara: `webcal://shellaquiles.github.io/cron-quiles/cronquiles-gdl.ics`

**Características de la interfaz web:**
- Diseño terminal con colores verde/negro/blanco
- **Pestañas de ciudades** (nuevo): Cambia fácilmente entre CDMX y Guadalajara
- Calendario mensual interactivo con eventos marcados
- Lista automática de todos los eventos del mes actual
- Navegación entre meses con botones anterior/siguiente
- Diseño responsive optimizado para móvil y escritorio
- Información completa de cada evento (fecha, hora, ubicación, tags, enlaces)
- **Visualización mejorada de títulos**: Separación visual del grupo, nombre del evento y ubicación con diferentes estilos
- **Descripciones expandibles**: Descripciones largas se muestran colapsadas con opción de expandir
- **Espaciado optimizado**: Diseño compacto con espacios reducidos entre elementos
- **Renderizado correcto de saltos de línea**: Las descripciones preservan el formato original
- **Persistencia de ciudad seleccionada**: La ciudad se guarda en localStorage

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

## 📧 Contacto

Para la comunidad **Shellaquiles** 🐢

---

**Nota**: Esta herramienta solo consume feeds ICS públicos. No requiere APIs privadas ni planes de pago.
