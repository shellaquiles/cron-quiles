"""
Schemas - Definiciones de tipo para la estructura de datos.
"""

from typing import TypedDict, List, Optional


class SourceSchema(TypedDict):
    """Esquema de una fuente/plataforma de un evento."""
    platform: str  # "meetup", "luma", "eventbrite", "website"
    url: str
    label: str  # "Ver en Meetup", etc.


class EventSchema(TypedDict):
    """Esquema de un evento normalizado en el JSON de salida."""
    title: str
    description: str
    url: str  # URL principal (compatibilidad)
    sources: List[SourceSchema]  # Todas las fuentes con info de plataforma
    location: str
    organizer: str
    dtstart: Optional[str]  # ISO format
    dtend: Optional[str]    # ISO format
    tags: List[str]
    source: str
    country: str
    country_code: str
    state: str
    state_code: str
    city: str
    city_code: str
    address: str
    hash_key: str


class CommunitySchema(TypedDict):
    """Esquema de una comunidad en el metadata del JSON."""
    name: str
    description: str


class JSONOutputSchema(TypedDict):
    """Esquema del archivo JSON final generado."""
    generated_at: str
    total_events: int
    city: Optional[str]
    communities: List[CommunitySchema]
    events: List[EventSchema]
