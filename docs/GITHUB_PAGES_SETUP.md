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

### 2. Verificar Permisos del Workflow

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
- **Archivo ICS**: `https://shellaquiles.github.io/cron-quiles/cronquiles.ics`
- **Archivo JSON**: `https://shellaquiles.github.io/cron-quiles/cronquiles.json`
- **WebCal (suscripción)**: `webcal://shellaquiles.github.io/cron-quiles/cronquiles.ics`

### 5. Verificar la Publicación

1. Ve a la pestaña **Actions** en tu repositorio
2. Busca el workflow "Update Events Calendar"
3. Verifica que se ejecute correctamente
4. Si hay errores, revisa los logs del workflow

## Archivos que se Publican

Los siguientes archivos se publican automáticamente en GitHub Pages:

- `index.html` - Página principal con instrucciones
- `cronquiles.ics` - Calendario ICS
- `cronquiles.json` - Datos JSON (si se genera)

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

### Personalizar el index.html

Puedes editar `index.html` para personalizar la apariencia y contenido de la página.

## Notas Importantes

- GitHub Pages puede tardar unos minutos en publicar los cambios
- El sitio se actualiza automáticamente cuando el workflow se ejecuta
- Los archivos se publican desde la raíz del repositorio
- Asegúrate de que `index.html` esté en la raíz del proyecto
