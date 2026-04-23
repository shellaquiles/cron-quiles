---
name: "Desarrollo Frontend y UX"
description: "Pautas para editar o interactuar con el render de gh-pages"
---

# Desarrollo y Frontend (`/gh-pages/`)

El directorio `gh-pages/` contiene el código estático (HTML, CSS, JS) que alimenta la cara pública y la interfaz de usuario del proyecto (ej: renderización de tarjetas, vistas de calendario, etc.).

## Estructura
- Archivos clave: `index.html`, `eventos.html`, `comunidades.html`, `suscribir.html`.
- Los datos visualizados los extrae directamente del backend en forma de `/data/cronquiles-mexico.json` o `/data/states_metadata.json`.

## Consola Interactiva (Terminal)

El proyecto cuenta con una interfaz de comandos directamente en la consola del navegador (DevTools), diseñada para usuarios técnicos y mantenimiento.

### Comandos Disponibles
- `about` / `cronquiles`: Muestra información general y el logo ASCII del proyecto.
- `eventos(dateStr)`: Lista los eventos del mes.
    - Sin argumentos: Muestra el mes actual.
    - Argumento `"YYYY-MM"`: Salta a una fecha específica (ej. `eventos("2026-04")`).
- `eventos.next`: Avanza al mes siguiente.
- `eventos.last` / `eventos.prev`: Retrocede al mes anterior.
- `eventos.reset`: Vuelve al mes actual.
- `comunidades`: Lista los gremios técnicos de la ciudad activa.
- `suscribir`: Muestra enlaces y ayuda para sincronizar calendarios ICS.
- `clear`: Limpia la pantalla de la consola.
- `help`: Muestra la guía de comandos.

**Nota**: Todos los comandos admiten el alias en singular (ej. `evento.next`).

### Desarrollo del Componente
La lógica reside en `gh-pages/js/ui/Terminal.js`. Utiliza getters en el objeto `window` para permitir la ejecución de comandos sin necesidad de paréntesis obligatorios cuando no llevan argumentos.

## Entorno Local de Pruebas
Si como Agente tienes la instrucción de "Cambiar el estilo visual" o "Ajustar el render de las fechas":
1. Ejecuta tus modificaciones en los `.html` de la carpeta `gh-pages/`.
2. Lanza el servidor usando el comando `make serve`.
3. Informa al usuario que el servidor está corriendo en `http://localhost:8000` para su validación visual.

**ADVERTENCIA**: Nunca toques los archivos HTML directamente desde el `src/`. El Backend en `cronquiles` produce **Datos**, la vista en `gh-pages/` los consume.
