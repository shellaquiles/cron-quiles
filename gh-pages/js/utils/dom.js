/**
 * Helper para manipulación del DOM
 */
export const DOM = {
    /**
     * Crea un elemento con clases y contenido
     * @param {string} tag
     * @param {Object} options { className, text, html, attributes, children }
     */
    create(tag, { className, text, html, attributes = {}, children = [] } = {}) {
        const el = document.createElement(tag);
        if (className) el.className = className;
        if (text) el.textContent = text;
        if (html) el.innerHTML = html;

        Object.entries(attributes).forEach(([key, value]) => {
            el.setAttribute(key, value);
        });

        children.forEach(child => {
            if (child) el.appendChild(child);
        });

        return el;
    },

    /**
     * Limpia un contenedor
     */
    clear(element) {
        if (element) element.innerHTML = '';
    }
};
