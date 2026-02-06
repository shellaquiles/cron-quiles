/**
 * Cron-Quiles Frontend Entry Point
 *
 * Orquestador principal que inicializa servicios y componentes.
 */
import { CONFIG } from './config.js';
import { i18n } from './core/I18n.js';
import { appStore } from './core/Store.js';
import { DataService } from './services/DataService.js';
import { Storage } from './services/Storage.js';
import { Calendar } from './ui/Calendar.js';
import { CommunityList } from './ui/CommunityList.js';
import { Header } from './ui/Header.js';

class App {
    constructor() {
        this.header = new Header();
        this.calendar = new Calendar('calendar-container');
        this.communityList = new CommunityList('communities-grid');

        this.init();
    }

    async init() {
        // 0. Cargar metadatos de estados
        this.states = await DataService.getStatesMetadata();

        // 1. Restaurar estado desde URL params, luego localStorage, luego defaults
        const urlParams = new URLSearchParams(window.location.search);
        const savedLang = urlParams.get('lang') || Storage.get(CONFIG.STORAGE_KEYS.LANG) || CONFIG.LANGUAGES.DEFAULT;
        let savedCity = urlParams.get('city') || Storage.get(CONFIG.STORAGE_KEYS.CITY) || CONFIG.CITIES.DEFAULT;

        // Verificar que la ciudad guardada aún exista en los metadatos (si no, usar default)
        if (this.states.length > 0 && !this.states.find(s => s.slug === savedCity)) {
            savedCity = CONFIG.CITIES.DEFAULT;
        }

        // Inicializar estado sin disparar suscripciones aún
        appStore.set('lang', savedLang);
        appStore.set('city', savedCity);

        // Sincronizar URL con el estado inicial
        this.updateUrlParams();

        // Renderizar tabs con ciudad activa
        this.renderTabs();

        // 2. Event listeners globales (después de init para evitar efectos durante arranque)
        this.bindEvents();

        // 3. Cargar datos iniciales
        this.loadCityData(savedCity);
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

        container.innerHTML = visibleStates.map(state => `
            <button class="city-tab ${state.slug === currentCity ? 'active' : ''}" data-city="${state.slug}" aria-label="${state.name}">
                ${state.emoji} ${state.name}
            </button>
        `).join('');
    }

    bindEvents() {
        // Cambio de ciudad (Delegación de eventos para tabs dinámicos)
        document.querySelector('.city-tabs').addEventListener('click', (e) => {
            const tab = e.target.closest('.city-tab');
            if (tab) {
                const city = tab.dataset.city;
                if (city) appStore.set('city', city);
            }
        });

        // Reacción a cambios de estado
        appStore.subscribe('city', (city) => this.onCityChange(city));
        appStore.subscribe('lang', (lang) => this.onLangChange(lang));
        appStore.subscribe('showPastEvents', () => this.renderTabs());
        appStore.subscribe('viewDate', () => this.renderTabs());
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
        // Persistir
        Storage.set(CONFIG.STORAGE_KEYS.CITY, city);
        this.updateUrlParams();

        // Re-render tabs to update active class (and potentially visibility if logic changes)
        this.renderTabs();

        // Actualizar datos
        this.loadCityData(city);
        this.updateDownloadLinks(city);
    }

    onLangChange(lang) {
        Storage.set(CONFIG.STORAGE_KEYS.LANG, lang);
        this.updateUrlParams();
        // Calendar se repinta automáticamente si reusamos los datos,
        // pero por simplicidad de este refactor, re-renderizamos con lo que tenga
        this.calendar.render();
    }

    async loadCityData(city) {
        const calendarContainer = document.getElementById('calendar-container');
        if (calendarContainer) {
            calendarContainer.innerHTML = `<div class="events-loading">${i18n.t('calendar.loading')}</div>`;
        }

        try {
            const data = await DataService.getCityData(city);
            const events = Array.isArray(data) ? data : (data.events || []);

            this.calendar.setEvents(events);
            this.communityList.render(data.communities || []);

        } catch (error) {
            console.error(error);
            const container = document.getElementById('calendar-container');
            if (container) {
                const isLocal = window.location.protocol === 'file:';
                const msg = isLocal
                    ? `Error: Protocolo file:// no soportado para fetch. Usa un servidor local.`
                    : `Error loading data for ${city}`;
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

// Helper global para copiar WebCal (mantenido del original, se podría mover a Utils)
document.querySelectorAll('.btn-secondary').forEach(btn => {
    if (btn.id === 'webcal-btn') {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.href.replace('webcal://', 'https://');
            navigator.clipboard.writeText(url).then(() => {
                const originalText = this.textContent;
                this.textContent = i18n.t('btn.copied');
                setTimeout(() => {
                    this.textContent = i18n.t('btn.copy.webcal');
                }, 2000);
            });
        });
    }
});
