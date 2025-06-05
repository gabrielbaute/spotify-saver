# SpotifySaver API

Una API REST construida con FastAPI para descargar música de Spotify vía YouTube Music.

## ⚙️ Configuración

### 1. Credenciales de Spotify API

1. Ve al [Dashboard de Spotify for Developers](https://developer.spotify.com/dashboard/applications)
2. Crea una nueva aplicación o usa una existente
3. Copia el `Client ID` y `Client Secret`
4. Crea un archivo `.env` en la raíz del proyecto:

```bash
# Copia el archivo de ejemplo
cp .env.example .env
```

5. Edita el archivo `.env` con tus credenciales:

```env
SPOTIFY_CLIENT_ID=tu_client_id_aqui
SPOTIFY_CLIENT_SECRET=tu_client_secret_aqui
SPOTIFYSAVER_OUTPUT_DIR=Music  # Opcional
```

### 2. Instalar dependencias

```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# O solo las dependencias de la API
pip install fastapi uvicorn
```

## 🚀 Inicio Rápido

### Ejecutar el servidor

```bash
# Usando Poetry
poetry run uvicorn spotifysaver.api.main:app --reload

# O directamente
python -m spotifysaver.api.main

# O usando el script
spotifysaver-api
```

El servidor estará disponible en: `http://localhost:8000`

## 📚 Documentación

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔌 Endpoints

### GET `/`
Información básica de la API.

### GET `/health`
Verificación de estado del servicio.

### GET `/api/v1/inspect`
Inspecciona una URL de Spotify y devuelve los metadatos sin descargar.

**Parámetros:**
- `spotify_url` (string): URL de Spotify

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/inspect?spotify_url=https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
```

### POST `/api/v1/download`
Inicia una tarea de descarga.

**Cuerpo de la petición:**
```json
{
  "spotify_url": "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy",
  "download_lyrics": false,
  "download_cover": true,
  "generate_nfo": false,
  "output_format": "m4a",
  "output_dir": "Music"
}
```

**Respuesta:**
```json
{
  "task_id": "uuid-task-id",
  "status": "pending",
  "spotify_url": "https://open.spotify.com/album/...",
  "content_type": "album",
  "message": "Download task started for album"
}
```

### GET `/api/v1/download/{task_id}/status`
Obtiene el estado de una tarea de descarga.

**Respuesta:**
```json
{
  "task_id": "uuid-task-id",
  "status": "processing",
  "progress": 45,
  "current_track": "Track Name",
  "total_tracks": 12,
  "completed_tracks": 5,
  "failed_tracks": 0,
  "output_directory": "/path/to/music",
  "started_at": "2024-01-01T12:00:00"
}
```

### GET `/api/v1/download/{task_id}/cancel`
Cancela una tarea de descarga.

### GET `/api/v1/downloads`
Lista todas las tareas de descarga.

## 💡 Ejemplos de Uso

### Python con requests

```python
import requests

# Inspeccionar un álbum
response = requests.get(
    "http://localhost:8000/api/v1/inspect",
    params={"spotify_url": "https://open.spotify.com/album/..."}
)
metadata = response.json()

# Iniciar descarga
download_request = {
    "spotify_url": "https://open.spotify.com/album/...",
    "download_lyrics": True,
    "download_cover": True,
    "generate_nfo": True
}
response = requests.post(
    "http://localhost:8000/api/v1/download",
    json=download_request
)
task = response.json()

# Verificar estado
status_response = requests.get(
    f"http://localhost:8000/api/v1/download/{task['task_id']}/status"
)
status = status_response.json()
```

### JavaScript/Node.js

```javascript
// Inspeccionar URL
const inspectResponse = await fetch(
  `http://localhost:8000/api/v1/inspect?spotify_url=${encodeURIComponent(spotifyUrl)}`
);
const metadata = await inspectResponse.json();

// Iniciar descarga
const downloadResponse = await fetch('http://localhost:8000/api/v1/download', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    spotify_url: spotifyUrl,
    download_lyrics: true,
    download_cover: true,
    generate_nfo: false
  })
});
const task = await downloadResponse.json();

// Verificar estado
const statusResponse = await fetch(
  `http://localhost:8000/api/v1/download/${task.task_id}/status`
);
const status = await statusResponse.json();
```

### cURL

```bash
# Inspeccionar
curl "http://localhost:8000/api/v1/inspect?spotify_url=https://open.spotify.com/track/..."

# Iniciar descarga
curl -X POST "http://localhost:8000/api/v1/download" \
  -H "Content-Type: application/json" \
  -d '{
    "spotify_url": "https://open.spotify.com/album/...",
    "download_lyrics": true,
    "download_cover": true
  }'

# Verificar estado
curl "http://localhost:8000/api/v1/download/{task_id}/status"
```

## ⚙️ Configuración

### Variables de Entorno

```bash
# Archivo .env
SPOTIFY_CLIENT_ID=tu_client_id
SPOTIFY_CLIENT_SECRET=tu_client_secret
YTDLP_COOKIES_PATH="cookies.txt"  # Opcional
SPOTIFYSAVER_OUTPUT_DIR="Music"   # Directorio de salida por defecto
```

### Configuración de CORS

Por defecto, la API permite conexiones desde:
- `http://localhost:*`
- `http://127.0.0.1:*`

Para modificar esto, edita `spotifysaver/api/config.py`.

## 🔄 Estados de Descarga

- **`pending`**: Tarea creada, esperando procesamiento
- **`processing`**: Descarga en progreso
- **`completed`**: Descarga completada exitosamente
- **`failed`**: Error durante la descarga
- **`cancelled`**: Tarea cancelada por el usuario

## 📁 Estructura de Salida

```
Music/
├── Artista/
│   ├── Álbum (Año)/
│   │   ├── 01 - Canción.m4a
│   │   ├── 01 - Canción.lrc  # Si se solicitan letras
│   │   ├── album.nfo         # Si se solicita NFO
│   │   └── cover.jpg         # Si se solicita portada
│   └── ...
└── Playlist Name/
    ├── Track 01.m4a
    ├── Track 02.m4a
    └── cover.jpg
```

## 🚨 Limitaciones

- Las descargas son procesadas secuencialmente para evitar sobrecarga
- El almacenamiento de tareas es en memoria (se reinicia con el servidor)
- Se recomienda usar Redis o una base de datos para producción
- Las cookies de YouTube Music pueden ser necesarias para contenido restringido

## 🛡️ Consideraciones de Seguridad

- La API no incluye autenticación por defecto
- No expongas la API directamente a internet sin autenticación
- Considera usar un proxy reverso (nginx) para producción
- Valida y sanitiza todas las URLs de entrada

## 📝 Logging

Los logs se generan usando el sistema de logging de SpotifySaver. Para habilitar logs detallados:

```python
from spotifysaver.spotlog import LoggerConfig
LoggerConfig.setup(level="DEBUG")
```
