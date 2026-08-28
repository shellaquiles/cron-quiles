/**
 * Servicio de Internacionalización
 * Maneja traducciones y formateo de fechas/monedas.
 */
import { CONFIG } from '../config.js';
import { appStore } from './Store.js';

// Diccionario de textos
const TRANSLATIONS = {
    es: {
        'site.subtitle': 'Calendario unificado de eventos tech en México',
        'theme.dark': 'MODO OSCURO',
        'theme.light': 'MODO CLARO',
        'filter.city': 'CIUDAD:',
        'filter.format': 'FORMATO:',
        'filter.all': 'TODOS',
        'filter.inPerson': 'PRESENCIAL',
        'filter.online': 'REMOTO',
        'badge.live': 'HOY',
        'desc.content': 'Este calendario agrega eventos de múltiples fuentes (Meetup, Luma, etc.) en un solo lugar. Los eventos se actualizan automáticamente cada 6 horas.',
        'calendar.title': 'Calendario de Eventos',
        'calendar.loading': 'Cargando eventos...',
        'calendar.empty': 'No hay eventos disponibles para mostrar.',
        'calendar.noEvents': 'No hay eventos programados en este periodo.',
        'section.communities': 'Comunidades Integradas',
        'section.communitiesLead': 'Grupos y gremios técnicos activos que forman parte de la red de Cron-Quiles.',
        'section.ics': 'Calendario ICS',
        'section.json': 'Datos JSON',
        'section.howto': 'Cómo usar',
        'badge.recommended': 'Recomendado',
        'ics.description': 'Archivo ICS estándar compatible con Google Calendar, Apple Calendar, Outlook y cualquier cliente de calendario.',
        'json.description': 'Archivo JSON con todos los eventos para uso programático o análisis.',
        'btn.register': 'Registro ↗',
        'btn.join': 'Unirse ↗',
        'btn.addCal': '+ Cal',
        'btn.download.ics': 'Descargar ICS',
        'btn.copy.webcal': 'Copiar WebCal',
        'btn.download.json': 'Descargar JSON',
        'btn.copied': '✓ Copiado!',
        'tip.label': 'Tip:',
        'tip.content': 'Para suscribirte automáticamente, usa la URL de WebCal o importa el archivo ICS en tu calendario favorito. Los eventos se actualizarán automáticamente.',
        'howto.google': 'Haz clic en "Copiar enlace" y pega la URL en Añadir calendario → Por URL',
        'howto.apple': 'Archivo → Nueva suscripción de calendario → pega la URL',
        'howto.outlook': 'Agregar calendario → Suscribir desde web → pega la URL',
        'communities.viewAll': 'Ver lista completa de comunidades integrada →',
        'communities.addYours': '¿Quieres agregar tu comunidad? Abre un PR o Issue en el repositorio.',
        'footer.project': 'Proyecto open source de la comunidad',
        'footer.github': 'Ver en GitHub',
        'footer.docs': 'Documentación',
        'footer.lastUpdate': 'Última actualización:',
        'footer.loading': 'Cargando...',
        'footer.notAvailable': 'No disponible',
        'cal.prev': '◀ Anterior',
        'cal.next': 'Siguiente ▶',
        'cal.today': 'Hoy',
        'cal.takeCalendar': 'Llévate este calendario',
        'cal.showMore': 'Ver más ↓',
        'cal.showLess': 'Ver menos ↑',
        'cal.eventsOf': 'Eventos de',
        'cal.viewEvent': 'Registro ↗',
        'cal.viewOnMap': 'Ver en mapa ↗',
        'cal.online': 'ONLINE',
        'cal.loadMore': 'Cargar siguiente mes ↓',
        'nav.eventos': 'Eventos',
        'nav.comunidades': 'Comunidades',
        'nav.descargar': 'Descargar',
        'nav.addCalendar': 'Añadir al calendario',
        'nav.howto': 'Cómo usar',
        'nav.cityLabel': 'Ciudad',
        'nav.linkInicio': 'Inicio',
        'nav.linkEventos': 'Eventos',
        'nav.linkSuscribir': 'Añadir al calendario',
        'nav.linkComunidades': 'Comunidades',
        'landing.verEventos': 'Ver eventos ↗',
        'landing.anadirCalendario': 'Añadir a mi calendario',
        'hint.welcome': 'Elige tu ciudad para ver eventos.',
        'hint.whereEvents': '¿Dónde buscas eventos?',
        'hint.whatIsThis': '¿Qué es esto?',
        'section.addCalendar': 'Añadir a mi calendario',
        'section.addCalendarLead': 'Sincroniza los eventos en tiempo real con Google Calendar, Apple Calendar o Outlook.',
        'btn.copy.webcal.plain': 'Copiar enlace de suscripción',
        'btn.copy.webcal.hint': 'Pega el enlace en tu app de calendario favorita para sincronización continua.',
        'btn.download.ics.plain': 'Descargar archivo (.ics)',
        'section.howtoLead': 'Pasos para suscribirte en tu cliente de calendario:',
        'months': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        'days': ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
        'locale': 'es-MX'
    },
    en: {
        'site.subtitle': 'Unified tech events calendar in Mexico',
        'theme.dark': 'DARK MODE',
        'theme.light': 'LIGHT MODE',
        'filter.city': 'CITY:',
        'filter.format': 'FORMAT:',
        'filter.all': 'ALL',
        'filter.inPerson': 'IN-PERSON',
        'filter.online': 'REMOTE',
        'badge.live': 'TODAY',
        'desc.content': 'This calendar aggregates tech events from multiple sources (Meetup, Luma, etc.) into a single place. Automatically updated every 6 hours.',
        'calendar.title': 'Events Calendar',
        'calendar.loading': 'Loading events...',
        'calendar.empty': 'No events available to display.',
        'calendar.noEvents': 'No events scheduled for this period.',
        'section.communities': 'Integrated Communities',
        'section.communitiesLead': 'Active tech groups and guilds powering the Cron-Quiles ecosystem.',
        'section.ics': 'ICS Calendar',
        'section.json': 'JSON Data',
        'section.howto': 'How to use',
        'badge.recommended': 'Recommended',
        'ics.description': 'Standard ICS calendar file compatible with Google Calendar, Apple Calendar, Outlook and any calendar client.',
        'json.description': 'Raw JSON file containing all events for programmatic integrations and data analysis.',
        'btn.register': 'Register ↗',
        'btn.join': 'Join ↗',
        'btn.addCal': '+ Cal',
        'btn.download.ics': 'Download ICS',
        'btn.copy.webcal': 'Copy WebCal',
        'btn.download.json': 'Download JSON',
        'btn.copied': '✓ Copied!',
        'tip.label': 'Tip:',
        'tip.content': 'To subscribe automatically, use the WebCal URL or import the ICS file in your calendar app.',
        'howto.google': 'Click "Copy Link" and paste into Add Calendar → From URL',
        'howto.apple': 'File → New Calendar Subscription → paste URL',
        'howto.outlook': 'Add Calendar → Subscribe from web → paste URL',
        'communities.viewAll': 'View full list of integrated communities →',
        'communities.addYours': 'Want to add your community? Open a PR or Issue on GitHub.',
        'footer.project': 'Open source community project by',
        'footer.github': 'View on GitHub',
        'footer.docs': 'Documentation',
        'footer.lastUpdate': 'Last update:',
        'footer.loading': 'Loading...',
        'footer.notAvailable': 'Not available',
        'cal.prev': '◀ Prev',
        'cal.next': 'Next ▶',
        'cal.today': 'Today',
        'cal.takeCalendar': 'Subscribe to this calendar',
        'cal.showMore': 'Show more ↓',
        'cal.showLess': 'Show less ↑',
        'cal.eventsOf': 'Events of',
        'cal.viewEvent': 'Register ↗',
        'cal.viewOnMap': 'View on map ↗',
        'cal.online': 'ONLINE',
        'cal.loadMore': 'Load next month ↓',
        'nav.eventos': 'Events',
        'nav.comunidades': 'Communities',
        'nav.descargar': 'Download',
        'nav.addCalendar': 'Add to calendar',
        'nav.howto': 'How to use',
        'nav.cityLabel': 'City',
        'nav.linkInicio': 'Home',
        'nav.linkEventos': 'Events',
        'nav.linkSuscribir': 'Add to calendar',
        'nav.linkComunidades': 'Communities',
        'landing.verEventos': 'View events ↗',
        'landing.anadirCalendario': 'Add to my calendar',
        'hint.welcome': 'Choose your city to view events.',
        'hint.whereEvents': 'Where are you looking for events?',
        'hint.whatIsThis': 'What is this?',
        'section.addCalendar': 'Add to my calendar',
        'section.addCalendarLead': 'Sync events in real-time with Google Calendar, Apple Calendar, or Outlook.',
        'btn.copy.webcal.plain': 'Copy subscription link',
        'btn.copy.webcal.hint': 'Paste link in your favorite calendar app for ongoing synchronization.',
        'btn.download.ics.plain': 'Download file (.ics)',
        'section.howtoLead': 'Steps to subscribe in your calendar client:',
        'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        'days': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        'locale': 'en-US'
    }
};

export class I18nService {
    constructor() {
        this.lang = CONFIG.LANGUAGES.DEFAULT;

        // Suscribirse a cambios de idioma en el store
        appStore.subscribe('lang', (newLang) => {
            this.lang = newLang;
            this.updateDOM();
        });
    }

    /**
     * Obtiene una traducción por clave
     */
    t(key) {
        return TRANSLATIONS[this.lang]?.[key] || TRANSLATIONS['es'][key] || key;
    }

    /**
     * Obtiene el locale actual (ej. es-MX)
     */
    getLocale() {
        return this.t('locale');
    }

    /**
     * Actualiza todos los elementos del DOM con atributo data-i18n
     */
    updateDOM() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            const translation = this.t(key);
            if (translation && translation !== key) {
                el.textContent = translation;
            }
        });
        document.documentElement.lang = this.lang;
    }
}

export const i18n = new I18nService();
