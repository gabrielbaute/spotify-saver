class SpotifySaverUI {
    constructor() {
        this.apiClient = new ApiClient();
        this.stateManager = new StateManager();
        this.uiManager = new UIManager(() => this.saveState());
        this.downloadManager = new DownloadManager(this.apiClient, this.uiManager, () => this.saveState());
        
        this.isInitialized = false;
        this.retryCount = 0;

        this.initialize();
    }

    async initialize() {
        try {
            this.initializeEventListeners();
            this.loadPersistedState();

            // Check API status with retry mechanism
            const apiAvailable = await this.apiClient.checkApiStatusWithRetry();

            if (apiAvailable) {
                this.uiManager.updateStatus('API connected and ready', 'success');
                await this.setDefaultOutputDir();
                await this.loadAppVersion();
                await this.checkAuthStatus();
            } else {
                this.uiManager.updateStatus('API not available. Make sure it is running.', 'error');
            }

            this.isInitialized = true;

            // If there was a download in progress, try to reconnect
            if (this.downloadManager.isDownloadInProgress && this.downloadManager.taskId) {
                this.downloadManager.startProgressMonitoring(this.downloadManager.taskId);
            }

        } catch (error) {
            console.error('Failed to initialize UI:', error);
            this.uiManager.updateStatus('Failed to initialize. Please refresh the page.', 'error');
        }
    }

    async checkAuthStatus() {
        const card = document.getElementById('auth-status-card');
        const text = document.getElementById('auth-status-text');
        const btn = document.getElementById('connect-spotify-btn');

        const status = await this.apiClient.getAuthStatus();

        card.classList.remove('auth-checking', 'auth-connected', 'auth-disconnected');

        if (status.authenticated) {
            card.classList.add('auth-connected');
            text.innerHTML = `Spotify connected as <strong>${status.user || status.user_id}</strong>`;
            btn.classList.add('hidden');
            this.uiManager.addLogEntry(`Spotify account connected as ${status.user || status.user_id}`, 'success');
        } else {
            card.classList.add('auth-disconnected');
            text.textContent = 'Spotify not connected — playlists require authentication';
            btn.classList.remove('hidden');
            this.uiManager.addLogEntry('Spotify account not connected. Playlists will not work until you connect.', 'warning');
        }
    }

    async handleConnectSpotify() {
        const btn = document.getElementById('connect-spotify-btn');
        btn.disabled = true;
        btn.textContent = 'Connecting...';
        this.uiManager.addLogEntry('Opening Spotify authorization page...', 'info');

        try {
            const authUrl = await this.apiClient.getAuthLoginUrl();
            window.location.href = authUrl;
        } catch (error) {
            this.uiManager.addLogEntry(`Failed to get auth URL: ${error.message}`, 'error');
            btn.disabled = false;
            btn.textContent = 'Connect Spotify';
        }
    }

    initializeEventListeners() {
        const downloadBtn = document.getElementById('download-btn');
        const spotifyUrl = document.getElementById('spotify-url');
        const clearLogsBtn = document.getElementById('clear-logs-btn');
        const connectBtn = document.getElementById('connect-spotify-btn');

        downloadBtn.addEventListener('click', () => this.downloadManager.startDownload());

        // Permitir iniciar descarga con Enter
        spotifyUrl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.downloadManager.isDownloadInProgress) {
                this.downloadManager.startDownload();
            }
        });

        connectBtn.addEventListener('click', () => this.handleConnectSpotify());

        // Botón para limpiar logs y estado
        clearLogsBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to clear logs and state? This cannot be undone.')) {
                this.uiManager.clearLog();
                this.uiManager.clearInspect();
                this.downloadManager.clearStates();
                this.stateManager.clearPersistedState();
                this.uiManager.updateStatus('API connected and ready', 'info');
                this.uiManager.addLogEntry('Logs and state manually cleared', 'info');
            }
        });
    }

    loadPersistedState() {
        const state = this.stateManager.loadPersistedState();
        if (!state) return;

        // Restaurar datos del formulario y UI
        this.stateManager.restoreFormData(state);

        // Restaurar estado de descarga
        if (state.downloadInProgress && state.currentTaskId) {
            this.downloadManager.restoreDownloadState(
                state.downloadInProgress,
                state.currentTaskId,
                state.downloadStartTime
            );
            this.uiManager.updateUI(true);
            this.uiManager.updateStatus('Reconnecting to download...', 'info');
            this.uiManager.addLogEntry('Reconnected - resuming download monitoring', 'info');
        }
    }

    saveState() {
        const appState = {
            downloadInProgress: this.downloadManager.isDownloadInProgress,
            currentTaskId: this.downloadManager.taskId,
            downloadStartTime: this.downloadManager.startTime
        };
        this.stateManager.saveState(appState);
    }

    async setDefaultOutputDir() {
        try {
            const defaultDir = await this.apiClient.getDefaultOutputDir();
            await this.uiManager.setDefaultOutputDir(defaultDir);
        } catch (error) {
            console.warn('Could not set default output directory:', error);
        }
    }

    async loadAppVersion() {
        try {
            const version = await this.apiClient.getAppVersion();
            if (version) {
                await this.uiManager.setAppVersion(version);
            }
        } catch (error) {
            console.warn('Could not load app version:', error);
        }
    }
}

// Inicializar la aplicación cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    new SpotifySaverUI();
});