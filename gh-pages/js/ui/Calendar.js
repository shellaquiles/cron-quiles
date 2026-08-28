/**
 * Componente Calendario y Navegación Multimes Suiza
 */
import { i18n } from '../core/I18n.js';
import { appStore } from '../core/Store.js';
import { DateUtils } from '../utils/dates.js';
import { DOM } from '../utils/dom.js';

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

function getGoogleCalendarUrl(event) {
    const title = event.title || event.summary || 'Evento Tech';
    const desc = (event.description || '') + (event.url ? `\n\nRegistro: ${event.url}` : '');
    const loc = event.location || (event.online ? 'Online' : '');
    
    let datesParam = '';
    if (event.dtstart) {
        const start = new Date(event.dtstart).toISOString().replace(/-|:|\.\d\d\d/g, '');
        const end = event.dtend 
            ? new Date(event.dtend).toISOString().replace(/-|:|\.\d\d\d/g, '')
            : new Date(new Date(event.dtstart).getTime() + 2 * 60 * 60 * 1000).toISOString().replace(/-|:|\.\d\d\d/g, '');
        datesParam = `&dates=${start}/${end}`;
    }
    
    return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(title)}&details=${encodeURIComponent(desc)}&location=${encodeURIComponent(loc)}${datesParam}`;
}

export class Calendar {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentDate = new Date();
        this.selectedDateStr = null; // YYYY-MM-DD o null si se ve todo el mes
        this.currentWeekOffset = 0;  // Offset de semanas dentro del mes
        this.events = [];
        this.hasLoadedOnce = false;

        // Atajos de teclado registrados
        this.initKeyboardShortcuts();

        // Suscribirse a cambios
        appStore.subscribe('formatFilter', () => this.render());
    }

    setEvents(events) {
        this.events = events || [];
        this.render();
    }

    changeMonth(direction) {
        this.currentDate.setMonth(this.currentDate.getMonth() + direction);
        this.selectedDateStr = null;
        this.currentWeekOffset = 0;
        appStore.set('viewDate', new Date(this.currentDate));
        this.render();
    }

    setMonthDate(year, month) {
        this.currentDate = new Date(year, month, 1);
        this.selectedDateStr = null;
        this.currentWeekOffset = 0;
        appStore.set('viewDate', new Date(this.currentDate));
        this.render();
    }

    getFilteredEvents() {
        const formatFilter = appStore.get('formatFilter') || 'all';
        let filtered = this.events;

        if (formatFilter === 'in-person') {
            filtered = filtered.filter(e => !this.isEventOnline(e));
        } else if (formatFilter === 'online') {
            filtered = filtered.filter(e => this.isEventOnline(e));
        }

        return filtered;
    }

    getEventDatesSet() {
        const dates = new Set();
        this.events.forEach(e => {
            if (e.dtstart) {
                const d = new Date(e.dtstart);
                const localeDateStr = d.toLocaleDateString('en-CA', { timeZone: 'America/Mexico_City' });
                dates.add(localeDateStr);
            }
        });
        return dates;
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

        // ==== 1. NAVEGADOR DE CALENDARIO SUIZO (PANEL SUPERIOR) ====
        const navPanel = DOM.create('div', { className: 'calendar-nav-panel' });

        // Nav Header
        const navHeader = DOM.create('div', { className: 'nav-header' });
        const monthDisplay = DOM.create('span', { 
            className: 'month-display', 
            id: 'currentMonthLabel',
            text: `${monthNames[month]} ${year}` 
        });

        const navActions = DOM.create('div', { className: 'nav-actions' });
        
        const viewAllBtn = DOM.create('button', {
            className: 'btn-nav',
            id: 'viewAllBtn',
            text: this.selectedDateStr ? i18n.t('cal.viewAllMonth') || 'VER TODO EL MES' : 'MES COMPLETO'
        });
        viewAllBtn.addEventListener('click', () => {
            this.selectedDateStr = null;
            this.render();
        });

        const prevMonthBtn = DOM.create('button', {
            className: 'btn-nav',
            id: 'prevMonthBtn',
            text: '← MES ANTERIOR'
        });
        prevMonthBtn.addEventListener('click', () => this.changeMonth(-1));

        const todayBtn = DOM.create('button', {
            className: 'btn-nav',
            id: 'todayBtn',
            text: 'HOY'
        });
        todayBtn.addEventListener('click', () => {
            const now = new Date();
            this.currentDate = new Date(now.getFullYear(), now.getMonth(), 1);
            this.selectedDateStr = now.toLocaleDateString('en-CA', { timeZone: 'America/Mexico_City' });
            this.render();
        });

        const nextMonthBtn = DOM.create('button', {
            className: 'btn-nav',
            id: 'nextMonthBtn',
            text: 'SIG MES →'
        });
        nextMonthBtn.addEventListener('click', () => this.changeMonth(1));

        navActions.append(viewAllBtn, prevMonthBtn, todayBtn, nextMonthBtn);
        navHeader.append(monthDisplay, navActions);
        navPanel.appendChild(navHeader);

        // Tira de días (7 días de la semana activa o deslizador)
        const stripContainer = DOM.create('div', { className: 'days-strip-container' });
        const daysStrip = DOM.create('div', { className: 'days-strip', id: 'daysStrip' });

        const weekDays = this.getWeekDaysForMonth(year, month, this.currentWeekOffset);
        const eventDates = this.getEventDatesSet();

        weekDays.forEach(day => {
            const cell = DOM.create('div', { className: 'day-cell' });
            cell.setAttribute('data-date', day.dateStr);

            if (this.selectedDateStr === day.dateStr) {
                cell.classList.add('active');
            }

            if (eventDates.has(day.dateStr)) {
                cell.classList.add('has-events');
            }

            const dayName = DOM.create('span', { className: 'day-name', text: day.name });
            const dayNum = DOM.create('span', { className: 'day-num', text: day.num });
            const indicator = DOM.create('span', { className: 'event-indicator' });

            cell.append(dayName, dayNum, indicator);

            cell.addEventListener('click', () => {
                if (this.selectedDateStr === day.dateStr) {
                    this.selectedDateStr = null; // Toggle off
                } else {
                    this.selectedDateStr = day.dateStr;
                }
                this.render();
            });

            daysStrip.appendChild(cell);
        });

        stripContainer.appendChild(daysStrip);
        navPanel.appendChild(stripContainer);

        // Barra de navegación entre semanas
        const weekSwitcherBar = DOM.create('div', { className: 'week-switcher-bar' });
        const prevWeekBtn = DOM.create('button', { text: '← Semana anterior' });
        prevWeekBtn.addEventListener('click', () => {
            this.currentWeekOffset--;
            this.render();
        });

        const weekInfo = DOM.create('span', { 
            text: `Días ${weekDays[0].num} - ${weekDays[weekDays.length - 1].num} de ${monthNames[month]}` 
        });

        const nextWeekBtn = DOM.create('button', { text: 'Semana siguiente →' });
        nextWeekBtn.addEventListener('click', () => {
            this.currentWeekOffset++;
            this.render();
        });

        weekSwitcherBar.append(prevWeekBtn, weekInfo, nextWeekBtn);
        navPanel.appendChild(weekSwitcherBar);

        this.container.appendChild(navPanel);

        // ==== 2. LISTA DE EVENTOS FILTRADOS ====
        this.renderEventList(year, month);
    }

    getWeekDaysForMonth(year, month, weekOffset = 0) {
        const firstDayOfMonth = new Date(year, month, 1);
        const dayOfWeek = (firstDayOfMonth.getDay() + 6) % 7; // Lunes = 0
        
        // Empezar desde el lunes de la semana correspondiente
        const startDay = new Date(year, month, 1 - dayOfWeek + (weekOffset * 7));
        const days = [];
        const dayNamesShort = ['LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB', 'DOM'];

        for (let i = 0; i < 7; i++) {
            const d = new Date(startDay.getFullYear(), startDay.getMonth(), startDay.getDate() + i);
            const dateStr = d.toLocaleDateString('en-CA', { timeZone: 'America/Mexico_City' });
            days.push({
                name: dayNamesShort[i],
                num: d.getDate(),
                dateStr: dateStr,
                isCurrentMonth: d.getMonth() === month
            });
        }
        return days;
    }

    renderEventList(year, month) {
        const eventsContainer = DOM.create('div', { className: 'event-list', id: 'eventList' });
        const relevantEvents = this.getFilteredEvents();

        let visibleEvents = [];

        if (this.selectedDateStr) {
            // Filtrar exactamente el día seleccionado
            visibleEvents = relevantEvents.filter(e => {
                if (!e.dtstart) return false;
                const d = new Date(e.dtstart);
                const dStr = d.toLocaleDateString('en-CA', { timeZone: 'America/Mexico_City' });
                return dStr === this.selectedDateStr;
            });
        } else {
            // Mostrar todos los eventos del mes visualizado
            visibleEvents = relevantEvents.filter(e => {
                if (!e.dtstart) return false;
                const d = new Date(e.dtstart);
                return d.getFullYear() === year && d.getMonth() === month;
            });
        }

        visibleEvents.sort((a, b) => new Date(a.dtstart) - new Date(b.dtstart));

        if (visibleEvents.length > 0) {
            visibleEvents.forEach(event => {
                eventsContainer.appendChild(this.createEventCard(event));
            });
        } else {
            const emptyMsg = DOM.create('div', {
                className: 'no-events-msg',
                attributes: { style: 'display: block;' },
                text: this.selectedDateStr 
                    ? `NO HAY EVENTOS PROGRAMADOS PARA EL ${this.selectedDateStr}` 
                    : `NO HAY EVENTOS REGISTRADOS EN ESTE MES.`
            });
            eventsContainer.appendChild(emptyMsg);
        }

        this.container.appendChild(eventsContainer);
    }

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

    shortenLocation(location, maxLen = 80) {
        if (!location || typeof location !== 'string') return '';
        const firstLine = location.split('\n')[0].trim();
        if (firstLine.length <= maxLen) return firstLine;
        return firstLine.slice(0, maxLen - 1).trim() + '…';
    }

    createEventCard(event) {
        const card = DOM.create('article', { className: 'event-item' });
        const d = new Date(event.dtstart);
        card.setAttribute('data-date', d.toLocaleDateString('en-CA', { timeZone: 'America/Mexico_City' }));

        // 1. Badge Fecha
        const dateBadgeInfo = DateUtils.formatDateBadge(event.dtstart);
        const dateCol = DOM.create('div', { className: 'date-badge' });
        dateCol.appendChild(DOM.create('span', { className: 'date-number', text: dateBadgeInfo.dayNumber }));
        dateCol.appendChild(DOM.create('span', { className: 'date-meta', text: dateBadgeInfo.dayMeta }));
        card.appendChild(dateCol);

        // 2. Info de Evento
        const infoCol = DOM.create('div', { className: 'event-content' });

        const metaRow = DOM.create('div', { className: 'event-meta' });
        const isToday = DateUtils.isToday(event.dtstart);
        if (isToday) {
            const liveBadge = DOM.create('span', { className: 'badge-live' });
            liveBadge.innerHTML = `<span class="live-dot"></span>${i18n.t('badge.live') || 'HOY'}`;
            metaRow.appendChild(liveBadge);
            metaRow.appendChild(DOM.create('span', { text: '•' }));
        }

        const startStr = DateUtils.formatTime(event.dtstart);
        const endStr = DateUtils.formatTime(event.dtend);
        const timeStr = (startStr && endStr && startStr !== endStr) ? `${startStr} - ${endStr}` : startStr;
        if (timeStr) {
            metaRow.appendChild(DOM.create('span', { text: `${timeStr} CST` }));
            metaRow.appendChild(DOM.create('span', { text: '•' }));
        }

        const isOnline = this.isEventOnline(event);
        let locText = isOnline ? 'ONLINE' : (event.location ? this.shortenLocation(event.location) : (event.city || 'México'));
        metaRow.appendChild(DOM.create('span', { text: locText.toUpperCase() }));

        infoCol.appendChild(metaRow);

        // Título
        const rawTitle = event.title || event.summary || 'Evento sin título';
        let categoryLabel = event.organizer || null;
        let displayName = rawTitle;

        if (rawTitle.includes('|')) {
            const parts = rawTitle.split('|').map(p => p.trim());
            if (parts.length >= 2) {
                categoryLabel = parts[0];
                displayName = parts[1];
            }
        }

        if (categoryLabel) {
            infoCol.appendChild(DOM.create('div', { className: 'event-organizer', text: categoryLabel }));
        }

        const titleEl = DOM.create('h2', { className: 'event-title' });
        if (event.url) {
            const link = DOM.create('a', {
                text: displayName,
                attributes: {
                    href: addUtmSource(event.url),
                    target: '_blank',
                    rel: 'noopener'
                }
            });
            titleEl.appendChild(link);
        } else {
            titleEl.textContent = displayName;
        }
        infoCol.appendChild(titleEl);

        // Tags
        const tagsWrapper = DOM.create('div', { className: 'tag-container' });
        if (isOnline) {
            tagsWrapper.appendChild(DOM.create('span', { className: 'tag', text: '#online' }));
        } else {
            tagsWrapper.appendChild(DOM.create('span', { className: 'tag', text: '#presencial' }));
        }

        if (event.tags && event.tags.length) {
            event.tags.forEach(t => {
                const tagText = t.startsWith('#') ? t : `#${t}`;
                tagsWrapper.appendChild(DOM.create('span', { className: 'tag', text: tagText }));
            });
        }
        infoCol.appendChild(tagsWrapper);

        card.appendChild(infoCol);

        // 3. Acciones
        const actionsCol = DOM.create('div', { className: 'event-actions' });
        const mainUrl = event.url || (event.sources && event.sources[0]?.url) || '#';
        const actionLabel = isOnline ? (i18n.t('btn.join') || 'Unirse ↗') : (i18n.t('btn.register') || 'Registro ↗');
        
        const regBtn = DOM.create('a', {
            className: 'btn-action',
            text: actionLabel,
            attributes: {
                href: addUtmSource(mainUrl),
                target: '_blank',
                rel: 'noopener'
            }
        });
        actionsCol.appendChild(regBtn);

        const calBtn = DOM.create('a', {
            className: 'btn-outline',
            text: '+ Cal',
            attributes: {
                href: getGoogleCalendarUrl(event),
                target: '_blank',
                rel: 'noopener',
                title: 'Añadir a Google Calendar'
            }
        });
        actionsCol.appendChild(calBtn);

        card.appendChild(actionsCol);
        return card;
    }

    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;

            const key = e.key.toLowerCase();
            const cells = Array.from(document.querySelectorAll('.day-cell'));
            const activeIndex = cells.findIndex(c => c.classList.contains('active'));

            if (key === '?' || (e.shiftKey && e.key === '/')) {
                e.preventDefault();
                const modal = document.getElementById('helpModal');
                if (modal) modal.classList.toggle('open');
                return;
            }

            switch (key) {
                case 'arrowright':
                case 'l':
                    e.preventDefault();
                    if (activeIndex !== -1 && activeIndex < cells.length - 1) {
                        cells[activeIndex + 1].click();
                    } else if (activeIndex === -1 && cells.length > 0) {
                        cells[0].click();
                    }
                    break;

                case 'arrowleft':
                case 'h':
                    e.preventDefault();
                    if (activeIndex > 0) {
                        cells[activeIndex - 1].click();
                    }
                    break;

                case ']':
                    e.preventDefault();
                    this.changeMonth(1);
                    break;

                case '[':
                    e.preventDefault();
                    this.changeMonth(-1);
                    break;

                case 't':
                    e.preventDefault();
                    const now = new Date();
                    this.currentDate = new Date(now.getFullYear(), now.getMonth(), 1);
                    this.selectedDateStr = now.toLocaleDateString('en-CA', { timeZone: 'America/Mexico_City' });
                    this.render();
                    break;

                case 'd':
                    e.preventDefault();
                    if (window.app && window.app.header) {
                        window.app.header.toggleTheme();
                    } else {
                        const themeBtn = document.getElementById('themeToggle');
                        if (themeBtn) themeBtn.click();
                    }
                    break;

                case 'a':
                case 'escape':
                    e.preventDefault();
                    this.selectedDateStr = null;
                    const modal = document.getElementById('helpModal');
                    if (modal && modal.classList.contains('open')) {
                        modal.classList.remove('open');
                    } else {
                        this.render();
                    }
                    break;
            }
        });
    }
}
