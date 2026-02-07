/**
 * Componente Lista de Comunidades
 */
import { DOM } from '../utils/dom.js';

/**
 * Agrega parámetros UTM a una URL para tracking.
 * @param {string} url - URL original
 * @returns {string} URL con parámetros UTM
 */
function addUtmSource(url) {
    if (!url) return url;
    try {
        const u = new URL(url);
        u.searchParams.set('utm_source', 'cronquiles');
        u.searchParams.set('utm_medium', 'community-card');
        return u.toString();
    } catch {
        return url;
    }
}

export class CommunityList {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    render(communities) {
        if (!this.container) return;
        DOM.clear(this.container);

        if (!communities || communities.length === 0) {
            this.container.innerHTML = '<div class="events-loading">Cargando comunidades...</div>';
            return;
        }

        const fragment = document.createDocumentFragment();

        communities.forEach(c => {
            const children = [
                DOM.create('div', { className: 'community-name', text: c.name }),
                DOM.create('div', { className: 'community-description', text: c.description })
            ];

            // Agregar enlaces a plataformas si existen
            if (c.links && c.links.length > 0) {
                const linksContainer = DOM.create('div', { className: 'community-links' });
                c.links.forEach(link => {
                    const btn = DOM.create('a', {
                        className: `event-source-btn event-source-${link.platform}`,
                        text: link.label,
                        attributes: {
                            href: addUtmSource(link.url),
                            target: '_blank',
                            rel: 'noopener'
                        }
                    });
                    linksContainer.appendChild(btn);
                });
                children.push(linksContainer);
            }

            const card = DOM.create('div', {
                className: 'community-card',
                children: children
            });
            fragment.appendChild(card);
        });

        this.container.appendChild(fragment);
    }
}
