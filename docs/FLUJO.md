# Flujo del pipeline y actualización de la página

Este documento describe el flujo completo: desde la configuración de feeds hasta la publicación del sitio en GitHub Pages.

## Resumen

1. **Entrada**: `config/feeds.yaml` (lista plana de feeds) y opcionalmente `config/manual_events.json`.
2. **Pipeline**: Descarga en paralelo → filtro México/Online → geocoding → merge con historial → deduplicación → agrupación por estado.
3. **Salida**: Archivos ICS/JSON en `gh-pages/data/` (nacional + por estado).
4. **Publicación**: El workflow de GitHub Actions ejecuta el pipeline y, si hay cambios, actualiza la rama `gh-pages` y despliega en GitHub Pages.

No hay configuración por “ciudad” en el YAML: el estado de cada evento se infiere por geocoding o por el feed; los calendarios por estado se generan dinámicamente.

---

## 1. Entrada (configuración)

| Archivo | Descripción |
|--------|-------------|
| `config/feeds.yaml` | Lista de feeds con `url`, `name`, `description`. Una sola lista; no hay sección por ciudad. |
| `config/manual_events.json` | Eventos inyectados a mano (opcional). |

El CLI lee estos archivos al iniciar (`main.py`).

---

## 2. Pipeline de agregación (`ICSAggregator.aggregate_feeds`)

### 2.1 Descarga en paralelo

- Cada entrada de `feeds.yaml` se clasifica por URL y se delega a un agregador:
  - **eventbrite.com** (organizador) → `EventbriteAggregator`
  - **lu.ma / luma.com** → `LumaAggregator`
  - **meetup.com** → `MeetupAggregator`
  - **hi.events / reuniones.** → `HiEventsAggregator`
  - Cualquier otra URL → `GenericICSAggregator`
- Los eventos de `manual_events.json` se procesan con `ManualAggregator`.
- Se usa un pool de workers (por defecto 10) para descargar todos los feeds en paralelo.
- Cada agregador devuelve una lista de `EventNormalized`.

### 2.2 Filtro por país

- Solo se conservan eventos con `country_code == "MX"` o eventos marcados como **online**. El resto se descarta.

### 2.3 Geocoding – Fase 1 (eventos recién descargados)

- A los eventos que no son online y no tienen `state_code` o `city` se les asigna ubicación vía geocoding (usando `data/geocoding_cache.json` y API si hace falta).
- Se persisten `geocoding_cache` y `data/luma_url_cache.json`.

### 2.4 Integración con historial

- Se deduplican los eventos recién descargados (por `hash_key`: título normalizado + bloque de tiempo).
- Se carga `data/history.json` (`HistoryManager`).
- Se hace **merge**: eventos nuevos + historial; si un evento ya existe por `hash_key`, se actualiza con la versión más completa.
- Se guarda de nuevo `data/history.json`.

### 2.5 Lista final desde historial

- La lista “oficial” de eventos sale de **historial**: `history_manager.get_all_events()`.
- Esos registros se reconstruyen como `EventNormalized`.

### 2.6 Geocoding – Fase 2 (healing)

- Si **no** se usa `--fast`: se buscan en la lista final eventos sin estado/ciudad (incluyendo históricos) y se geocodifican hasta un límite, actualizando `history.json` y cachés.

### 2.7 Orden y deduplicación final

- Se ordenan por `dtstart`.
- Se vuelve a deduplicar y se reescribe todo el historial con esa lista para mantener consistencia.

**Resultado**: Una única lista de `EventNormalized` (México + online, deduplicada y con historial aplicado).

---

## 3. Generación de salida (`main.py`)

- **Calendario nacional**: `gh-pages/data/cronquiles-mexico.ics` y `cronquiles-mexico.json` con todos los eventos.
- **Por estado/entidad**: `group_events_by_state(all_events)` agrupa por `state_code` (o `"ONLINE"` si no hay estado). Para cada grupo:
  - `gh-pages/data/cronquiles-{slug}.ics` y `cronquiles-{slug}.json`  
  (ej. `cronquiles-mx-cmx.ics`, `cronquiles-online.json`).
- **Metadatos para el frontend**: `gh-pages/data/states_metadata.json` (conteos, meses activos, emojis).
- **Docs**: Se ejecuta `tools/update_communities_status.py` para actualizar `docs/COMMUNITIES.md`.

Los estilos y el HTML/JS del sitio viven en la carpeta **`gh-pages/`** en la rama **main**; no hay una copia “propia” de estilos en la rama `gh-pages`. En cada despliegue se copia todo `gh-pages/*` desde main (más `data/` generados) a la rama `gh-pages`.

---

## 4. Publicación (GitHub Actions)

Workflow: `.github/workflows/update-events.yml`.

### 4.1 Cuándo se ejecuta

- **Schedule**: cada 6 horas (`cron: '0 */6 * * *'`).
- **Push**: en cada push a `main` o `master`.
- **Manual**: desde la pestaña **Actions** → "Update Events Calendar" → **Run workflow**.

### 4.2 Pasos del workflow

1. Checkout del repo (rama main/master).
2. Restaurar desde la rama `gh-pages`: `data/history.json`, `data/geocoding_cache.json`, y copia previa de `gh-pages/data/` para comparar.
3. Ejecutar el pipeline: `uv run python -m cronquiles.main --all-cities --json --output-dir gh-pages/data/`.
4. **Verificar si hay cambios**: comparar los datos generados con los previos; si no hay diferencias, no se hace commit ni deploy.
5. **Si hay cambios**:
   - Copiar `gh-pages/*` (desde main) + `data/` + `docs/COMMUNITIES.md` a un directorio temporal.
   - Hacer checkout a la rama `gh-pages` (orphan si no existe).
   - Reemplazar el contenido de la rama con ese directorio.
   - Commit con mensaje tipo "🤖 Auto-update: Refresh events calendar & persist data [skip ci]" y push a `gh-pages`.
   - Configurar Pages, subir artifact y desplegar con `deploy-pages`.

La página que ves en `https://<usuario>.github.io/cron-quiles/` es el contenido de esa rama (o del artifact que sube el workflow). Se actualiza solo cuando el workflow corre y detecta cambios en los datos.

---

## 5. Archivos clave

| Ubicación | Descripción |
|-----------|-------------|
| `config/feeds.yaml` | Fuente de verdad de feeds (una lista plana). |
| `config/manual_events.json` | Eventos manuales (opcional). |
| `data/history.json` | Base de datos de eventos (persistida entre ejecuciones). |
| `data/geocoding_cache.json` | Cache de geocoding. |
| `data/luma_url_cache.json` | Cache de URLs de Luma. |
| `gh-pages/` (en main) | HTML, CSS, JS y lugar donde el pipeline escribe `gh-pages/data/`. |
| Rama `gh-pages` | Contenido publicado: copia de `gh-pages/*` + `data/` + `docs/COMMUNITIES.md`. |

---

## 6. Comandos útiles

```bash
# Instalación
make install-dev

# Ejecutar pipeline (todos los feeds, salida en gh-pages/data/)
make run-all
# o
make run ARGS="--all-cities --json --output-dir gh-pages/data/"

# Modo rápido (sin healing de geocoding)
make run ARGS="--fast"

# Probar el sitio localmente (después de generar datos)
make serve
# o desde gh-pages: ./serve.sh o python3 serve.py
```

Para más detalle sobre la estructura del proyecto, ver `docs/PROJECT_STRUCTURE.md`. Para configuración de GitHub Pages, ver `docs/GITHUB_PAGES_SETUP.md`.
