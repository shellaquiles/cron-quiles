/**
 * Wrapper seguro para LocalStorage
 */
export const Storage = {
    get(key, defaultValue = null) {
        const item = localStorage.getItem(key);
        if (item === null) return defaultValue;

        try {
            return JSON.parse(item);
        } catch (e) {
            // Si no es JSON válido (por ejemplo, una cadena simple guardada previamente), retornar tal cual
            return item || defaultValue;
        }
    },

    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Error writing to storage', e);
        }
    },

    remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Error removing from storage', e);
        }
    }
};
