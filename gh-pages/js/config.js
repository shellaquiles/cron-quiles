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

    // Ciudades soportadas y sus metadatos
    CITIES: {
        DEFAULT: 'mexico',
        SUPPORTED: ['mexico', 'cdmx', 'gdl', 'puebla', 'monterrey'],
        NAMES: {
            'mexico': 'México',
            'cdmx': 'Ciudad de México',
            'gdl': 'Guadalajara',
            'puebla': 'Puebla',
            'monterrey': 'Monterrey'
        }
    },

    // Intervalos de tiempo
    REFRESH_INTERVAL: 6 * 60 * 60 * 1000, // 6 horas (referencia visual)

    // Rutas de archivos (se asume relativo a la raíz del sitio)
    PATHS: {
        getDataUrl: (city) => city === 'mexico' ? `data/cronquiles-mexico.json` : `data/cronquiles-${city}.json`,
        getIcsUrl: (city) => city === 'mexico' ? `data/cronquiles-mexico.ics` : `data/cronquiles-${city}.ics`,
        getWebCalUrl: (city) => `webcal://${window.location.host}${window.location.pathname.replace('index.html', '')}data/cronquiles-${city}.ics`
    }
};
