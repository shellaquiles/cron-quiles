Actúa como un **Senior Automation Engineer / Python Architect**.
Estás construyendo una herramienta **open source**, sin APIs privadas ni pagos, para la comunidad **Shellaquiles**.

### Contexto

* Tengo múltiples feeds **ICS públicos** de eventos tech en México (Meetup, Luma).
* No tengo acceso a APIs oficiales ni planes de pago.
* Quiero centralizarlos todos en **un solo calendario unificado**.

### Objetivo técnico

1. Consumir múltiples URLs **.ics**
2. Normalizar los eventos (título, fecha, hora, ubicación, link, organizador)
3. Deduplicar eventos similares (mismo título + fecha ± tolerancia)
4. Generar:

   * Un **ICS unificado**
   * (opcional) Un JSON para futuros usos

### Restricciones

* ❌ No usar APIs privadas
* ❌ No scraping agresivo
* ✅ Solo HTTP GET a feeds públicos
* ✅ Python 3.10+

### Requisitos técnicos

* Usar librerías estándar:

  * `requests`
  * `icalendar`
  * `python-dateutil`
* Manejar:

  * Timezones
  * Eventos recurrentes
  * Cancelaciones
* Tolerar feeds caídos sin romper el proceso

### Deduplicación

Implementa una estrategia razonable:

* Normalizar título (lowercase, sin emojis, sin puntuación)
* Comparar fecha/hora (±2 horas)
* Si coinciden → conservar uno
* Priorizar eventos con:

  1. URL válida
  2. Descripción más larga

### Output

* Archivo: `cronquiles.ics`
* (opcional) `cronquiles.json`

### Entregables

* Código funcional
* README.md claro
* Ejemplo de `feeds.yaml`

### Extras (si hay tiempo)

* Tags automáticos por keywords (Python, AI, Cloud, DevOps)
* CLI simple (`python main.py`)

### ⚠️ IMPORTANTE: Documentación y Actualización

**En cada cambio o feature nueva, DEBES:**

1. **Actualizar documentación**:
   - ✅ README.md si cambia funcionalidad, uso o estructura
   - ✅ CHANGELOG.md con los cambios realizados
   - ✅ Docstrings en el código (módulos, clases, funciones)
   - ✅ Comentarios inline donde sea necesario

2. **Actualizar archivos relacionados**:
   - ✅ `docs/PROJECT_STRUCTURE.md` si cambia la estructura
   - ✅ `CONTRIBUTING.md` si cambian procesos de desarrollo
   - ✅ Tests si agregas/modificas funcionalidad
   - ✅ `requirements.txt` si agregas dependencias

3. **Mantener consistencia**:
   - ✅ Ejemplos de código en README deben funcionar
   - ✅ Rutas y nombres de archivos actualizados
   - ✅ Badges y metadata correctos
   - ✅ Links internos funcionando

4. **Verificar antes de commit**:
   - ✅ Documentación sincronizada con código
   - ✅ No dejar referencias a archivos/estructuras antiguas
   - ✅ Ejemplos actualizados y funcionales

**Regla de oro**: Si cambias código, cambia documentación. Si cambias estructura, actualiza todos los archivos que la referencien.

Piensa paso a paso, justifica decisiones técnicas y genera código limpio, comentado y listo para producción ligera. **Nunca dejes documentación desactualizada.**
