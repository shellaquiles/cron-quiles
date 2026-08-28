/**
 * Componente Header con Switcher Dual (Modo Claro / Modo Matrix)
 */
import { i18n } from '../core/I18n.js';
import { appStore } from '../core/Store.js';
import { DataService } from '../services/DataService.js';

export const BRAND_LOGOS = {
    calendar: {
        id: 'calendar',
        name: 'Concepto 1: The Cron Calendar Terminal (>_ Cursor)',
        svg: `<svg class="brand-logo-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="17" rx="2"></rect>
            <line x1="8" y1="2" x2="8" y2="5"></line>
            <line x1="16" y1="2" x2="16" y2="5"></line>
            <line x1="3" y1="9" x2="21" y2="9"></line>
            <path d="M7 14l3 2-3 2"></path>
            <line x1="13" y1="18" x2="17" y2="18" class="prompt-cursor"></line>
        </svg>`
    },
    cronloop: {
        id: 'cronloop',
        name: 'Concepto 2: The Cronjob Loop (* * * * * + Clock)',
        svg: `<svg class="brand-logo-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9"></circle>
            <line x1="12" y1="3" x2="12" y2="5"></line>
            <line x1="12" y1="19" x2="12" y2="21"></line>
            <path d="M8 10l3 2-3 2"></path>
            <line x1="13" y1="14" x2="16" y2="14" class="prompt-cursor"></line>
        </svg>`
    },
    matrixgrid: {
        id: 'matrixgrid',
        name: 'Concepto 3: The Swiss Matrix Grid ([ $ ])',
        svg: `<svg class="brand-logo-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="1"></rect>
            <line x1="3" y1="8" x2="21" y2="8"></line>
            <path d="M7 13l2 2-2 2"></path>
            <line x1="12" y1="17" x2="16" y2="17" class="prompt-cursor"></line>
            <circle cx="17" cy="12" r="1.5" fill="currentColor"></circle>
        </svg>`
    },
    hex: {
        id: 'hex',
        name: 'Concepto 4: Caparazón Hexagonal (Terminal Shell)',
        svg: `<svg class="brand-logo-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L21 7.5V16.5L12 22L3 16.5V7.5L12 2Z"></path>
            <path d="M12 2V22"></path>
            <path d="M3 7.5L21 16.5"></path>
            <path d="M3 16.5L21 7.5"></path>
            <circle cx="12" cy="12" r="2.5" fill="currentColor"></circle>
        </svg>`
    },
    grid: {
        id: 'grid',
        name: 'Concepto 5: Cronómetro / Pixel-Grid',
        svg: `<svg class="brand-logo-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="1"></rect>
            <path d="M3 9H21"></path>
            <path d="M3 15H21"></path>
            <path d="M9 3V21"></path>
            <path d="M15 3V21"></path>
            <path d="M9 9L15 15" stroke-width="2.5"></path>
        </svg>`
    },
    prompt: {
        id: 'prompt',
        name: 'Concepto 6: Typographic Prompt ($> Shell)',
        svg: `<svg class="brand-logo-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 17L10 12L4 7"></path>
            <line x1="12" y1="17" x2="20" y2="17" stroke-width="2.5"></line>
        </svg>`
    }
};

export class Header {
    constructor() {
        this.initTheme();
        this.initBrandLogo();
        this.bindEvents();
        
        appStore.subscribe('city', () => this.updateLastModified());
        appStore.subscribe('lang', () => {
            this.updateLastModified();
            this.updateThemeLabels();
        });
    }

    initTheme() {
        const savedTheme = localStorage.getItem('theme');
        // Por defecto SIEMPRE oscuro (salvo que se haya guardado explícitamente 'light')
        const isDark = savedTheme !== 'light';
        this.applyTheme(isDark);
    }

