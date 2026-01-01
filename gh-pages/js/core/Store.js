/**
 * StateManager - Sistema simple de Publicación/Suscripción
 * Permite que componentes reaccionen a cambios de estado global (Ciudad, Idioma)
 * sin acoplamiento directo.
 */
export class Store {
    constructor(initialState = {}) {
        this.state = initialState;
        this.listeners = new Map();
    }

    /**
     * Obtiene una parte del estado
     * @param {string} key
     */
    get(key) {
        return this.state[key];
    }

    /**
     * Actualiza el estado y notifica a los suscriptores
     * @param {string} key
     * @param {any} value
     */
    set(key, value) {
        if (this.state[key] === value) return; // No notificar si no hay cambio

        this.state[key] = value;
        this._notify(key, value);
    }

    /**
     * Suscribe una función a cambios en una clave específica
     * @param {string} key
     * @param {Function} callback
     * @returns {Function} Función para desuscribirse
     */
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }
        this.listeners.get(key).add(callback);

        // Retorna función unsubscribe
        return () => {
            if (this.listeners.has(key)) {
                this.listeners.get(key).delete(callback);
            }
        };
    }

    _notify(key, value) {
        if (this.listeners.has(key)) {
            this.listeners.get(key).forEach(callback => callback(value));
        }
    }
}

// Singleton global para la aplicación
export const appStore = new Store();
