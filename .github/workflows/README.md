# GitHub Actions Workflow – Update Events Calendar

Este workflow ejecuta el pipeline de Cron-Quiles y, si hay cambios en los datos, actualiza la rama `gh-pages` y despliega en GitHub Pages.

## ¿Qué hace?

1. Restaura desde la rama `gh-pages`: `data/history.json`, `data/geocoding_cache.json`, y copia previa de `gh-pages/data/`.
2. Ejecuta el pipeline: descarga feeds desde `config/feeds.yaml`, normaliza, filtra por México/Online, geocodifica, merge con historial, deduplica.
3. Genera en `gh-pages/data/`: `cronquiles-mexico.ics/json`, `cronquiles-{slug}.ics/json` por estado, `states_metadata.json`.
4. Compara los datos generados con los previos; **solo si hay cambios**:
   - Hace checkout a la rama `gh-pages` (orphan si no existe).
   - Copia `gh-pages/*` (desde main) + `data/` + `docs/COMMUNITIES.md`.
   - Commit con mensaje "🤖 Auto-update: Refresh events calendar & persist data [skip ci]" y push a `gh-pages`.
   - Sube artifact y despliega con GitHub Pages.

Para el flujo completo del pipeline y publicación, ver **`docs/FLUJO.md`**.

## Activación

El workflow se ejecuta cuando:
- **Schedule**: cada 6 horas (`cron: '0 */6 * * *'`).
- **Push**: en cada push a `main` o `master`.
- **Manual**: Actions → "Update Events Calendar" → Run workflow.

## Permisos necesarios

Para que el workflow pueda hacer commit y push a la rama `gh-pages`:

1. En **Settings → Actions → General**, en "Workflow permissions", selecciona **Read and write permissions**.
2. Opcional: "Allow GitHub Actions to create and approve pull requests" si usas flujos que lo requieran.

## Ver logs

Ve a la pestaña **Actions** en GitHub para ver:
- Historial de ejecuciones del workflow "Update Events Calendar"
- Logs de cada paso (restaurar estado, generar calendarios, verificar cambios, publicar)
- Errores si los hay
