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
        this.renderTabs();

        // 1. Restaurar estado (idioma y ciudad)
        const savedLang = Storage.get(CONFIG.STORAGE_KEYS.LANG) || CONFIG.LANGUAGES.DEFAULT;
        let savedCity = Storage.get(CONFIG.STORAGE_KEYS.CITY) || CONFIG.CITIES.DEFAULT;

        // Verificar que la ciudad guardada aún exista en los metadatos (si no, usar default)
        if (this.states.length > 0 && !this.states.find(s => s.slug === savedCity)) {
            savedCity = CONFIG.CITIES.DEFAULT;
        }

        // Esto disparará las suscripciones iniciales en I18n y Header
        appStore.set('lang', savedLang);
        appStore.set('city', savedCity);

        // 2. Event listeners globales
        this.bindEvents();

        // 3. Cargar datos iniciales
        this.loadCityData(savedCity);
    }

    renderTabs() {
        const container = document.querySelector('.city-tabs');
        if (!container || !this.states.length) return;

        container.innerHTML = this.states.map(state => `
            <button class="city-tab" data-city="${state.slug}" aria-label="${state.name}">
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
    }

    onCityChange(city) {
        // Persistir
        Storage.set(CONFIG.STORAGE_KEYS.CITY, city);

        // Actualizar UI Tabs
        document.querySelectorAll('.city-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.city === city);
        });

        // Actualizar datos
        this.loadCityData(city);
        this.updateDownloadLinks(city);
    }

    onLangChange(lang) {
        Storage.set(CONFIG.STORAGE_KEYS.LANG, lang);
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
