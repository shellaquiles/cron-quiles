# Especificaciones del Proyecto Cron-Quiles

Actúa como un **Senior Automation Engineer / Python Architect**.
Estás construyendo una herramienta **open source**, sin APIs privadas ni pagos, para la comunidad **Shellaquiles**.

### Contexto

* Tengo múltiples feeds **ICS públicos** de eventos tech en México (Meetup, Luma).
* No tengo acceso a APIs oficiales ni planes de pago.
* Quiero centralizarlos todos en **un solo calendario unificado**.

### Objetivo técnico

1. Consumir múltiples URLs **.ics**
2. Normalizar los eventos (título, fecha, hora, ubicación, link, organizador)
3. Deduplicar eventos similares (mismo título + fecha ± tolerancia)
4. Generar por ciudad:

   * Un **ICS unificado** por ciudad (`cronquiles-{slug}.ics`)
   * Un **JSON** con eventos y comunidades (`cronquiles-{slug}.json`)

### Estado Actual del Proyecto (v1.8.0+)

El proyecto es completamente funcional y opera bajo Github Actions.

**Funcionalidades Implementadas:**
1.  **Soporte Multifuente**: Consume feeds ICS de Meetup, Luma, Google Calendar y Hi.Events.
2.  **Generación Dinámica de Estados**: Detecta el estado de cada evento y genera calendarios separados automáticamente (`mx-cmx`, `mx-jal`, etc.).
    *   **Normalización ISO**: Transforma abreviaturas comunes (ej: MX-NL) a códigos ISO estándar.
    *   **Frontend Inteligente**: Renderiza pestañas de navegación dinámicamente basándose en el manifiesto `states_metadata.json`.
3.  **Arquitectura Modular de Agregadores**:
    *   **Separación de Responsabilidades**: Lógica de extracción desacoplada en `src/cronquiles/aggregators/`.
    *   **Soporte Extensible**: Fácil adición de nuevos adaptadores (ej: Eventbrite, Luma).
4.  **Deduplicación Robusta**:
    *   Identifica eventos duplicados por título y hora (tolerancia ±2 horas).
    *   Normaliza zonas horarias a UTC para evitar falsos positivos.
    *   **NO PIERDE DATOS**: Si hay duplicados con diferentes links, los agrega a la descripción del evento principal ("Otras fuentes: ...").
4.  **Extracción Inteligente de Metadatos**:
    *   Prioriza nombres de grupos configurados manualmente > X-WR-CALNAME (del ICS) > Organizador del evento.
    *   Detecta automáticamente URLs de eventos Luma (`lu.ma`, `luma.com`) dentro de la descripción si no están en el campo URL principal.
5.  **Formato de Títulos Estandarizado**: `Grupo|Nombre|Ubicación` (ej: "Python CDMX|Charla Mensual|Online").
6.  **Detección de Ubicación**: Clasifica automáticamente como "Online", "Ciudad, Estado" o "País".
    *   Enriquecimiento de ubicación desde Meetup (JSON-LD/Next.js).
7.  **Sistema de Configuración**: `feeds.yaml` con lista plana de feeds.
    *   Estructura: `feeds: [ {url, name, description}, ... ]`.
    *   Desacoplado de la lógica de ciudades: el sistema infiere el estado desde cada evento.
8.  **Salida Dual**: Genera tanto `.ics` (para calendarios) como `.json` (para integraciones).
    *   Archivos por ciudad: `cronquiles-{slug}.ics` y `cronquiles-{slug}.json`.
    *   JSON incluye campo `communities` con lista de comunidades integradas y sus enlaces a múltiples plataformas.
    *   JSON incluye campo `sources` en eventos con información de todas las plataformas disponibles.
9.  **Logging Detallado**: Registra el proceso de agregación y estadísticas de eventos procesados.
10. **Tags automáticos**: Detección por keywords en título y descripción (python, ai, cloud, etc).
11. **Interfaz web moderna**: Diseño terminal estilo shellaquiles-org con calendario visual embebido.
    *   Tabs de ciudad generados dinámicamente.
    *   Comunidades dinámicas cargadas desde JSON (mapeo robusto por URL).
