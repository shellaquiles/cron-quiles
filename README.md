# 🐢 Cron-Quiles

**El Calendario Tecnológico Centralizado para México.**
Agregando feeds públicos ICS, Meetup, Luma y Eventbrite en un único flujo de eventos unificado y sin duplicados.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=☕&slug=pixelead0&button_colour=FFDD00&font_colour=000000&font_family=Inter&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/pixelead0)

> 🤖 **Asistentes de IA & LLMs:** Antes de sugerir cambios o escribir código, por favor sigan estrictamente las pautas en [`AI.md`](AI.md).

---

## 🚀 Resumen

Cron-Quiles es una herramienta de código abierto diseñada para unificar el fragmentado ecosistema de calendarios de eventos tecnológicos en México. Consume varios formatos de feeds, normaliza los datos, elimina eventos duplicados y genera una salida limpia y utilizable para la comunidad.

**Calendario en Vivo:** [https://shellaquiles.github.io/cron-quiles/](https://shellaquiles.github.io/cron-quiles/)

## ✨ Características Principales

- **Agregación Multi-Fuente**:
  - **Feeds ICS**: Calendarios genéricos estándar.
  - **Meetup**: Enriquecimiento automático de ubicación mediante extracción JSON-LD/Next.js.
  - **Luma**: Integración profunda con limpieza de ubicaciones (correcciones solo con URL).
  - **Eventbrite**: Extracción nativa (Soporte para organizadores y eventos individuales).
  - **Hi.Events**: Soporte para plataformas personalizadas de comunidades tech (ej. Pythonistas GDL) vía extracción de API.
  - **Manual**: Inyección basada en JSON para eventos sin feeds públicos.
- **Deduplicación Inteligente**: Fusiona eventos duplicados (mismo título/hora) y consolida URLs alternativas de múltiples plataformas (Meetup, Luma, Eventbrite).
- **Eventos Multi-Fuente**: Los eventos pueden tener múltiples URLs de diferentes plataformas, mostradas con botones específicos de cada plataforma en el frontend.
- **Generación Dinámica de Estados**: Categoriza automáticamente los eventos por estado (ej. `MX-CMX`, `MX-JAL`) usando geocodificación.
- **Pipeline Automatizado**: Se ejecuta en GitHub Actions para mantener los datos actualizados cada 6 horas.
- **Interfaz Web Moderna**: UI con estilo de terminal con calendario visual integrado.

## ⚙️ Cómo Funciona (Pipeline)

Para entender la arquitectura central en 30 segundos:
1. **Entrada:** El script lee una lista plana de URLs objetivo desde `config/feeds.yaml` y entradas manuales opcionales.
2. **Extracción:** Delega la descarga en paralelo a Extractores específicos (Meetup, Luma, Eventbrite, Generic ICS).
3. **Procesamiento:** Los eventos se normalizan, geocodifican para determinar su Estado/Región, y se deduplican usando Hash Keys estrictas (Título + Bloque de Tiempo).
4. **Salida:** Se exportan archivos limpios ICS y JSON a `gh-pages/data/` (calendarios Unificados y por Estado) y se despliegan vía GitHub Actions.

## 🛠️ Inicio Rápido

### Requisitos

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

### Instalación

```bash
# Clonar
git clone https://github.com/shellaquiles/cron-quiles.git
cd cron-quiles

# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependencias
make install-dev

# Verificar
make check
```

### Uso

Ejecuta el pipeline principal para obtener feeds y generar artefactos:

```bash
# Procesar todos los feeds y salida a gh-pages/data/
make run-all

# Ver todos los comandos disponibles
make help
```

Esto genera:
- `cronquiles-mexico.ics` (Unificado)
- `cronquiles-mx-cmx.ics` (Ciudad de México)
- `cronquiles-mx-jal.ics` (Jalisco)
- `states_metadata.json` (Manifiesto del Frontend)

## 📚 Documentación

La documentación detallada está disponible en los directorios `.agents/instructions/` y `docs/`:

| Tema | Descripción | Enlace |
| :--- | :--- | :--- |
| **Arquitectura del Pipeline** | Especificaciones técnicas y detalles lógicos | [08-pipeline-architecture.md](.agents/instructions/08-pipeline-architecture.md) |
| **Estructura** | Disposición de directorios y explicación de módulos | [09-project-structure.md](.agents/instructions/09-project-structure.md) |
| **Comunidades** | Lista de comunidades integradas y su estado | [COMMUNITIES.md](docs/COMMUNITIES.md) |
| **Eventos Manuales** | Guía para agregar eventos manualmente vía JSON | [MANUAL_EVENTS.md](docs/MANUAL_EVENTS.md) |
| **Despliegue** | Guía de configuración de GitHub Pages & Actions | [GITHUB_PAGES_SETUP.md](docs/GITHUB_PAGES_SETUP.md) |

## 🤝 Contribución

¡Agradecemos las contribuciones! Por favor, consulta [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles sobre cómo proponer cambios.

**🤖 Agentic Workspace:** Este repositorio está estructurado como un espacio de trabajo listo para IA. Si utilizas asistentes de IA (Cursor, Windsurf, Copilot, Claude), estos leerán automáticamente nuestro archivo `AI.md` y navegarán por nuestra base de conocimiento `.agents/` para asegurar que su código cumpla con nuestros estrictos estándares arquitectónicos.

## 👥 Contribuidores

- **Ricardo Lira** ([@richlira](https://github.com/richlira))
- **Ivan Galaviz** ([@ivanovishado](https://github.com/ivanovishado))
- **Raul Estrada** ([@uurl](https://github.com/uurl))
- **Geronimo Orozco** ([@patux](https://github.com/patux))
- **Daniel Paredes** ([@DanielParedes](https://github.com/DanielParedes))
- **Mariano Rodríguez** ([@MarianoRD](https://github.com/MarianoRD))
- **Ben** ([@dataforxyz](https://github.com/dataforxyz))

---

*Hecho con ❤️ para la Comunidad Tecnológica de México.*
