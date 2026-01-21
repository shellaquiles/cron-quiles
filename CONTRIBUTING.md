# Contribuyendo a Cron-Quiles

¡Gracias por tu interés en contribuir! 🐢

Este documento proporciona guías y estándares para contribuir al proyecto.

## Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor:

1. Verifica que no haya un issue existente sobre el mismo problema
2. Crea un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducirlo
   - Comportamiento esperado vs actual
   - Versión de Python y sistema operativo

### Sugerir Mejoras

Las sugerencias son bienvenidas:

1. Abre un issue con la etiqueta `enhancement`
2. Describe la mejora propuesta y por qué sería útil
3. Si es posible, incluye ejemplos de cómo funcionaría

### Contribuir Código

#### Setup Inicial

```bash
# Fork y clonar
git clone https://github.com/TU-USUARIO/cron-quiles.git
cd cron-quiles

# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependencias
make install-dev

# Verificar
make test
make check
```

#### Implementar cambios

1. **Fork el repositorio**

2. **Crea una rama para tu feature**:
   ```bash
   git checkout -b feature/mi-nueva-feature
   ```

3. **Haz tus cambios**:
   - Sigue el estilo de código existente
   - Agrega comentarios cuando sea necesario
   - Actualiza la documentación si es relevante

4. **Prueba tus cambios**:
   ```bash
   make run-all
   # O ejecuta los tests:
   make test
   ```

5. **Commit tus cambios**:
   ```bash
   git commit -m "feat: agregar nueva funcionalidad"
   ```

   Usa mensajes de commit descriptivos siguiendo [Conventional Commits](https://www.conventionalcommits.org/) **en español**:

   **Formato**: `tipo(ámbito): descripción`

   **Tipos de commit**:
   - `feat:` para nuevas funcionalidades
   - `fix:` para correcciones de bugs
   - `docs:` para cambios en documentación
   - `style:` para cambios de formato (espacios, comas, etc.)
   - `refactor:` para refactorización de código sin cambiar funcionalidad
   - `perf:` para mejoras de rendimiento
   - `test:` para agregar o modificar tests
   - `chore:` para tareas de mantenimiento (dependencias, config, etc.)
   - `ci:` para cambios en CI/CD
   - `build:` para cambios en el sistema de build
   - `revert:` para revertir un commit anterior

   **Ejemplos**:
   ```bash
   git commit -m "feat(calendario): agregar soporte para Google Calendar"
   git commit -m "fix(ics): corregir parsing de eventos recurrentes"
   git commit -m "docs(readme): actualizar instrucciones de instalación"
   git commit -m "refactor(aggregator): simplificar lógica de deduplicación"
   git commit -m "test(ics_aggregator): agregar tests para eventos duplicados"
   git commit -m "chore(deps): actualizar dependencias a última versión"
   ```

   **Reglas importantes**:
   - Usa español en la descripción
   - La descripción debe estar en minúsculas (excepto nombres propios)
   - No termines la descripción con punto
   - El ámbito es opcional pero recomendado
   - Para commits que rompen compatibilidad, agrega `!` después del tipo: `feat!: cambio que rompe compatibilidad`

6. **Push a tu fork**:
   ```bash
   git push origin feature/mi-nueva-feature
   ```

7. **Abre un Pull Request**:
   - Describe claramente qué cambios hiciste y por qué
   - Menciona cualquier issue relacionado
   - Espera feedback y está abierto a sugerencias

## Estándares de Código

- **Python 3.10+**: Asegúrate de que tu código sea compatible
- **PEP 8**: Sigue las convenciones de estilo de Python
- **Docstrings**: Documenta funciones y clases importantes
- **Type hints**: Úsalos cuando sea apropiado
- **Manejo de errores**: Maneja errores gracefully, no rompas el proceso completo

## Áreas donde Necesitamos Ayuda

- 🌐 Agregar más feeds ICS de eventos tech en México
- 🏷️ Mejorar la detección de tags automáticos
- 🔍 Mejorar la estrategia de deduplicación
- 📅 Mejor manejo de eventos recurrentes
- 🧪 Agregar tests automatizados
- 📚 Mejorar documentación
- 🌍 Soporte para más idiomas/regiones

## Preguntas?

Si tienes preguntas, abre un issue con la etiqueta `question` o contacta a los mantenedores.

¡Gracias por contribuir a la comunidad Shellaquiles! 🐢
