---
name: "Añadir Evento Manual"
description: "Prompt para inyectar JSON en la base de manuales cuando no existe un ICS oficial"
---

# Añadir Evento Manual a DB

Usa esta plantilla para solicitar al Agente que añada un evento físico o en línea de manera estricta al `config/manual_events.json`.

```text
Por favor, añade el siguiente evento manual a `config/manual_events.json` usando el esquema Pydantic esperado.

- Título: [TITULO]
- Descripción: [TEXTO]
- URL (opcional, si hay registro): [URL]
- Locación: [DIRECCION]
- Estado/Ciudad: [ESTADO]
- Organizador: [NOMBRE_COMUNIDAD]
- Fecha y Hora de Inicio: [Ej: 2026-05-02 15:00]
- Fecha y Hora de Fin: [Ej: 2026-05-02 21:00]
- Etiquetas: [TAG1, TAG2]

Instrucciones para el Asistente:
1. Abre `config/manual_events.json` como array.
2. Anexa el diccionario.
3. Asegura que `dtstart` y `dtend` estén en formato ISO 8601 **incluyendo la zona horaria UTC-6 u otra pertinente** (Ej: `2026-05-02T15:00:00-06:00`).
4. Añade los strings literales obligatorios para "source": "Manual", y parsea ciudad/estado en los fields como "MX", "MX-CMX", "cdmx" según corresponda.
```
