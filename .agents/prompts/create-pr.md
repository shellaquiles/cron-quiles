---
name: "Crear Pull Request con Template"
description: "Prompt para generar la descripción de un PR basándose en el template oficial"
---

# Generar Descripción de Pull Request

Usa este prompt cuando estés listo para crear un Pull Request. El asistente deberá leer el template y completar la información basada en los cambios realizados.

```text
Por favor, genera la descripción para mi Pull Request basándote estrictamente en el template ubicado en `.github/PULL_REQUEST_TEMPLATE.md`.

Instrucciones para el Asistente:
1. Lee el contenido actual de `.github/PULL_REQUEST_TEMPLATE.md`.
2. Analiza los cambios realizados en la rama actual (git diff).
3. Completa cada sección del template:
   - **Descripción**: Resume los cambios técnicos y funcionales.
   - **Tipo de Cambio**: Marca con [x] las categorías que correspondan.
   - **Checklist**: Verifica qué puntos se han cumplido realmente.
   - **Cómo se ha Probado**: Detalla los comandos o tests ejecutados.
   - **Issues Relacionados**: Menciona si cierra algún issue.
4. Devuelve el contenido final listo para ser copiado en el cuerpo del PR en GitHub.
```
