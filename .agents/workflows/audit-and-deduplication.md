---
description: "Paso a paso para auditar la deduplicación de eventos usando las herramientas y validación formal de hashes."
---

# Workflow: Auditoría de Deduplicación y Colisiones

**Propósito**: Ejecutar comandos preventivos cuando el output parezca estar emitiendo eventos repetidos en tiempo o título.

1. Correr el limpiador de logs base:
```bash
make clean
```

2. Ejecutar la herramienta designada de deduplicación:
```bash
// turbo
make tools-deduplicate
```

3. Verificar las colisiones resultantes revisando `data/history.json` o los nuevos hashes generados. Si observas que dos eventos diferentes comparten hashes por un issue en timezone:
   - Activa el filtro unitario de testing `make test-filter FILTER="normalize_title"`
   - Verifica el componente `models.py` para aislar el cambio en la tolerancia del Time Block.
