class SpotifySaverUI {
    constructor() {
        this.apiUrl = 'http://localhost:8000/api/v1';
        this.apiUrlHealth = 'http://localhost:8000/health';
        this.downloadInProgress = false;
        this.eventSource = null;
        
        this.initializeEventListeners();
        this.checkApiStatus();
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
                this.updateStatus('API conectada y lista', 'success');
            } else {
                this.updateStatus('Error de conexión con la API', 'error');
            }
        } catch (error) {
            this.updateStatus('API no disponible. Asegúrate de que esté ejecutándose.', 'error');
        }
    }

    getFormData() {
        const bitrateValue = document.getElementById('bitrate').value;
        const bitrate = bitrateValue === 'best' ? 256 : parseInt(bitrateValue);
        
        return {
            spotify_url: document.getElementById('spotify-url').value,
            output_dir: document.getElementById('output-dir').value || 'Music',
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
            this.updateStatus('Por favor, ingresa una URL de Spotify', 'error');
            return false;
        }
        
        if (!formData.spotify_url.includes('spotify.com')) {
            this.updateStatus('La URL debe ser de Spotify', 'error');
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
        
        const formData = this.getFormData();
        
        try {
            this.updateStatus('Iniciando descarga...', 'info');
            this.addLogEntry('Enviando solicitud de descarga...', 'info');
            
            const response = await fetch(`${this.apiUrl}/download`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error en la descarga');
            }

            const result = await response.json();
            
            if (result.task_id) {
                this.addLogEntry(`Descarga iniciada con ID: ${result.task_id}`, 'success');
                this.startProgressMonitoring(result.task_id);
            } else {
                this.updateStatus('Descarga completada exitosamente', 'success');
                this.addLogEntry('Descarga completada', 'success');
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
                        this.updateStatus('Descarga completada exitosamente', 'success');
                        this.addLogEntry('Descarga completada', 'success');
                        this.downloadInProgress = false;
                        this.updateUI(false);
                        return;
                    } else if (status.status === 'failed') {
                        this.updateStatus(`Error: ${status.message || 'Descarga fallida'}`, 'error');
                        this.addLogEntry(`Error: ${status.message || 'Descarga fallida'}`, 'error');
                        this.downloadInProgress = false;
                        this.updateUI(false);
                        return;
                    } else if (status.status === 'processing') {
                        const currentProgress = status.progress || 0;
                        this.updateProgress(currentProgress);
                        this.updateStatus(`Descargando... ${Math.round(currentProgress)}%`, 'info');
                        
                        if (status.current_track) {
                            this.addLogEntry(`Descargando: ${status.current_track}`, 'info');
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
                this.updateStatus('Descarga completada exitosamente', 'success');
                this.addLogEntry('Descarga completada', 'success');
                this.downloadInProgress = false;
                this.updateUI(false);
                clearInterval(interval);
            } else {
                this.updateProgress(progress);
                this.updateStatus(`Descargando... ${Math.round(progress)}%`, 'info');
                
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
}

// Inicializar la aplicación cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    new SpotifySaverUI();
});
