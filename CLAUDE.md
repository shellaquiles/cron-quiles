# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cron-Quiles is a Python tool that aggregates tech event calendars from multiple sources (Meetup, Luma, Eventbrite, ICS feeds) into unified, deduplicated calendars for Mexico. It runs automatically via GitHub Actions every 6 hours.

## Common Commands

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the main pipeline (generates ICS/JSON files in gh-pages/data/)
python main.py --all-cities --json --output-dir gh-pages/data/

# Run tests
python -m pytest tests/ -v

# Run a single test file
python -m pytest tests/test_ics_aggregator.py -v

# Run tests with specific test name
python -m pytest tests/ -v -k "test_normalize_title"

# Lint code
pip install flake8
flake8 src/ --max-line-length=127

# Local dev server for gh-pages
cd gh-pages && python serve.py
```

## Architecture

### Core Pipeline (`src/cronquiles/`)

- **`main.py`**: CLI entry point with argument parsing. Loads feeds from `config/feeds.yaml`, orchestrates aggregation, and generates output files.
- **`ics_aggregator.py`**: `ICSAggregator` class - the main orchestrator. Dispatches to specific aggregators based on URL patterns, handles deduplication, geocoding, and history management.
- **`models.py`**: `EventNormalized` class - normalizes events from different sources into a unified format. Handles title cleaning, tag extraction, timezone conversion, and hash key generation for deduplication.
- **`history_manager.py`**: Persists events to `data/history.json` for historical data preservation and merge logic.

### Aggregators (`src/cronquiles/aggregators/`)

Each aggregator extracts events from a specific source type:
- `ics.py`: Generic ICS feed parser (base implementation)
- `meetup.py`: Meetup-specific extraction with JSON-LD enrichment for locations
- `luma.py`: Luma calendar integration with URL cleaning
- `eventbrite.py`: Eventbrite organizer and single event support
- `manual.py`: JSON-based manual event injection from `config/manual_events.json`

### Source Routing Logic

The `ICSAggregator.aggregate_feeds()` method routes URLs to aggregators:
- `eventbrite.com` URLs → EventbriteAggregator
- `lu.ma` or `luma.com` URLs → LumaAggregator
- `meetup.com` URLs → MeetupAggregator
- Everything else → GenericICSAggregator

### Deduplication

Events are deduplicated using hash keys based on normalized title + time block (2-hour tolerance in UTC). When duplicates are found, the best version is kept (preferring events with URLs and longer descriptions) and alternative URLs are merged into the description.

### Output Generation

Files are generated in `gh-pages/data/`:
- `cronquiles-mexico.ics/json` - National unified calendar
- `cronquiles-{state-code}.ics/json` - Per-state calendars (e.g., `cronquiles-mx-cmx.ics`)
- `cronquiles-online.ics/json` - Online-only events
- `states_metadata.json` - Frontend manifest with state info

### Country Filtering

Only events in Mexico (`country_code == "MX"`) or Online events are processed. Non-Mexico events are filtered out.

## Key Files

- `config/feeds.yaml`: List of all feed sources with URLs, names, and descriptions
- `config/manual_events.json`: Manual event entries (optional)
- `data/history.json`: Persistent event history database
- `data/geocoding_cache.json`: Cached geocoding results to avoid API rate limits

## Tools Directory

Maintenance scripts in `tools/`:
- `scrape_meetup_history.py`: Extract historical Meetup events
- `populate_cache_from_history.py`: Pre-populate geocoding cache
- `scan_feeds_and_cache.py`: Scan feeds and ensure cache completeness
- `update_communities_status.py`: Update community status in docs

## Documentation Requirements

When making changes:
1. Update `CHANGELOG.md` with changes
2. Update `docs/COMMUNITIES.md` if adding new feeds to `config/feeds.yaml`
3. Keep docstrings and inline comments current
4. Do not commit generated files in `gh-pages/data/` manually (GitHub Actions handles this)

## Code Style

- Python 3.10+
- Black for formatting
- Flake8 for linting (max line length 127)
- Type hints encouraged
- Docstrings for modules, classes, and public functions
- **All comments and code documentation must be in Spanish**
- User-facing labels and strings should be in Spanish (e.g., "Ver en Meetup" not "View on Meetup")
