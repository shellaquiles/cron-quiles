/**
 * Servicio de Datos
 * Se encarga de obtener los eventos y comunidades.
 */
import { CONFIG } from '../config.js';

export class DataService {
    /**
     * Obtiene los datos para una ciudad específica
     * @param {string} city ID de la ciudad
     * @returns {Promise<Object>} Datos del JSON
     */
    static async getCityData(city) {
        const url = CONFIG.PATHS.getDataUrl(city);

        try {
            const response = await fetch(url);
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error(`NOT_FOUND`);
                }
                throw new Error(`HTTP_${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error fetching data for ${city}:`, error);
            throw error;
        }
    }

    /**
     * Obtiene la fecha de última modificación del archivo ICS
     * @param {string} city
     * @returns {Promise<Date|null>}
     */
    static async getLastModified(city) {
        const url = CONFIG.PATHS.getIcsUrl(city);
        try {
            const response = await fetch(url, { method: 'HEAD' });
            const lastModified = response.headers.get('last-modified');
            return lastModified ? new Date(lastModified) : null;
        } catch (error) {
            console.warn(`Error check last-modified for ${city}`, error);
            return null;
        }
    }
}
