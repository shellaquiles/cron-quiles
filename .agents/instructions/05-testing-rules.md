# Reglas de Testing (`/tests/`)

El repositorio cuenta con una suite de pruebas construida con `pytest`. Cualquier modificación a la lógica del pipeline debe validarse usando los comandos provistos por el Makefile.

## Comandos Principales:
- `make test`: Ejecuta toda la suite (ideal previo a un PR).
- `make test-filter FILTER="[test_name]"`: Ejecuta una prueba particular o una clase. Vital para debuggear el comportamiento del bloque de tiempo o el ruteador de la arquitectura base.

## Anatomía de los Tests:
- `test_ics_aggregator.py`: Contiene las pruebas para la lógica base del motor (el ruteo hacia Meetup/Luma/Eventbrite, la consolidación de hashes y la lógica dura de deduplicación).
- `test_dynamic_generation.py`: Se enfoca en probar que la salida de los archivos `json/ics` y la renderización en su formato final no rompa las expectativas del front-end.
- Carpeta `tests/manual/`: Scripts o entornos de pruebas experimentales que no corren en el CI pipeline.
