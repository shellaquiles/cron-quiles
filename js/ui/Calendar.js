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

        // Return only events from the start of the current month onwards
        const now = new Date();
        const startOfCurrentMonth = new Date(now.getFullYear(), now.getMonth(), 1);

        return this.events.filter(e => {
            if (!e.dtstart) return false;
            return new Date(e.dtstart) >= startOfCurrentMonth;
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

        const prevBtn = DOM.create('button', { className: 'calendar-nav', text: i18n.t('cal.prev') });
        prevBtn.addEventListener('click', () => this.changeMonth(-1));

        const nextBtn = DOM.create('button', { className: 'calendar-nav', text: i18n.t('cal.next') });
        nextBtn.addEventListener('click', () => this.changeMonth(1));

        const title = DOM.create('div', { className: 'calendar-title', text: `${monthNames[month]} ${year}` });

        header.append(prevBtn, title, nextBtn);
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

        // Días actuales
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            date.setHours(0, 0, 0, 0);

            const dayEvents = this.getEventsForDate(date);
            let className = 'calendar-day';

            if (date.getTime() === today.getTime()) className += ' today';
            if (dayEvents.length > 0) className += ' has-events';

            grid.appendChild(DOM.create('div', {
                className,
                text: day.toString()
            }));
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
    }

    renderEventList(year, month) {
        const eventsListContainer = DOM.create('div', { className: 'calendar-events-list', id: 'calendar-events-list' });

        // Fix Timezone Bug: Normalize comparisons to year/month parts
        // Filter events belonging to this month (regardless of time)
        // AND apply the global history filter
        const relevantEvents = this.getFilteredEvents();

        const monthEvents = relevantEvents.filter(e => {
            if (!e.dtstart) return false;
            const d = new Date(e.dtstart);
            return d.getFullYear() === year && d.getMonth() === month;
        }).sort((a, b) => new Date(a.dtstart) - new Date(b.dtstart));

        const monthNames = i18n.t('months');
        const titleText = `${i18n.t('cal.eventsOf')} ${monthNames[month]} ${year}`;
        const monthHeading = DOM.create('h3', { text: titleText });
        monthHeading.id = 'events-list-top';
        eventsListContainer.appendChild(monthHeading);

        if (monthEvents.length > 0) {
            const listWrapper = DOM.create('div', { className: 'calendar-month-events' });
            monthEvents.forEach(event => {
                listWrapper.appendChild(this.createEventCard(event));
            });
            eventsListContainer.appendChild(listWrapper);
        } else {
            // Month is empty -> Show "No events" BUT check for upcoming events
            eventsListContainer.appendChild(DOM.create('p', {
                text: i18n.t('calendar.noEvents'),
                attributes: { style: 'color: var(--terminal-gray); margin-bottom: var(--spacing-lg);' }
            }));

            // Show Upcoming Events Logic
            const nextEvents = this.getUpcomingEvents(year, month, 3);
            if (nextEvents.length > 0) {
                eventsListContainer.appendChild(DOM.create('h3', {
                    text: '🔜 Próximos eventos', // Hardcoded fallback or add to i18n
                    attributes: { style: 'color: var(--terminal-green); margin-top: var(--spacing-xl);' }
                }));

                const listWrapper = DOM.create('div', { className: 'calendar-month-events' });
                nextEvents.forEach(event => {
                    listWrapper.appendChild(this.createEventCard(event));
                });
                eventsListContainer.appendChild(listWrapper);
            }
        }

        this.container.appendChild(eventsListContainer);
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

    // Mapeo de location string a slug de ciudad
    static LOCATION_TO_SLUG = {
        'Online': 'online',
        'México|Ciudad de México': 'mx-cmx',
        'México|Jalisco': 'mx-jal',
        'México|Nuevo León': 'mx-nle',
        'México|Aguascalientes': 'mx-agu',
        'México|Estado de México': 'mx-mex',
        'México|Puebla': 'mx-pue',
        'México|Querétaro': 'mx-que',
        'México|Yucatán': 'mx-yuc',
    };

    createEventCard(event) {
        const dateStr = DateUtils.formatDate(event.dtstart);
        const startStr = DateUtils.formatTime(event.dtstart);
        const endStr = DateUtils.formatTime(event.dtend);
        const timeStr = (startStr && endStr && startStr !== endStr) ? `${startStr} - ${endStr}` : startStr;

        // Título parseado
        let titleNode;
        let locationBadge = null;
        const rawTitle = event.title || event.summary || 'Evento sin título';

        if (rawTitle.includes('|')) {
            const parts = rawTitle.split('|');
            if (parts.length >= 3) {
                let locationText = parts.slice(2).join('|').trim();
                // Si el campo location del evento dice "Online", respetar eso sobre el título
                const evtLoc = (event.location || '').trim().toLowerCase();
                if (evtLoc === 'online' && locationText.toLowerCase() !== 'online') {
                    locationText = 'Online';
                }
                const slug = Calendar.LOCATION_TO_SLUG[locationText];

                titleNode = DOM.create('div', {
                    html: `
                        <div class="event-title-group">${parts[0].trim()}</div>
                        <div class="event-title-name">${parts[1].trim()}</div>
                    `
                });

                // Badge de ubicación clickeable (top-center del card)
                locationBadge = DOM.create('span', {
                    className: 'event-location-badge' + (slug ? ' event-location-badge--clickable' : ''),
                    text: locationText
                });
                if (slug) {
                    locationBadge.dataset.city = slug;
                    locationBadge.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        appStore.set('city', slug);
                    });
                }
            } else {
                titleNode = document.createTextNode(rawTitle);
            }
        } else {
            titleNode = document.createTextNode(rawTitle);
        }

        // Title container (no link — source buttons handle that)
        let titleContainer = DOM.create('div', { className: 'calendar-month-event-title' });
        if (typeof titleNode === 'string') titleContainer.textContent = titleNode;
        else titleContainer.appendChild(titleNode);

        // Location
        const locationNode = event.location
            ? DOM.create('span', { className: 'calendar-month-event-location', text: `📍 ${event.location}` })
            : null;

        // Description with toggle
        const descNode = this.createDescriptionNode(event.description);

        // Tags
        let tagsNode = null;
        if (event.tags && event.tags.length) {
            tagsNode = DOM.create('div', { className: 'calendar-month-event-tags' });
            event.tags.forEach(tag => {
                tagsNode.appendChild(DOM.create('span', { className: 'calendar-month-event-tag', text: tag }));
            });
        }

        const card = DOM.create('div', { className: 'calendar-month-event' });

        const details = DOM.create('div', { className: 'calendar-month-event-details' });
        if (locationNode) details.appendChild(locationNode);
        if (descNode) details.appendChild(descNode);

        // Links a fuentes del evento (soporte multi-fuente)
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
            details.appendChild(sourcesContainer);
        } else if (event.url) {
            // Fallback para eventos sin sources (compatibilidad)
            details.appendChild(DOM.create('a', {
                className: 'event-link',
                text: i18n.t('cal.viewEvent'),
                attributes: {
                    href: addUtmSource(event.url),
                    target: '_blank',
                    style: 'color: var(--terminal-green); margin-top: 5px; display: inline-block;'
                }
            }));
        }

        // Footer: source buttons + tags on same row
        if (tagsNode || details.querySelector('.event-sources')) {
            const footer = DOM.create('div', { className: 'event-card-footer' });
            const sourcesEl = details.querySelector('.event-sources');
            if (sourcesEl) { details.removeChild(sourcesEl); footer.appendChild(sourcesEl); }
            if (tagsNode) footer.appendChild(tagsNode);
            details.appendChild(footer);
        }

        if (locationBadge) card.appendChild(locationBadge);
        card.append(
            titleContainer,
            DOM.create('div', { className: 'calendar-month-event-date', text: `${dateStr}${timeStr ? ' • ' + timeStr : ''}` }),
            details
        );

        return card;
    }

    createDescriptionNode(rawDesc) {
        if (!rawDesc) return null;

        // Limpieza de descripción
        const lines = rawDesc.split('\n');
        const processed = lines.length > 1 ? lines.slice(1).map(l => l.trim()).join('\n') : rawDesc;
        const clean = processed.replace(/(\n\s*){3,}/g, '\n\n').trim();

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
                    toggle.textContent = i18n.t('cal.showLess');
                } else {
                    textDiv.classList.add('collapsed');
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
