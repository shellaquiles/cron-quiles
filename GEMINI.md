# GEMINI.md

This file provides context and working guidelines for Gemini when interacting with the code in this repository.

## 📋 Project Overview

**Cron-Quiles** is a Python tool that aggregates tech event calendars from multiple sources (Meetup, Luma, Eventbrite ICS feeds) into unified, de‑duplicated calendars for Mexico.

**Automatic execution:** GitHub Actions every 6 hours or on push to main/master.

**Full pipeline:** See FLUJO.md for the detailed deployment flow.

---

## 🚀 Main Commands

### Installation
```bash
make install-dev  # Production + development dependencies
make install      # Production only
```

### Run the pipeline
```bash
make run-all                                    # All feeds → gh-pages/data/
make run ARGS="--all-cities --output-dir out/"  # Custom output directory
make run ARGS="--fast"                          # Skip geocoding (faster)
```

### Tests
```bash
make test                                  # All tests
make test-file FILE=test_ics_aggregator.py # Specific file
make test-filter FILTER="normalize_title"  # Filtered
```

### Linting & Formatting
```bash
make lint          # Check code
make format        # Format
make format-check  # Check without changing
```

### Local server
```bash
make serve  # http://localhost:8000
```

### Tools
```bash
make tools-deduplicate      # Remove duplicates
make tools-populate-cache   # Populate geocoding cache
make tools-scan-feeds       # Scan feeds
make tools-scrape-meetup    # Scrape Meetup events
```

### Management
```bash
make clean   # Clean generated files
make update  # Update dependencies
make check   # Verify environment
make help    # See all commands
```

---

## 📦 Dependency Management with uv

### Installing uv
```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Basic usage
```bash
uv sync --frozen              # Install from lockfile
uv sync --frozen --all-extras # With dev extras
uv add requests               # Add a dependency
uv add --dev pytest           # Add a dev dependency
uv lock --upgrade-package requests  # Upgrade specific package
uv lock --upgrade             # Upgrade everything
```

---

## 🏗️ Project Architecture

### Core pipeline (cronquiles)

| Module | Description |
|--------|-------------|
| `main.py` | CLI entry point. Loads feeds from `config/feeds.yaml`, orchestrates aggregation, generates output files |
| `ics_aggregator.py` | `ICSAggregator` class – the main orchestrator. Dispatches to specific aggregators, handles deduplication, geocoding and history |
| `models.py` | `EventNormalized` class – normalizes events from different sources. Cleans titles, extracts tags, converts timezones, generates hash keys |
| `history_manager.py` | Persists events to history.json to preserve historical data and merge logic |

### Aggregators (aggregators)

Each aggregator extracts events from a specific source type:

- **`ics.py`**: Generic ICS feed parser (base implementation)
- **`meetup.py`**: Meetup‑specific extraction with JSON‑LD enrichment for locations
- **`luma.py`**: Luma calendar integration with URL cleaning
- **`eventbrite.py`**: Organizer and single‑event support for Eventbrite
events from it.
- **`manual.py`**: Manual event injection from JSON in manual_events.json

### Source routing logic

The `ICSAggregator.aggregate_feeds()` method routes URLs to aggregators:

```python
# Routing logic
if "eventbrite.com" in url → EventbriteAggregator
if "lu.ma" or "luma.com" in url → LumaAggregator  
if "meetup.com" in url → MeetupAggregator
else → GenericICSAggregator
```

### Deduplication

Events are deduplicated using hash keys based on:
- Normalized title + time block (2‑hour tolerance in UTC)

When duplicates are found:
- The best version is kept (prefers events with URLs and longer descriptions)
- Alternative URLs are merged into the description

### Output generation

Files are generated in data:

```
cronquiles-mexico.ics/json           # Unified national calendar
cronquiles-{state-code}.ics/json     # Per-state (e.g. cronquiles-mx-cmx.ics)
cronquiles-online.ics/json           # Online‑only events
states_metadata.json                 # Frontend manifest with state info
```

**`online` field in JSON:** Events include `online: true/false` (from `EventNormalized._is_online()`) so the frontend can show “en línea” and omit “Ver en mapa” for online events.

### Country filtering

**Only processed:**
- Events in Mexico (`country_code == "MX"`)
- Online events

Out‑of‑Mexico events are filtered out.

---

## 📁 Key Files

| File/Directory | Purpose |
|----------------|---------|
| `feeds.yaml` | List of all feed sources with URLs, names and descriptions |
| `manual_events.json` | Manual event entries (optional) |
| `history.json` | Persistent event history database |
| `data/geocoding_cache.json` | Cached geocoding results (avoids API rate limits) |
| `gh-pages` | Frontend (HTML, CSS, JS). Multipage: index, eventos, suscribir, comunidades. See README.md |

### Frontend (gh-pages)

**Features:**
- **Multipage:** index, eventos, suscribir, comunidades
- **Interactive calendar:** click day → scroll to that day’s events
- **Event cards:** date first, “Ver en mapa” (physical), “en línea” (online)

---

## 🛠️ Tools Directory

Maintenance scripts in tools:

| Script | Function |
|--------|----------|
| `scrape_meetup_history.py` | Extract historical Meetup events |
| `populate_cache_from_history.py` | Pre‑populate geocoding cache |
| `scan_feeds_and_cache.py` | Scan feeds and ensure cache completeness |
| `update_communities_status.py` | Update community status in docs |

---

## 📝 Documentation Requirements

When making changes:

1. ✅ Update CHANGELOG.md with the changes
2. ✅ Update COMMUNITIES.md if you add feeds to feeds.yaml
3. ✅ Keep docstrings and inline comments current
4. ❌ Do **not** manually commit generated files in data (GitHub Actions handles them)
5. ✅ **Pipeline/deployment:** The canonical description is in FLUJO.md. Update that file if aggregation steps, output layout, or workflow change.

---

## 🎨 Coding Style

### Technical conventions
- **Python:** 3.10+
- **Formatting:** Black
- **Linting:** Flake8 (max line length 127)
- **Type hints:** Recommended
- **Docstrings:** For modules, classes and public functions

### Language conventions
- ✅ **All code comments and documentation must be in Spanish**
- ✅ **User‑facing labels and strings in Spanish** (e.g. “Ver en Meetup” not “View on Meetup”)

---

## 💡 Notes for Gemini

When working on this project:

1. **Context first:** Review FLUJO.md before modifying the pipeline
2. **Tests:** Run `make test` before committing
3. **Format:** Use `make format` to maintain consistency
4. **Language:** Keep all code and documentation in Spanish
5. **Don’t touch:** Files in data are autogenerated

### Typical workflow
```bash
# 1. Make code changes
# 2. Format
make format

# 3. Test
make test

# 4. Verify
make lint

# 5. Run pipeline locally
make run-all

# 6. Inspect output in gh-pages/data/
```

---

## 🔍 Troubleshooting Common Issues

**Pipeline fails:**
- Run `make check` to validate environment
- Check logs in workflows

**Duplicate events:**
- Run `make tools-deduplicate`
- Review hash logic in `models.py`

**Slow geocoding:**
- Use `make run ARGS="--fast"` for testing
- Populate cache: `make tools-populate-cache`

**Feeds not aggregating:**
- Verify format in feeds.yaml
- Review routing in `ics_aggregator.py`

---

**Last updated:** This document should be kept in sync with changes to the project architecture.
