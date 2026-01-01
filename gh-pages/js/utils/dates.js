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
        if (!date) return i18n.t('desc.content'); // Fallback string handling logic inherited...
        // Actually return generic error string depending on lang if needed
        // but simplest is to leverage i18n inside formatting
        const d = new Date(date);
        return d.toLocaleDateString(i18n.getLocale(), {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            timeZone: 'America/Mexico_City'
        });
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
