/**
 * Componente Header con Switcher Dual (Modo Claro / Modo Matrix)
 */
import { i18n } from '../core/I18n.js';
import { appStore } from '../core/Store.js';
import { DataService } from '../services/DataService.js';

export class Header {
    constructor() {
        this.initTheme();
        this.bindEvents();
        
        appStore.subscribe('city', () => this.updateLastModified());
        appStore.subscribe('lang', () => {
            this.updateLastModified();
            this.updateThemeLabels();
        });
    }

    initTheme() {
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        const isDark = savedTheme ? savedTheme === 'dark' : (savedTheme === null ? true : systemPrefersDark);
        this.applyTheme(isDark);
    }

    applyTheme(isDark) {
        const htmlElement = document.documentElement;
        const themeLabel = document.getElementById('themeLabel');
        const themeIcon = document.getElementById('themeIcon');
        
        if (isDark) {
            htmlElement.classList.add('dark');
            htmlElement.removeAttribute('data-theme');
            if (themeLabel) themeLabel.textContent = i18n.t('theme.light') || 'MODO CLARO';
            if (themeIcon) themeIcon.textContent = '☀️';
            localStorage.setItem('theme', 'dark');
        } else {
            htmlElement.classList.remove('dark');
            htmlElement.removeAttribute('data-theme');
            if (themeLabel) themeLabel.textContent = 'MATRIX OSCURO';
            if (themeIcon) themeIcon.textContent = '🟢';
            localStorage.setItem('theme', 'light');
        }
    }

    toggleTheme() {
        const isCurrentlyDark = document.documentElement.classList.contains('dark');
        this.applyTheme(!isCurrentlyDark);
    }

    updateThemeLabels() {
        const isDark = document.documentElement.classList.contains('dark');
        const themeLabel = document.getElementById('themeLabel');
        const themeIcon = document.getElementById('themeIcon');
        if (themeLabel) {
            themeLabel.textContent = isDark ? (i18n.t('theme.light') || 'MODO CLARO') : 'MATRIX OSCURO';
        }
        if (themeIcon) {
            themeIcon.textContent = isDark ? '☀️' : '🟢';
        }
    }

    bindEvents() {
        // Theme Toggle (Alternar entre Claro y Matrix)
        const themeToggleBtn = document.getElementById('themeToggle');
        if (themeToggleBtn) {
            themeToggleBtn.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

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
        if (!element || !city) return;

        element.textContent = i18n.t('footer.loading');

        const date = await DataService.getLastModified(city);
        if (date) {
            element.textContent = date.toLocaleString(i18n.getLocale(), {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                timeZone: 'America/Mexico_City'
            });
        } else {
            element.textContent = i18n.t('footer.notAvailable');
        }
    }
}
