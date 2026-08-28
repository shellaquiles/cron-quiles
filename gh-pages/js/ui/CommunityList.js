/**
 * Componente Lista de Comunidades - Editorial Theme
 */
import { DOM } from '../utils/dom.js';
import { i18n } from '../core/I18n.js';

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
            this.container.innerHTML = `<div class="events-empty">${i18n.t('calendar.empty')}</div>`;
            return;
        }

        const fragment = document.createDocumentFragment();

        communities.forEach(c => {
            const card = DOM.create('div', { className: 'community-card' });

            const nameEl = DOM.create('div', { className: 'community-name', text: c.name });
            card.appendChild(nameEl);

            if (c.description) {
                const descEl = DOM.create('div', { className: 'community-description', text: c.description });
                card.appendChild(descEl);
            }

            if (c.links && c.links.length > 0) {
                const linksContainer = DOM.create('div', { className: 'community-links' });
                c.links.forEach(link => {
                    const btn = DOM.create('a', {
                        className: 'btn btn-outline',
                        text: `${link.label || 'Link'} ↗`,
                        attributes: {
                            href: addUtmSource(link.url),
                            target: '_blank',
                            rel: 'noopener',
                            style: 'font-size: 0.7rem; padding: 0.25rem 0.6rem;'
                        }
                    });
                    linksContainer.appendChild(btn);
                });
                card.appendChild(linksContainer);
            }

            fragment.appendChild(card);
        });

        this.container.appendChild(fragment);
    }
}
