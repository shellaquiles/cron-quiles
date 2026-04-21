---
description: "Simulador local del paso Final antes de un Merge a Main (Pipeline)"
---

# Workflow: Simulación Final de Pipeline

**Propósito**: Asegurar localmente que la Action de Github no va a fallar antes de subir los cambios a QA/Main.

1. Actualizar caché velozmente sin saturar APIs:
```bash
// turbo
make tools-populate-cache
```

2. Ejecutar aggregator con argumento especial rápido (skips location APIs profundas y testing unitario):
```bash
// turbo
make run ARGS="--fast"
```

3. Correr formateo crítico (flake8 strict):
```bash
// turbo
make lint
make format-check
```

4. Tras este chequeo, el Agente debe confirmar visual o textualmente si se generaron los `.json` y `.ics` en formato correcto (revisando GH-Pages output logs).
