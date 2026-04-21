---
name: "Añadir Nuevo Feed a Cron-Quiles"
description: "Prompt estandarizado para inyectar una nueva URL de Meetup, Luma o Eventbrite al pipeline"
---

# Añadir Nuevo Feed

Para solicitarle al Agente o Copilot que añada un nuevo Feed, simplemente invoca el siguiente Prompt y provee los datos necesarios.

```text
Agrega la siguiente comunidad tecnológica al archivo `config/feeds.yaml`:
- Nombre: [NOMBRE_AQUÍ]
- URL (ICS / Luma / Meetup): [URL_AQUÍ]
- Descripción: [DESCRIPCION_AQUÍ]

Instrucciones para el Asistente:
1. Abre `config/feeds.yaml`.
2. Inserta el nuevo registro respetando el formato exacto existente (incluyendo los comentarios delimitadores `# ---`).
3. Verifica la validez de la URL según `.agents/rules/01-architecture-routing.md`.
4. Tras guardarlo, dirígete a `docs/COMMUNITIES.md` y registra la comunidad allí también (según dicta `04-documentation-rules.md`).
5. (Opcional) Ejecuta `make run ARGS="--fast"` para validar que el nuevo link no rompe el parseo de Pydantic.
```
