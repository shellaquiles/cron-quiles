import sys
import os
import requests
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from cronquiles.models import EventNormalized
from icalendar import Event


class TestLumaEnrichment(unittest.TestCase):
    def test_enrich_location(self):
        url = "https://luma.com/event/evt-myXglGrlwok8Sie"

        # Create a dummy event
        event_ical = Event()
        event_ical.add("summary", "Test Event")
        event_ical.add("url", url)
        event_norm = EventNormalized(event_ical, source_url="")

        print(f"Original Location: {event_norm.location}")

        session = requests.Session()
        success = event_norm.enrich_location_from_luma(session)

        print(f"Enrichment Success: {success}")
        print(f"New Location: {event_norm.location}")
        print(f"Address: {event_norm.address}")
        print(f"City: {event_norm.city}")

        self.assertTrue(success)
        self.assertNotEqual(event_norm.location, "")
        self.assertNotEqual(event_norm.location, "Check event page for more details")
        self.assertIn("Cuauhtémoc", event_norm.location)
        # Ensure coordinates are removed
        self.assertNotIn("19.42", event_norm.location)
        # self.assertIn("Pinterest México", event_norm.location) # Only visible if authenticated/not obfuscated


if __name__ == "__main__":
    unittest.main()
