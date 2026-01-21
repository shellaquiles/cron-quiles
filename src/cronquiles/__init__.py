"""
Cron-Quiles - Agregador de calendarios tech (Meetup, Luma, ICS) que se actualiza solo.
"""

__version__ = "1.9.0"
__author__ = "Shellaquiles Community"

from .ics_aggregator import EventNormalized, ICSAggregator

__all__ = ["ICSAggregator", "EventNormalized"]
