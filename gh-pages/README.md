# Cron-Quiles Frontend

This directory contains the static site generator output and the source code for the frontend application. It is built with **Vanilla JS** using **ES Modules** for a modular, dependency-free architecture.

## Development

The project uses native ES Modules, so you must serve it via a local HTTP server to avoid CORS issues with `file://` protocol.

### Prerequisites

- Python 3 (already included in most systems) OR Node.js

### Running Locally

You have two easy options:

1.  **Using Python (Recommended)**:
    ```bash
    cd gh-pages
    ./serve.sh
    # Or manually: python3 -m http.server 8000
    ```
    Open [http://localhost:8000](http://localhost:8000)

2.  **Using Node/NPM**:
    ```bash
    npx serve gh-pages
    ```

## Architecture

The codebase is organized into logical layers:

```text
gh-pages/
├── css/                 # Styling
│   ├── styles.css       # Entry point
│   ├── variables.css    # Design tokens (colors, spacing)
│   ├── layout.css       # Global layout & reset
│   └── components.css   # Reusable UI components
├── js/                  # Application Logic
│   ├── app.js           # Main Entry Point (Bootstrapper)
│   ├── config.js        # Global constants (Cities, Langs, Paths)
│   ├── core/            # Core Infrastructure
│   │   ├── Store.js     # State Management (Pub/Sub)
│   │   └── I18n.js      # Internationalization
│   ├── services/        # Data Layer
│   │   ├── DataService.js # Fetches JSON/ICS data
│   │   └── Storage.js   # LocalStorage wrapper
│   ├── ui/              # UI Components
│   │   ├── Calendar.js  # Complex Calendar Logic
│   │   ├── Header.js    # Navbar & Controls
│   │   └── CommunityList.js
│   └── utils/           # Helpers
│       ├── dates.js     # Date formatting
│       └── dom.js       # DOM manipulation
└── index.html           # Main HTML (uses type="module")
```

### Key Concepts

-   **State Management**: `appStore` in `core/Store.js` manages global state like selected City and Language. Components subscribe to changes.
-   **No Build Step**: The code runs directly in modern browsers. No Webpack/Vite required for development, though one could be added for production optimization (minification) if traffic scales significantly.
-   **Internationalization**: All text is abstracted in `core/I18n.js`. State changes trigger DOM updates automatically.

## Adding Features

-   **New City**: Add it to `CONFIG.CITIES` in `js/config.js`.
-   **New Component**: Create a class in `js/ui/`, accept a container ID, and instantiate it in `js/app.js`.
-   **New Translation**: Add keys to `TRANSLATIONS` in `js/core/I18n.js`.