12. **Manejo robusto de timezones**: Conversión a UTC para lógica interna, preservando original.
13. **Publicación automática**: GitHub Actions actualiza feeds y Pages cada 6 horas.
14. **Persistencia de Historial**: Sistema de "memoria" (`data/history.json`) para preservar eventos pasados y mejorar datos (direcciones completas) mediante scraping.
15. **Limpieza Avanzada**: Regex robusto para eliminar artefactos `vText` y basura de títulos.
16. **Merge Inteligente**: Fusiona datos históricos con feeds vivos, preservando siempre la mejor versión de la información (ej: ubicación detallada).
17. **Filtrado Global por País**: El sistema solo procesa eventos donde el país detectado es México (`MX`) o el evento es `Online`. Esto mantiene el calendario enfocado y optimiza el rendimiento.
18. **Codificación Robusta**: Sistema automático para detectar y corregir problemas de codificación (mojibake) tanto en feeds externos como en archivos de datos locales (`geocoding_cache.json`, `history.json`). Maneja secuencias complejas como `¬∫` -> `º` y limpieza de caracteres basurairrecuperables.

### Deduplicación

Estrategia implementada:
* Normalizar título (lowercase, sin emojis, sin puntuación)
* Comparar fecha/hora (±2 horas usando bloques de 2 horas en UTC)
* Si coinciden → conservar uno
* Priorizar eventos con:
  1. URL válida
  2. Descripción más larga
* **Merge de fuentes**: Si los duplicados tienen URLs diferentes de diferentes plataformas (Meetup, Luma, Eventbrite), se combinan en el campo `sources` del evento, manteniendo información de plataforma y etiquetas.
* **Campo `sources`**: Array de objetos con `platform`, `url`, y `label` para cada fuente del evento.

### Output

**Archivos generados dinámicamente**:
* `gh-pages/data/states_metadata.json` - Manifiesto para el frontend
* `gh-pages/data/cronquiles-mexico.ics/json` - Calendario nacional
* `gh-pages/data/cronquiles-{slug}.ics/json` - Calendarios por estado (ej: `cronquiles-mx-cmx.ics`)
* `gh-pages/data/cronquiles-online.ics/json` - Eventos sin ubicación física

**Formato JSON**:
* Campo `sources` en eventos: Array de objetos con `platform` (meetup/luma/eventbrite/website), `url`, y `label`
* Campo `links` en comunidades: Array de objetos con información de todas las plataformas disponibles
* Cache persistente: `data/luma_url_cache.json` almacena conversiones de URLs vanity de Luma a URLs de API

**Interfaz web**:
* `gh-pages/index.html` - Página con calendario embebido y tabs por ciudad
* Botones de plataforma estilizados por color (rojo Meetup, morado Luma, naranja Eventbrite)
* Enlaces de comunidades con múltiples plataformas visibles en las tarjetas

### Entregables

* ✅ Código funcional y bien documentado
* ✅ README.md completo y actualizado
* ✅ Ejemplo de `feeds.yaml` y `list_icals.txt`
* ✅ CHANGELOG.md con historial de cambios
* ✅ Documentación de estructura del proyecto
* ✅ Tests básicos
* ✅ GitHub Actions workflow
* ✅ Interfaz web moderna
* ✅ Documentación de setup

### Estructura del proyecto

```
cron-quiles/
├── main.py                    # Punto de entrada CLI (raíz)
├── src/
│   └── cronquiles/
│       ├── __init__.py        # Paquete Python
│       ├── main.py            # CLI principal
│       ├── ics_aggregator.py  # Orchestrador del pipeline
│       ├── aggregators/       # Paquete de agregadores
│       │   ├── base.py        # Interface BaseAggregator
│       │   ├── ics.py         # Parser genérico ICS
│       │   ├── eventbrite.py  # Extractor Eventbrite + Adapter
│       │   ├── luma.py        # Extractor Luma
│       │   ├── meetup.py      # Extractor Meetup
│       │   ├── manual.py      # Agregador de eventos manuales
│       │   └── hievents.py    # Extractor Hi.Events
│       ├── history_manager.py # Gestor de persistencia
│       ├── models.py          # Modelos de datos
│       └── schemas.py         # Esquemas de validación y serialización
├── config/
│   ├── feeds.yaml            # Configuración de feeds (YAML)
│   ├── list_icals.txt        # Lista alternativa de feeds (texto)
│   └── manual_events.json    # Eventos agregados manualmente
├── docs/
│   ├── AGENTS.md             # Este archivo (especificaciones)
│   ├── PROJECT_STRUCTURE.md   # Documentación de estructura
│   ├── COMMUNITIES.md        # Lista de comunidades integradas
│   └── GITHUB_PAGES_SETUP.md # Guía de setup de GitHub Pages
├── gh-pages/                  # Archivos para GitHub Pages
│   ├── css/                  # Estilos CSS
│   ├── js/                   # Scripts JavaScript
│   ├── index.html            # Página principal con calendario embebido y tabs
│   ├── data/                 # Subdirectorio de datos
│   │   ├── cronquiles-mexico.ics # Calendario unificado (Todo México)
│   │   ├── cronquiles-mx-cmx.json # JSON de CDMX (generado)
│   │   ├── cronquiles-mx-jal.json # JSON de Jalisco (generado)
│   │   └── states_metadata.json  # Manifiesto dinámico
│   ├── serve.py             # Servidor HTTP para desarrollo local
│   └── serve.sh             # Script para iniciar servidor
├── tests/
│   └── test_ics_aggregator.py # Tests básicos
├── requirements.txt          # Dependencias Python
├── pyproject.toml            # Configuración del proyecto
├── README.md                 # Documentación principal
├── CHANGELOG.md              # Historial de cambios
└── CONTRIBUTING.md           # Guía para contribuidores
```

