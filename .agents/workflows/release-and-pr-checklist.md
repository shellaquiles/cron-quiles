---
description: "Protocolo y checklist para la preparación de PRs y Releases (Versionado SemVer)"
---

# Workflow: Preparación de PR y Release

**Propósito**: Estandarizar el proceso de versionado semántico, actualización de documentación y validación antes de abrir un Pull Request o publicar un Release en Cron-Quiles.

---

## 1. Validación de Calidad y Pipeline

Antes de tocar versiones, asegurar que el pipeline y el código pasen todas las pruebas:

```bash
# 1.1 Ejecutar suite de pruebas unitarias
make test

# 1.2 Verificar formateo y linting estricto
make lint
make format-check

# 1.3 Simular corrida rápida del pipeline
make run ARGS="--fast"
```

---

## 2. Protocolo de Versionado (SemVer)

Cuando los cambios ameriten un nuevo release (`patch`, `minor` o `major`):

1. **Fuente Única de Verdad (`VERSION`)**:
   - Actualizar el número de versión en el archivo plano [`VERSION`](file:///home/kubrick/www/cron-quiles/VERSION) (ej. `1.9.2` o `2.0.0`).
   - *Nota:* `pyproject.toml`, `ics_aggregator.py` y el frontend leen automáticamente de este archivo.

2. **Actualizar `CHANGELOG.md`**:
   - Mover los cambios acumulados de `## [Unreleased]` a una nueva sección con la versión y fecha:
     ```markdown
     ## [Unreleased]

     ---

     ## [X.Y.Z] - AAAA-MM-DD
     ### Added / Changed / Fixed
     ...
     ```
   - Actualizar las URLs de comparación al final de [`CHANGELOG.md`](file:///home/kubrick/www/cron-quiles/CHANGELOG.md):
     ```markdown
     [Unreleased]: https://github.com/shellaquiles/cron-quiles/compare/vX.Y.Z...HEAD
     [X.Y.Z]: https://github.com/shellaquiles/cron-quiles/compare/vPREV...vX.Y.Z
     ```

3. **Verificar `SECURITY.md`** (si aplica):
   - Asegurar que la tabla de versiones soportadas en [`SECURITY.md`](file:///home/kubrick/www/cron-quiles/SECURITY.md) refleje la nueva rama de versiones activas.

---

## 3. Preparación del Commit y Tag

1. **Commit de Release**:
   ```bash
   git add VERSION CHANGELOG.md SECURITY.md
   git commit -m "chore: release vX.Y.Z"
   ```

2. **Crear Tag Git Anotado**:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   ```

---

## 4. Checklist para el Pull Request (PR)

Al abrir el PR hacia `main`:

* [ ] Las pruebas pasan localmente (`make test`).
* [ ] No hay errores de linting ni formateo (`make lint`).
* [ ] El archivo `VERSION` contiene la versión correcta.
* [ ] `CHANGELOG.md` documenta los cambios bajo `[Unreleased]` o la nueva versión `[X.Y.Z]`.
* [ ] Si hay nuevas dependencias, se actualizaron en `pyproject.toml` y `uv.lock`.
* [ ] Si se agregaron comunidades/eventos, se validaron los feeds y las coordenadas geográficas.
