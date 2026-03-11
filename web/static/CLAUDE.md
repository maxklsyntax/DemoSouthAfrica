# web/static/

Frontend assets served by Flask.

- `css/style.css` — Card-based responsive dashboard layout. CSS custom properties for theming. Mobile-friendly grid.
- `js/dashboard.js` — Polls `/api/*` endpoints every 3 seconds and updates the DOM. Check Label / Check Weight buttons trigger analysis + SAP DM send. Camera preview at 1fps. No framework dependencies, vanilla JS.
