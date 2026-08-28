/**
 * Utilidades para manejo de fechas
 */
import { i18n } from '../core/I18n.js';

export const DateUtils = {
    /**
     * Formatea una fecha para mostrar el día
     * @param {string|Date} date
     * @returns {string} Fecha formateada
     */
    formatDate(date) {
        if (!date) return '';
        const d = new Date(date);
        return d.toLocaleDateString(i18n.getLocale(), {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            timeZone: 'America/Mexico_City'
        });
    },

    /**
     * Fecha corta para escaneo rápido (día + mes abrev.)
     * @param {string|Date} date
     * @returns {string} ej. "6 feb" (es) o "Feb 6" (en)
     */
    formatShortDate(date) {
        if (!date) return '';
        const d = new Date(date);
        const locale = i18n.getLocale();
        const day = d.getDate();
        const monthStr = d.toLocaleDateString(locale, { month: 'short', timeZone: 'America/Mexico_City' }).replace(/\./g, '');
        const month = locale.startsWith('es') ? monthStr.toLowerCase() : monthStr;
        return locale.startsWith('es') ? `${day} ${month}` : `${month} ${day}`;
    },

    /**
     * Retorna partes separadas para el badge de fecha editorial
     * @param {string|Date} date 
     * @returns {{dayNumber: string, dayMeta: string}} ej: { dayNumber: "28", dayMeta: "AGO / VIE" }
     */
    formatDateBadge(date) {
        if (!date) return { dayNumber: '--', dayMeta: '' };
        const d = new Date(date);
        const locale = i18n.getLocale();
        
        const dayNumber = d.toLocaleDateString(locale, { day: '2-digit', timeZone: 'America/Mexico_City' });
        const monthStr = d.toLocaleDateString(locale, { month: 'short', timeZone: 'America/Mexico_City' }).replace(/\./g, '').toUpperCase();
        const weekdayStr = d.toLocaleDateString(locale, { weekday: 'short', timeZone: 'America/Mexico_City' }).replace(/\./g, '').toUpperCase();

        return {
            dayNumber,
            dayMeta: `${monthStr} / ${weekdayStr}`
        };
    },

    /**
     * Verifica si una fecha corresponde al día de hoy en la zona horaria de México
     * @param {string|Date} date 
     * @returns {boolean}
     */
    isToday(date) {
        if (!date) return false;
        const d = new Date(date);
        const now = new Date();
        
        const dStr = d.toLocaleDateString('en-CA', { timeZone: 'America/Mexico_City' });
        const nowStr = now.toLocaleDateString('en-CA', { timeZone: 'America/Mexico_City' });
        return dStr === nowStr;
    },

    /**
     * Formatea la hora
     * @param {string|Date} date
     */
    formatTime(date) {
        if (!date) return '';
        const d = new Date(date);
        return d.toLocaleTimeString(i18n.getLocale(), {
            hour: '2-digit',
            minute: '2-digit',
            timeZone: 'America/Mexico_City'
        });
    },

    /**
     * Normaliza a inicio del día (00:00:00)
     */
    startOfDay(date) {
        const d = new Date(date);
        d.setHours(0, 0, 0, 0);
        return d;
    },

    /**
     * Obtiene los días del mes
     */
    getDaysInMonth(year, month) {
        return new Date(year, month + 1, 0).getDate();
    }
};
