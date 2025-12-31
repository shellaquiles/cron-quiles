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
4. Generar:

   * Un **ICS unificado**
   * (opcional) Un JSON para futuros usos

### Estado Actual del Proyecto (v1.6.0)

El proyecto es completamente funcional y opera bajo Github Actions.

**Funcionalidades Implementadas:**
1.  **Soporte Multifuente**: Consume feeds ICS de Meetup, Luma y Google Calendar.
2.  **Deduplicación Robusta**:
    *   Identifica eventos duplicados por título y hora (tolerancia ±2 horas).
    *   Normaliza zonas horarias a UTC para evitar falsos positivos.
    *   **NO PIERDE DATOS**: Si hay duplicados con diferentes links, los agrega a la descripción del evento principal ("Otras fuentes: ...").
3.  **Extracción Inteligente de Metadatos**:
    *   Prioriza nombres de grupos configurados manualmente > X-WR-CALNAME (del ICS) > Organizador del evento.
    *   Detecta automáticamente URLs de eventos Luma (`lu.ma`, `luma.com`) dentro de la descripción si no están en el campo URL principal.
4.  **Formato de Títulos Estandarizado**: `Grupo|Nombre|Ubicación` (ej: "Python CDMX|Charla Mensual|Online").
5.  **Detección de Ubicación**: Clasifica automáticamente como "Online", "Ciudad, Estado" o "País".
    *   Enriquecimiento de ubicación desde Meetup (JSON-LD/Next.js).
6.  **Sistema de Configuración**: `feeds.yaml` centralizado para gestionar fuentes.
7.  **Salida Dual**: Genera tanto `.ics` (para calendarios) como `.json` (para integraciones).
8.  **Logging Detallado**: Registra el proceso de agregación y estadísticas de eventos procesados.
9.  **Tags automáticos**: Detección por keywords en título y descripción (python, ai, cloud, etc).
10. **Interfaz web moderna**: Diseño terminal estilo shellaquiles-org con calendario visual embebido.
11. **Manejo robusto de timezones**: Conversión a UTC para lógica interna, preservando original.
12. **Publicación automática**: GitHub Actions actualiza feeds y Pages cada 6 horas.

### Deduplicación

Estrategia implementada:
* Normalizar título (lowercase, sin emojis, sin puntuación)
* Comparar fecha/hora (±2 horas usando bloques de 2 horas en UTC)
* Si coinciden → conservar uno
* Priorizar eventos con:
  1. URL válida
  2. Descripción más larga
* **Merge de links**: Si los duplicados tienen URLs diferentes, se agregan al final de la descripción.

### Output

* Archivo: `gh-pages/cronquiles.ics` (calendario ICS unificado)
* Archivo opcional: `gh-pages/cronquiles.json` (JSON con eventos)
* Interfaz web: `gh-pages/index.html` (página con calendario embebido)

### Entregables

* ✅ Código funcional y bien documentado
* ✅ README.md completo y actualizado
* ✅ Ejemplo de `feeds.yaml` y `list_icals.txt`
* ✅ CHANGELOG.md con historial de cambios
* ✅ Documentación de estructura del proyecto
* ✅ Tests básicos
* ✅ GitHub Actions workflow
* ✅ Interfaz web moderna
* ✅ Documentación de Google Calendar setup

### Estructura del proyecto

```
cron-quiles/
├── main.py                    # Punto de entrada CLI (raíz)
├── src/
│   └── cronquiles/
│       ├── __init__.py        # Paquete Python
│       ├── main.py            # CLI principal
│       ├── ics_aggregator.py  # Lógica de agregación y deduplicación
│       └── google_calendar.py # Publicación en Google Calendar (opcional)
├── config/
│   ├── feeds.yaml            # Configuración de feeds (YAML)
│   └── list_icals.txt        # Lista alternativa de feeds (texto)
├── docs/
│   ├── AGENTS.md             # Este archivo (especificaciones)
│   ├── PROJECT_STRUCTURE.md   # Documentación de estructura
│   ├── COMMUNITIES.md        # Lista de comunidades integradas
│   └── GITHUB_PAGES_SETUP.md # Guía de setup de GitHub Pages
├── gh-pages/                  # Archivos para GitHub Pages
│   ├── index.html            # Página principal con calendario embebido
│   ├── cronquiles.ics        # Calendario ICS (generado)
│   ├── cronquiles.json      # JSON con eventos (generado)
│   ├── serve.py             # Servidor HTTP para desarrollo local
│   └── serve.sh             # Script para iniciar servidor
├── examples/
│   └── example_event.py      # Ejemplo de formato de eventos
├── tests/
│   └── test_ics_aggregator.py # Tests básicos
├── requirements.txt          # Dependencias Python
├── pyproject.toml            # Configuración del proyecto
├── README.md                 # Documentación principal
├── CHANGELOG.md              # Historial de cambios
└── CONTRIBUTING.md           # Guía para contribuidores
```

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

3. **Mantener consistencia**:
   - ✅ Ejemplos de código en README deben funcionar
   - ✅ Rutas y nombres de archivos actualizados
   - ✅ Badges y metadata correctos
   - ✅ Links internos funcionando

4. **Verificar antes de commit**:
   - ✅ Documentación sincronizada con código
   - ✅ No dejar referencias a archivos/estructuras antiguas
   - ✅ Ejemplos actualizados y funcionales
   - ✅ **NO commitear archivos generados manualmente**: `gh-pages/cronquiles.ics` y `gh-pages/cronquiles.json`
     - Estos archivos son generados automáticamente por GitHub Actions
     - Si necesitas probar localmente, usa `git update-index --assume-unchanged` para ignorarlos temporalmente
     - Los archivos en `gh-pages/` son publicados automáticamente por el workflow

**Regla de oro**: Si cambias código, cambia documentación. Si cambias estructura, actualiza todos los archivos que la referencien.

### Archivos generados (no commitear manualmente)

Los siguientes archivos son generados automáticamente y **NO deben incluirse en commits manuales**:

* `gh-pages/cronquiles.ics` - Generado automáticamente por el script
* `gh-pages/cronquiles.json` - Generado automáticamente por el script (si se usa `--json`)

**Razón**: Estos archivos se generan automáticamente por GitHub Actions cada 6 horas. Si los commiteas manualmente, pueden causar conflictos innecesarios y el workflow los sobrescribirá de todas formas.

**Para desarrollo local**:
```bash
# Ignorar temporalmente estos archivos en git
git update-index --assume-unchanged gh-pages/cronquiles.ics
git update-index --assume-unchanged gh-pages/cronquiles.json

# Para volver a trackearlos (si es necesario)
git update-index --no-assume-unchanged gh-pages/cronquiles.ics
git update-index --no-assume-unchanged gh-pages/cronquiles.json
```

Piensa paso a paso, justifica decisiones técnicas y genera código limpio, comentado y listo para producción ligera. **Nunca dejes documentación desactualizada.**
