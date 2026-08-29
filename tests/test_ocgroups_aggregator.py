import unittest
from unittest.mock import MagicMock
from cronquiles.aggregators.ocgroups import OCGroupsAggregator


SAMPLE_GROUP_HTML = """
<!DOCTYPE html>
<html>
<head><title>Cloud Native Mexico City</title></head>
<body>
  <h1>Cloud Native Mexico City</h1>
  <article>
    <a href="/cncf/group/e5vgp72/event/q6858bh">
      <div class="card-title">Cloud Native CDMX - Beyond Tool Sprawl</div>
    </a>
  </article>
  <article>
    <a href="/cncf/group/e5vgp72/event/qc4rwuk">
      <div class="card-title">Cloud Native CDMX - Workshop</div>
    </a>
  </article>
</body>
</html>
"""

SAMPLE_EVENT_ONLINE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Event 1</title></head>
<body>
  <h1>Cloud Native CDMX - Beyond Tool Sprawl</h1>
  <span class="custom-badge">virtual</span>
  <div id="attendance-container-main" data-attendance-container data-starts="2026-09-17T18:00:00+00:00"></div>
  <div data-registration-window-date-panel>
    <div>September 17, 2026</div>
    <div>12:00 PM - 02:00 PM CST</div>
  </div>
  <div class="markdown">Descripción del evento online.</div>
</body>
</html>
"""

SAMPLE_EVENT_INPERSON_HTML = """
<!DOCTYPE html>
<html>
<head><title>Event 2</title></head>
<body>
  <h1>Cloud Native CDMX - Workshop</h1>
  <div id="attendance-container-main" data-attendance-container data-starts="2026-10-28T22:00:00+00:00"></div>
  <div data-registration-window-date-panel>
    <div>October 28, 2026</div>
    <div>04:00 PM - 08:00 PM CST</div>
  </div>
  <div class="border">
    <div>Location</div>
    <div class="rounded-full bg-white/80">Montes Urales 445, Mexico City</div>
  </div>
  <div class="markdown">Descripción del workshop presencial.</div>
</body>
</html>
"""


class TestOCGroupsAggregator(unittest.TestCase):
    def test_extract_mocked_group(self):
        mock_session = MagicMock()

        def side_effect(url, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            if "group/e5vgp72" in url and "event" not in url:
                mock_resp.text = SAMPLE_GROUP_HTML
            elif "q6858bh" in url:
                mock_resp.text = SAMPLE_EVENT_ONLINE_HTML
            elif "qc4rwuk" in url:
                mock_resp.text = SAMPLE_EVENT_INPERSON_HTML
            else:
                mock_resp.status_code = 404
                mock_resp.text = "Not found"
            return mock_resp

        mock_session.get.side_effect = side_effect

        aggregator = OCGroupsAggregator(session=mock_session)
        events = aggregator.extract(
            "https://ocgroups.dev/cncf/group/e5vgp72", "Cloud Native Mexico City"
        )

        self.assertEqual(len(events), 2)

        # Evento 1 (Online)
        ev1 = next(e for e in events if "beyond tool sprawl" in e.title.lower())
        self.assertEqual(ev1.location, "Online")
        self.assertTrue(ev1._is_online())
        self.assertEqual(ev1.organizer, "Cloud Native Mexico City")

        # Evento 2 (Presencial)
        ev2 = next(e for e in events if "workshop" in e.title.lower())
        self.assertEqual(ev2.location, "Montes Urales 445, Mexico City")
        self.assertEqual(ev2.organizer, "Cloud Native Mexico City")


if __name__ == "__main__":
    unittest.main()
