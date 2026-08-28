/**
 * Cron-Quiles Frontend Entry Point - Editorial Theme
 */
import { CONFIG } from './config.js';
import { i18n } from './core/I18n.js';
import { appStore } from './core/Store.js';
import { DataService } from './services/DataService.js';
import { Storage } from './services/Storage.js';
import { Calendar } from './ui/Calendar.js?v=3';
import { CommunityList } from './ui/CommunityList.js';
import { Header } from './ui/Header.js';
import { Terminal } from './ui/Terminal.js';

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
        this.terminal = new Terminal();
        this.calendar = document.getElementById('calendar-container') ? new Calendar('calendar-container') : null;
        this.communityList = document.getElementById('communities-grid') ? new CommunityList('communities-grid') : null;

        this.init();
    }

    async init() {
        this.states = await DataService.getStatesMetadata();

        const urlParams = new URLSearchParams(window.location.search);
        const savedLang = urlParams.get('lang') || Storage.get(CONFIG.STORAGE_KEYS.LANG) || CONFIG.LANGUAGES.DEFAULT;
        let savedCity = urlParams.get('city') || Storage.get(CONFIG.STORAGE_KEYS.CITY) || CONFIG.CITIES.DEFAULT;
        let savedFormat = urlParams.get('format') || 'all';

        if (this.states.length > 0 && !this.states.find(s => s.slug === savedCity)) {
            savedCity = CONFIG.CITIES.DEFAULT;
        }

        appStore.set('lang', savedLang);
        appStore.set('city', savedCity);
        appStore.set('formatFilter', savedFormat);

        this.updateUrlParams();
        this.renderTabs();
        this.bindEvents();

        if (this.page === 'index') {
            this.updateLandingLinks();
            this.loadFeaturedEvents(savedCity);
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
        const pillsContainer = document.getElementById('cityPillsContainer') || document.querySelector('.city-filter-group .filter-pills-scroll');
        if (!pillsContainer || !this.states.length) return;

        const currentCity = appStore.get('city');

        const visibleStates = this.states.filter(state => {
            if (state.slug === 'mexico') return true;
            if (state.slug === currentCity) return true;
            return (state.event_count || 0) > 0;
        });

        pillsContainer.innerHTML = visibleStates.map(state => `
            <button class="filter-pill ${state.slug === currentCity ? 'active' : ''}" data-city="${state.slug}" aria-label="${state.name}">
                ${state.name} (${state.event_count || 0})
            </button>
        `).join('');
    }

    bindEvents() {
        // Filtro de Ciudad
        const cityContainer = document.querySelector('.city-filter-group');
        if (cityContainer) {
            cityContainer.addEventListener('click', (e) => {
                const pill = e.target.closest('.filter-pill');
                if (pill && pill.dataset.city) {
                    appStore.set('city', pill.dataset.city);
                }
            });
            cityContainer.addEventListener('change', (e) => {
                if (e.target.id === 'city-select') {
                    appStore.set('city', e.target.value);
                }
            });
        }

        // Filtro de Formato (Presencial, Remoto, Todos)
        const formatContainer = document.querySelector('.format-filter-group');
        if (formatContainer) {
            formatContainer.addEventListener('click', (e) => {
                const pill = e.target.closest('.filter-pill');
                if (pill && pill.dataset.format) {
                    formatContainer.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
                    pill.classList.add('active');
                    appStore.set('formatFilter', pill.dataset.format);
                }
            });
        }

        // Subscripciones a store
        appStore.subscribe('city', (city) => this.onCityChange(city));
        appStore.subscribe('lang', (lang) => this.onLangChange(lang));

        // Responsive resize
        let lastMobile = window.matchMedia('(max-width: 768px)').matches;
        window.addEventListener('resize', () => {
            const nowMobile = window.matchMedia('(max-width: 768px)').matches;
            if (nowMobile !== lastMobile) {
                lastMobile = nowMobile;
                this.renderTabs();
            }
        });
    }

    updateUrlParams() {
        const params = new URLSearchParams(window.location.search);
        const city = appStore.get('city');
        const lang = appStore.get('lang');
        const format = appStore.get('formatFilter');

        if (city) params.set('city', city);
        else params.delete('city');

        if (lang && lang !== CONFIG.LANGUAGES.DEFAULT) params.set('lang', lang);
        else params.delete('lang');

        if (format && format !== 'all') params.set('format', format);
        else params.delete('format');

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
            this.loadFeaturedEvents(city);
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
        this.renderTabs();
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
            if (calendarContainer) {
                const msg = `No hay datos para "${city}". Ejecuta: make run-all`;
                calendarContainer.innerHTML = `<div class="events-error">${msg}</div>`;
            }
        }
    }

    async loadFeaturedEvents(city) {
        const listContainer = document.getElementById('featured-events-list');
        if (!listContainer) return;

        try {
            const data = await DataService.getCityData(city);
            const events = Array.isArray(data) ? data : (data.events || []);
            const now = new Date();
            
            // Tomar los próximos 4 eventos a partir de hoy
            const upcoming = events.filter(e => {
                if (!e.dtstart) return false;
                return new Date(e.dtstart) >= new Date(now.getFullYear(), now.getMonth(), now.getDate());
            }).sort((a, b) => new Date(a.dtstart) - new Date(b.dtstart)).slice(0, 4);

            if (upcoming.length === 0) {
                listContainer.innerHTML = `<div class="events-empty">${i18n.t('calendar.noEvents')}</div>`;
                return;
            }

            const tempCalendar = new Calendar('featured-events-list');
            listContainer.innerHTML = '';
            upcoming.forEach(e => {
                listContainer.appendChild(tempCalendar.createEventCard(e));
            });
        } catch (e) {
            console.error(e);
        }
    }

    updateDownloadLinks(city) {
        const setHref = (id, url) => {
            const el = document.getElementById(id);
            if (el) el.href = url;
        };

        setHref('download-ics-btn', CONFIG.PATHS.getIcsUrl(city));
        setHref('download-json-btn', CONFIG.PATHS.getDataUrl(city));
        setHref('webcal-btn', CONFIG.PATHS.getWebCalUrl(city));
    }
}

// Bootstrap
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});

// Clipboard WebCal
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
