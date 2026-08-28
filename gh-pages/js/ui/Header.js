/**
 * Componente Header con Selector Multitema
 */
import { i18n } from '../core/I18n.js';
import { appStore } from '../core/Store.js';
import { DataService } from '../services/DataService.js';

export const THEMES = [
    { id: 'green', name: 'VERDE MATRIX', icon: '🟢', isDark: true },
    { id: 'amber', name: 'ÁMBAR VT220', icon: '🟠', isDark: true },
    { id: 'cyan', name: 'CYBERPUNK', icon: '🔵', isDark: true },
    { id: 'obsidian', name: 'OBSIDIAN', icon: '⚪', isDark: true },
    { id: 'solarized', name: 'SOLARIZED', icon: '🔷', isDark: true },
    { id: 'light', name: 'MODO CLARO', icon: '☀️', isDark: false }
];

export class Header {
    constructor() {
        this.currentThemeIndex = 0;
        this.initTheme();
        this.bindEvents();
        
        appStore.subscribe('city', () => this.updateLastModified());
        appStore.subscribe('lang', () => {
            this.updateLastModified();
            this.updateThemeLabels();
        });
    }

    initTheme() {
        const savedThemeId = localStorage.getItem('theme_preset') || (localStorage.getItem('theme') === 'light' ? 'light' : 'green');
        const themeIdx = THEMES.findIndex(t => t.id === savedThemeId);
        this.currentThemeIndex = themeIdx !== -1 ? themeIdx : 0;
        this.applyTheme(THEMES[this.currentThemeIndex]);
    }

    applyTheme(themeObj) {
        const htmlElement = document.documentElement;
        const themeLabel = document.getElementById('themeLabel');
        const themeIcon = document.getElementById('themeIcon');
        
        // Limpiar clases y asignar dataset
        htmlElement.setAttribute('data-theme', themeObj.id);

        if (themeObj.isDark) {
            htmlElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            htmlElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }

        localStorage.setItem('theme_preset', themeObj.id);

        if (themeLabel) themeLabel.textContent = themeObj.name;
        if (themeIcon) themeIcon.textContent = themeObj.icon;
    }

    cycleTheme() {
        this.currentThemeIndex = (this.currentThemeIndex + 1) % THEMES.length;
        this.applyTheme(THEMES[this.currentThemeIndex]);
    }

    setThemeById(themeId) {
        const idx = THEMES.findIndex(t => t.id === themeId);
        if (idx !== -1) {
            this.currentThemeIndex = idx;
            this.applyTheme(THEMES[idx]);
        }
    }

    updateThemeLabels() {
        const currentTheme = THEMES[this.currentThemeIndex];
        const themeLabel = document.getElementById('themeLabel');
        if (themeLabel && currentTheme) {
            themeLabel.textContent = currentTheme.name;
        }
    }

    bindEvents() {
        // Theme Toggle / Ciclo de Temas
        const themeToggleBtn = document.getElementById('themeToggle');
        if (themeToggleBtn) {
            themeToggleBtn.addEventListener('click', () => {
                this.cycleTheme();
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
