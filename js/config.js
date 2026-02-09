/**
 * Configuración central de la aplicación
 * Define constantes y opciones para fácil mantenimiento.
 */
export const CONFIG = {
    // Configuración de LocalStorage
    STORAGE_KEYS: {
        LANG: 'cron-quiles-lang',
        CITY: 'cron-quiles-city'
    },

    // Idiomas soportados
    LANGUAGES: {
        DEFAULT: 'es',
        SUPPORTED: ['es', 'en']
    },

    // Ciudades/Estados soportadas (se cargarán dinámicamente)
    CITIES: {
        DEFAULT: 'mexico'
    },

    // Intervalos de tiempo
    REFRESH_INTERVAL: 6 * 60 * 60 * 1000, // 6 horas (referencia visual)

    // Rutas de archivos (se asume relativo a la raíz del sitio)
    PATHS: {
        getMetadataUrl: () => `data/states_metadata.json`,
        getDataUrl: (city) => city === 'mexico' ? `data/cronquiles-mexico.json` : `data/cronquiles-${city}.json`,
        getIcsUrl: (city) => city === 'mexico' ? `data/cronquiles-mexico.ics` : `data/cronquiles-${city}.ics`,
        getWebCalUrl: (city) => {
            const base = (window.location.pathname || '/').replace(/\/[^/]*$/, '/');
            return `webcal://${window.location.host}${base}data/cronquiles-${city}.ics`;
        }
    }
};
