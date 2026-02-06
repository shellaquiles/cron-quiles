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
        'cmd.description': 'cat descripcion.txt',
        'cmd.calendar': './calendario.sh',
        'cmd.files': 'ls calendarios/',
        'cmd.json': 'cat datos.json',
        'cmd.tips': 'cat tips.txt',
        'cmd.howto': './como-usar.sh',
        'desc.content': 'Este calendario agrega eventos de múltiples fuentes (Meetup, Luma, etc.) en un solo lugar. Los eventos se actualizan automáticamente cada 6 horas.',
        'calendar.title': '📅 Calendario de Eventos',
        'calendar.loading': 'Cargando calendario...',
        'calendar.empty': 'No hay eventos disponibles para mostrar en el calendario',
        'calendar.noEvents': 'No hay eventos programados este mes',
        'section.communities': 'Comunidades Integradas',
        'section.ics': 'Calendario ICS',
        'section.json': 'Datos JSON',
        'section.howto': 'Cómo usar',
        'badge.recommended': 'Recomendado',
        'ics.description': 'Archivo ICS estándar compatible con Google Calendar, Apple Calendar, Outlook y cualquier cliente de calendario.',
        'json.description': 'Archivo JSON con todos los eventos para uso programático o análisis.',
        'btn.download.ics': 'Descargar ICS',
        'btn.copy.webcal': 'Copiar WebCal',
        'btn.download.json': 'Descargar JSON',
        'btn.copied': '✓ Copiado!',
        'tip.label': 'Tip:',
        'tip.content': 'Para suscribirte automáticamente, usa la URL de WebCal o importa el archivo ICS en tu calendario favorito. Los eventos se actualizarán automáticamente.',
        'howto.google': 'Haz clic en "Copiar WebCal" o importa el archivo ICS',
        'howto.apple': 'Archivo → Nueva suscripción de calendario → pega la URL WebCal',
        'howto.outlook': 'Agregar calendario → Suscribir desde web → pega la URL WebCal',
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
        'cal.showMore': 'Ver más →',
        'cal.showLess': 'Ver menos ←',
        'cal.eventsOf': 'Eventos de',
        'cal.viewEvent': 'Ver evento →',
        'cal.viewOnMap': 'Ver en mapa',
        'cal.online': 'en línea',
        'cal.loadMore': 'Cargar siguiente mes ▼',
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
        'landing.verEventos': 'Ver eventos',
        'landing.anadirCalendario': 'Añadir a mi calendario',
        'hint.welcome': 'Elige tu ciudad para ver eventos.',
        'hint.whereEvents': '¿Dónde buscas eventos?',
        'hint.whatIsThis': '¿Qué es esto?',
        'section.addCalendar': 'Añadir a mi calendario',
        'section.addCalendarLead': 'Para que los eventos se actualicen solos en Google Calendar, Apple Calendar o Outlook.',
        'btn.copy.webcal.plain': 'Copiar enlace para suscribirme',
        'btn.copy.webcal.hint': 'Pega el enlace en tu app de calendario y los eventos se actualizarán solos.',
        'btn.download.ics.plain': 'Descargar archivo (.ics)',
        'section.howtoLead': 'Pasos para tener los eventos en tu calendario:',
        'months': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        'days': ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
        'locale': 'es-MX'
    },
    en: {
        'site.subtitle': 'Unified tech events calendar in Mexico',
        'cmd.description': 'cat description.txt',
        'cmd.calendar': './calendar.sh',
        'cmd.files': 'ls calendars/',
        'cmd.json': 'cat data.json',
        'cmd.tips': 'cat tips.txt',
        'cmd.howto': './how-to-use.sh',
        'desc.content': 'This calendar aggregates events from multiple sources (Meetup, Luma, etc.) in one place. Events are updated automatically every 6 hours.',
        'calendar.title': '📅 Events Calendar',
        'calendar.loading': 'Loading calendar...',
        'calendar.empty': 'No events available to display in the calendar',
        'calendar.noEvents': 'No events scheduled this month',
        'section.communities': 'Integrated Communities',
        'section.ics': 'ICS Calendar',
        'section.json': 'JSON Data',
        'section.howto': 'How to use',
        'badge.recommended': 'Recommended',
        'ics.description': 'Standard ICS file compatible with Google Calendar, Apple Calendar, Outlook and any calendar client.',
        'json.description': 'JSON file with all events for programmatic use or analysis.',
        'btn.download.ics': 'Download ICS',
        'btn.copy.webcal': 'Copy WebCal',
        'btn.download.json': 'Download JSON',
        'btn.copied': '✓ Copied!',
        'tip.label': 'Tip:',
        'tip.content': 'To subscribe automatically, use the WebCal URL or import the ICS file in your favorite calendar. Events will update automatically.',
        'howto.google': 'Click "Copy WebCal" or import the ICS file',
        'howto.apple': 'File → New Calendar Subscription → paste the WebCal URL',
        'howto.outlook': 'Add calendar → Subscribe from web → paste the WebCal URL',
        'communities.viewAll': 'View full list of integrated communities →',
        'communities.addYours': 'Want to add your community? Open a PR or Issue in the repository.',
        'footer.project': 'Open source project by',
        'footer.github': 'View on GitHub',
        'footer.docs': 'Documentation',
        'footer.lastUpdate': 'Last update:',
        'footer.loading': 'Loading...',
        'footer.notAvailable': 'Not available',
        'cal.prev': '◀ Previous',
        'cal.next': 'Next ▶',
        'cal.today': 'Today',
        'cal.takeCalendar': 'Take this calendar',
        'cal.showMore': 'Show more →',
        'cal.showLess': 'Show less ←',
        'cal.eventsOf': 'Events of',
        'cal.viewEvent': 'View event →',
        'cal.viewOnMap': 'View on map',
        'cal.online': 'online',
        'cal.loadMore': 'Load next month ▼',
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
        'landing.verEventos': 'View events',
        'landing.anadirCalendario': 'Add to my calendar',
        'hint.welcome': 'Choose your city to see events.',
        'hint.whereEvents': 'Where are you looking for events?',
        'hint.whatIsThis': 'What is this?',
        'section.addCalendar': 'Add to my calendar',
        'section.addCalendarLead': 'So events update automatically in Google Calendar, Apple Calendar, or Outlook.',
        'btn.copy.webcal.plain': 'Copy link to subscribe',
        'btn.copy.webcal.hint': 'Paste the link in your calendar app and events will update automatically.',
        'btn.download.ics.plain': 'Download file (.ics)',
        'section.howtoLead': 'Steps to get events in your calendar:',
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
