import json
import logging
import os
from typing import Dict, List

from .models import EventNormalized

logger = logging.getLogger(__name__)


class HistoryManager:
    """
    Gestor de persistencia de eventos históricos.
    Mantiene una base de datos JSON local para preservar eventos pasados.
    """

    def __init__(self, history_file: str = "data/history.json"):
        self.history_file = history_file
        self.events: Dict[str, dict] = {}  # Key: hash_key, Value: Event dict
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Asegura que el directorio de datos existe."""
        dirname = os.path.dirname(self.history_file)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

    def load_history(self):
        """Carga la historia desde el archivo JSON."""
        if not os.path.exists(self.history_file):
            logger.info(f"No existing history file found at {self.history_file}")
            return

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            loaded_count = 0
            for item in data:
                # Usar from_dict para disparar la lógica de healing/standardization
                instance = EventNormalized.from_dict(item)
                item_healed = instance.to_dict()

                # Usar hash_key si existe, sino reconstruir como antes
                key = (
                    item_healed.get("hash_key")
                    or f"{item_healed['title']}_{item_healed['dtstart']}"
                )
                self.events[key] = item_healed
                loaded_count += 1

            logger.info(
                f"Loaded {loaded_count} historical events from {self.history_file}"
            )

        except Exception as e:
            logger.error(f"Error loading history: {e}")

    def save_history(self):
        """Guarda el estado actual en el archivo JSON."""
        try:
            # Convertir a lista y ordenar por fecha (descendiente, mas recientes primero)
            events_list = list(self.events.values())
            events_list.sort(key=lambda x: x.get("dtstart") or "", reverse=True)

            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(events_list, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {len(events_list)} events to history file")

        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def merge_events(self, new_events: List[EventNormalized]):
        """
        Fusiona nuevos eventos con la historia existente.

        Args:
            new_events: Lista de objetos EventNormalized recolectados recientemente.
        """
        new_count = 0
        update_count = 0

        for event in new_events:
            event_dict = event.to_dict()
            # Usar hash_key para merge consistente
            key = event_dict.get("hash_key")
            if not key:
                key = f"{event_dict['title']}_{event_dict['dtstart']}"

            if key not in self.events:
                self.events[key] = event_dict
                new_count += 1
            else:
                # Merge inteligente: Preservar datos de mayor calidad
                existing_event = self.events[key]
                merged_event = event_dict.copy()

                # Regla 1: Preservar ubicación si es más detallada en historia
                # (Asumimos que más largo = más detalle, ej: "Wizeline, Calle..." vs "Wizeline")
                old_loc = existing_event.get("location", "")
                new_loc = merged_event.get("location", "")
                if old_loc and len(old_loc) > len(new_loc):
                    merged_event["location"] = old_loc

                # Regla 2: Preservar descripción si la nueva está vacía
                if not merged_event.get("description") and existing_event.get(
                    "description"
                ):
                    merged_event["description"] = existing_event.get("description")

                self.events[key] = merged_event
                update_count += 1

        logger.info(
            f"Merged history: {new_count} new, {update_count} updated. Total: {len(self.events)}"
        )

    def get_all_events(self) -> List[dict]:
        """Retorna todos los eventos ordenados por fecha."""
        events = list(self.events.values())
        events.sort(key=lambda x: x.get("dtstart") or "", reverse=True)
        return events
