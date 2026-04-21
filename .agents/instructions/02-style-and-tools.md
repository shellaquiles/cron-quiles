# Directrices de Estilo y Herramientas (cronquiles)

## Estilo de Código Base
- **Versión Core**: Python 3.10+
- **Formateo**: Obligatoriamente `black`
- **Linting**: Obligatoriamente `flake8` (max line length 127)
- **Tipado**: Type hints requeridos en la medida de lo posible.
- **Documentación**: Docstrings para módulos, clases, y funciones públicas.

> [!IMPORTANT]
> REGLA DE IDIOMA
> ABSOLUTAMENTE TODOS los comentarios de código y la documentación interna deben estar en **Español**. Los textos de interfaz para usuarios en `gh-pages` siempre en Español (ej. usar "Ver en Meetup" y nunca "View on Meetup").

## Manejo de Dependencias y Herramientas (uv / Make)
El proyecto confía enteramente en `uv`. No utilices pip tradicional para instalaciones base a menos que sea una emergencia de entorno aislado.

### Instalación Core `uv`
```bash
uv sync --frozen              # Instalar solo desde uv.lock
uv sync --frozen --all-extras # Instalar entorno dev
uv add <dependencia>          # Agregar requerimientos de producción
uv lock --upgrade             # Actualizar lockfile profundo
```

### Make Interface
Debes operar el proyecto principalmente a través de Makefile, no mediante llamadas arbitrarias a binarios de python:
- `make format` y `make lint`: Aseguramiento de calidad previo a commit.
- `make test`: Ejecución de suite unitaria en `pytest`.
- `make clean`: Purgar los archivos de caché generados automáticamentes.
