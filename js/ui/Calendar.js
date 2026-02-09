/**
 * Componente Calendario Complejo
 * Maneja la visualización de la cuadrícula, eventos y navegación.
 */
import { i18n } from '../core/I18n.js';
import { appStore } from '../core/Store.js';
import { DateUtils } from '../utils/dates.js';
import { DOM } from '../utils/dom.js';

/**
 * Adds utm_source=cron-quiles to a URL for tracking outgoing links.
 * @param {string} url - The original URL
 * @returns {string} - URL with utm_source parameter added
 */
function addUtmSource(url) {
    if (!url) return url;
    try {
        const urlObj = new URL(url);
        urlObj.searchParams.set('utm_source', 'cron-quiles');
        return urlObj.toString();
    } catch {
        return url;
    }
}

export class Calendar {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        // Local state removed, using appStore
        this.currentDate = new Date(); // Initialize for local use, but sync with store

        // Initialize store with current view
        appStore.set('viewDate', this.currentDate);

        // Subscribe to global state changes
        appStore.subscribe('showPastEvents', () => {
            this.render();
        });
    }

    setEvents(events) {
        this.events = events || [];
        this.render();
    }

    /**
     * Cambia el mes visualizado
     * @param {number} direction -1 o 1
     */
    changeMonth(direction) {
        this.currentDate.setMonth(this.currentDate.getMonth() + direction);
        appStore.set('viewDate', new Date(this.currentDate)); // Update global view date (cloned)
        this.render();
    }



    /**
     * Get events filtered by current policy
     */
    getFilteredEvents() {
        const showPastEvents = appStore.get('showPastEvents');

        if (showPastEvents) {
            return this.events;
        }

        // Retornar solo eventos de hoy en adelante
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        return this.events.filter(e => {
            if (!e.dtstart) return false;
            return new Date(e.dtstart) >= today;
        });
    }

    render() {
        if (!this.container) return;
        DOM.clear(this.container);

        if (this.events.length === 0 && !this.hasLoadedOnce) {
            this.container.innerHTML = `<div class="events-empty">${i18n.t('calendar.empty')}</div>`;
            return;
        }
        this.hasLoadedOnce = true;

        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const monthNames = i18n.t('months');
        const dayNames = i18n.t('days');

        // ==== Header del Calendario ====
        const header = DOM.create('div', { className: 'calendar-header' });

        const prevBtn = DOM.create('button', {
            className: 'calendar-nav calendar-nav-prev',
            attributes: { 'aria-label': i18n.t('cal.prev') }
        });
        prevBtn.innerHTML = '<span class="calendar-nav-icon" aria-hidden="true">←</span><span class="calendar-nav-text">' + i18n.t('cal.prev') + '</span>';
        prevBtn.addEventListener('click', () => this.changeMonth(-1));

        const nextBtn = DOM.create('button', {
            className: 'calendar-nav calendar-nav-next',
            attributes: { 'aria-label': i18n.t('cal.next') }
        });
        nextBtn.innerHTML = '<span class="calendar-nav-icon" aria-hidden="true">→</span><span class="calendar-nav-text">' + i18n.t('cal.next') + '</span>';
        nextBtn.addEventListener('click', () => this.changeMonth(1));

        const todayBtn = DOM.create('button', { className: 'calendar-nav calendar-nav-today', text: i18n.t('cal.today') });
        todayBtn.addEventListener('click', () => {
            this.currentDate = new Date();
            appStore.set('viewDate', new Date(this.currentDate));
            this.render();
        });

        const title = DOM.create('div', { className: 'calendar-title', text: `${monthNames[month]} ${year}` });

        header.append(prevBtn, nextBtn, title, todayBtn);
        this.container.appendChild(header);




        // ==== Grid del Calendario ====
        const grid = DOM.create('div', { className: 'calendar-grid' });

        // Cabeceras de días
        dayNames.forEach(day => {
            grid.appendChild(DOM.create('div', { className: 'calendar-day-header', text: day }));
        });

        // Lógica de días
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDayOfWeek = firstDay.getDay();

        // Días previos (mes anterior)
        for (let i = 0; i < startingDayOfWeek; i++) {
            const d = new Date(year, month, -startingDayOfWeek + i + 1);
            grid.appendChild(DOM.create('div', {
                className: 'calendar-day other-month',
                text: d.getDate().toString()
            }));
        }

        // Días actuales (clicables: desplazar a la lista del día)
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            date.setHours(0, 0, 0, 0);

            const dayEvents = this.getEventsForDate(date);
            let className = 'calendar-day';

            if (date.getTime() === today.getTime()) className += ' today';
            if (dayEvents.length > 0) className += ' has-events';

            const dayKey = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const dayCell = DOM.create('div', {
                className,
                text: day.toString(),
                attributes: { 'data-date': dayKey }
            });
            dayCell.addEventListener('click', () => this.scrollToDay(dayKey));
            grid.appendChild(dayCell);
        }

        // Días siguientes (relleno)
        const totalSlots = 42; // 6 filas de 7
        const filledSlots = startingDayOfWeek + daysInMonth;
        for (let i = 1; i <= (totalSlots - filledSlots); i++) {
            grid.appendChild(DOM.create('div', {
                className: 'calendar-day other-month',
                text: i.toString()
            }));
        }

        this.container.appendChild(grid);

        // ==== Lista de Eventos ====
        this.renderEventList(year, month);

        // CTA: Llévate este calendario (multipágina → suscribir.html, single-page → #descargar)
        const ctaWrap = DOM.create('div', { className: 'calendar-take-cta-wrap' });
        const ctaHref = (window.location.pathname || '').includes('eventos') ? 'suscribir.html' : '#descargar';
        const cta = DOM.create('a', {
            className: 'calendar-take-cta btn btn-secondary',
            text: i18n.t('cal.takeCalendar'),
            attributes: { href: ctaHref }
        });
        ctaWrap.appendChild(cta);
        this.container.appendChild(ctaWrap);
    }

    renderEventList(year, month) {
        const eventsListContainer = DOM.create('div', { className: 'calendar-events-list', id: 'calendar-events-list' });

        // Rastrear el último mes cargado para "cargar más"
        this.lastLoadedYear = year;
        this.lastLoadedMonth = month;

        this.appendMonthEvents(eventsListContainer, year, month);

        this.container.appendChild(eventsListContainer);
    }

    /**
     * Agrega los eventos de un mes al contenedor y un botón para cargar el siguiente mes.
     */
    appendMonthEvents(container, year, month) {
        const relevantEvents = this.getFilteredEvents();

        const monthEvents = relevantEvents.filter(e => {
            if (!e.dtstart) return false;
            const d = new Date(e.dtstart);
            return d.getFullYear() === year && d.getMonth() === month;
        }).sort((a, b) => new Date(a.dtstart) - new Date(b.dtstart));

        const monthNames = i18n.t('months');
        const titleText = `${i18n.t('cal.eventsOf')} ${monthNames[month]} ${year}`;
        container.appendChild(DOM.create('h3', { text: titleText }));

        if (monthEvents.length > 0) {
            // Agrupar por día para anclas de scroll (clic en el calendario)
            const byDay = {};
            monthEvents.forEach(event => {
                const d = new Date(event.dtstart);
                const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
                if (!byDay[key]) byDay[key] = [];
                byDay[key].push(event);
            });

            const dayNamesShort = i18n.t('days');
            Object.keys(byDay).sort().forEach(dayKey => {
                const [y, m, day] = dayKey.split('-').map(Number);
                const date = new Date(y, m - 1, day);
                const dayName = dayNamesShort[date.getDay()];
                const section = DOM.create('div', {
                    className: 'calendar-day-events',
                    attributes: { id: `day-${dayKey}` }
                });
                const heading = DOM.create('h4', {
                    className: 'calendar-day-events-title',
                    text: `${dayName} ${day}`
                });
                section.appendChild(heading);
                const listWrapper = DOM.create('div', { className: 'calendar-month-events' });
                byDay[dayKey].forEach(event => listWrapper.appendChild(this.createEventCard(event)));
                section.appendChild(listWrapper);
                container.appendChild(section);
            });
        } else {
            container.appendChild(DOM.create('p', {
                text: i18n.t('calendar.noEvents'),
                attributes: { style: 'color: var(--terminal-gray); margin-bottom: var(--spacing-lg);' }
            }));
        }

        // Verificar si hay eventos en meses posteriores
        const nextMonthStart = new Date(year, month + 1, 1);
        const hasMoreEvents = relevantEvents.some(e => {
            if (!e.dtstart) return false;
            return new Date(e.dtstart) >= nextMonthStart;
        });

        // Remover botón anterior si existe
        const oldBtn = container.querySelector('.load-more-btn');
        if (oldBtn) oldBtn.remove();

        if (hasMoreEvents) {
            const loadMoreBtn = DOM.create('button', {
                className: 'load-more-btn',
                text: i18n.t('cal.loadMore') || 'Cargar siguiente mes ▼'
            });
            loadMoreBtn.addEventListener('click', () => {
                loadMoreBtn.remove();
                // Avanzar al siguiente mes
                const nextDate = new Date(this.lastLoadedYear, this.lastLoadedMonth + 1, 1);
                this.lastLoadedYear = nextDate.getFullYear();
                this.lastLoadedMonth = nextDate.getMonth();
                this.appendMonthEvents(container, this.lastLoadedYear, this.lastLoadedMonth);
            });
            container.appendChild(loadMoreBtn);
        }
    }

    /**
     * Desplaza la vista hacia la sección del día en la lista de eventos.
     * @param {string} dayKey - Formato YYYY-MM-DD
     */
    scrollToDay(dayKey) {
        const el = document.getElementById(`day-${dayKey}`);
        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            el.classList.add('calendar-day-events-highlight');
            setTimeout(() => el.classList.remove('calendar-day-events-highlight'), 2000);
        }
    }

    /**
     * Get next N events after the specified month
     */
    getUpcomingEvents(currentYear, currentMonth, limit) {
        // Create a date for the start of next month
        const nextMonthStart = new Date(currentYear, currentMonth + 1, 1);

        return this.events
            .filter(e => {
                if (!e.dtstart) return false;
                const d = new Date(e.dtstart);
                return d >= nextMonthStart;
            })
            .sort((a, b) => new Date(a.dtstart) - new Date(b.dtstart))
            .slice(0, limit);
    }

    /**
     * Etiqueta corta de estado/ubicación para filtro visual al hacer scroll (ej. CDMX, Jal, En línea).
     */
    getPlaceLabel(event) {
        if (this.isEventOnline(event)) return i18n.t('cal.online');
        const code = (event.state_code || '').replace(/^MX-/, '').toUpperCase();
        if (code === 'CMX') return 'CDMX';
        if (code === 'JAL') return 'Jal';
        if (code === 'NLE') return 'NL';
        if (code === 'PUE') return 'Pue';
        if (code === 'QRO') return 'Qro';
        if (code === 'YUC') return 'Yuc';
        if (code === 'AGS') return 'Ags';
        if (code.length >= 2) return code.charAt(0) + code.slice(1).toLowerCase();
        if (event.city) return event.city.trim().split(',')[0];
        if (event.state) return event.state.trim().split(',')[0];
        return '';
    }

    /**
     * Detecta si el evento es online (URL como ubicación o flag del backend).
     */
    isEventOnline(event) {
        if (event.online === true) return true;
        const loc = (event.location || '').trim();
        if (!loc) return false;
        if (loc.toLowerCase().startsWith('http://') || loc.toLowerCase().startsWith('https://')) return true;
        const lower = loc.toLowerCase();
        if (lower === 'online' || lower === 'virtual' || lower === 'en línea') return true;
        if (lower.includes('luma.com') || lower.includes('meetup.com') || lower.includes('zoom')) return true;
        return false;
    }

    /**
     * URL de Google Maps para buscar la dirección (abre en nueva pestaña).
     */
    getMapsUrl(location) {
        if (!location || typeof location !== 'string') return '#';
        const query = location.split('\n')[0].trim().replace(/\s+/g, ' ');
        return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
    }

    /**
     * Acorta la ubicación para mostrar en una línea (evita bloques repetidos).
     */
    shortenLocation(location, maxLen = 90) {
        if (!location || typeof location !== 'string') return '';
        const firstLine = location.split('\n')[0].trim();
        if (firstLine.length <= maxLen) return firstLine;
        return firstLine.slice(0, maxLen - 1).trim() + '…';
    }

    createEventCard(event) {
        const dateStr = DateUtils.formatDate(event.dtstart);
        const startStr = DateUtils.formatTime(event.dtstart);
        const endStr = DateUtils.formatTime(event.dtend);
        const timeStr = (startStr && endStr && startStr !== endStr) ? `${startStr} - ${endStr}` : startStr;

        const rawTitle = event.title || event.summary || 'Evento sin título';
        let categoryLabel = null;
        let displayName = rawTitle;

        if (rawTitle.includes('|')) {
            const parts = rawTitle.split('|').map(p => p.trim());
            if (parts.length >= 2) {
                categoryLabel = parts[0];
                displayName = parts[1];
            }
        }

        // Título: solo nombre del evento (sin duplicar ubicación en el título)
        const titleContainer = DOM.create('div', { className: 'calendar-month-event-title' });
        if (event.url) {
            const link = DOM.create('a', {
                attributes: { href: addUtmSource(event.url), target: '_blank', rel: 'noopener' },
                text: displayName
            });
            titleContainer.appendChild(link);
        } else {
            titleContainer.textContent = displayName;
        }

        // Ubicación: solo para presenciales (dirección + "Ver en mapa"). Online: "en línea" solo en la pill de estado.
        const isOnline = this.isEventOnline(event);
        const locationText = isOnline
            ? ''
            : (event.location ? this.shortenLocation(event.location) : (rawTitle.includes('|') ? rawTitle.split('|').slice(2).join(' | ').trim() : ''));
        let locationNode = null;
        if (locationText) {
            locationNode = DOM.create('div', { className: 'calendar-month-event-location' });
            const locationRow = DOM.create('div', { className: 'event-location-row' });
            const locationSpan = DOM.create('span', { className: 'event-location-text', text: locationText });
            locationRow.appendChild(locationSpan);
            locationNode.appendChild(locationRow);
            if (event.location) {
                const mapsUrl = this.getMapsUrl(event.location);
                const mapLink = DOM.create('a', {
                    className: 'event-map-link',
                    text: i18n.t('cal.viewOnMap'),
                    attributes: {
                        href: mapsUrl,
                        target: '_blank',
                        rel: 'noopener',
                        'data-i18n': 'cal.viewOnMap'
                    }
                });
                locationNode.appendChild(mapLink);
            }
        }

        // Descripción (sin repetir Address ni Hosted by si ya los mostramos)
        const descNode = this.createDescriptionNode(event.description, event.location, categoryLabel);

        // Tags
        let tagsNode = null;
        if (event.tags && event.tags.length) {
            tagsNode = DOM.create('div', { className: 'calendar-month-event-tags' });
            event.tags.forEach(tag => {
                tagsNode.appendChild(DOM.create('span', { className: 'calendar-month-event-tag', text: tag }));
            });
        }

        const card = DOM.create('div', { className: 'calendar-month-event' });

        // 1. Fecha + estado a primer vista (filtros visuales al hacer scroll)
        const shortDate = DateUtils.formatShortDate(event.dtstart);
        const placeLabel = this.getPlaceLabel(event);
        const dateFirstBlock = DOM.create('div', { className: 'event-date-first' });
        dateFirstBlock.appendChild(DOM.create('span', { className: 'event-date-pill', text: shortDate }));
        if (timeStr) {
            dateFirstBlock.appendChild(DOM.create('span', { className: 'event-time-pill', text: timeStr }));
        }
        if (placeLabel) {
            const placePill = DOM.create('span', {
                className: 'event-place-pill',
                text: placeLabel,
                attributes: placeLabel === i18n.t('cal.online') ? { 'data-i18n': 'cal.online' } : {}
            });
            dateFirstBlock.appendChild(placePill);
        }
        card.appendChild(dateFirstBlock);

        // 2. Badge de categoría (si existe)
        if (categoryLabel) {
            const badge = DOM.create('div', { className: 'event-title-group', text: categoryLabel });
            card.appendChild(badge);
        }

        // 3. Título (nombre del evento)
        card.appendChild(titleContainer);

        // 4. Ubicación (una línea; sin repetir en descripción)
        if (locationNode) card.appendChild(locationNode);

        // 5. CTA: Ver en Luma / Meetup / etc.
        if (event.sources && event.sources.length > 0) {
            const sourcesContainer = DOM.create('div', { className: 'event-sources' });
            event.sources.forEach(source => {
                const btn = DOM.create('a', {
                    className: `event-source-btn event-source-${source.platform}`,
                    text: source.label,
                    attributes: {
                        href: addUtmSource(source.url),
                        target: '_blank',
                        rel: 'noopener'
                    }
                });
                sourcesContainer.appendChild(btn);
            });
            card.appendChild(sourcesContainer);
        } else if (event.url) {
            const fallbackLink = DOM.create('a', {
                className: 'event-source-btn event-source-website',
                text: i18n.t('cal.viewEvent'),
                attributes: { href: addUtmSource(event.url), target: '_blank', rel: 'noopener' }
            });
            card.appendChild(fallbackLink);
        }

        // 6. Descripción (colapsable; sin Address ni Hosted by repetidos)
        if (descNode) card.appendChild(descNode);

        // 7. Tags
        if (tagsNode) card.appendChild(tagsNode);

        return card;
    }

    createDescriptionNode(rawDesc, eventLocation, categoryLabel) {
        if (!rawDesc) return null;

        // Limpieza de descripción
        let lines = rawDesc.split('\n');
        const processed = lines.length > 1 ? lines.slice(1).map(l => l.trim()).join('\n') : rawDesc;
        let clean = processed.replace(/(\n\s*){3,}/g, '\n\n').trim();

        // Quitar bloque "Address:" cuando ya mostramos ubicación arriba (evitar redundancia)
        if (eventLocation && clean.includes('Address:')) {
            const addrIdx = clean.indexOf('Address:');
            const afterAddr = clean.slice(addrIdx + 'Address:'.length).trim();
            const addrBlockEnd = afterAddr.indexOf('\n\n') >= 0 ? afterAddr.indexOf('\n\n') : afterAddr.length;
            clean = (clean.slice(0, addrIdx).trim() + (afterAddr.slice(addrBlockEnd).trim() ? '\n\n' + afterAddr.slice(addrBlockEnd).trim() : '')).replace(/(\n\s*){3,}/g, '\n\n').trim();
        }

        // Quitar "Hosted by X" / "Organizado por X" cuando ya mostramos organizador en el badge
        if (categoryLabel && clean) {
            clean = clean
                .replace(/Hosted by\s+[^\n]+/gi, '')
                .replace(/Organizado por\s+[^\n]+/gi, '')
                .replace(/(\n\s*){3,}/g, '\n\n')
                .trim();
        }

        // Reducir redundancia bilingüe: dos líneas seguidas mismo mensaje (ej. idioma del evento)
        const locale = (i18n.getLocale() || '').toLowerCase();
        const preferEs = locale.startsWith('es');
        const descLines = clean.split('\n').map(l => l.trim()).filter(Boolean);
        if (descLines.length >= 2 && descLines[0].length < 120 && descLines[1].length < 120) {
            const hasEn = (descLines[0].includes('Spanish') || descLines[0].includes('English') || descLines[0].includes('subtitles'));
            const hasEs = (descLines[1].includes('español') || descLines[1].includes('inglés') || descLines[1].includes('subtítulos'));
            if (hasEn && hasEs) {
                clean = preferEs ? descLines[1] : descLines[0];
            }
        }

        if (!clean) return null;

        const isLong = clean.length > 300;
        const wrapper = DOM.create('div');

        const textDiv = DOM.create('div', {
            className: `calendar-month-event-description ${isLong ? 'collapsed' : ''}`,
            text: clean
        });
        wrapper.appendChild(textDiv);

        if (isLong) {
            const toggle = DOM.create('span', {
                className: 'calendar-month-event-toggle',
                text: i18n.t('cal.showMore')
            });
            toggle.onclick = () => {
                const isCollapsed = textDiv.classList.contains('collapsed');
                if (isCollapsed) {
                    textDiv.classList.remove('collapsed');
                    toggle.classList.add('expanded');
                    toggle.textContent = i18n.t('cal.showLess');
                } else {
                    textDiv.classList.add('collapsed');
                    toggle.classList.remove('expanded');
                    toggle.textContent = i18n.t('cal.showMore');
                }
            };
            wrapper.appendChild(toggle);
        }

        return wrapper;

    }

    getEventsForDate(date) {
        return this.events.filter(event => {
            if (!event.dtstart) return false;
            const d = new Date(event.dtstart);
            d.setHours(0, 0, 0, 0);
            return d.getTime() === date.getTime();
        });
    }
}
