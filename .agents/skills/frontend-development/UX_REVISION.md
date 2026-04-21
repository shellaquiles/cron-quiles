# Revisión UI/UX — Laws of UX (escritorio y móvil)

Revisión crítica del frontend de Cron-Quiles aplicando los principios de [Laws of UX](https://lawsofux.com/). Incluye observaciones para escritorio y móvil.

---

## 1. Aesthetic-Usability Effect

> Los usuarios perciben diseños estéticamente placenteros como más usables.

**Estado:** ✅ Bien aplicado. La estética terminal (verde sobre oscuro, JetBrains Mono) es coherente en todas las páginas y transmite identidad. Los colores WCAG (variables `--event-text-primary` a `--event-text-quaternary`) mantienen legibilidad sin romper el estilo.

**Sugerencias:**
- **Escritorio:** Mantener. El borde izquierdo verde en fichas y el gradiente sutil refuerzan la jerarquía.
- **Móvil:** En móvil las fichas pasan a borde inferior solo; la jerarquía se mantiene. Valorar dejar un pequeño acento izquierdo (ej. 3px) también en móvil para no perder la “firma” visual.

---

## 2. Ley de Similitud / Proximidad (Gestalt)

> Elementos similares o cercanos se perciben como un grupo.

**Estado:** ✅ Parcialmente bien. En la ficha de evento: fecha + hora + pill de estado están en `.event-date-first` (proximidad correcta). Título, ubicación, CTA y descripción están bien separados.

**Problemas:**
- **Nav principal:** El enlace de la página actual (`.section-nav-link.active`) no tiene estilo propio en CSS, por lo que no se distingue del resto. Rompe la “similitud con excepción” y dificulta saber “dónde estoy”.
- **Solución:** Añadir estilo para `.section-nav-link.active` (fondo/color/borde) para que la página actual sea reconocible de un vistazo.

---

## 3. Hick's Law

> El tiempo de decisión aumenta con el número y complejidad de opciones.

**Estado:** ✅ Aceptable. Solo 4 enlaces en la nav. Selector de ciudad en móvil muestra todas las ciudades con eventos (o las del mes visible), que puede ser muchas.

**Sugerencias:**
- **Escritorio:** Tabs de ciudad están bien; no añadir más opciones en la misma fila.
- **Móvil:** Si la lista de ciudades crece mucho, considerar agrupar por región o poner “Más visitadas” primero (Goal-Gradient: acercar al objetivo rápido).

---

## 4. Fitts's Law

> El tiempo para alcanzar un objetivo depende de la distancia y del tamaño del objetivo.

**Estado:** ✅ En general bien. Botones de calendario (←, →, Hoy) y `.section-nav-link` tienen `min-height: 44px`. `.city-tab` y `.event-source-btn` también.

**Problemas:**
- **Lang switcher (ES | EN):** En `components.css`, `.lang-btn` tiene `padding: 4px 12px` y no tiene `min-height` ni `min-width`. En móvil pueden quedar por debajo de 44px de área táctil.
- **Solución:** Aumentar área táctil del lang switcher en móvil (min 44px) o al menos en altura.

---

## 5. Jakob's Law

> Los usuarios esperan que el sitio funcione como otros que ya conocen.

**Estado:** ✅ Bien. Calendario mensual con flechas y “Hoy” es un patrón conocido. Nav horizontal, footer con enlaces, botones “Ver en Meetup”/“Ver en mapa” son reconocibles. Selector de ciudad en móvil como `<select>` es estándar.

**Sugerencias:**
- Mantener “Hoy” visible en el header del calendario (ya está).
- No cambiar el orden lógico: fecha → título → ubicación → CTA.

---

## 6. Doherty Threshold

> La productividad aumenta cuando la respuesta del sistema está por debajo de ~400 ms.

**Estado:** ✅ Aceptable. Cambios de ciudad y de mes son síncronos (re-render inmediato). Scroll al día al hacer clic en la celda usa `behavior: 'smooth'` (sensación fluida). No hay llamadas lentas bloqueantes en la UI.

**Sugerencias:**
- Mantener el estado de carga (“Cargando calendario…”) mientras llegan datos.
- Evitar animaciones largas en transiciones de contenido.

---

## 7. Chunking

> La información se entiende mejor en bloques significativos.

**Estado:** ✅ Bien aplicado. Ficha de evento: (1) fecha/hora/estado, (2) grupo/organizador, (3) título, (4) ubicación + mapa, (5) CTA, (6) descripción colapsable, (7) tags. Cada bloque tiene una función clara. Lista de eventos agrupada por día (`.calendar-day-events`) con título “Lun 15” mejora el escaneo.

**Móvil:** Mismo chunking; el orden se mantiene. Correcto.

---

## 8. Serial Position Effect (primacía/recencia)

> Lo primero y lo último se recuerda mejor.

**Estado:** ✅ Aplicado. La fecha/hora y el estado (incl. “en línea”) están al inicio de la ficha. El CTA principal (“Ver en Meetup”/etc.) está en posición destacada antes de la descripción larga. Los tags al final cierran el bloque. Bien.

---

## 9. Ley de Prägnanz (simplicidad)

> Las personas interpretan las formas de la manera más simple posible.

**Estado:** ✅ Bueno. Sin elementos decorativos innecesarios. Una sola línea de fecha corta (pill), una sola ubicación, sin repetición de “en línea”. Descripción colapsable reduce ruido.

**Sugerencias:**
- Evitar añadir más bordes o líneas dentro de la ficha.
- En móvil, el cambio de ficha “con borde” a “solo borde inferior” simplifica; coherente con Prägnanz.

---

## 10. Ley de la Región Común

> Los elementos dentro de un límite (borde, fondo) se perciben como grupo.

**Estado:** ✅ Correcto. Cada ficha (`.calendar-month-event`) tiene borde y fondo; el calendario (`.calendar-container`) está en una caja; la nav tiene fondo y borde inferior. Las secciones “Por día” (`.calendar-day-events`) tienen título y borde inferior.

---

## 11. Accesibilidad y focus

> Teclado y lectores de pantalla deben poder usar la interfaz.

**Estado:** ⚠️ Mejorable. Hay `:focus` en `.section-nav-link` y en enlaces/toggle de la ficha. No en todos los controles se usa `:focus-visible` para no mostrar anillo en clic (solo en teclado).

**Sugerencias:**
- Usar `:focus-visible` en nav, tabs, botones del calendario y lang switcher, con `outline` claro (2px verde) para no depender solo de `:focus`.
- Asegurar que el orden de tab sea lógico: header → nav → selector ciudad → contenido → footer.

---

## 12. Resumen por vista

### Escritorio
- **Fortalezas:** Jerarquía clara, chunking correcto, targets grandes en nav y calendario, estética consistente.
- **Mejoras:** (1) Estilo visible para “página actual” en la nav. (2) Revisar `:focus-visible` en todos los interactivos.

### Móvil
- **Fortalezas:** Calendario en una fila (← mes → Hoy), grid a ancho completo, celdas y botones con 44px, selector de ciudad con etiqueta, fichas edge-to-edge legibles.
- **Mejoras:** (1) Área táctil del lang switcher (ES/EN) ≥ 44px. (2) Mismo estilo de “página actual” en nav (scroll horizontal). (3) Evitar que el nav tape el título de la sección al hacer scroll a ancla (`scroll-margin-top` ya está; verificar valor).

---

## Cambios recomendados (prioridad)

1. **Alta:** Añadir estilo para `.section-nav-link.active` (Ley de Similitud, Jakob).
2. **Alta:** Aumentar área táctil del lang switcher en móvil (Fitts).
3. **Media:** Usar `:focus-visible` en nav, tabs, calendario y lang (accesibilidad).
4. **Baja:** Valorar un pequeño acento izquierdo en la ficha en móvil (Aesthetic-Usability, opcional).

Este documento sirve como referencia para futuras iteraciones de diseño y para validar decisiones con Laws of UX.
