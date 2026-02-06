# Configuración de GitHub Pages

Esta guía te ayudará a configurar GitHub Pages para publicar automáticamente el calendario de eventos.

## Pasos de Configuración

### 1. Habilitar GitHub Pages en el Repositorio

1. Ve a tu repositorio en GitHub: `https://github.com/shellaquiles/cron-quiles`
2. Haz clic en **Settings** (Configuración)
3. En el menú lateral, haz clic en **Pages**
4. En la sección **Source** (Fuente):
   - Selecciona **GitHub Actions** como fuente
5. Guarda los cambios

### 2. Configurar Secretos del Repositorio

Para que la geocodificación funcione correctamente en CI (usando Google Maps en lugar de Nominatim), debes agregar tu API Key:

1. Ve a **Settings** (Configuración) -> **Secrets and variables** -> **Actions**.
2. Haz clic en **New repository secret**.
3. Nombre: `GOOGLE_MAPS_API_KEY`
4. Valor: Tu API Key de Google Maps Platform.
5. Haz clic en **Add secret**.

### 3. Verificar Permisos del Workflow

El workflow `.github/workflows/update-events.yml` ya está configurado con los permisos necesarios:

```yaml
permissions:
  contents: write
  pages: write
  id-token: write
```

Estos permisos permiten:
- `contents: write`: Hacer commits automáticos
- `pages: write`: Publicar en GitHub Pages
- `id-token: write`: Autenticación OIDC

### 3. Verificar que el Workflow Funciona

El workflow se ejecutará automáticamente:
- Cada 6 horas (cron schedule)
- Cuando hagas push a `main` o `master`
- Cuando cambies archivos de configuración o código
- Manualmente desde la pestaña **Actions**

### 4. Acceder a tu Sitio

Una vez configurado, tu sitio estará disponible en:

- **URL principal**: `https://shellaquiles.github.io/cron-quiles/`
- **Calendario nacional ICS**: `https://shellaquiles.github.io/cron-quiles/data/cronquiles-mexico.ics`
- **Calendario nacional JSON**: `https://shellaquiles.github.io/cron-quiles/data/cronquiles-mexico.json`
- **WebCal (suscripción nacional)**: `webcal://shellaquiles.github.io/cron-quiles/data/cronquiles-mexico.ics`
- **Por estado**: `data/cronquiles-{slug}.ics` y `data/cronquiles-{slug}.json` (ej. `cronquiles-mx-cmx`, `cronquiles-online`)

Para el flujo completo del pipeline y cómo se actualiza la página, ver **`docs/FLUJO.md`**.

### 5. Verificar la Publicación

1. Ve a la pestaña **Actions** en tu repositorio
2. Busca el workflow "Update Events Calendar"
3. Verifica que se ejecute correctamente
4. Si hay errores, revisa los logs del workflow
5. **Verificar Commits Automáticos**: El workflow también actualiza automáticamente `docs/COMMUNITIES.md` en la rama principal si hubo cambios en los estados de las comunidades.

## Archivos que se Publican

Los siguientes archivos se publican automáticamente en GitHub Pages desde la carpeta `gh-pages/`:

- `gh-pages/index.html` - Página principal con diseño terminal y calendario embebido
- `gh-pages/css/` - Estilos CSS (layout, componentes, variables)
- `gh-pages/js/` - Scripts JavaScript (lógica de calendario, tabs, etc.)
- `gh-pages/data/cronquiles-mexico.ics/json` - Calendario nacional
- `gh-pages/data/cronquiles-{slug}.ics/json` - Calendarios por estado (ej. mx-cmx, online)
- `gh-pages/data/states_metadata.json` - Manifiesto para el frontend

**Características de la interfaz:**
- Diseño terminal estilo shellaquiles-org (verde/negro/blanco)
- Calendario mensual visual con eventos del mes
- Navegación entre meses
- Visualización automática de todos los eventos del mes actual
- Diseño responsive para móvil y escritorio

## Solución de Problemas

### El sitio no se publica

1. Verifica que GitHub Pages esté habilitado con **GitHub Actions** como fuente
2. Revisa los logs del workflow en la pestaña **Actions**
3. Asegúrate de que el workflow tenga los permisos correctos

### Los archivos no se actualizan

1. Verifica que el workflow se esté ejecutando
2. Revisa que los archivos `.ics` y `.json` se estén generando correctamente
3. Verifica los logs del paso "Generate calendar"

### Error de permisos

Si ves errores de permisos:
1. Ve a **Settings** → **Actions** → **General**
2. En "Workflow permissions", selecciona **Read and write permissions**
3. Marca la casilla "Allow GitHub Actions to create and approve pull requests"

## Personalización

### Cambiar la Frecuencia de Actualización

Edita `.github/workflows/update-events.yml` y modifica el cron:

```yaml
schedule:
  # Cada 6 horas (actual)
  - cron: '0 */6 * * *'

  # Cada 12 horas
  - cron: '0 */12 * * *'

  # Diario a las 3 AM UTC
  - cron: '0 3 * * *'
```

### Personalizar el index.html, CSS y JS

Puedes editar:
- `gh-pages/index.html`: Estructura HTML y contenido
- `gh-pages/css/*.css`: Estilos, variables y layout
- `gh-pages/js/*.js`: Lógica de la aplicación

El diseño actual incluye:
- Tema terminal con colores verde/negro/blanco
- Calendario mensual visual embebido
- Lista automática de eventos del mes
- Estilos responsive para móvil

### Desarrollo Local

Para probar el sitio localmente antes de publicar:

```bash
cd gh-pages
python3 serve.py
# O
./serve.sh
```

Luego abre `http://localhost:8000/index.html` en tu navegador.

Ver `gh-pages/README-LOCAL.md` para más detalles.

## Notas Importantes

- GitHub Pages puede tardar unos minutos en publicar los cambios
- El sitio se actualiza automáticamente cuando el workflow se ejecuta
- Los archivos se generan directamente en `gh-pages/` por el workflow
- El workflow genera `cronquiles.ics` y `cronquiles.json` en `gh-pages/` antes de publicar
- Los archivos en `gh-pages/` se publican automáticamente en GitHub Pages
