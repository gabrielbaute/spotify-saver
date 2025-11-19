class ApiClient {
    constructor() {
        this.apiUrl = `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;
        this.apiUrlHealth = `${window.location.protocol}//${window.location.hostname}:8000/health`;
        this.apiUrlVersion = `${window.location.protocol}//${window.location.hostname}:8000/version`;
        this.maxRetries = 3;
    }

    async checkApiStatusWithRetry() {
        for (let i = 0; i < this.maxRetries; i++) {
            const success = await this.checkApiStatus();
            if (success) {
                return true;
            }
            
            if (i < this.maxRetries - 1) {
                await new Promise(resolve => setTimeout(resolve, 2000 * (i + 1))); // Exponential backoff
            }
        }
        return false;
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
                return true;
            } else {
                return false;
            }
        } catch (error) {
            console.warn('API status check failed:', error);
            return false;
        }
    }

    async getDefaultOutputDir() {
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
                return data.output_dir || 'Music';
            } else {
                return 'Music';
            }
        } catch (error) {
            console.warn('Could not fetch default output directory, using fallback:', error);
            return 'Music';
        }
    }

    async getAppVersion() {
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
                return data.version || null;
            } else {
                console.warn('Could not fetch app version from API');
                return null;
            }
        } catch (error) {
            console.warn('Could not fetch app version, using fallback:', error);
            return null;
        }
    }

    async inspectSpotifyUrl(spotifyUrl) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout
        
        const response = await fetch(`${this.apiUrl}/inspect?spotify_url=${encodeURIComponent(spotifyUrl)}`, {
            signal: controller.signal,
            method: 'GET',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || 'Error inspecting URL');
        }
        
        return await response.json();
    }

    async startDownload(formData) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

        const response = await fetch(`${this.apiUrl}/download`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(formData),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || 'Download error');
        }

        return await response.json();
    }

    async getDownloadStatus(taskId) {
        try {
            const response = await fetch(`${this.apiUrl}/download/${taskId}/status`);
            if (response.ok) {
                return await response.json();
            }
            return null;
        } catch (error) {
            console.warn('Error checking download status:', error);
            return null;
        }
    }
}