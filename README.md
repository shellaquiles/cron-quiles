# 🐢 Cron-Quiles

**The Centralized Tech Calendar for Mexico.**
Aggregating public ICS feeds, Meetup, Luma, and Eventbrite into a single, unified, and deduplicated event stream.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=☕&slug=pixelead0&button_colour=FFDD00&font_colour=000000&font_family=Inter&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/pixelead0)

---

## 🚀 Overview

Cron-Quiles is an open-source tool designed to unify the fragmented landscape of tech event calendars in Mexico. It consumes various feed formats, normalizes the data, deduplicates events, and generates a clean, usable output for the community.

**Live Calendar:** [https://shellaquiles.github.io/cron-quiles/](https://shellaquiles.github.io/cron-quiles/)

## ✨ Key Features

- **Multi-Source Aggregation**:
  - **ICS Feeds**: Standard generic calendars.
  - **Meetup**: Automatic location enrichment via JSON-LD/Next.js extraction.
  - **Luma**: Deep integration with location cleaning (URL-only fixes).
  - **Eventbrite**: Native extraction (Organizer & Single Event support).
  - **Hi.Events**: Support for custom tech community platforms (e.g., Pythonistas GDL) via API extraction.
  - **Manual**: JSON-based injection for events without public feeds.
- **Smart Deduplication**: Merges duplicate events (same title/time) and consolidates alternative URLs.
- **Dynamic State Generation**: Automatically categorizes events by state (e.g., `MX-CMX`, `MX-JAL`) using geocoding.
- **Automated Pipeline**: runs on GitHub Actions to keep data fresh every 6 hours.
- **Modern Web Interface**: Terminal-styled UI with embedded visual calendar.

## 🛠️ Quick Start

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

This generates:
- `cronquiles-mexico.ics` (Unified)
- `cronquiles-mx-cmx.ics` (Mexico City)
- `cronquiles-mx-jal.ics` (Jalisco)
- `states_metadata.json` (Frontend Manifest)

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

| Topic | Description | Link |
| :--- | :--- | :--- |
| **Architecture** | Technical specifications and logic details | [AGENTS.md](docs/AGENTS.md) |
| **Structure** | Directory layout and module explanation | [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) |
| **Communities** | List of integrated communities and their status | [COMMUNITIES.md](docs/COMMUNITIES.md) |
| **Manual Events** | Guide to adding events manually via JSON | [MANUAL_EVENTS.md](docs/MANUAL_EVENTS.md) |
| **Deployment** | GitHub Pages & Actions setup guide | [GITHUB_PAGES_SETUP.md](docs/GITHUB_PAGES_SETUP.md) |

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to propose changes.

## 👥 Contributors

- **Ricardo Lira** ([@richlira](https://github.com/richlira))
- **Ivan Galaviz** ([@ivanovishado](https://github.com/ivanovishado))
- **Pixelead0** ([@pixelead0](https://github.com/pixelead0))
- **Raul Estrada** ([@uurl](https://github.com/uurl))
- **Geronimo Orozco** ([@patux](https://github.com/patux))
- **Daniel Paredes** ([@DanielParedes](https://github.com/DanielParedes))
- **Mariano Rodríguez** ([@marianox](https://github.com/marianox))

---

*Built with ❤️ for the Mexican Tech Community.*