### Herramientas de Mantenimiento

* **Scraper de Historial** (`tools/scrape_meetup_history.py`):
  * Extrae eventos pasados de Meetup (requiere cookie).
  * Obtiene direcciones completas (calle, número) que no vienen en el ICS público.
  * Alimenta `data/history.json`.

* **Limpieza de Historial** (`HistoryManager`):
  * Deduplica inteligentemente usando hashes consistentes.
  * Permite regenerar calendarios sin perder datos antiguos.

* **Deduplicación de Eventos** (`tools/deduplicate_events.py`):
  * Limpia duplicados en `history.json` re-normalizando eventos.

* **Ordenamiento de Historial** (`tools/sort_history.py`):
  * Asegura el ordenamiento cronológico descendente del historial.

* **Población de Cache** (`tools/populate_cache_from_history.py`):
  * Extrae todas las ubicaciones de `history.json` verificado y las inserta en `geocoding_cache.json` para evitar re-consultar la API.

* **Escaneo de Feeds** (`tools/scan_feeds_and_cache.py`):
  * Descarga todos los feeds ICS configurados, extrae las ubicaciones y asegura que estén presentes en el cache.

* **Actualización de Estados** (`tools/update_communities_status.py`):
  * Actualiza automáticamente el estado de las comunidades en `docs/COMMUNITIES.md` basándose en la fecha de su último evento.

### Clasificación de Comunidades
Se define el estatus de una comunidad basado en la fecha de su último evento:
* **Activo**: Eventos en los últimos 12 meses.
* **En Pausa**: Eventos entre 12 y 18 meses.
* **Inactivo**: Más de 18 meses sin eventos.

### Próximas mejoras posibles
* Filtros por tags o fechas en CLI
* Mejora en el manejo de eventos recurrentes complejos
* Soporte para más fuentes de feeds (Eventbrite, etc.)
* API REST para consultar eventos
* Notificaciones de nuevos eventos
* Exportación a otros formatos (CSV, etc.)

### ⚠️ IMPORTANTE: Documentación y Actualización

**En cada cambio o feature nueva, DEBES:**

1. **Actualizar documentación**:
   - ✅ README.md si cambia funcionalidad, uso o estructura
   - ✅ CHANGELOG.md con los cambios realizados
   - ✅ Docstrings en el código (módulos, clases, funciones)
   - ✅ Comentarios inline donde sea necesario

2. **Actualizar archivos relacionados**:
   - ✅ `docs/PROJECT_STRUCTURE.md` si cambia la estructura
   - ✅ `CONTRIBUTING.md` si cambian procesos de desarrollo
   - ✅ Tests si agregas/modificas funcionalidad
   - ✅ `requirements.txt` si agregas dependencias
   - ✅ `docs/COMMUNITIES.md` si agregas un nuevo feed en `config/feeds.yaml`

3. **Mantener consistencia**:
   - ✅ Ejemplos de código en README deben funcionar
   - ✅ Rutas y nombres de archivos actualizados
   - ✅ Badges y metadata correctos
   - ✅ Links internos funcionando

4. **Verificar antes de commit**:
   - ✅ Documentación sincronizada con código
   - ✅ No dejar referencias a archivos/estructuras antiguas
   - ✅ Ejemplos actualizados y funcionales
   - ✅ **NO commitear archivos generados manualmente**: `gh-pages/cronquiles-*.ics` y `gh-pages/cronquiles-*.json`
     - Estos archivos son generados automáticamente por GitHub Actions
     - Si necesitas probar localmente, usa `git update-index --assume-unchanged` para ignorarlos temporalmente
     - Los archivos en `gh-pages/` son publicados automáticamente por el workflow

