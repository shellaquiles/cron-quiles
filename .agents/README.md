# Agentic Workspace Topology

Este directorio define la "inteligencia" y el contexto operacional para los asistentes de código de Inteligencia Artificial (Copilot, Cursor, Roo Code, Antigravity) que operen sobre el repositorio `cron-quiles`.

Basado en el estándar de arquitectura de agentes (Abril 2026), el directorio se divide estrictamente en los siguientes dominios de responsabilidad:

## 1. Instructions (`/instructions/`)
**Para directivas de contexto "always-on".**
Contiene las reglas absolutas del proyecto que el LLM debe tener siempre cargadas en memoria (system prompt). Aquí viven los lineamientos de arquitectura, convenciones de Python, formato y directrices de idioma.

## 2. Prompts (`/prompts/`)
**Para tareas nombradas de un solo uso (one-off tasks).**
Fragmentos o plantillas diseñadas para ser inyectadas en una sesión cuando se requiere la redacción de un PR, la creación de un test unitario específico o la traducción de un bloque de código bajo ciertas normas acotadas.

## 3. Skills (`/skills/`)
**Para flujos de trabajo reutilizables (reusable workflows).**
Documentación procedimental extensa que le enseña al agente cómo realizar tareas complejas compuestas por múltiples pasos. Ej: *Cómo auditar una deduplicación*, *Cómo dar de alta un nuevo agregador ICS*.

## 4. Custom Agents (`/custom_agents/`)
**Para la definición de roles y límites de herramientas.**
Manifiestos (YAML/JSON) que definen perfiles especializados. Ej: Un agente `QA_Tester` que solo tiene permisos para ejecutar `pytest` y leer código, o un agente `Data_Healer` especializado en reparar el archivo `history.json`.

## 5. MCP (`/mcp/`)
**Contexto externo en vivo (Model Context Protocol).**
Configuraciones para montar servidores MCP que permiten al LLM conectarse de forma segura a recursos locales o cloud del proyecto (por ejemplo, acceder a la base de datos de producción temporalmente, interactuar con el Slack de la comunidad, o consultar la API de Notion/Luma en tiempo real).

## 6. Hooks (`/hooks/`)
**Para la aplicación de paradas estrictas (hard stop enforcement).**
Scripts (Bash/Python) y directivas que el agente debe ejecutar obligatoriamente antes de confirmar una acción crítica (ej. correr linting riguroso antes de comitear, o solicitar aprobación humana `portal/callbacks.py` antes de sobreescribir el historial de eventos).
