# Guía de Migración: pip → uv

Este documento ayuda a contribuyentes existentes a migrar de `pip` y `requirements.txt` a `uv`.

## ¿Por qué migrar a uv?

- **70% más rápido**: Instalación de dependencias más rápida
- **Reproducible**: `uv.lock` garantiza builds idénticas en todos los entornos
- **Comando único**: `make install-dev` en lugar de crear venv y activar manualmente
- **Mejor DX**: Comandos simplificados con `Makefile`

## Instalación de uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verificar instalación
uv --version
```

## Migración Paso a Paso

### 1. Actualizar setup local

Si tienes un venv antiguo, puedes eliminarlo:

```bash
rm -rf venv/
```

### 2. Instalar dependencias con uv

```bash
# Instalar todas las dependencias (prod + dev)
make install-dev

# O si quieres solo dependencias de producción
make install
```

### 3. Usar nuevos comandos

#### Antes (pip + venv)
```bash
source venv/bin/activate
python -m pytest tests/ -v
python -m pip install -r requirements.txt
pip install --upgrade pytest
```

#### Ahora (uv + Make)
```bash
make test
make install-dev
make update  # Actualiza todas las dependencias
```

## Tabla de Comandos Equivalentes

| Tarea | Antes (pip) | Ahora (uv/Make) |
|-------|-------------|-----------------|
| **Instalar dependencias** | `pip install -r requirements.txt` | `make install-dev` |
| **Crear/activar venv** | `python -m venv venv` + `source venv/bin/activate` | `make install-dev` (automático) |
| **Ejecutar tests** | `python -m pytest tests/ -v` | `make test` |
| **Ejecutar tests específico** | `python -m pytest tests/test_foo.py -v` | `make test-file FILE=test_foo.py` |
| **Agregar dependencia** | `pip install requests` + actualizar requirements.txt | `uv add requests` |
| **Agregar dev dependency** | `pip install pytest` + actualizar requirements.txt | `uv add --dev pytest` |
| **Linting** | `pip install flake8` + `flake8 src/` | `make lint` |
| **Formateo** | `pip install black` + `black src/` | `make format` |
| **Ejecutar pipeline** | `python main.py --all-cities --json` | `make run-all` |
| **Ver comandos** | (sin ayuda integrada) | `make help` |
| **Actualizar dependencias** | Editar requirements.txt + reinstalar | `make update` |

## Cambios en las Herramientas de Desarrollo

### Antes
```bash
# Setup inicial
python3 -m venv venv
source venv/bin/activate  # o: venv\Scripts\activate en Windows
pip install -r requirements.txt
pip install -e .

# Desarrollo
python -m pytest tests/ -v
python -m black src/
python -m flake8 src/ --max-line-length=127
```

### Ahora
```bash
# Setup inicial
make install-dev

# Desarrollo
make test
make format
make lint
```

## Características Nuevas con uv

### Agregar Dependencias

```bash
# Agregar a producción
uv add requests

# Agregar a desarrollo
uv add --dev pytest

# Agregar versión específica
uv add "requests==2.31.0"
```

### Actualizar Dependencias

```bash
# Actualizar todas
make update
# o: uv lock --upgrade

# Actualizar paquete específico
uv lock --upgrade-package requests

# Sincronizar cambios en pyproject.toml
make sync
# o: uv sync
```

### Ejecutar Comandos

```bash
# Ejecutar comando sin activar venv
uv run python script.py

# Ejecutar pytest desde lockfile
uv run pytest tests/ -v

# Ejecutar herramienta instalada en pyproject.toml
uv run black src/
```

## Solución de Problemas

### "uv: command not found"

**Solución**: Asegúrate de que uv está instalado en PATH:
```bash
# Reinstalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reiniciar shell
exec $SHELL
```

### "ModuleNotFoundError" después de instalar dependencias

**Solución**: Sincronizar el entorno:
```bash
make sync
# o: uv sync --frozen
```

### CI falla después de actualizar dependencies

**Solución**: Asegúrate de que `uv.lock` está commiteado:
```bash
git add uv.lock
git commit -m "chore: actualizar uv.lock"
```

### Necesito volver a pip

uv es 100% compatible con `requirements.txt`. Puedes generar uno:

```bash
make requirements-freeze
# o: uv pip freeze > requirements.txt
```

Luego usar pip como antes:
```bash
pip install -r requirements.txt
```

## Beneficios en CI/CD

Con uv en GitHub Actions:

- **Setup ~70% más rápido**: uv instala dependencias en segundos vs minutos con pip
- **Cache automático**: uv detecta cambios en `uv.lock` automáticamente
- **Determinista**: Mismo `uv.lock` = exactamente mismo entorno

## Comparación de velocidad

Instalación típica (12 dependencias):

| Tool | Tiempo | Cache |
|------|--------|-------|
| pip sin cache | ~45s | No |
| pip con cache | ~25s | Sí |
| **uv** | **~5s** | **Nativo** |

## Próximos Pasos

1. ✅ Instalar uv
2. ✅ Ejecutar `make install-dev`
3. ✅ Reemplazar comandos antiguos con nuevos
4. ✅ Disfrutar de desarrollo más rápido

¿Preguntas? Abre un issue o pregunta en la comunidad.

---

**Notas importantes**:
- `uv.lock` **debe** estar commiteado en git
- `pyproject.toml` es la fuente única de verdad para dependencias
- `requirements.txt` se genera desde `pyproject.toml` solo si es necesario
- Todos los scripts usan `uv run` para garantizar entorno correcto
