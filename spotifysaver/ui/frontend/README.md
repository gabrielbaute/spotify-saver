# SpotifySaver UI - Modular Architecture

This directory contains the frontend for SpotifySaver, organized into modular JavaScript files for better maintainability.

## File Structure

### Core Modules

1. **`app.js`** - Main Application Controller
   - Initializes and coordinates all other modules
   - Handles application lifecycle and state persistence
   - Entry point for the application

2. **`api-client.js`** - API Communication Layer
   - Handles all HTTP requests to the SpotifySaver API
   - Includes retry mechanisms and timeout handling
   - Methods: health checks, inspect URLs, start downloads, get status

3. **`state-manager.js`** - State Persistence Manager
   - Manages localStorage operations
   - Handles saving/loading application state
   - Preserves download progress across page reloads

4. **`download-manager.js`** - Download Process Controller
   - Orchestrates the download workflow
   - Manages download progress monitoring
   - Handles track state management and progress simulation

5. **`ui-manager.js`** - UI Updates & Visualization
   - Controls all DOM updates and visual feedback
   - Manages logs, progress indicators, and track status icons
   - Handles rendering of inspection data

### Supporting Files

- **`index.html`** - Main HTML structure
- **`styles.css`** - CSS styling
- **`script.js.backup`** - Original monolithic script (backup)

## Dependencies

The modules are loaded in dependency order:
```html
<script src="api-client.js"></script>
<script src="state-manager.js"></script>
<script src="ui-manager.js"></script>
<script src="download-manager.js"></script>
<script src="app.js"></script>
```

## Key Features Preserved

- ✅ SPA routing support
- ✅ Download progress monitoring
- ✅ State persistence across reloads
- ✅ Log deduplication with cooldown
- ✅ Track status icons with real-time updates
- ✅ Error handling and retry mechanisms
- ✅ API connectivity checks
- ✅ Responsive UI updates

## Architecture Benefits

- **Separation of Concerns**: Each module has a single responsibility
- **Maintainability**: Easier to modify specific functionality
- **Testability**: Individual modules can be tested in isolation
- **Readability**: Smaller, focused files are easier to understand
- **Scalability**: New features can be added as separate modules

## Module Communication

- **App.js** orchestrates all modules and passes callbacks for state synchronization
- **Download Manager** uses UI Manager for visual updates
- **All modules** can trigger state saves through callback functions
- **Error handling** is centralized in the main app controller

## Usage

The application auto-initializes when the page loads via:
```javascript
document.addEventListener('DOMContentLoaded', () => {
    new SpotifySaverUI();
});
```

No manual initialization required.