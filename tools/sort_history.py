#!/usr/bin/env python3
import sys
import logging
from pathlib import Path

# Add src to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from cronquiles.history_manager import HistoryManager

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def sort_history():
    logger.info("Sorting history via HistoryManager...")
    hm = HistoryManager("data/history.json")
    hm.load_history()
    # Save triggers the sort
    hm.save_history()
    logger.info("Done.")

if __name__ == "__main__":
    sort_history()
