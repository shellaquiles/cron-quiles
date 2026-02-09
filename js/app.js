/**
 * Cron-Quiles Frontend Entry Point
 *
 * Orquestador principal. Soporta multipágina: index (inicio), eventos, suscribir, comunidades.
 */
import { CONFIG } from './config.js';
import { i18n } from './core/I18n.js';
import { appStore } from './core/Store.js';
import { DataService } from './services/DataService.js';
import { Storage } from './services/Storage.js';
import { Calendar } from './ui/Calendar.js';
import { CommunityList } from './ui/CommunityList.js';
import { Header } from './ui/Header.js';

function getPage() {
    const p = (window.location.pathname || '').toLowerCase();
    if (p.includes('eventos')) return 'eventos';
    if (p.includes('suscribir')) return 'suscribir';
    if (p.includes('comunidades')) return 'comunidades';
    return 'index';
}

class App {
    constructor() {
        this.page = getPage();
        this.header = new Header();
        this.calendar = document.getElementById('calendar-container') ? new Calendar('calendar-container') : null;
        this.communityList = document.getElementById('communities-grid') ? new CommunityList('communities-grid') : null;

        this.init();
    }

    async init() {
        this.states = await DataService.getStatesMetadata();

        const urlParams = new URLSearchParams(window.location.search);
        const savedLang = urlParams.get('lang') || Storage.get(CONFIG.STORAGE_KEYS.LANG) || CONFIG.LANGUAGES.DEFAULT;
        let savedCity = urlParams.get('city') || Storage.get(CONFIG.STORAGE_KEYS.CITY) || CONFIG.CITIES.DEFAULT;

        if (this.states.length > 0 && !this.states.find(s => s.slug === savedCity)) {
            savedCity = CONFIG.CITIES.DEFAULT;
        }

        appStore.set('lang', savedLang);
        appStore.set('city', savedCity);

        this.updateUrlParams();
        this.renderTabs();
        this.bindEvents();

        if (this.page === 'index') {
            this.updateLandingLinks();
        } else if (this.calendar || this.communityList) {
            this.loadCityData(savedCity);
        }

        if (this.page === 'suscribir') {
            this.updateSuscribirLinks();
        }

        this.header.updateLastModified();
    }

    updateLandingLinks() {
        const city = appStore.get('city');
        const btn = document.getElementById('btn-ver-eventos');
        if (btn) btn.href = `eventos.html?city=${encodeURIComponent(city)}`;
    }

    updateSuscribirLinks() {
        const city = appStore.get('city');
        const setHref = (id, url) => {
            const el = document.getElementById(id);
            if (el) el.href = url;
        };
        setHref('download-ics-btn', CONFIG.PATHS.getIcsUrl(city));
        setHref('webcal-btn', CONFIG.PATHS.getWebCalUrl(city));
    }

    renderTabs() {
        const container = document.querySelector('.city-tabs');
        if (!container || !this.states.length) return;

        const showPast = appStore.get('showPastEvents');
        const viewDate = appStore.get('viewDate') || new Date();

        // Format viewDate to YYYY-MM for comparison
        const year = viewDate.getFullYear();
        const month = String(viewDate.getMonth() + 1).padStart(2, '0');
        const viewMonthStr = `${year}-${month}`;

        const currentCity = appStore.get('city');

        const visibleStates = this.states.filter(state => {

            if (state.slug === 'mexico') return true;
            if (state.slug === currentCity) return true; // Keep active tab visible

            if (showPast) return true;

            // Check if city has any active month >= viewMonthStr
            if (!state.active_months || !Array.isArray(state.active_months)) {
                // Fallback to future_event_count if active_months not present (compatibility)
                return (state.future_event_count || 0) > 0;
            }

            // active_months is sorted, check if any is >= viewMonthStr
            const isVisible = state.active_months.some(m => m >= viewMonthStr);
            return isVisible;
        });

        const isMobile = window.matchMedia('(max-width: 768px)').matches;

        if (isMobile) {
            container.innerHTML = `
                <div class="city-select-wrapper">
                    <label class="city-select-label" for="city-select">${i18n.t('hint.whereEvents')}</label>
                    <select id="city-select" class="city-select" aria-label="${i18n.t('nav.cityLabel')}">
                        ${visibleStates.map(state => `
                            <option value="${state.slug}" ${state.slug === currentCity ? 'selected' : ''}>
                                ${state.emoji || ''} ${state.name}
                            </option>
                        `).join('')}
                    </select>
                </div>
            `;
        } else {
            container.innerHTML = visibleStates.map(state => `
                <button class="city-tab ${state.slug === currentCity ? 'active' : ''}" data-city="${state.slug}" aria-label="${state.name}">
                    ${state.emoji} ${state.name}
                </button>
            `).join('');
        }
    }

