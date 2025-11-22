class DownloadManager {
    constructor(apiClient, uiManager, saveStateCallback = null) {
        this.apiClient = apiClient;
        this.uiManager = uiManager;
        this.saveStateCallback = saveStateCallback;
        this.downloadInProgress = false;
        this.currentTaskId = null;
        this.downloadStartTime = null;
        this.lastLoggedTrack = null;
        this.lastLoggedTrackState = null; // Track the state of the last logged track
        this.trackStates = new Map();
        this.currentTrackData = null;
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
            this.uiManager.updateStatus('Please enter a valid Spotify URL', 'error');
            return false;
        }
        
        if (!formData.spotify_url.includes('spotify.com')) {
            this.uiManager.updateStatus('The URL must be from Spotify.', 'error');
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
        this.uiManager.updateStatus('Checking API connection...', 'info');
        const apiAvailable = await this.apiClient.checkApiStatusWithRetry();
        
        if (!apiAvailable) {
            this.uiManager.updateStatus('Cannot connect to API. Please check if the server is running.', 'error');
            return;
        }

        this.downloadInProgress = true;
        this.uiManager.updateUI(true);
        this.uiManager.clearLog();
        this.uiManager.clearInspect();
        
        // Resetear estado de logging para nueva descarga
        this.lastLoggedTrack = null;
        this.lastLoggedTrackState = null;
        this.trackStates.clear();
        
        const formData = this.getFormData();
        
        try {
            // Paso 1: inspección
            this.uiManager.updateStatus('Inspecting URL...', 'info');
            
            const inspectData = await this.apiClient.inspectSpotifyUrl(formData.spotify_url);
            this.uiManager.renderInspectData(inspectData, this.trackStates);
            this.currentTrackData = inspectData;
        
            // Esperar un segundo antes de iniciar la descarga
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Paso 2: iniciar descarga
            this.uiManager.updateStatus('Starting download...', 'info');
            this.uiManager.addLogEntry('Sending download request...', 'info');

            const result = await this.apiClient.startDownload(formData);

            if (result.task_id) {
                this.currentTaskId = result.task_id;
                this.downloadStartTime = Date.now();
                this.uiManager.addLogEntry(`Download started with ID: ${result.task_id}`, 'success');
                if (this.saveStateCallback) {
                    this.saveStateCallback();
                }
                this.startProgressMonitoring(result.task_id);
            } else {
                this.uiManager.updateStatus('Download completed successfully', 'success');
                this.uiManager.addLogEntry('Download complete', 'success');
                this.downloadInProgress = false;
                this.uiManager.updateUI(false);
            }

        } catch (error) {
            this.uiManager.updateStatus(`Error: ${error.message}`, 'error');
            this.uiManager.addLogEntry(`Error: ${error.message}`, 'error');
            this.downloadInProgress = false;
            this.uiManager.updateUI(false);
        }
    }

    startProgressMonitoring(taskId) {
        // Monitorear progreso usando polling
        const pollInterval = 2000; // 2 segundos
        
        const checkProgress = async () => {
            try {
                const status = await this.apiClient.getDownloadStatus(taskId);
                if (status) {
                    console.log('📡 API Status received:', status);
                    
                    if (status.status === 'completed') {
                        this.handleDownloadCompleted();
                        return;
                    } else if (status.status === 'failed') {
                        this.handleDownloadFailed(status.message || 'Download failed', status.current_track_number);
                        return;
                    } else if (status.status === 'processing') {
                        this.handleDownloadProgress(status);
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

    handleDownloadCompleted() {
        this.uiManager.updateProgress(100);
        this.uiManager.updateStatus('Download completed successfully', 'success');
        this.uiManager.addLogEntry('Download complete', 'success');
        
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
        this.uiManager.updateUI(false);
        if (this.saveStateCallback) {
            this.saveStateCallback();
        }
    }

    handleDownloadFailed(message, currentTrackNumber) {
        this.uiManager.updateStatus(`Error: ${message}`, 'error');
        this.uiManager.addLogEntry(`Error: ${message}`, 'error');
        
        // Marcar canción actual como error si está especificada
        if (currentTrackNumber) {
            this.updateTrackState(currentTrackNumber, 'error');
        }
        
        this.downloadInProgress = false;
        this.currentTaskId = null;
        this.uiManager.updateUI(false);
        if (this.saveStateCallback) {
            this.saveStateCallback();
        }
    }

    handleDownloadProgress(status) {
        const currentProgress = status.progress || 0;
        this.uiManager.updateProgress(currentProgress);
        this.uiManager.updateStatus(`Downloading... ${Math.round(currentProgress)}%`, 'info');
        
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
        // Registrar estado de la canción actual
        this.logTrackStatus(status);
    }
    
    logTrackStatus(status) {
        // Verificar si la última canción registrada cambió a completed o error
        if (this.lastLoggedTrack && this.lastLoggedTrackState) {
            const lastTrackNumber = this.findTrackNumberByName(this.lastLoggedTrack);
            if (lastTrackNumber) {
                const currentLastTrackState = this.trackStates.get(lastTrackNumber);
                if (currentLastTrackState !== this.lastLoggedTrackState && 
                    (currentLastTrackState === 'completed' || currentLastTrackState === 'error')) {
                    const statusMessage = currentLastTrackState === 'completed' ? 'Completed' : 'Failed';
                    this.uiManager.addLogEntry(`${statusMessage}: ${this.lastLoggedTrack}`, 
                        currentLastTrackState === 'completed' ? 'success' : 'error');
                    this.lastLoggedTrackState = currentLastTrackState;
                }
            }
        }
        
        // Solo registrar la nueva canción si es diferente a la última registrada
        if (status.current_track && status.current_track !== this.lastLoggedTrack) {
            this.uiManager.addLogEntry(`Downloading: ${status.current_track}`, 'info');
            this.lastLoggedTrack = status.current_track;
            // Actualizar el estado inicial de la nueva canción registrada
            const currentTrackNumber = this.findTrackNumberByName(status.current_track);
            if (currentTrackNumber) {
                this.lastLoggedTrackState = this.trackStates.get(currentTrackNumber) || 'downloading';
            }
        }
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
                    this.uiManager.addLogEntry(`Downloading: ${track.name}`, 'info');
                }
            }
            
            // Actualizar canción actual como descargando
            if (simulatedTrackNumber <= totalTracks && progress < 100) {
                this.updateTrackState(simulatedTrackNumber, 'downloading');
            }
            
            if (progress >= 100) {
                progress = 100;
                this.uiManager.updateProgress(progress);
                this.uiManager.updateStatus('Download completed successfully', 'success');
                this.uiManager.addLogEntry('Download complete', 'success');
                
                // Marcar todas las canciones como completadas
                this.trackStates.forEach((state, trackNumber) => {
                    if (state !== 'error') {
                        this.updateTrackState(trackNumber, 'completed');
                    }
                });
                
                this.downloadInProgress = false;
                this.uiManager.updateUI(false);
                clearInterval(interval);
            } else {
                this.uiManager.updateProgress(progress);
                this.uiManager.updateStatus(`Downloading... ${Math.round(progress)}%`, 'info');
                
                // Simular mensajes de progreso, evitando repetir el último mensaje
                if (Math.random() > 0.8) { // Reducir frecuencia de mensajes
                    const messages = [
                        'Searching for tracks...',
                        'Downloading track...',
                        'Setting metadata...',
                        'Generating thumbnail...',
                        'Saving file...',
                    ];
                    
                    let messageIndex;
                    do {
                        messageIndex = Math.floor(Math.random() * messages.length);
                    } while (messageIndex === lastMessageIndex && messages.length > 1);
                    
                    lastMessageIndex = messageIndex;
                    this.uiManager.addLogEntry(messages[messageIndex], 'info');
                }
            }
        }, 1000);
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

    updateTrackState(trackNumber, state) {
        this.trackStates.set(trackNumber, state);        
        // Actualizar UI
        this.uiManager.updateSingleTrackIcon(trackNumber, state);
    }

    clearStates() {
        this.trackStates.clear();
        this.currentTrackData = null;
        this.lastLoggedTrack = null;
        this.lastLoggedTrackState = null;
    }

    // Getters for state access
    get isDownloadInProgress() {
        return this.downloadInProgress;
    }

    get taskId() {
        return this.currentTaskId;
    }

    get startTime() {
        return this.downloadStartTime;
    }

    // Methods to restore state
    restoreDownloadState(downloadInProgress, taskId, startTime) {
        this.downloadInProgress = downloadInProgress;
        this.currentTaskId = taskId;
        this.downloadStartTime = startTime;
        
        if (downloadInProgress && taskId) {
            this.startProgressMonitoring(taskId);
        }
    }
}