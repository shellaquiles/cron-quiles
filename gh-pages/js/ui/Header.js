/**
 * Componente Header
 * Maneja el switch de idioma y la visualización de la última actualización
 */
import { i18n } from '../core/I18n.js';
import { appStore } from '../core/Store.js';
import { DataService } from '../services/DataService.js';

export class Header {
    constructor() {
        this.bindEvents();
        // Suscribirse a cambios para actualizar fecha
        appStore.subscribe('city', () => this.updateLastModified());
        appStore.subscribe('lang', () => this.updateLastModified());
    }

    bindEvents() {
        // Language Switcher
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const lang = btn.dataset.lang;
                appStore.set('lang', lang);
            });
        });

        // Actualizar UI activa del idioma
        appStore.subscribe('lang', (currentLang) => {
            document.querySelectorAll('.lang-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.lang === currentLang);
            });
        });
    }

    async updateLastModified() {
        const city = appStore.get('city');
        const element = document.getElementById('last-update');
        if (!element) return;

        element.textContent = i18n.t('footer.loading');

        const date = await DataService.getLastModified(city);
        if (date) {
            // Formato personalizado para fecha/hora
            element.textContent = date.toLocaleString(i18n.getLocale(), {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } else {
            element.textContent = i18n.t('footer.notAvailable');
        }
    }
}
