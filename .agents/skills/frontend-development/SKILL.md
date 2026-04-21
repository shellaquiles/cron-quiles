---
name: "Desarrollo Frontend y UX"
description: "Pautas para editar o interactuar con el render de gh-pages"
---

# Desarrollo y Frontend (`/gh-pages/`)

El directorio `gh-pages/` contiene el código estático (HTML, CSS, JS) que alimenta la cara pública y la interfaz de usuario del proyecto (ej: renderización de tarjetas, vistas de calendario, etc.).

## Estructura
- Archivos clave: `index.html`, `eventos.html`, `comunidades.html`, `suscribir.html`.
- Los datos visualizados los extrae directamente del backend en forma de `/data/cronquiles-mexico.json` o `/data/states_metadata.json`.

## Entorno Local de Pruebas
Si como Agente tienes la instrucción de "Cambiar el estilo visual" o "Ajustar el render de las fechas":
1. Ejecuta tus modificaciones en los `.html` de la carpeta `gh-pages/`.
2. Lanza el servidor usando el comando `make serve`.
3. Informa al usuario que el servidor está corriendo en `http://localhost:8000` para su validación visual.

**ADVERTENCIA**: Nunca toques los archivos HTML directamente desde el `src/`. El Backend en `cronquiles` produce **Datos**, la vista en `gh-pages/` los consume.
