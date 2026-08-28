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
        this.isFullMonthActive = false; // Alternador de vista semana / todo el mes
        this.events = [];
        this.hasLoadedOnce = false;

        // Atajos de teclado registrados
        this.initKeyboardShortcuts();

        // Suscribirse a cambios
        appStore.subscribe('formatFilter', () => this.render());
    }

    setEvents(events) {
        this.events = events || [];
        
        // Auto-enfoque inteligente: Si el mes actual no tiene ningún evento,
        // navegar automáticamente al mes más cercano con eventos (futuro o más reciente).
        if (this.events.length > 0) {
            const currentYear = this.currentDate.getFullYear();
            const currentMonth = this.currentDate.getMonth();
            const hasEventsInCurrentMonth = this.events.some(e => {
                if (!e.dtstart) return false;
                const d = new Date(e.dtstart);
                return d.getFullYear() === currentYear && d.getMonth() === currentMonth;
            });

            if (!hasEventsInCurrentMonth) {
                // Buscar eventos futuros o el evento más reciente
                const now = new Date();
                const futureEvents = this.events
                    .filter(e => e.dtstart && new Date(e.dtstart) >= now)
                    .sort((a, b) => new Date(a.dtstart) - new Date(b.dtstart));

                if (futureEvents.length > 0) {
                    const targetDate = new Date(futureEvents[0].dtstart);
                    this.currentDate = new Date(targetDate.getFullYear(), targetDate.getMonth(), 1);
                } else {
                    // Si todos son pasados, ir al más reciente
                    const sorted = [...this.events]
                        .filter(e => e.dtstart)
                        .sort((a, b) => new Date(b.dtstart) - new Date(a.dtstart));
                    if (sorted.length > 0) {
                        const targetDate = new Date(sorted[0].dtstart);
                        this.currentDate = new Date(targetDate.getFullYear(), targetDate.getMonth(), 1);
                    }
                }
                this.selectedDateStr = null;
                this.currentWeekOffset = 0;
            }
        }

        this.render();
    }

    changeYear(direction) {
        const nextYear = this.currentDate.getFullYear() + direction;
        const currentMonth = this.currentDate.getMonth();
        this.setMonthDate(nextYear, currentMonth);
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

        // ==== 1. NAVEGADOR DE 12 MESES (YEAR TIMELINE SUIZA) ====
        const navPanel = DOM.create('div', { className: 'calendar-controls-box' });

        // Tira horizontal interactiva de los 12 meses del año flanqueada por botones de año [ ◀ ] y [ ▶ ]
        const monthsTimeline = DOM.create('div', { className: 'months-timeline', id: 'monthsTimeline' });
        
        const prevYearBtn = DOM.create('button', {
            className: 'timeline-year-nav',
            id: 'btnPrevYear',
            title: `Año anterior (${year - 1})`,
            text: '◀'
        });
        prevYearBtn.addEventListener('click', () => {
            this.isUpcomingView = false;
            this.changeYear(-1);
        });
        monthsTimeline.appendChild(prevYearBtn);

        const monthShortNames = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'];
        
        // Contar eventos por cada mes del año actual y calcular densidad
        const monthEventCounts = new Array(12).fill(0);
        this.events.forEach(e => {
            if (e.dtstart) {
                const d = new Date(e.dtstart);
                if (d.getFullYear() === year) {
                    monthEventCounts[d.getMonth()]++;
                }
            }
        });

        const maxEventsInYear = Math.max(...monthEventCounts, 1);

        monthShortNames.forEach((shortName, idx) => {
            const count = monthEventCounts[idx];
            const hasEv = count > 0;
            
            // Nivel de intensidad de calor (Heatmap)
            let density = 'none';
            if (count > 0) {
                const ratio = count / maxEventsInYear;
                if (ratio >= 0.7) density = 'max';
                else if (ratio >= 0.35) density = 'high';
                else if (ratio >= 0.15) density = 'mid';
                else density = 'low';
            }

            const isSelectedMonth = !this.isUpcomingView && idx === month;

            const monthTab = DOM.create('button', {
                className: `month-tab ${isSelectedMonth ? 'active' : ''} ${hasEv ? 'has-events' : ''} density-${density}`,
                attributes: { 
                    'data-month': idx,
                    'data-density': density,
                    'title': `${monthNames[idx]} ${year}: ${count} eventos`
                },
                text: shortName
            });

            monthTab.addEventListener('click', () => {
                this.isUpcomingView = false;
                this.setMonthDate(year, idx);
            });

            monthsTimeline.appendChild(monthTab);
        });

        const nextYearBtn = DOM.create('button', {
            className: 'timeline-year-nav',
            id: 'btnNextYear',
            title: `Año siguiente (${year + 1})`,
            text: '▶'
        });
        nextYearBtn.addEventListener('click', () => {
            this.isUpcomingView = false;
            this.changeYear(1);
        });
        monthsTimeline.appendChild(nextYearBtn);

        navPanel.appendChild(monthsTimeline);

        // Cabecera Editorial del Mes Seleccionado o Vista de Próximos Eventos
        const monthHeaderRow = DOM.create('div', { className: 'month-summary-bar' });
        const relevantEvents = this.getFilteredEvents();
        const now = new Date();
        const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());

        let displayedEvents = [];
        let headerTitleText = '';
        let headerCountText = '';

        if (this.isUpcomingView) {
            // Filtrar todos los eventos desde hoy hacia el futuro
            displayedEvents = relevantEvents.filter(e => {
                if (!e.dtstart) return false;
                return new Date(e.dtstart) >= startOfToday;
            });

            // Si no hay eventos a futuro, traer los más recientes del histórico
            if (displayedEvents.length === 0 && relevantEvents.length > 0) {
                displayedEvents = [...relevantEvents]
                    .filter(e => e.dtstart)
                    .sort((a, b) => new Date(b.dtstart) - new Date(a.dtstart))
                    .slice(0, 30);
            }

            headerTitleText = 'PRÓXIMOS EVENTOS';
            headerCountText = `${displayedEvents.length} eventos futuros`;
        } else {
            // Modo Mes Seleccionado
            displayedEvents = relevantEvents.filter(e => {
                if (!e.dtstart) return false;
                const d = new Date(e.dtstart);
                return d.getFullYear() === year && d.getMonth() === month;
            });

            headerTitleText = `${monthNames[month].toUpperCase()} ${year}`;
            headerCountText = `${displayedEvents.length} eventos en total`;
        }

        const leftSummary = DOM.create('div', { className: 'summary-left' });
        const monthTitle = DOM.create('span', { 
            className: 'month-title-display', 
            id: 'currentMonthYear',
            text: headerTitleText
        });
        const totalCountSpan = DOM.create('span', {
            className: 'month-events-count',
            text: headerCountText
        });
        leftSummary.append(monthTitle, totalCountSpan);

        // Botón de alternar vista con iconos vectoriales Lucide
        const toggleBtn = DOM.create('button', {
            className: `btn-upcoming-toggle ${this.isUpcomingView ? 'active' : ''}`,
            id: 'btnUpcomingToggle'
        });

        if (this.isUpcomingView) {
            // Icono Lucide Calendar
            toggleBtn.innerHTML = `
                <svg class="ui-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect width="18" height="18" x="3" y="4" rx="2" ry="2"></rect>
                    <line x1="16" x2="16" y1="2" y2="6"></line>
                    <line x1="8" x2="8" y1="2" y2="6"></line>
                    <line x1="3" x2="21" y1="10" y2="10"></line>
                </svg>
                <span>VER POR MES</span>
            `;
        } else {
            // Icono Lucide Sparkles / Zap
            toggleBtn.innerHTML = `
                <svg class="ui-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"></path>
                </svg>
                <span>TODOS LOS PRÓXIMOS</span>
            `;
        }
        toggleBtn.addEventListener('click', () => {
            this.isUpcomingView = !this.isUpcomingView;
            if (!this.isUpcomingView) {
                // Volver a situar en el mes actual o con eventos
                const nowDate = new Date();
                this.currentDate = new Date(nowDate.getFullYear(), nowDate.getMonth(), 1);
            }
            this.render();
        });

        monthHeaderRow.append(leftSummary, toggleBtn);
        navPanel.appendChild(monthHeaderRow);

        this.container.appendChild(navPanel);

        // ==== 2. LISTA DE EVENTOS (FEED CRONOLÓGICO CONTINUO) ====
        this.renderEventList(year, month, displayedEvents);
    }

    renderEventList(year, month, visibleEvents = []) {
        const eventsContainer = DOM.create('div', { className: 'event-list', id: 'eventList' });

        visibleEvents.sort((a, b) => new Date(a.dtstart) - new Date(b.dtstart));

        if (visibleEvents.length > 0) {
            visibleEvents.forEach(event => {
                eventsContainer.appendChild(this.createEventCard(event));
            });
        } else {
            const emptyContainer = DOM.create('div', {
                className: 'no-events-msg',
                attributes: { style: 'display: block; text-align: center;' }
            });

            const msgText = DOM.create('p', {
                text: this.selectedDateStr 
                    ? `NO HAY EVENTOS PROGRAMADOS PARA EL ${this.selectedDateStr}` 
                    : `NO HAY EVENTOS REGISTRADOS EN ESTE MES (${monthNames[month].toUpperCase()} ${year}).`
            });
            emptyContainer.appendChild(msgText);

            // Si hay eventos en otros meses, mostrar enlaces rápidos para saltar a ellos
            if (relevantEvents.length > 0) {
                const monthsWithEvents = new Map();
                relevantEvents.forEach(e => {
                    if (e.dtstart) {
                        const d = new Date(e.dtstart);
                        const k = `${d.getFullYear()}-${d.getMonth()}`;
                        const label = `${monthNames[d.getMonth()]} ${d.getFullYear()}`;
                        monthsWithEvents.set(k, { year: d.getFullYear(), month: d.getMonth(), label });
                    }
                });

                if (monthsWithEvents.size > 0) {
                    const jumpHint = DOM.create('div', { 
                        style: 'margin-top: 0.8rem; font-size: 0.8rem; color: var(--text-muted);',
                        text: 'MESES CON EVENTOS DISPONIBLES: ' 
                    });
                    
                    monthsWithEvents.forEach(({ year: y, month: m, label }) => {
                        const jumpBtn = DOM.create('button', {
                            className: 'btn-nav',
                            style: 'margin: 0.2rem 0.4rem; display: inline-block;',
                            text: `${label} ↗`
                        });
                        jumpBtn.addEventListener('click', () => {
                            this.setMonthDate(y, m);
                        });
                        jumpHint.appendChild(jumpBtn);
                    });

                    emptyContainer.appendChild(jumpHint);
                }
            }

            eventsContainer.appendChild(emptyContainer);
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

    getPlatformName(url) {
        if (!url || typeof url !== 'string') return 'Registro ↗';
        const lower = url.toLowerCase();
        if (lower.includes('lu.ma') || lower.includes('luma.com')) return 'Ver en Luma ↗';
        if (lower.includes('meetup.com')) return 'Ver en Meetup ↗';
        if (lower.includes('eventbrite.')) return 'Ver en Eventbrite ↗';
        if (lower.includes('ticketmaster.')) return 'Boletos ↗';
        if (lower.includes('github.com')) return 'Ver en GitHub ↗';
        if (lower.includes('youtube.com') || lower.includes('youtu.be')) return 'Ver en YouTube ↗';
        if (lower.includes('twitch.tv')) return 'Ver en Twitch ↗';
        if (lower.includes('zoom.us')) return 'Entrar a Zoom ↗';
        if (lower.includes('discord.')) return 'Unirse a Discord ↗';
        return 'Registro ↗';
    }

    getStateBadge(event) {
        if (this.isEventOnline(event)) return 'ONLINE';
        const raw = (event.state || event.city_code || event.city || '').toUpperCase();
        if (raw.includes('PUE') || raw.includes('PUEBLA')) return 'PUE';
        if (raw.includes('CMX') || raw.includes('CDMX') || raw.includes('CIUDAD DE MÉXICO') || raw.includes('MEXICO CITY')) return 'CDMX';
        if (raw.includes('JAL') || raw.includes('JALISCO') || raw.includes('GUADALAJARA')) return 'JAL';
        if (raw.includes('BCN') || raw.includes('BAJA') || raw.includes('TIJUANA')) return 'BCN';
        if (raw.includes('NLE') || raw.includes('NUEVO LEÓN') || raw.includes('MONTERREY')) return 'MTY';
        if (raw.includes('YUC') || raw.includes('YUCATÁN') || raw.includes('MÉRIDA')) return 'YUC';
        if (raw.includes('QRO') || raw.includes('QUERÉTARO')) return 'QRO';
        if (raw.includes('TLA') || raw.includes('TLAXCALA')) return 'TLA';
        if (raw.includes('MEX') || raw.includes('EDOMEX')) return 'MEX';
        return raw.slice(0, 4) || 'MX';
    }

    formatMarkdown(text) {
        if (!text || typeof text !== 'string') return '';
        
        // 1. Limpieza de textos redundantes y URLs de feeds
        let clean = text
            .replace(/Get up-to-date information at:\s*https?:\/\/\S+/gi, '')
            .replace(/Find more information on\s*https?:\/\/\S+/gi, '')
            .replace(/Hosted by.*/gi, '')
            .replace(/https?:\/\/\S+/gi, '') // URLs sueltas repetitivas
            .replace(/#{1,6}\s*/g, ' ')       // Títulos ### convertidos a espacio
            .trim();

        // 2. Escape básico de seguridad HTML
        clean = clean
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // 3. Renderizar Markdown enriquecido: Negrita (** o __), Cursiva (* o _), Código (`), Enlaces ([texto](url))
        clean = clean
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/__([^_]+)__/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>')
            .replace(/_([^_]+)_/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

        return clean;
    }

    cleanDescription(text) {
        return this.formatMarkdown(text);
    }

    createEventCard(event) {
        const card = DOM.create('article', { className: 'event-item' });
        const d = new Date(event.dtstart);
        card.setAttribute('data-date', d.toLocaleDateString('en-CA', { timeZone: 'America/Mexico_City' }));

        // 1. Badge de Fecha
        const dateBadgeInfo = DateUtils.formatDateBadge(event.dtstart);
        const dateCol = DOM.create('div', { className: 'date-badge' });
        dateCol.appendChild(DOM.create('span', { className: 'date-number', text: dateBadgeInfo.dayNumber }));
        dateCol.appendChild(DOM.create('span', { className: 'date-meta', text: dateBadgeInfo.dayMeta }));
        card.appendChild(dateCol);

        // 2. Información del Evento
        const infoCol = DOM.create('div', { className: 'event-content' });

        // Parsear Título y Organizador primero
        const rawTitle = event.title || event.summary || 'Evento sin título';
        let orgName = event.organizer || null;
        let displayName = rawTitle;

        if (rawTitle.includes('|')) {
            const parts = rawTitle.split('|').map(p => p.trim());
            if (parts.length >= 2) {
                orgName = parts[0];
                displayName = parts[1];
            }
        }

        // Fila 1: Comunidad + Estado + Live
        const metaTop = DOM.create('div', { className: 'event-meta-top' });
        
        if (orgName) {
            metaTop.appendChild(DOM.create('span', { className: 'org-badge', text: orgName.toUpperCase() }));
        }

        const isOnline = this.isEventOnline(event);
        const stateCode = this.getStateBadge(event);
        const stateBadge = DOM.create('span', { 
            className: `badge-state state-${stateCode.toLowerCase()}`, 
            attributes: { 'data-state': stateCode.toLowerCase() },
            text: stateCode 
        });
        metaTop.appendChild(stateBadge);

        const isToday = DateUtils.isToday(event.dtstart);
        if (isToday) {
            const liveBadge = DOM.create('span', { className: 'badge-live' });
            liveBadge.innerHTML = `<span class="live-dot"></span>${i18n.t('badge.live') || 'HOY'}`;
            metaTop.appendChild(liveBadge);
        }

        infoCol.appendChild(metaTop);

        // Fila 2: Título Principal
        const titleEl = DOM.create('h2', { className: 'event-title' });
        const mainUrl = event.url || (event.sources && event.sources[0]?.url) || '#';
        if (mainUrl && mainUrl !== '#') {
            const link = DOM.create('a', {
                text: displayName,
                attributes: {
                    href: addUtmSource(mainUrl),
                    target: '_blank',
                    rel: 'noopener'
                }
            });
            titleEl.appendChild(link);
        } else {
            titleEl.textContent = displayName;
        }
        infoCol.appendChild(titleEl);

        // Fila 3: CUÁNDO (Horario con Icono Lineal)
        const startStr = DateUtils.formatTime(event.dtstart);
        const endStr = DateUtils.formatTime(event.dtend);
        const timeStr = (startStr && endStr && startStr !== endStr) ? `${startStr} – ${endStr} CST` : (startStr ? `${startStr} CST` : '');
        if (timeStr) {
            const timeRow = DOM.create('div', { className: 'meta-row' });
            timeRow.innerHTML = `
                <svg class="ui-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <span class="meta-text"><strong>${timeStr}</strong></span>
            `;
            infoCol.appendChild(timeRow);
        }

        // Fila 4: DÓNDE (Sede + Link de Mapa Integrado con Icono Lineal)
        const venueRow = DOM.create('div', { className: 'meta-row' });
        if (!isOnline && event.location) {
            const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(event.location)}`;
            venueRow.innerHTML = `
                <svg class="ui-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"></path>
                    <circle cx="12" cy="10" r="3"></circle>
                </svg>
                <a href="${mapUrl}" target="_blank" rel="noopener" class="venue-link" title="Abrir ubicación en Google Maps">
                    <span>${this.shortenLocation(event.location)}</span>
                    <span class="link-arrow">↗</span>
                </a>
            `;
            infoCol.appendChild(venueRow);
        } else if (isOnline) {
            venueRow.innerHTML = `
                <svg class="ui-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="2" y1="12" x2="22" y2="12"></line>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
                <span class="meta-text">Evento Virtual / Remoto</span>
            `;
            infoCol.appendChild(venueRow);
        }

        // Fila 4: Tags de Tecnología
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

        // 3. Acciones (Exactamente 2 botones fijos)
        const actionsCol = DOM.create('div', { className: 'event-actions' });
        const platformLabel = this.getPlatformName(mainUrl);
        
        const regBtn = DOM.create('a', {
            className: 'btn-main',
            text: platformLabel,
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

                case '}':
                    e.preventDefault();
                    this.changeYear(1);
                    break;

                case '{':
                    e.preventDefault();
                    this.changeYear(-1);
                    break;

                case 'arrowright':
                case 'l':
                case ']':
                    e.preventDefault();
                    this.setMonthDate(this.currentDate.getFullYear(), (this.currentDate.getMonth() + 1) % 12);
                    break;

                case 'arrowleft':
                case 'h':
                case '[':
                    e.preventDefault();
                    this.setMonthDate(this.currentDate.getFullYear(), (this.currentDate.getMonth() + 11) % 12);
                    break;

                case 't':
                    e.preventDefault();
                    this.isUpcomingView = false;
                    const nowT = new Date();
                    this.setMonthDate(nowT.getFullYear(), nowT.getMonth());
                    break;

                case 'u':
                case 'p':
                    e.preventDefault();
                    this.isUpcomingView = !this.isUpcomingView;
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
                    e.preventDefault();
                    this.isFullMonthActive = !this.isFullMonthActive;
                    if (this.isFullMonthActive) this.selectedDateStr = null;
                    this.render();
                    break;

                case 'escape':
                    e.preventDefault();
                    this.selectedDateStr = null;
                    this.isFullMonthActive = false;
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