**Regla de oro**: Si cambias código, cambia documentación. Si cambias estructura, actualiza todos los archivos que la referencien.

### Archivos generados (no commitear manualmente)

Los siguientes archivos son generados automáticamente y **NO deben incluirse en commits manuales**:

* `gh-pages/data/cronquiles-mx-cmx.ics` - Calendario ICS de CDMX
* `gh-pages/data/cronquiles-mx-cmx.json` - JSON de eventos de CDMX
* `gh-pages/data/cronquiles-mx-jal.ics` - Calendario ICS de Jalisco
* `gh-pages/data/cronquiles-mx-jal.json` - JSON de eventos de Jalisco

**Razón**: Estos archivos se generan automáticamente por GitHub Actions cada 6 horas. Si los commiteas manualmente, pueden causar conflictos innecesarios y el workflow los sobrescribirá de todas formas.

**Para desarrollo local**:
```bash
# Ignorar temporalmente estos archivos en git
git update-index --assume-unchanged gh-pages/data/cronquiles-cdmx.ics
git update-index --assume-unchanged gh-pages/data/cronquiles-cdmx.json
git update-index --assume-unchanged gh-pages/data/cronquiles-gdl.ics
git update-index --assume-unchanged gh-pages/data/cronquiles-gdl.json

# Para volver a trackearlos (si es necesario)
git update-index --no-assume-unchanged gh-pages/data/cronquiles-cdmx.ics
git update-index --no-assume-unchanged gh-pages/data/cronquiles-cdmx.json
git update-index --no-assume-unchanged gh-pages/data/cronquiles-gdl.ics
git update-index --no-assume-unchanged gh-pages/data/cronquiles-gdl.json
```

Piensa paso a paso, justifica decisiones técnicas y genera código limpio, comentado y listo para producción ligera. **Nunca dejes documentación desactualizada.**

### ♻️ Reutilización de Código y Dependencias (OBLIGATORIO)

**Regla #1: Reutiliza antes de crear**

* **Antes de escribir código nuevo**, busca si ya existe:

  1. una función/utilidad dentro del repo (`src/cronquiles/`, `utils.py`, `models.py`, `history_manager.py`, etc.)
  2. una librería Python establecida en PyPI para resolverlo
* Si existe algo similar, **refactoriza/reusa** en vez de duplicar.

**Regla #2: No inventes librerías, módulos ni APIs**

* **Prohibido**:
  * inventar nombres de paquetes (“cronquiles-tools”, “ical_superparser”, etc.)
  * inventar campos de un ICS/fuente si no están en el input real
  * inventar endpoints o “APIs públicas” que no existan
* Si no estás seguro de que algo exista, dilo explícitamente:
  **“No tengo evidencia de que exista X; propongo alternativa Y usando librerías estándar.”**

**Regla #3: Si propones una dependencia, debe ser real y verificable**
* Cada vez que sugieras una librería externa, debes incluir:
  * **Nombre exacto del paquete PyPI**
  * **Para qué se usa** en el proyecto (1 línea)
  * **Alternativa estándar** (stdlib) si aplica
  * **Licencia/estabilidad** (si la conoces; si no, indícalo sin inventar)
* Si se agrega una dependencia:
  * actualiza `requirements.txt` y/o `pyproject.toml`
  * agrega tests mínimos y docstrings
  * actualiza README/CHANGELOG (según tu regla de oro)

**Regla #4: Prioridad de elección (orden estricto)**
1. Código existente del repo (refactor si hace falta)
2. Python stdlib
3. Librerías “de facto standard” y maduras
4. Código nuevo (solo si 1–3 no cubren el caso)

**Regla #5: No “construyas frameworks”**

* Evita crear mini-frameworks internos si una librería probada ya resuelve el problema.
* Mantén cambios pequeños, incrementales y revisables (PR-friendly).

**Formato de respuesta esperado al proponer cambios**

* ✅ “Encontré/reutilizo X del repo”
* ✅ “Uso librería Y (PyPI: `...`) porque …”
* ✅ “Si Y no aplica, alternativa con stdlib: …”
* ✅ “No invento fuentes/campos; me baso en: (menciona de dónde sale)”
