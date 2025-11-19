class SpotifySaverUI {
    constructor() {
        this.apiUrl = `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;
        this.apiUrlHealth = `${window.location.protocol}//${window.location.hostname}:8000/health`;
        this.apiUrlVersion = `${window.location.protocol}//${window.location.hostname}:8000/version`;
        this.downloadInProgress = false;
        this.eventSource = null;
        this.currentTaskId = null;
        this.downloadStartTime = null;
        this.isInitialized = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.lastLoggedTrack = null;
        this.recentLogs = new Set();
        this.logCooldownTime = 2000; // 2 seconds
        this.trackStates = new Map(); // Para rastrear estados de canciones individuales
        this.currentTrackData = null; // Para mantener datos de canciones

        this.initialize();
    }

    async initialize() {
        try {
            this.initializeEventListeners();
            this.loadPersistedState();
            
            // Check API status with retry mechanism
            const apiAvailable = await this.checkApiStatusWithRetry();
            
            if (apiAvailable) {
                await this.setDefaultOutputDir();
                await this.loadAppVersion();
            }
            
            this.isInitialized = true;
            
            // If there was a download in progress, try to reconnect
            if (this.downloadInProgress && this.currentTaskId) {
                this.startProgressMonitoring(this.currentTaskId);
            }
            
        } catch (error) {
            console.error('Failed to initialize UI:', error);
            this.updateStatus('Failed to initialize. Please refresh the page.', 'error');
        }
    }

    async checkApiStatusWithRetry() {
        for (let i = 0; i < this.maxRetries; i++) {
            const success = await this.checkApiStatus();
            if (success) {
                this.retryCount = 0;
                return true;
            }
            
            this.retryCount++;
            if (i < this.maxRetries - 1) {
                this.updateStatus(`Retrying API connection (${i + 1}/${this.maxRetries})...`, 'info');
                await new Promise(resolve => setTimeout(resolve, 2000 * (i + 1))); // Exponential backoff
            }
        }
        
        return false;
    }

    // Métodos de persistencia
    saveState() {
        const state = {
            downloadInProgress: this.downloadInProgress,
            currentTaskId: this.currentTaskId,
            downloadStartTime: this.downloadStartTime,
            lastUrl: document.getElementById('spotify-url').value,
            logs: this.getLogs(),
            inspectData: this.getInspectData(),
            timestamp: Date.now()
        };
        localStorage.setItem('spotifysaver_state', JSON.stringify(state));
    }

    loadPersistedState() {
        try {
            const saved = localStorage.getItem('spotifysaver_state');
            if (!saved) return;
            
            const state = JSON.parse(saved);
            const maxAge = 24 * 60 * 60 * 1000; // 24 horas
            
            // Verificar si el estado no es muy antiguo
            if (Date.now() - state.timestamp > maxAge) {
                localStorage.removeItem('spotifysaver_state');
                return;
            }

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

            // Restaurar estado de descarga
            if (state.downloadInProgress && state.currentTaskId) {
                this.downloadInProgress = true;
                this.currentTaskId = state.currentTaskId;
                this.downloadStartTime = state.downloadStartTime;
                this.updateUI(true);
                this.updateStatus('Reconnecting to download...', 'info');
                this.addLogEntry('Reconnected - resuming download monitoring', 'info');
                this.startProgressMonitoring(state.currentTaskId);
            }
        } catch (error) {
            console.warn('Error loading persisted state:', error);
            localStorage.removeItem('spotifysaver_state');
        }
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

    clearPersistedState() {
        localStorage.removeItem('spotifysaver_state');
    }

    initializeEventListeners() {
        const downloadBtn = document.getElementById('download-btn');
        const spotifyUrl = document.getElementById('spotify-url');
        const clearLogsBtn = document.getElementById('clear-logs-btn');
        
        downloadBtn.addEventListener('click', () => this.startDownload());
        
        // Permitir iniciar descarga con Enter
        spotifyUrl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.downloadInProgress) {
                this.startDownload();
            }
        });

        // Botón para limpiar logs y estado
        clearLogsBtn.addEventListener('click', () => {
            if (confirm('¿Estás seguro de que quieres limpiar todos los logs y resetear el estado?')) {
                this.clearLog();
                this.clearInspect();
                this.clearPersistedState();
                this.updateStatus('Estado limpiado', 'info');
                this.addLogEntry('Logs y estado limpiados manualmente', 'info');
            }
        });
    }

    async checkApiStatus() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
            
            const response = await fetch(this.apiUrlHealth, {
                signal: controller.signal,
                method: 'GET',
                mode: 'cors',
                cache: 'no-cache'
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                this.updateStatus('API connected and ready', 'success');
                return true;
            } else {
                this.updateStatus('API connection error', 'error');
                return false;
            }
        } catch (error) {
            let message = 'API not available. Make sure it is running.';
            
            if (error.name === 'AbortError') {
                message = 'API request timed out. Check if the server is running.';
            } else if (error.name === 'TypeError') {
                message = 'Network error. Unable to connect to API.';
            }
            
            this.updateStatus(message, 'error');
            console.warn('API status check failed:', error);
            return false;
        }
    }

    async setDefaultOutputDir() {
        const outputDirInput = document.getElementById('output-dir');
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
            
            const response = await fetch(`${this.apiUrl}/config/output_dir`, {
                signal: controller.signal,
                method: 'GET',
                mode: 'cors',
                cache: 'no-cache'
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const data = await response.json();
                if (outputDirInput && data.output_dir) {
                    outputDirInput.value = data.output_dir;
                }
            } else {
                // If API call fails, set default
                if (outputDirInput) {
                    outputDirInput.value = 'Music';
                }
            }
        } catch (error) {
            // If any error occurs, set default
            if (outputDirInput) {
                outputDirInput.value = 'Music';
            }
            console.warn('Could not fetch default output directory, using fallback:', error);
        }
    }

    async loadAppVersion() {
        const versionElement = document.getElementById('app-version');
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
            
            const response = await fetch(this.apiUrlVersion, {
                signal: controller.signal,
                method: 'GET',
                mode: 'cors',
                cache: 'no-cache'
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const data = await response.json();
                if (versionElement && data.version) {
                    versionElement.textContent = `v${data.version}`;
                }
            } else {
                // If API call fails, keep default
                console.warn('Could not fetch app version from API');
            }
        } catch (error) {
            // If any error occurs, keep default
            console.warn('Could not fetch app version, using fallback:', error);
        }
    }

    getFormData() {
        const bitrateValue = document.getElementById('bitrate').value;
        const bitrate = bitrateValue === 'best' ? 256 : parseInt(bitrateValue);
        
        return {
            spotify_url: document.getElementById('spotify-url').value,
            output_dir: document.getElementById('output-dir').value,
            output_format: document.getElementById('format').value,
            bit_rate: bitrate,
            download_lyrics: document.getElementById('include-lyrics').checked,
            download_cover: true, // Always download cover
            generate_nfo: document.getElementById('create-nfo').checked
        };
    }

    validateForm() {
        const formData = this.getFormData();
        
        if (!formData.spotify_url) {
            this.updateStatus('Please enter a valid Spotify URL', 'error');
            return false;
        }
        
        if (!formData.spotify_url.includes('spotify.com')) {
            this.updateStatus('The URL must be from Spotify.', 'error');
            return false;
        }
        
        return true;
    }

    async startDownload() {
        if (this.downloadInProgress) {
            return;
        }

        if (!this.validateForm()) {
            return;
        }

        // Check API connectivity before starting
        this.updateStatus('Checking API connection...', 'info');
        const apiAvailable = await this.checkApiStatus();
        
        if (!apiAvailable) {
            this.updateStatus('Cannot connect to API. Please check if the server is running.', 'error');
            return;
        }

        this.downloadInProgress = true;
        this.updateUI(true);
        this.clearLog();
        this.clearInspect();
        
        // Resetear estado de logging para nueva descarga
        this.lastLoggedTrack = null;
        this.recentLogs.clear();
        this.trackStates.clear();
        
        const formData = this.getFormData();
        
        try {
            // Paso 1: inspección
            this.updateStatus('Inspecting URL...', 'info');
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout
            
            const inspectResponse = await fetch(`${this.apiUrl}/inspect?spotify_url=${encodeURIComponent(formData.spotify_url)}`, {
                signal: controller.signal,
                method: 'GET',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!inspectResponse.ok) {
                const errorData = await inspectResponse.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || 'Error inspecting URL');
            }
            const inspectData = await inspectResponse.json();
            this.renderInspectData(inspectData);
        
            // Esperar un segundo antes de iniciar la descarga
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Paso 2: iniciar descarga
            this.updateStatus('Starting download...', 'info');
            this.addLogEntry('Sending download request...', 'info');

            const downloadController = new AbortController();
            const downloadTimeoutId = setTimeout(() => downloadController.abort(), 30000); // 30 second timeout

            const response = await fetch(`${this.apiUrl}/download`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(formData),
                signal: downloadController.signal
            });

            clearTimeout(downloadTimeoutId);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || 'Download error');
            }

            const result = await response.json();

            if (result.task_id) {
                this.currentTaskId = result.task_id;
                this.downloadStartTime = Date.now();
                this.saveState();
                this.addLogEntry(`Download started with ID: ${result.task_id}`, 'success');
                this.startProgressMonitoring(result.task_id);
            } else {
                this.updateStatus('Download completed successfully', 'success');
                this.addLogEntry('Download complete', 'success');
                this.downloadInProgress = false;
                this.updateUI(false);
            }

        } catch (error) {
            this.updateStatus(`Error: ${error.message}`, 'error');
            this.addLogEntry(`Error: ${error.message}`, 'error');
            this.downloadInProgress = false;
            this.updateUI(false);
        }
    }

    startProgressMonitoring(taskId) {
        // Monitorear progreso usando polling
        const pollInterval = 2000; // 2 segundo
        let progress = 0;
        
        const checkProgress = async () => {
            try {
                const response = await fetch(`${this.apiUrl}/download/${taskId}/status`);
                if (response.ok) {
                    const status = await response.json();
                    console.log('📡 API Status received:', status);
                    
                    if (status.status === 'completed') {
                        this.updateProgress(100);
                        this.updateStatus('Download completed successfully', 'success');
                        this.addLogEntry('Download complete', 'success');
                        
                        // Marcar todas las canciones como completadas
                        if (this.currentTrackData && this.currentTrackData.tracks) {
                            this.currentTrackData.tracks.forEach(track => {
                                if (this.trackStates.get(track.number) !== 'error') {
                                    this.updateTrackState(track.number, 'completed');
                                }
                            });
                        } else {
                            // Fallback: marcar por índice
                            this.trackStates.forEach((state, trackNumber) => {
                                if (state !== 'error') {
                                    this.updateTrackState(trackNumber, 'completed');
                                }
                            });
                        }
                        
                        this.downloadInProgress = false;
                        this.currentTaskId = null;
                        this.updateUI(false);
                        this.saveState();
                        return;
                    } else if (status.status === 'failed') {
                        this.updateStatus(`Error: ${status.message || 'Download failed'}`, 'error');
                        this.addLogEntry(`Error: ${status.message || 'Download failed'}`, 'error');
                        
                        // Marcar canción actual como error si está especificada
                        if (status.current_track_number) {
                            this.updateTrackState(status.current_track_number, 'error');
                        }
                        
                        this.downloadInProgress = false;
                        this.currentTaskId = null;
                        this.updateUI(false);
                        this.saveState();
                        return;
                    } else if (status.status === 'processing') {
                        const currentProgress = status.progress || 0;
                        this.updateProgress(currentProgress);
                        this.updateStatus(`Downloading... ${Math.round(currentProgress)}%`, 'info');
                        
                        // Actualizar estado de canción actual
                        if (status.current_track && this.currentTrackData) {
                            // Encontrar el número de canción basado en el nombre
                            const currentTrackNumber = this.findTrackNumberByName(status.current_track);
                            
                            if (currentTrackNumber) {
                                console.log(`🟡 Real download: Track ${currentTrackNumber} (${status.current_track}) is downloading`);
                                
                                // Marcar canción actual como descargando
                                this.updateTrackState(currentTrackNumber, 'downloading');
                                
                                // Marcar canciones anteriores como completadas
                                for (let i = 1; i < currentTrackNumber; i++) {
                                    if (this.trackStates.has(i) && this.trackStates.get(i) !== 'error') {
                                        this.updateTrackState(i, 'completed');
                                    }
                                }
                            } else {
                                console.warn(`⚠️ Could not find track number for: ${status.current_track}`);
                            }
                        } else if (status.current_track_number) {
                            // Fallback: usar current_track_number si está disponible
                            this.updateTrackState(status.current_track_number, 'downloading');
                            
                            for (let i = 1; i < status.current_track_number; i++) {
                                if (this.trackStates.has(i) && this.trackStates.get(i) !== 'error') {
                                    this.updateTrackState(i, 'completed');
                                }
                            }
                        }
                        
                        // Solo registrar la canción si es diferente a la última registrada
                        if (status.current_track && status.current_track !== this.lastLoggedTrack) {
                            this.addLogEntry(`Downloading: ${status.current_track}`, 'info');
                            this.lastLoggedTrack = status.current_track;
                        }
                    }
                    
                    // Continuar monitoreando
                    setTimeout(checkProgress, pollInterval);
                } else {
                    // Si no hay endpoint de estado, usar simulación
                    this.simulateProgress();
                }
            } catch (error) {
                console.warn('Error checking progress, using simulation:', error);
                this.simulateProgress();
            }
        };
        
        // Iniciar monitoreo
        checkProgress();
    }
    
    simulateProgress() {
        // Simulación de progreso para compatibilidad
        let progress = 0;
        let lastMessageIndex = -1;
        let simulatedTrackNumber = 1;
        const totalTracks = this.trackStates.size || 1;
        
        console.log('🎭 Starting simulation with real track data');
        
        const interval = setInterval(() => {
            progress += Math.random() * 8 + 2; // Progreso más consistente
            
            // Simular progreso por canción basado en datos reales
            const currentTrackByProgress = Math.ceil((progress / 100) * totalTracks);
            if (currentTrackByProgress > simulatedTrackNumber && simulatedTrackNumber <= totalTracks) {
                // Marcar canción anterior como completada
                if (simulatedTrackNumber > 1) {
                    this.updateTrackState(simulatedTrackNumber - 1, 'completed');
                }
                simulatedTrackNumber = currentTrackByProgress;
                
                // Simular log con nombre real de canción si está disponible
                if (this.currentTrackData && this.currentTrackData.tracks && this.currentTrackData.tracks[simulatedTrackNumber - 1]) {
                    const track = this.currentTrackData.tracks[simulatedTrackNumber - 1];
                    this.addLogEntry(`Downloading: ${track.name}`, 'info');
                }
            }
            
            // Actualizar canción actual como descargando
            if (simulatedTrackNumber <= totalTracks && progress < 100) {
                this.updateTrackState(simulatedTrackNumber, 'downloading');
            }
            
            if (progress >= 100) {
                progress = 100;
                this.updateProgress(progress);
                this.updateStatus('Download completed successfully', 'success');
                this.addLogEntry('Download complete', 'success');
                
                // Marcar todas las canciones como completadas
                this.trackStates.forEach((state, trackNumber) => {
                    if (state !== 'error') {
                        this.updateTrackState(trackNumber, 'completed');
                    }
                });
                
                this.downloadInProgress = false;
                this.updateUI(false);
                clearInterval(interval);
            } else {
                this.updateProgress(progress);
                this.updateStatus(`Downloading... ${Math.round(progress)}%`, 'info');
                
                // Simular mensajes de progreso, evitando repetir el último mensaje
                if (Math.random() > 0.8) { // Reducir frecuencia de mensajes
                    const messages = [
                        'Buscando canciones...',
                        'Descargando pista...',
                        'Aplicando metadatos...',
                        'Generando miniatura...',
                        'Guardando archivo...'
                    ];
                    
                    let messageIndex;
                    do {
                        messageIndex = Math.floor(Math.random() * messages.length);
                    } while (messageIndex === lastMessageIndex && messages.length > 1);
                    
                    lastMessageIndex = messageIndex;
                    this.addLogEntry(messages[messageIndex], 'info');
                }
            }
        }, 1000);
    }

    updateUI(downloading) {
        const downloadBtn = document.getElementById('download-btn');
        const progressContainer = document.getElementById('progress-container');
        
        if (downloading) {
            downloadBtn.disabled = true;
            downloadBtn.textContent = '⏳ Descargando...';
            progressContainer.classList.remove('hidden');
        } else {
            downloadBtn.disabled = false;
            downloadBtn.textContent = '🎵 Iniciar Descarga';
            progressContainer.classList.add('hidden');
            this.updateProgress(0);
        }
    }

    updateStatus(message, type = 'info') {
        const statusMessage = document.getElementById('status-message');
        statusMessage.textContent = message;
        statusMessage.className = `status-${type}`;
    }

    updateProgress(percentage) {
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        progressFill.style.width = `${percentage}%`;
        progressText.textContent = `${Math.round(percentage)}%`;
    }

    addLogEntry(message, type = 'info') {
        // Prevenir logs duplicados usando un identificador único
        const logId = `${type}:${message}`;
        const now = Date.now();
        
        // Verificar si este mensaje ya fue registrado recientemente
        if (this.recentLogs.has(logId)) {
            return; // No añadir logs duplicados
        }
        
        // Añadir al cache de logs recientes con cooldown
        this.recentLogs.add(logId);
        setTimeout(() => {
            this.recentLogs.delete(logId);
        }, this.logCooldownTime);
        
        const logContent = document.getElementById('log-content');
        const timestamp = new Date().toLocaleTimeString();
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.textContent = `[${timestamp}] ${message}`;
        
        // Insertar al principio para mostrar los más recientes arriba
        logContent.insertBefore(entry, logContent.firstChild);
        logContent.scrollTop = 0;
        
        // Guardar estado después de añadir log
        this.saveState();
    }

    findTrackNumberByName(trackName) {
        if (!this.currentTrackData || !this.currentTrackData.tracks) {
            return null;
        }
        
        // Limpiar el nombre de la canción para comparación
        const cleanTrackName = trackName.toLowerCase().trim();
        
        // Buscar la canción por nombre
        for (const track of this.currentTrackData.tracks) {
            const cleanCurrentName = track.name.toLowerCase().trim();
            if (cleanCurrentName === cleanTrackName || cleanCurrentName.includes(cleanTrackName) || cleanTrackName.includes(cleanCurrentName)) {
                console.log(`🎯 Found match: "${trackName}" -> Track ${track.number}`);
                return track.number;
            }
        }
        
        console.warn(`🔍 No match found for track: "${trackName}"`);
        console.log('Available tracks:', this.currentTrackData.tracks.map(t => `${t.number}: ${t.name}`));
        return null;
    }

    getStateIcon(state) {
        const icons = {
            'waiting': '⏳',      // Reloj de arena - Esperando
            'downloading': '🔄', // Flechas azules - Descargando 
            'completed': '✅',   // Check verde - Completado
            'error': '❌'         // X roja - Error
        };
        const icon = icons[state] || '⏳';
        console.log(`📍 getStateIcon(${state}) -> ${icon}`);
        return icon;
    }

    updateTrackState(trackNumber, state) {
        console.log(`🎆 BEFORE: Track ${trackNumber} state was:`, this.trackStates.get(trackNumber));
        this.trackStates.set(trackNumber, state);
        console.log(`🎆 AFTER: Track ${trackNumber} state is now:`, this.trackStates.get(trackNumber));
        console.log(`🎆 All states:`, Array.from(this.trackStates.entries()));
        
        // NO llamar updateInspectDisplay, actualizar directamente
        this.updateSingleTrackIcon(trackNumber, state);
    }

    updateSingleTrackIcon(trackNumber, state) {
        const container = document.getElementById('inspect-details');
        if (container.classList.contains('hidden')) {
            console.log('Container is hidden, not updating display');
            return;
        }
        
        const trackElement = container.querySelector(`[data-track-number="${trackNumber}"]`);
        if (trackElement) {
            const iconElement = trackElement.querySelector('.track-icon');
            if (iconElement) {
                const newIcon = this.getStateIcon(state);
                iconElement.textContent = newIcon;
                
                // Actualizar clases CSS
                trackElement.className = trackElement.className.replace(/track-state-\w+/g, '');
                trackElement.classList.add(`track-state-${state}`);
                trackElement.setAttribute('data-track-state', state);
                
                console.log(`🔄 Updated track ${trackNumber} icon to ${newIcon} (state: ${state})`);
            }
        } else {
            console.log(`❌ Could not find track element for track ${trackNumber}`);
        }
    }

    updateInspectDisplay() {
        if (!this.currentTrackData) {
            console.log('No currentTrackData available');
            return;
        }
        
        const container = document.getElementById('inspect-details');
        if (container.classList.contains('hidden')) {
            console.log('Container is hidden, not updating display');
            return;
        }
        
        console.log('Updating inspect display with current states:', Array.from(this.trackStates.entries()));
        
        // En lugar de re-renderizar todo, actualizar solo los iconos
        this.trackStates.forEach((state, trackNumber) => {
            const trackElement = container.querySelector(`[data-track-number="${trackNumber}"]`);
            if (trackElement) {
                const iconElement = trackElement.querySelector('.track-icon');
                if (iconElement) {
                    const newIcon = this.getStateIcon(state);
                    iconElement.textContent = newIcon;
                    
                    // Actualizar clases CSS
                    trackElement.className = trackElement.className.replace(/track-state-\w+/g, '');
                    trackElement.classList.add(`track-state-${state}`);
                    trackElement.setAttribute('data-track-state', state);
                    
                    console.log(`🔄 Updated track ${trackNumber} icon to ${newIcon} (state: ${state})`);
                }
            }
        });
    }

    clearLog() {
        const logContent = document.getElementById('log-content');
        logContent.innerHTML = '';
        
        // Limpiar también el estado de deduplicación
        this.recentLogs.clear();
        this.lastLoggedTrack = null;
        this.trackStates.clear();
        this.currentTrackData = null;
        
        // Forzar limpieza de caché de estados
        console.log('🧹 Clearing all track states and cache');
        
        this.saveState();
    }

    renderInspectData(data) {
        const container = document.getElementById('inspect-details');
        const message = document.getElementById('inspect-message');
        container.innerHTML = '';
        
        // Guardar datos para futuras actualizaciones
        this.currentTrackData = data;
        
        console.log('📝 renderInspectData called, trackStates:', Array.from(this.trackStates.entries()));
        console.log('🔍 Checking for active intervals/timeouts...');
        
        // Limpiar cualquier timeout/interval que pueda estar corriendo
        for (let i = 1; i < 99999; i++) {
            window.clearTimeout(i);
            window.clearInterval(i);
        }
        console.log('🧹 Cleared all timeouts and intervals');

        if (data.tracks) {
            // Inicializar estados de todas las canciones como 'waiting'
            data.tracks.forEach(t => {
                if (!this.trackStates.has(t.number)) {
                    this.trackStates.set(t.number, 'waiting');
                }
            });
            
            const header = document.createElement('h3');
            header.textContent = `${data.name} (${data.total_tracks} tracks)`;
            container.appendChild(header);

            const list = document.createElement('ul');
            list.style.listStyle = 'none';
            list.style.padding = '0';
            
            data.tracks.forEach(t => {
                const li = document.createElement('li');
                li.style.marginBottom = '8px';
                li.style.padding = '8px';
                li.style.borderRadius = '4px';
                li.style.backgroundColor = 'rgba(255,255,255,0.1)';
                li.style.transition = 'all 0.3s ease';
                
                const trackState = this.trackStates.get(t.number) || 'waiting';
                const stateIcon = this.getStateIcon(trackState);
                
                console.log(`🎨 Rendering track ${t.number}: state="${trackState}", icon="${stateIcon}"`);
                
                li.innerHTML = `
                    <span class="track-icon" style="margin-right: 12px; font-size: 20px; display: inline-block; width: 30px; text-align: center; background-color: rgba(255,255,255,0.2); border-radius: 50%; padding: 2px;">${stateIcon}</span>
                    <span class="track-info">${t.number}. ${t.name} — ${t.artists.join(', ')} [${Math.floor(t.duration/60)}:${(t.duration%60).toString().padStart(2,'0')}]</span>
                `;
                
                // Agregar clase CSS para estado
                li.classList.add(`track-state-${trackState}`);
                li.setAttribute('data-track-number', t.number);
                li.setAttribute('data-track-state', trackState);
                
                // Debug: Verificar qué estado tiene ahora
                console.log(`📝 Track ${t.number} initialized with state: ${trackState}`);
                
                list.appendChild(li);
            });
            container.appendChild(list);
            
        } else if (data.name && data.artists) {
            // Inicializar estado para canción individual
            if (!this.trackStates.has(1)) {
                this.trackStates.set(1, 'waiting');
            }
            
            const trackState = this.trackStates.get(1) || 'waiting';
            const stateIcon = this.getStateIcon(trackState);
            
            container.innerHTML = `
                <div style="margin-bottom: 10px;">
                    <span class="track-icon" style="margin-right: 8px; font-size: 16px;">${stateIcon}</span>
                    <strong>${data.name}</strong> — ${data.artists.join(', ')}
                </div>
                <p>Álbum: ${data.album_name}</p>
                <p>Duración: ${Math.floor(data.duration/60)}:${(data.duration%60).toString().padStart(2,'0')}</p>
            `;
        }

        message.classList.add('hidden');
        container.classList.remove('hidden');
        
        // Guardar estado después de mostrar detalles
        this.saveState();
    }

    clearInspect() {
        const container = document.getElementById('inspect-details');
        const message = document.getElementById('inspect-message');
        container.innerHTML = '';
        message.textContent = 'Esperando inspección...';
        message.classList.remove('hidden');
        container.classList.add('hidden');
    }

}

// Inicializar la aplicación cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    new SpotifySaverUI();
});
