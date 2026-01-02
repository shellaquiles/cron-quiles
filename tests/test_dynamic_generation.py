import unittest
import sys
from pathlib import Path
from datetime import datetime
from icalendar import Event
from dateutil import tz

# Agregar src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from cronquiles.models import EventNormalized
from cronquiles.ics_aggregator import ICSAggregator
from cronquiles.main import generate_states_metadata

class TestStateNormalization(unittest.TestCase):
    def setUp(self):
        self.dt = datetime(2024, 3, 15, 18, 0, 0, tzinfo=tz.UTC)

    def _create_event(self, location, country_code="MX", state_code=""):
        ev = Event()
        ev.add("summary", "Test Event")
        ev.add("dtstart", self.dt)
        ev.add("location", location)

        event_norm = EventNormalized(ev, "https://example.com/feed.ics")
        event_norm.country_code = country_code
        event_norm.state_code = state_code
        event_norm._standardize_location()
        return event_norm

    def test_mexico_state_normalization(self):
        # Case 1: MX-Jal. (with dot and mixed case)
        ev1 = self._create_event("Guadalajara, Jalisco", state_code="MX-Jal.")
        self.assertEqual(ev1.state_code, "MX-JAL")

        # Case 2: MX-N.L. (with dots)
        ev2 = self._create_event("Monterrey, N.L.", state_code="MX-N.L.")
        self.assertEqual(ev2.state_code, "MX-NLE") # Normalized to ISO standard

        # Case 3: MX-Tlax. (abbreviated)
        ev3 = self._create_event("Tlaxcala", state_code="MX-Tlax.")
        self.assertEqual(ev3.state_code, "MX-TLA") # Normalized to ISO standard

        # Case 4: CDMX variations
        ev4 = self._create_event("Roma Norte, DF", state_code="DF")
        self.assertEqual(ev4.state_code, "MX-CMX")
        self.assertEqual(ev4.state, "Ciudad de México")

    def test_online_grouping(self):
        ev = self._create_event("Online", state_code="")
        # _standardize_location should not touch it if it is empty,
        # but group_events_by_state should categorize it as ONLINE
        self.assertEqual(ev.state_code, "")

        aggregator = ICSAggregator()
        grouped = aggregator.group_events_by_state([ev])
        self.assertIn("ONLINE", grouped)
        self.assertEqual(len(grouped["ONLINE"]), 1)

class TestGroupingLogic(unittest.TestCase):
    def test_group_by_state(self):
        aggregator = ICSAggregator()

        # Mock events
        ev1 = EventNormalized(Event(), "f1")
        ev1.state_code = "MX-CMX"

        ev2 = EventNormalized(Event(), "f2")
        ev2.state_code = "MX-JAL"

        ev3 = EventNormalized(Event(), "f3")
        ev3.state_code = "MX-CMX"

        ev4 = EventNormalized(Event(), "f4")
        ev4.state_code = "" # Online

        grouped = aggregator.group_events_by_state([ev1, ev2, ev3, ev4])

        self.assertEqual(len(grouped["MX-CMX"]), 2)
        self.assertEqual(len(grouped["MX-JAL"]), 1)
        self.assertEqual(len(grouped["ONLINE"]), 1)

if __name__ == "__main__":
    unittest.main()
