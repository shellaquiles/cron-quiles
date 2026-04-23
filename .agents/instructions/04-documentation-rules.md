# Reglas de Documentación

Todo Pull Request o modificación hecha por humanos o Agentes en `cron-quiles` debe acatar las siguientes validaciones:

1. **CHANGELOG.md**:
   Toda funcionalidad nueva, script, o fix importante al pipeline de agregación DEBE reflejarse en el `CHANGELOG.md` bajo la versión que corresponda.

2. **COMMUNITIES.md**:
   Si se da de alta un nuevo canal en `config/feeds.yaml`, es **obligatorio** documentarlo en `docs/COMMUNITIES.md` para que los contribuyentes y la documentación pública se mantengan sincronizados.

3. **FLUJO.md**:
   Cualquier cambio a la arquitectura de agregación, al layout final de la salida en `/data/` o al flujo del Github Action, requiere una actualización inmediata a `docs/FLUJO.md`. Esta es la fuente de la verdad para el despliegue.

4. Archivos generados:
   Bajo ningún motivo debes comitear el resultado de `/data/` (especialmente `cronquiles-mexico.ics` o `.json`) dentro de un PR. Estas salidas son administradas y comiteadas exclusivamente por el pipeline de GitHub Actions en la rama de despliegue.

5. **Pull Requests**:
   Cada vez que se cree un Pull Request (PR), es **obligatorio** utilizar el template ubicado en `.github/PULL_REQUEST_TEMPLATE.md`. El Agente debe leer este archivo y completar todas las secciones correspondientes (Descripción, Tipo de Cambio, Checklist, etc.) para asegurar la consistencia y calidad de la documentación del cambio.
