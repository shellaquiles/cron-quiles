#!/usr/bin/env python3
import sys
import json
import logging
from pathlib import Path

# Add src to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from cronquiles.history_manager import HistoryManager
from cronquiles.models import EventNormalized

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def deduplicate():
    history_file = "data/history.json"
    hm = HistoryManager(history_file)

    if not Path(history_file).exists():
        logger.error("No history file found.")
        return

    logger.info("Loading existing history...")
    with open(history_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    logger.info(f"Original count: {len(data)}")

    # New dict key -> event
    reindexed_events = {}
    duplicates_found = 0

    for item in data:
        # Re-create normalized instance to get the canonical hash key
        # We assume 'source' field is enough to make a dummy object if needed,
        # but from_dict handles most logic.

        # NOTE: from_dict might re-normalize titles.
        # We rely on this behavior to catch "Cdmx Vim Meetup" vs "cdmx-vim-meetup"

        try:
            instance = EventNormalized.from_dict(item)
            key = instance.hash_key

            # Conflict resolution
            if key in reindexed_events:
                duplicates_found += 1
                existing = reindexed_events[key]
                new_one = instance.to_dict()

                # Check which one is better
                # Heuristic: More keys is better? Or presense of city_code?
                score_existing = len(str(existing))
                score_new = len(str(new_one))

                # Also prefer the one that has valid city_code if the other doesn't
                has_code_ex = bool(existing.get('city_code'))
                has_code_new = bool(new_one.get('city_code'))

                if has_code_new and not has_code_ex:
                    reindexed_events[key] = new_one
                elif score_new > score_existing and (has_code_new == has_code_ex):
                    reindexed_events[key] = new_one
                else:
                    # Keep existing
                    pass
            else:
                reindexed_events[key] = instance.to_dict()

        except Exception as e:
            logger.error(f"Error processing item {item.get('title')}: {e}")

    logger.info(f"Duplicates identified and merged: {duplicates_found}")
    logger.info(f"Final count: {len(reindexed_events)}")

    # Update HM internal state and save
    hm.events = reindexed_events
    hm.save_history()

if __name__ == "__main__":
    deduplicate()
