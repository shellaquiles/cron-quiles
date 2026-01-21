"""
Tests básicos para el agregador ICS.

Nota: Estos son tests básicos. Se pueden expandir con más casos de prueba.
"""

import sys
import unittest
from datetime import datetime
from pathlib import Path

from dateutil import tz
from icalendar import Event

# Agregar src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from cronquiles.ics_aggregator import (
    EventNormalized,
    ICSAggregator,
    extract_community_url,
    detect_platform_from_url,
    get_platform_label_for_community
)


class TestEventNormalized(unittest.TestCase):
    """Tests para la clase EventNormalized."""

    def test_normalize_title(self):
        """Test de normalización de títulos."""
        event = Event()
        event.add("summary", "🐍 Meetup Python - ML!")
        event.add("dtstart", datetime(2024, 3, 15, 18, 0, 0, tzinfo=tz.UTC))

        event_norm = EventNormalized(event, "https://example.com/feed.ics")

        # Debe remover emojis, convertir a lowercase, remover puntuación
        self.assertIn("meetup python", event_norm.title.lower())
        self.assertNotIn("🐍", event_norm.title)

    def test_extract_tags(self):
        """Test de extracción de tags."""
        event = Event()
        event.add("summary", "Python Meetup sobre Machine Learning")
        event.add("description", "Aprende sobre AI y TensorFlow")
        event.add("dtstart", datetime(2024, 3, 15, 18, 0, 0, tzinfo=tz.UTC))

        event_norm = EventNormalized(event, "https://example.com/feed.ics")

        # Debe detectar tags relevantes
        self.assertIn("python", event_norm.tags)
        self.assertIn("ai", event_norm.tags)

    def test_hash_key_generation(self):
        """Test de generación de hash_key para deduplicación."""
        event1 = Event()
        event1.add("summary", "Python Meetup")
        event1.add("dtstart", datetime(2024, 3, 15, 18, 30, 0, tzinfo=tz.UTC))

        event2 = Event()
        event2.add("summary", "Python Meetup")
        event2.add("dtstart", datetime(2024, 3, 15, 19, 15, 0, tzinfo=tz.UTC))

        event_norm1 = EventNormalized(event1, "https://example.com/feed1.ics")
        event_norm2 = EventNormalized(event2, "https://example.com/feed2.ics")

        # Deben tener el mismo hash_key (mismo título, misma hora redondeada)
        self.assertEqual(event_norm1.hash_key, event_norm2.hash_key)


class TestICSAggregator(unittest.TestCase):
    """Tests para la clase ICSAggregator."""

    def test_initialization(self):
        """Test de inicialización del agregador."""
        aggregator = ICSAggregator(timeout=30, max_retries=2)
        self.assertEqual(aggregator.timeout, 30)
        self.assertEqual(aggregator.max_retries, 2)

    def test_deduplicate_events(self):
        """Test de deduplicación de eventos."""
        aggregator = ICSAggregator()

        # Crear eventos similares
        events = []
        for i in range(3):
            event = Event()
            event.add("summary", "Python Meetup")
            event.add("dtstart", datetime(2024, 3, 15, 18, i * 10, 0, tzinfo=tz.UTC))
            event.add(
                "description", f"Descripción {i}" * (i + 1)
            )  # Diferentes longitudes
            if i == 1:
                event.add("url", "https://example.com/event")
            events.append(EventNormalized(event, f"https://example.com/feed{i}.ics"))

        deduplicated = aggregator.deduplicate_events(events)

        # Debe quedar solo 1 evento (el mejor)
        self.assertEqual(len(deduplicated), 1)
        # Debe ser el que tiene URL (prioridad)
        self.assertTrue(deduplicated[0].url.startswith("http"))

    def test_extract_luma_link(self):
        """Test de extracción de link de Luma desde la descripción."""
        event = Event()
        event.add("summary", "Luma Event")
        # Descripción real de Luma
        event.add(
            "description",
            "Get up-to-date information at: https://luma.com/z4d0punf\\n\\nHosted by Martin",
        )
        event.add("dtstart", datetime(2024, 3, 15, 18, 0, 0, tzinfo=tz.UTC))

        # Simulamos que no hay URL en el campo URL
        event_norm = EventNormalized(event, "https://api2.luma.com/ics/get")

        # Debería extraer el link de luma (luma.com o lu.ma)
        self.assertEqual(event_norm.url, "https://luma.com/z4d0punf")


class TestCommunityURLExtraction(unittest.TestCase):
    """Tests para las funciones de extracción de URLs de comunidades."""

    def test_extract_meetup_url(self):
        """Test de extracción de URL de Meetup desde el feed ICS."""
        result = extract_community_url("https://www.meetup.com/ai-cdmx/events/ical")
        self.assertEqual(result, "https://www.meetup.com/ai-cdmx")

        result = extract_community_url("https://www.meetup.com/python-mexico/events/ical")
        self.assertEqual(result, "https://www.meetup.com/python-mexico")

    def test_extract_luma_api_url(self):
        """Test de extracción de URL de Luma desde la API ICS."""
        result = extract_community_url("https://api2.luma.com/ics/get?entity=calendar&id=cal-gKhhS6fDDrX3mqz")
        self.assertEqual(result, "https://lu.ma/cal-gKhhS6fDDrX3mqz")

    def test_extract_luma_direct_url(self):
        """Test de URLs directas de Luma (sin transformación)."""
        result = extract_community_url("https://luma.com/ai-cdmx")
        self.assertEqual(result, "https://luma.com/ai-cdmx")

        result = extract_community_url("https://lu.ma/sudo_fciencias_2026")
        self.assertEqual(result, "https://lu.ma/sudo_fciencias_2026")

    def test_extract_eventbrite_url(self):
        """Test de URLs de Eventbrite (sin transformación)."""
        result = extract_community_url("https://www.eventbrite.com.mx/o/epam-27283356907")
        self.assertEqual(result, "https://www.eventbrite.com.mx/o/epam-27283356907")

    def test_detect_platform(self):
        """Test de detección de plataforma desde URL."""
        self.assertEqual(detect_platform_from_url("https://www.meetup.com/ai-cdmx"), "meetup")
        self.assertEqual(detect_platform_from_url("https://lu.ma/cal-123"), "luma")
        self.assertEqual(detect_platform_from_url("https://luma.com/ai-cdmx"), "luma")
        self.assertEqual(detect_platform_from_url("https://api2.luma.com/ics/get?id=123"), "luma")
        self.assertEqual(detect_platform_from_url("https://www.eventbrite.com.mx/o/123"), "eventbrite")
        self.assertEqual(detect_platform_from_url("https://other-site.com/events"), "website")

    def test_get_platform_label(self):
        """Test de etiquetas de plataforma para comunidades."""
        self.assertEqual(get_platform_label_for_community("meetup"), "Meetup")
        self.assertEqual(get_platform_label_for_community("luma"), "Luma")
        self.assertEqual(get_platform_label_for_community("eventbrite"), "Eventbrite")
        self.assertEqual(get_platform_label_for_community("website"), "Sitio web")


if __name__ == "__main__":
    unittest.main()