    bindEvents() {
        const tabsContainer = document.querySelector('.city-tabs');
        if (!tabsContainer) return;

        // Cambio de ciudad: tabs (desktop) o select (móvil)
        tabsContainer.addEventListener('click', (e) => {
            const tab = e.target.closest('.city-tab');
            if (tab) {
                const city = tab.dataset.city;
                if (city) appStore.set('city', city);
            }
        });
        tabsContainer.addEventListener('change', (e) => {
            if (e.target.classList.contains('city-select')) {
                appStore.set('city', e.target.value);
            }
        });

        // Reacción a cambios de estado
        appStore.subscribe('city', (city) => this.onCityChange(city));
        appStore.subscribe('lang', (lang) => this.onLangChange(lang));
        appStore.subscribe('showPastEvents', () => this.renderTabs());
        appStore.subscribe('viewDate', () => this.renderTabs());

        // Al redimensionar, alternar entre tabs (desktop) y select (móvil)
        let lastMobile = window.matchMedia('(max-width: 768px)').matches;
        window.addEventListener('resize', () => {
            const nowMobile = window.matchMedia('(max-width: 768px)').matches;
            if (nowMobile !== lastMobile) {
                lastMobile = nowMobile;
                this.renderTabs();
            }
        });
    }

    /**
     * Actualiza los query params de la URL sin recargar la página.
     */
    updateUrlParams() {
        const params = new URLSearchParams(window.location.search);
        const city = appStore.get('city');
        const lang = appStore.get('lang');

        if (city) {
            params.set('city', city);
        } else {
            params.delete('city');
        }

        if (lang && lang !== CONFIG.LANGUAGES.DEFAULT) {
            params.set('lang', lang);
        } else {
            params.delete('lang');
        }

        const qs = params.toString();
        const newUrl = window.location.pathname + (qs ? '?' + qs : '');
        window.history.replaceState(null, '', newUrl);
    }

    onCityChange(city) {
        Storage.set(CONFIG.STORAGE_KEYS.CITY, city);
        this.updateUrlParams();
        this.renderTabs();

        if (this.page === 'index') {
            this.updateLandingLinks();
        } else if (this.calendar || this.communityList) {
            this.loadCityData(city);
            this.updateDownloadLinks(city);
        }

        if (this.page === 'suscribir') {
            this.updateSuscribirLinks();
        }
    }

    onLangChange(lang) {
        Storage.set(CONFIG.STORAGE_KEYS.LANG, lang);
        this.updateUrlParams();
        if (this.calendar) this.calendar.render();
        this.header.updateLastModified();
    }

    async loadCityData(city) {
        const calendarContainer = document.getElementById('calendar-container');
        if (calendarContainer) {
            calendarContainer.innerHTML = `<div class="events-loading">${i18n.t('calendar.loading')}</div>`;
        }

        try {
            const data = await DataService.getCityData(city);
            const events = Array.isArray(data) ? data : (data.events || []);

            if (this.calendar) this.calendar.setEvents(events);
            if (this.communityList) this.communityList.render(data.communities || []);

        } catch (error) {
            console.error(error);
            const container = document.getElementById('calendar-container');
            if (container) {
                const isLocal = window.location.protocol === 'file:';
                let msg;
                if (isLocal) {
                    msg = 'Error: No se puede cargar con file://. Usa un servidor local (make serve).';
                } else {
                    msg = `No hay datos para "${city}". En local ejecuta: make run-all`;
                }
                container.innerHTML = `<div class="events-error">${msg}</div>`;
            }
        }
    }

    updateDownloadLinks(city) {
        const setHref = (id, url) => {
            const el = document.getElementById(id);
            if (el) el.href = url;
        }

        setHref('download-ics-btn', CONFIG.PATHS.getIcsUrl(city));
        setHref('download-json-btn', CONFIG.PATHS.getDataUrl(city));
        setHref('webcal-btn', CONFIG.PATHS.getWebCalUrl(city));
    }
}

// Bootstrap
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});

// Copiar enlace WebCal al portapapeles (botón principal "Copiar enlace para suscribirme")
document.addEventListener('DOMContentLoaded', () => {
    const webcalBtn = document.getElementById('webcal-btn');
    if (webcalBtn) {
        webcalBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.href.replace('webcal://', 'https://');
            navigator.clipboard.writeText(url).then(() => {
                const originalText = this.textContent;
                this.textContent = i18n.t('btn.copied');
                setTimeout(() => {
                    this.textContent = i18n.t('btn.copy.webcal.plain');
                }, 2000);
            });
        });
    }
});
