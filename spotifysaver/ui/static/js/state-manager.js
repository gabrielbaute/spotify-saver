class StateManager {
    constructor() {
        this.storageKey = 'spotifysaver_state';
    }

    saveState(appState) {
        const state = {
            downloadInProgress: appState.downloadInProgress,
            currentTaskId: appState.currentTaskId,
            downloadStartTime: appState.downloadStartTime,
            lastUrl: document.getElementById('spotify-url').value,
            logs: this.getLogs(),
            inspectData: this.getInspectData(),
            timestamp: Date.now()
        };
        localStorage.setItem(this.storageKey, JSON.stringify(state));
    }

    loadPersistedState() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            if (!saved) return null;
            
            const state = JSON.parse(saved);
            const maxAge = 24 * 60 * 60 * 1000; // 24 horas
            
            // Verificar si el estado no es muy antiguo
            if (Date.now() - state.timestamp > maxAge) {
                localStorage.removeItem(this.storageKey);
                return null;
            }

            return state;
        } catch (error) {
            console.warn('Error loading persisted state:', error);
            localStorage.removeItem(this.storageKey);
            return null;
        }
    }

    clearPersistedState() {
        localStorage.removeItem(this.storageKey);
    }

    getLogs() {
        const logEntries = document.querySelectorAll('.log-entry');
        // Invertir para mantener el orden cronológico original al guardar
        return Array.from(logEntries).reverse().map(entry => ({
            text: entry.textContent,
            className: entry.className
        }));
    }

    restoreLogs(logs) {
        const logContent = document.getElementById('log-content');
        logContent.innerHTML = '';
        // Invertir el orden de los logs para mostrar los más recientes primero
        logs.reverse().forEach(log => {
            const entry = document.createElement('div');
            entry.className = log.className;
            entry.textContent = log.text;
            logContent.appendChild(entry);
        });
        logContent.scrollTop = 0;
    }

    getInspectData() {
        const container = document.getElementById('inspect-details');
        if (container.classList.contains('hidden') || !container.innerHTML.trim()) {
            return null;
        }
        return {
            html: container.innerHTML,
            visible: !container.classList.contains('hidden')
        };
    }

    restoreInspectData(data) {
        if (!data || !data.html) return;
        
        const container = document.getElementById('inspect-details');
        const message = document.getElementById('inspect-message');
        
        container.innerHTML = data.html;
        if (data.visible) {
            message.classList.add('hidden');
            container.classList.remove('hidden');
        }
    }

    restoreFormData(state) {
        // Restaurar URL
        if (state.lastUrl) {
            document.getElementById('spotify-url').value = state.lastUrl;
        }

        // Restaurar logs
        if (state.logs && state.logs.length > 0) {
            this.restoreLogs(state.logs);
        }

        // Restaurar detalles de inspección
        if (state.inspectData) {
            this.restoreInspectData(state.inspectData);
        }
    }
}