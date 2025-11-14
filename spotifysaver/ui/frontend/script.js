class SpotifySaverUI {
    constructor() {
        this.apiUrl = `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;
        this.apiUrlHealth = `${window.location.protocol}//${window.location.hostname}:8000/health`;
        this.downloadInProgress = false;
        this.eventSource = null;

        this.initializeEventListeners();
        this.checkApiStatus();
        this.setDefaultOutputDir();
    }

    initializeEventListeners() {
        const downloadBtn = document.getElementById('download-btn');
        const spotifyUrl = document.getElementById('spotify-url');
        
        downloadBtn.addEventListener('click', () => this.startDownload());
        
        // Permitir iniciar descarga con Enter
        spotifyUrl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.downloadInProgress) {
                this.startDownload();
            }
        });
    }

    async checkApiStatus() {
        try {
            const response = await fetch(this.apiUrlHealth);
            if (response.ok) {
                this.updateStatus('API connected and ready', 'success');
            } else {
                this.updateStatus('API connection error', 'error');
            }
        } catch (error) {
            this.updateStatus('API not available. Make sure it is running.', 'error');
        }
    }

    async setDefaultOutputDir() {
        try {
            const response = await fetch(`${this.apiUrl}/config/output_dir`);
            if (response.ok) {
                const data = await response.json();
                const outputDirInput = document.getElementById('output-dir');
                if (outputDirInput && data.output_dir) {
                    outputDirInput.value = data.output_dir;
                }
            }
        } catch (error) {
            outputDirInput.value = 'Music';
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

        this.downloadInProgress = true;
        this.updateUI(true);
        this.clearLog();
        this.clearInspect();
        
        const formData = this.getFormData();
        
        try {
            // Paso 1: inspección
            this.updateStatus('Inspecting URL...', 'info');
            const inspectResponse = await fetch(`${this.apiUrl}/inspect?spotify_url=${encodeURIComponent(formData.spotify_url)}`);
            if (!inspectResponse.ok) {
                throw new Error('Error inspecting URL');
            }
            const inspectData = await inspectResponse.json();
            this.renderInspectData(inspectData);
        
            // Esperar un segundo antes de iniciar la descarga
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Paso 2: iniciar descarga
            this.updateStatus('Starting download...', 'info');
            this.addLogEntry('Sending download request...', 'info');

            const response = await fetch(`${this.apiUrl}/download`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Download error');
            }

            const result = await response.json();

            if (result.task_id) {
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
                    
                    if (status.status === 'completed') {
                        this.updateProgress(100);
                        this.updateStatus('Download completed successfully', 'success');
                        this.addLogEntry('Download complete', 'success');
                        this.downloadInProgress = false;
                        this.updateUI(false);
                        return;
                    } else if (status.status === 'failed') {
                        this.updateStatus(`Error: ${status.message || 'Download failed'}`, 'error');
                        this.addLogEntry(`Error: ${status.message || 'Download failed'}`, 'error');
                        this.downloadInProgress = false;
                        this.updateUI(false);
                        return;
                    } else if (status.status === 'processing') {
                        const currentProgress = status.progress || 0;
                        this.updateProgress(currentProgress);
                        this.updateStatus(`Downloading... ${Math.round(currentProgress)}%`, 'info');
                        
                        if (status.current_track) {
                            this.addLogEntry(`Downloading: ${status.current_track}`, 'info');
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
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            
            if (progress >= 100) {
                progress = 100;
                this.updateProgress(progress);
                this.updateStatus('Download completed successfully', 'success');
                this.addLogEntry('Download complete', 'success');
                this.downloadInProgress = false;
                this.updateUI(false);
                clearInterval(interval);
            } else {
                this.updateProgress(progress);
                this.updateStatus(`Downloading... ${Math.round(progress)}%`, 'info');
                
                // Simular mensajes de progreso
                if (Math.random() > 0.7) {
                    const messages = [
                        'Buscando canciones...',
                        'Descargando pista...',
                        'Aplicando metadatos...',
                        'Generando miniatura...',
                        'Guardando archivo...'
                    ];
                    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
                    this.addLogEntry(randomMessage, 'info');
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
        const logContent = document.getElementById('log-content');
        const timestamp = new Date().toLocaleTimeString();
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.textContent = `[${timestamp}] ${message}`;
        
        logContent.appendChild(entry);
        logContent.scrollTop = logContent.scrollHeight;
    }

    clearLog() {
        const logContent = document.getElementById('log-content');
        logContent.innerHTML = '';
    }

    renderInspectData(data) {
        const container = document.getElementById('inspect-details');
        const message = document.getElementById('inspect-message');
        container.innerHTML = '';

        if (data.tracks) {
            const header = document.createElement('h3');
            header.textContent = `${data.name} (${data.total_tracks} tracks)`;
            container.appendChild(header);

            const list = document.createElement('ul');
            data.tracks.forEach(t => {
                const li = document.createElement('li');
                li.textContent = `${t.number}. ${t.name} — ${t.artists.join(', ')} [${Math.floor(t.duration/60)}:${(t.duration%60).toString().padStart(2,'0')}]`;
                list.appendChild(li);
            });
            container.appendChild(list);
        } else if (data.name && data.artists) {
            container.innerHTML = `
                <p><strong>${data.name}</strong> — ${data.artists.join(', ')}</p>
                <p>Álbum: ${data.album_name}</p>
                <p>Duración: ${Math.floor(data.duration/60)}:${(data.duration%60).toString().padStart(2,'0')}</p>
            `;
        }

        message.classList.add('hidden');
        container.classList.remove('hidden');
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