    applyTheme(isDark) {
        const htmlElement = document.documentElement;
        const themeLabel = document.getElementById('themeLabel');
        const themeIcon = document.getElementById('themeIcon');
        
        if (isDark) {
            htmlElement.classList.add('dark');
            htmlElement.classList.remove('light');
            if (themeLabel) themeLabel.textContent = i18n.t('theme.light') || 'MODO CLARO';
            if (themeIcon) themeIcon.textContent = '☀️';
            localStorage.setItem('theme', 'dark');
        } else {
            htmlElement.classList.remove('dark');
            htmlElement.classList.add('light');
            if (themeLabel) themeLabel.textContent = 'MATRIX OSCURO';
            if (themeIcon) themeIcon.textContent = '🟢';
            localStorage.setItem('theme', 'light');
        }

        const currentLogo = localStorage.getItem('brand_logo') || 'calendar';
        this.updateFavicon(currentLogo);
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

    initBrandLogo() {
        const savedLogo = localStorage.getItem('brand_logo') || 'calendar';
        this.applyLogo(savedLogo);
    }

    updateFavicon(logoKey) {
        const isDark = document.documentElement.classList.contains('dark') || !document.documentElement.classList.contains('light');
        const strokeColor = isDark ? '%2300ff66' : '%2309090b';
        const bgColor = isDark ? '%23040805' : '%23ffffff';

        let svgIcon = '';
        if (logoKey === 'calendar') {
            svgIcon = `<rect x='3' y='4' width='18' height='17' rx='2' stroke='${strokeColor}' stroke-width='2'/><line x1='8' y1='2' x2='8' y2='5' stroke='${strokeColor}' stroke-width='2'/><line x1='16' y1='2' x2='16' y2='5' stroke='${strokeColor}' stroke-width='2'/><line x1='3' y1='9' x2='21' y2='9' stroke='${strokeColor}' stroke-width='2'/><path d='M7 14l3 2-3 2' stroke='${strokeColor}' stroke-width='2'/><line x1='13' y1='18' x2='17' y2='18' stroke='${strokeColor}' stroke-width='2'/>`;
        } else if (logoKey === 'cronloop') {
            svgIcon = `<circle cx='12' cy='12' r='9' stroke='${strokeColor}' stroke-width='2'/><line x1='12' y1='3' x2='12' y2='5' stroke='${strokeColor}' stroke-width='2'/><line x1='12' y1='19' x2='12' y2='21' stroke='${strokeColor}' stroke-width='2'/><path d='M8 10l3 2-3 2' stroke='${strokeColor}' stroke-width='2'/><line x1='13' y1='14' x2='16' y2='14' stroke='${strokeColor}' stroke-width='2'/>`;
        } else if (logoKey === 'matrixgrid') {
            svgIcon = `<rect x='3' y='3' width='18' height='18' rx='1' stroke='${strokeColor}' stroke-width='2'/><line x1='3' y1='8' x2='21' y2='8' stroke='${strokeColor}' stroke-width='2'/><path d='M7 13l2 2-2 2' stroke='${strokeColor}' stroke-width='2'/><line x1='12' y1='17' x2='16' y2='17' stroke='${strokeColor}' stroke-width='2'/><circle cx='17' cy='12' r='1.5' fill='${strokeColor}'/>`;
        } else {
            svgIcon = `<path d='M12 2L21 7.5V16.5L12 22L3 16.5V7.5L12 2Z' stroke='${strokeColor}' stroke-width='1.8'/><path d='M12 2V22' stroke='${strokeColor}' stroke-width='1.8'/><path d='M3 7.5L21 16.5' stroke='${strokeColor}' stroke-width='1.8'/><path d='M3 16.5L21 7.5' stroke='${strokeColor}' stroke-width='1.8'/><circle cx='12' cy='12' r='2.5' fill='${strokeColor}'/>`;
        }

        const faviconDataUrl = `data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'>${svgIcon}</svg>`;
        
        let link = document.querySelector("link[rel~='icon']");
        if (!link) {
            link = document.createElement('link');
            link.rel = 'icon';
            document.head.appendChild(link);
        }
        link.href = faviconDataUrl;
    }

    initTypography() {
        const savedTypo = localStorage.getItem('brand_typography') || 'mono';
        this.applyTypography(savedTypo);
    }

    applyTypography(typoKey) {
        const brandTitleEls = document.querySelectorAll('.brand-title');
        brandTitleEls.forEach(el => {
            el.classList.remove('brand-swiss', 'brand-mono');
            if (typoKey === 'swiss') {
                el.classList.add('brand-swiss');
            } else {
                el.classList.add('brand-mono');
            }
        });
        localStorage.setItem('brand_typography', typoKey);
    }

    cycleTypography() {
        const current = localStorage.getItem('brand_typography') || 'mono';
        const next = current === 'mono' ? 'swiss' : 'mono';
        this.applyTypography(next);
    }

    applyLogo(logoKey) {
        const logoConfig = BRAND_LOGOS[logoKey] || BRAND_LOGOS.calendar;
        const brandTitleEls = document.querySelectorAll('.brand-title');
        
        brandTitleEls.forEach(el => {
            el.innerHTML = `${logoConfig.svg}<span class="brand-text">CRON-QUILES</span>`;
            el.setAttribute('title', `Logo: ${logoConfig.name} (Clic/'L': cambiar logo | 'F': cambiar tipografía)`);
        });

        const currentTypo = localStorage.getItem('brand_typography') || 'mono';
        this.applyTypography(currentTypo);

        this.updateFavicon(logoConfig.id);
        localStorage.setItem('brand_logo', logoConfig.id);
    }

    cycleLogo() {
        const keys = Object.keys(BRAND_LOGOS);
        const currentKey = localStorage.getItem('brand_logo') || 'calendar';
        const currentIndex = keys.indexOf(currentKey);
        const nextKey = keys[(currentIndex + 1) % keys.length];
        this.applyLogo(nextKey);
    }

    bindEvents() {
        // Clic en el logo para alternar logos de forma interactiva
        document.querySelectorAll('.brand-title').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                this.cycleLogo();
            });
        });

        // Atajos de teclado:
        // 'L' -> Cambiar logo SVG
        // 'F' -> Cambiar tipografía (Swiss Grotesk vs CLI Mono)
        document.addEventListener('keydown', (e) => {
            if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;
            const key = e.key.toLowerCase();
            if (key === 'l') {
                this.cycleLogo();
            } else if (key === 'f') {
                this.cycleTypography();
            }
        });

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

    async updateVersion() {
        const elements = document.querySelectorAll('[data-version]');
        if (!elements.length) return;

        const city = appStore.get('city');
        const version = await DataService.getVersion(city);
        if (version) {
            elements.forEach(el => { el.textContent = `v${version}`; });
        }
        // Si no hay version en el JSON, el fallback estático del HTML permanece
    }
}
