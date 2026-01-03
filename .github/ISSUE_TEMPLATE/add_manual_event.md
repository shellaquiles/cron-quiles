---
name: 📝 Agregar Evento Manual
about: Sugiere un evento único que no tiene feed (Conferencias, Talleres aislados)
title: '[MANUAL] Nombre del Evento'
labels: manual-event, review-needed
assignees: ''
---

## Detalles del Evento

- **Título**: [Nombre del evento]
- **Organizador**: [Nombre de la comunidad/empresa]
- **Fecha y Hora**: [YYYY-MM-DD HH:MM] (Zona Horaria MX)
- **Ubicación**: [Dirección completa: Calle, Número, Colonia, Ciudad]
- **Link de Registro**: [URL de registro o información]

## JSON Sugerido (Opcional pero apreciado)

```json
{
    "title": "Nombre del Evento",
    "description": "Descripción breve...",
    "url": "https://link-al-evento.com",
    "location": "Dirección completa",
    "country": "México",
    "country_code": "MX",
    "city": "Ciudad",
    "city_code": "slug-ciudad",
    "state": "Estado",
    "state_code": "MX-XXX",
    "organizer": "Organizador",
    "dtstart": "2026-XX-XXT19:00:00-06:00",
    "dtend": "2026-XX-XXT21:00:00-06:00",
    "tags": ["tag1", "tag2"],
    "source": "Manual"
}
```

## Checklist
- [ ] El evento es relevante para tecnología/programación.
- [ ] No existe un feed recurrente para este organizador (si existe, usa "Agregar Nuevo Feed").
- [ ] La fecha es futura.
