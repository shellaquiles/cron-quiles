import { appStore } from '../core/Store.js';
import { i18n } from '../core/I18n.js';
import { DataService } from '../services/DataService.js';

/**
 * Terminal Component
 * Handles the interactive console experience and visual terminal prompts.
 */
export class Terminal {
    constructor() {
        this.init();
    }

    init() {
        this.setupConsoleCommands();
        
        // Setup visual terminal only when the page is fully ready to avoid layout shift/warnings
        if (document.readyState === 'complete') {
            this.setupVisualTerminal();
        } else {
            window.addEventListener('load', () => this.setupVisualTerminal());
        }
    }

    /**
     * Setup global console functions for browser devtools
     */
    setupConsoleCommands() {
        const logo = `
   %c██████╗ ██████╗  ██████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗██╗     ███████╗███████╗
  ██╔════╝ ██╔══██╗██╔═══██╗████╗  ██║██╔═══██╗██║   ██║██║██║     ██╔════╝██╔════╝
  ██║      ██████╔╝██║   ██║██╔██╗ ██║██║   ██║██║   ██║██║██║     █████╗  ███████╗
  ██║      ██╔══██╗██║   ██║██║╚██╗██║██║ ▄ ██║██║   ██║██║██║     ██╔══╝  ╚════██║
  ╚██████╗ ██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝╚██████╔╝██║███████╗███████╗███████║
   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚════▀▀  ╚═════╝ ╚═╝╚══════╝╚══════╝╚══════╝
        `;

        const logShellaquiles = () => {
            console.log(`%c{{ %cshell%caquiles%c.org %c}}`,
                'color: #9CA3AF; font-weight: bold;',
                'color: #22C55E; font-weight: bold;',
                'color: #E5E7EB; font-weight: bold;',
                'color: #F43F5E; font-weight: bold;',
                'color: #9CA3AF; font-weight: bold;'
            );
        };

        const about = async () => {
            const city = (appStore.get('city') || 'mexico').toLowerCase();
            const version = await DataService.getVersion(city) || '2.0.1';
            setTimeout(() => {
                console.log(logo, 'color: #00ff00;');
                console.log(`%c🐢 Cron-Quiles v${version} | Calendario Unificado de Eventos Tech en México`, 'color: #00ff00; font-weight: bold; font-size: 1.2em;');
                console.log(`%cEl calendario unificado del ecosistema tecnológico en México.`, 'color: #00ff00; font-style: italic;');
                console.log(`%cFuentes actuales: %cMeetup, Luma, Eventbrite, Google Developer Groups (GDG), Open Community Groups (OCGroups), HiEvents, iCal Feeds.`, 'color: #aaa;', 'color: #00ff00;');
            }, 0);
            return "Un proyecto de shellaquiles.org por pixelead0.";
        };

        // Terminal state for console navigation
        this.consoleMonthOffset = 0;

        const listEvents = async (offset = 0) => {
            const citySlug = (appStore.get('city') || 'mexico').toLowerCase();
            const now = new Date();
            const targetDate = new Date(now.getFullYear(), now.getMonth() + offset, 1);
            const monthName = targetDate.toLocaleDateString('es-MX', { month: 'long', year: 'numeric' });
            
            console.log(`%c[SYSTEM] Consultando eventos para ${citySlug.toUpperCase()} en ${monthName}...`, 'color: #00ff00; font-family: monospace;');
            
            try {
                const data = await DataService.getCityData(citySlug);
                const events = Array.isArray(data) ? data : (data.events || []);
                
                // Filter events by the target month and exclude online events
                const filteredEvents = events.filter(e => {
                    const d = new Date(e.dtstart);
                    const isSameMonth = d.getFullYear() === targetDate.getFullYear() && d.getMonth() === targetDate.getMonth();
                    const isPresencial = !e.online;
                    return isSameMonth && isPresencial;
                }).sort((a, b) => new Date(a.dtstart) - new Date(b.dtstart));

                if (filteredEvents.length === 0) {
                    console.log(`%c[EMPTY] No hay eventos registrados para ${monthName}.`, "color: #aaa;");
                    console.log(`%cTip: Usa %ceventos.next%c o %ceventos.last%c para navegar.`, "color: #555;", "color: #00ff00;", "color: #555;", "color: #00ff00;", "color: #555;");
                } else {
                    const formattedEvents = filteredEvents.map(e => {
                        const dateObj = new Date(e.dtstart);
                        
                        let comunidad = e.organizer || 'Comunidad Desconocida';
                        let titulo = e.title || 'Sin título';
                        if (titulo.includes('|')) {
                            const parts = titulo.split('|').map(p => p.trim());
                            comunidad = parts[0];
                            titulo = parts[1];
                        }

                        return {
                            fecha: dateObj.toLocaleDateString('es-MX', { day: '2-digit', month: '2-digit' }),
                            hora: dateObj.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' }),
                            comunidad: comunidad,
                            titulo: titulo,
                            ubicacion: e.location || (e.online ? 'En Línea' : 'Por confirmar'),
                            registro: e.url || 'N/A'
                        };
                    });

                    console.log(`%c[DATA] Se encontraron ${filteredEvents.length} eventos presenciales en ${monthName}:`, 'color: #00ff00;');
                    console.table(formattedEvents);
                    console.log(`%cComandos: %ceventos.next%c (sig) | %ceventos.last%c (prev) | %ceventos.reset%c (actual)`, "color: #aaa;", "color: #00ff00;", "color: #aaa;", "color: #00ff00;", "color: #aaa;", "color: #00ff00;", "color: #aaa;");
                }
            } catch (err) {
                console.log(`%c[ERROR] Fallo en la matriz de datos (${err.message}).`, "color: #ff0000;");
            }
            return `Vista: ${monthName}`;
        };

        const searchEvents = async (query, includeAll = false) => {
            if (!query || typeof query !== 'string' || !query.trim()) {
                console.log("%c[ERROR] Especifica un término de búsqueda. Ej: %ceventos.buscar('python')%c o %ceventos('python')", "color: #ff0000;", "color: #00ff00;", "color: #ff0000;");
                return "Búsqueda vacía.";
            }

            const cleanQuery = query.trim().toLowerCase();
            const citySlug = (appStore.get('city') || 'mexico').toLowerCase();
            const now = new Date();

            const scope = includeAll ? 'todos los eventos' : 'próximos eventos';
            console.log(`%c[SYSTEM] Buscando "${query}" en ${citySlug.toUpperCase()} (${scope})...`, 'color: #00ff00; font-family: monospace;');

            try {
                const data = await DataService.getCityData(citySlug);
                const events = Array.isArray(data) ? data : (data.events || []);

                const matchedEvents = events.filter(e => {
                    // Por defecto solo proximos; .all incluye pasados también
                    if (!includeAll && new Date(e.dtstart) < now) return false;

                    const title = (e.title || '').toLowerCase();
                    const organizer = (e.organizer || '').toLowerCase();
                    const description = (e.description || '').toLowerCase();
                    const location = (e.location || '').toLowerCase();
                    return title.includes(cleanQuery) || organizer.includes(cleanQuery) || description.includes(cleanQuery) || location.includes(cleanQuery);
                }).sort((a, b) => new Date(a.dtstart) - new Date(b.dtstart));

                if (matchedEvents.length === 0) {
                    const hint = includeAll
                        ? `No se encontraron eventos para "${query}".`
                        : `No se encontraron próximos eventos para "${query}". Prueba con %ceventos.buscar("${query}").all%c para ver el historial completo.`;
                    console.log(`%c[EMPTY] ${hint}`, "color: #aaa;", "color: #00ff00;", "color: #aaa;");
                } else {
                    const formattedEvents = matchedEvents.map(e => {
                        const dateObj = new Date(e.dtstart);
                        let comunidad = e.organizer || 'Comunidad Desconocida';
                        let titulo = e.title || 'Sin título';
                        if (titulo.includes('|')) {
                            const parts = titulo.split('|').map(p => p.trim());
                            comunidad = parts[0];
                            titulo = parts[1];
                        }

                        return {
                            fecha: dateObj.toLocaleDateString('es-MX', { day: '2-digit', month: '2-digit', year: 'numeric' }),
                            hora: dateObj.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' }),
                            comunidad: comunidad,
                            titulo: titulo,
                            formato: e.online ? 'En Línea' : 'Presencial',
                            ubicacion: e.location || (e.online ? 'En Línea' : 'Por confirmar'),
                            registro: e.url || 'N/A'
                        };
                    });

                    const label = includeAll ? `todos los eventos` : `próximos eventos`;
                    console.log(`%c[DATA] ${matchedEvents.length} ${label} para "${query}":`, 'color: #00ff00;');
                    console.table(formattedEvents);
                    if (!includeAll) {
                        console.log(`%cTip: Usa %ceventos.buscar("${query}").all%c para ver el historial completo.`, "color: #555;", "color: #00ff00;", "color: #555;");
                    }
                }
            } catch (err) {
                console.log(`%c[ERROR] Fallo en la matriz de datos (${err.message}).`, "color: #ff0000;");
            }
            return `Resultados (${scope}) para: "${query}"`;
        };

        // .all → devuelve un getter que ejecuta searchEvents con includeAll=true
        searchEvents.all = null; // placeholder; se sobreescribe por query abajo

        const eventos = (target) => {
            if (target && typeof target === 'string') {
                const trimmed = target.trim();
                // Check if target is YYYY-MM
                if (/^\d{4}-\d{2}$/.test(trimmed)) {
                    const parts = trimmed.split('-');
                    const targetYear = parseInt(parts[0]);
                    const targetMonth = parseInt(parts[1]) - 1; // 0-indexed
                    const now = new Date();
                    const currentYear = now.getFullYear();
                    const currentMonth = now.getMonth();
                    
                    this.consoleMonthOffset = (targetYear - currentYear) * 12 + (targetMonth - currentMonth);
                    return listEvents(this.consoleMonthOffset);
                }
                // Si es cualquier otro texto, ejecutar búsqueda por comunidad/término
                return searchEvents(trimmed);
            }
            
            this.consoleMonthOffset = 0;
            return listEvents(0);
        };

        const regiones = async () => {
            try {
                const states = await DataService.getStatesMetadata();
                console.log("%c🌍 Regiones disponibles:", "color: #00ff00; font-weight: bold;");
                const list = states.map(s => ({
                    slug: s.slug,
                    nombre: s.name,
                    eventos: s.event_count || s.count || '?'
                }));
                list.unshift({ slug: 'mexico', nombre: 'Todo México', eventos: 'Global' });
                console.table(list);
            } catch (e) {
                console.log("%c[ERROR] No se pudieron cargar las regiones.", "color: #ff0000;");
            }
            return "Usa eventos.region('slug') para cambiar.";
        };

        const region = (slug) => {
            if (!slug) return regiones();
            appStore.set('city', slug.toLowerCase());
            this.consoleMonthOffset = 0;
            return listEvents(0);
        };

        eventos.next = () => {
            this.consoleMonthOffset++;
            return listEvents(this.consoleMonthOffset);
        };

        eventos.prev = () => {
            this.consoleMonthOffset--;
            return listEvents(this.consoleMonthOffset);
        };

        eventos.last = eventos.prev; // Alias requested by user

        /**
         * makeSearch(query) → devuelve una Promise con getter .all
         * Uso:
         *   eventos.buscar("python")       → próximos eventos
         *   eventos.buscar("python").all   → todos (historial incluido)
         */
        const makeSearch = (query) => {
            // Ejecutar búsqueda próximos por defecto
            const promise = searchEvents(query, false);

            // Agregar getter .all a la promise para acceso tipo eventos.buscar("python").all
            Object.defineProperty(promise, 'all', {
                get: () => searchEvents(query, true),
                configurable: true
            });

            return promise;
        };

        eventos.buscar = makeSearch;
        eventos.comunidad = makeSearch;
        eventos.region = region;
        eventos.regiones = regiones;

        eventos.reset = () => {
            this.consoleMonthOffset = 0;
            return listEvents(0);
        };

        const comunidades = async () => {
            const city = (appStore.get('city') || 'mexico').toLowerCase();
            console.log(`%c[SYSTEM] Listando comunidades en ${city.toUpperCase()}...`, 'color: #00ff00;');
            
            try {
                const data = await DataService.getCityData(city);
                const communities = data.communities || [];
                
                if (communities.length === 0) {
                    console.log("%c[EMPTY] No hay comunidades registradas en esta ciudad aún.", "color: #aaa;");
                } else {
                    console.log(`%c🏘️ Comunidades en ${city}:`, 'color: #00ff00; font-weight: bold;');
                    communities.forEach(c => {
                        console.log(`%c- ${c.name}`, 'color: #fff; font-weight: bold;');
                        if (c.description) console.log(`  %c${c.description}`, 'color: #aaa;');
                    });
                }
            } catch (err) {
                console.log(`%c[ERROR] No se pudo conectar con el gremio (${err.message}).`, "color: #ff0000;");
            }
            return "Fin del reporte de comunidades.";
        };

        const help = () => {
            setTimeout(() => {
                console.log(`
%c┌─────────────────────────────────────────────────────────────────┐
│                 COMANDOS DE CONSOLA CRON-QUILES                 │
├─────────────────────────────────────────────────────────────────┤
│  %cabout%c                          - Acerca del proyecto y versión │
│  %ceventos%c                        - Actividades del mes actual    │
│  %ceventos("YYYY-MM")%c             - Ir a un mes específico        │
│  %ceventos("comunidad")%c           - Buscar por comunidad/tema     │
│  %ceventos.buscar("query")%c        - Búsqueda directa de eventos   │
│  %ceventos.next%c / %ceventos.last%c    - Mes siguiente / anterior      │
│  %ceventos.region("slug")%c         - Cambiar región (ej: "mexico") │
│  %ceventos.regiones()%c             - Listar regiones disponibles   │
│  %ccomunidades%c                    - Directorio de comunidades     │
│  %csuscribir%c                      - Enlaces de suscripción iCal   │
│  %cclear%c                          - Limpiar la consola            │
│  %chelp%c                           - Mostrar esta guía de comandos │
└─────────────────────────────────────────────────────────────────┘
                `, 
                'color: #00ff00; font-weight: bold;',
                'color: #00ff00;', 'color: inherit;',
                'color: #00ff00;', 'color: inherit;',
                'color: #00ff00;', 'color: inherit;',
                'color: #00ff00;', 'color: inherit;',
                'color: #00ff00;', 'color: inherit;',
                'color: #00ff00;', 'color: inherit;', 'color: #00ff00;', 'color: inherit;',
                'color: #00ff00;', 'color: inherit;',
                'color: #00ff00;', 'color: inherit;',
                'color: #00ff00;', 'color: inherit;',
                'color: #00ff00;', 'color: inherit;',
                'color: #00ff00;', 'color: inherit;',
                'color: #00ff00;', 'color: inherit;'
                );
            }, 0);
            return "Consola interactiva de Cron-Quiles lista.";
        };

        const suscribir = () => {
            console.log(`%c📅 Suscripción al Calendario`, 'color: #00ff00; font-weight: bold;');
            console.log(`%cSincroniza los eventos en tiempo real con Google Calendar, Apple Calendar u Outlook.`, 'color: #fff;');
            console.log(`%cURL: https://shellaquiles.github.io/cron-quiles/suscribir.html`, 'color: #00ff00; text-decoration: underline;');
            return "Enlaces de suscripción disponibles en la web.";
        };

        const clear = () => {
            console.clear();
            console.log("%cConsola de Cron-Quiles limpia. 🐢", "color: #00ff00; font-weight: bold; font-size: 1.1em;");
            return "";
        };

        // Assign to window object with getters for easy access (typing 'help' instead of 'help()')
        const commands = {
            about,
            eventos,
            evento: eventos, // Alias for common typo
            comunidades,
            help,
            suscribir,
            clear,
            shellaquiles: about,
            cronquiles: about
        };

        const logProjectHeader = () => {
            console.log(`%cCron-Quiles es un proyecto de %c{{ %cshell%caquiles%c.org %c}}`,
                'color: #00ff00; font-weight: bold;',
                'color: #9CA3AF; font-weight: bold;',
                'color: #22C55E; font-weight: bold;',
                'color: #E5E7EB; font-weight: bold;',
                'color: #F43F5E; font-weight: bold;',
                'color: #9CA3AF; font-weight: bold;'
            );
        };

        /**
         * Creates a console-friendly command wrapper
         */
        const createCommand = (name, cmdFunc) => {
            const wrapper = function(...args) {
                const result = cmdFunc(...args);
                if (result instanceof Promise) {
                    result.finally(() => logProjectHeader());
                } else {
                    logProjectHeader();
                }
                return result;
            };

            // Recursively wrap sub-commands (like .next, .last) as GETTERS
            Object.keys(cmdFunc).forEach(prop => {
                const subCmd = cmdFunc[prop];
                if (typeof subCmd === 'function') {
                    Object.defineProperty(wrapper, prop, {
                        get: () => createCommand(`${name}.${prop}`, subCmd),
                        configurable: true
                    });
                } else {
                    wrapper[prop] = subCmd;
                }
            });

            // Handle console display
            wrapper.toString = function() {
                const result = cmdFunc();
                if (result instanceof Promise) {
                    result.finally(() => logProjectHeader());
                    return `[COMMAND] Ejecutando ${name}...`;
                }
                logProjectHeader();
                return result || "";
            };
            
            return wrapper;
        };

        Object.keys(commands).forEach(key => {
            const originalCmd = commands[key];
            Object.defineProperty(window, key, {
                get: function() {
                    return createCommand(key, originalCmd);
                },
                configurable: true
            });
        });

        // Add to console for people who prefer console.help()
        console.help = help;
        console.about = about;
        console.eventos = eventos;

        // Welcome message: Auto-trigger about() on load
        setTimeout(() => {
            about();
            setTimeout(() => {
                console.log("%cEscribe %chelp%c para ver los comandos disponibles.", "color: #aaa;", "color: #00ff00; font-weight: bold;", "color: #aaa;");
            }, 500);
        }, 1000);
    }

    /**
     * Setup visual terminal animations for the landing page
     */
    setupVisualTerminal() {
        const prompts = document.querySelectorAll('.home-content .prompt');
        const outputs = document.querySelectorAll('.home-content .output');

        // Animate prompts one by one
        prompts.forEach((prompt, index) => {
            const commandText = prompt.querySelector('.command-text');
            if (!commandText) return;
            
            const originalText = commandText.textContent;
            commandText.textContent = '';
            commandText.style.visibility = 'visible'; // Reveal the element before typing
            
            setTimeout(() => {
                this.typeWriter(commandText, originalText, 0, () => {
                    // Show corresponding output after typing
                    const output = outputs[index];
                    if (output) {
                        output.style.display = 'block';
                        // Add fade-in class for CSS animation
                        setTimeout(() => {
                            output.classList.add('fade-in');
                        }, 50);
                    }
                });
            }, index * 2000); // 2s gap between commands
        });
    }

    /**
     * Simple typing animation
     */
    typeWriter(element, text, i, callback) {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            setTimeout(() => this.typeWriter(element, text, i + 1, callback), 60);
        } else if (callback) {
            setTimeout(callback, 300);
        }
    }
}
