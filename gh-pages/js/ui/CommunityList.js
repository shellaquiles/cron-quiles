/**
 * Componente Lista de Comunidades
 */
import { DOM } from '../utils/dom.js';

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
            const card = DOM.create('div', {
                className: 'community-card',
                children: [
                    DOM.create('div', { className: 'community-name', text: c.name }),
                    DOM.create('div', { className: 'community-description', text: c.description })
                ]
            });
            fragment.appendChild(card);
        });

        this.container.appendChild(fragment);
    }
}
