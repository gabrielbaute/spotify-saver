# SpotifySaver 🎵

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-orange?logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-2023.7.6%2B-red)](https://github.com/yt-dlp/yt-dlp)
[![YouTube Music](https://img.shields.io/badge/YouTube_Music-API-yellow)](https://ytmusicapi.readthedocs.io/)
[![Spotify](https://img.shields.io/badge/Spotify-API-1ED760?logo=spotify)](https://developer.spotify.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Herramienta todo-en-uno para descarga y organización de música, diseñada para integración con Jellyfin.

## ✨ Características principales
- Descarga de audio desde YouTube Music con metadata de Spotify ✔️
- Obtención de letras sincronizadas (.lrc) desde LRC Lib ✔️
- Generación de archivos `.info` para Jellyfin 🚧
- Estructura de carpetas automática (Artista/Álbum) ✔️
- CLI ✔️

La app se conecta a las API's de Spotify y de YoutubeMusic. El objetivo es generar un archivo .info en xml para completar la metadata que requiere jellyfin cuando construye las librerías de música.

## 🔧 Requisitos

- Python 3.8+
- FFmpeg (para conversión de formatos)
- Cuenta de desarrollador en [Spotify Dashboard](https://developer.spotify.com/dashboard/)

## 🛠 Instalación
```bash
# Instalación con Poetry (recomendado)
git clone https://github.com/gabrielbaute/spotify-saver.git
cd spotify-saver
poetry install

# O con pip
pip install git+https://github.com/gabrielbaute/spotify-saver.git
```
⚠️ IMPORTANTE: Debes acceder a tu cuenta de spotify como desarrollador, crear una app y obtener así una "client id" y un "client secret", debes colocar esa info en un archivo .env en el directorio raíz del proyecto.

## 💻 Uso de la CLI

### Comandos disponibles

| Comando                | Descripción                                      | Ejemplo                                      |
|------------------------|--------------------------------------------------|----------------------------------------------|
| `download [URL]`       | Descarga track/álbum de Spotify                 | `spotifysaver download "URL_SPOTIFY"`     |
| `version`              | Muestra la versión instalada                    | `spotifysaver version`                    |

### Opciones principales

| Opción               | Descripción                              | Valores aceptados       |
|----------------------|------------------------------------------|-------------------------|
| `--lyrics`           | Descargar letras sincronizadas (.lrc)   | Flag (sin valor)        |
| `--output DIR`       | Directorio de salida                     | Ruta válida            |
| `--format FORMATO`   | Formato de audio                         | `m4a` (default), `mp3` |

### Ejemplos prácticos

1. **Descargar un álbum completo con letras:**
   ```bash
   spotifysaver download "https://open.spotify.com/album/..." --lyrics
   ```

2. **Descargar un track en formato MP3 (aún en desarrollo 🚧):**
   ```bash
   spotifysaver download "https://open.spotify.com/track/..." --format mp3
   ```

3. **Usar un directorio personalizado:**
   ```bash
   spotifysaver download "URL" --output "~/Music/Spotify"

## 🎛 Configuración

Crea un archivo `.env` en la raíz del proyecto con tus credenciales de Spotify:

```ini
SPOTIFY_CLIENT_ID=tu_client_id
SPOTIFY_CLIENT_SECRET=tu_client_secret
```

También puedes consultar el archivo .example.env

## 📦 Estructura de salida

```
Music/
├── Artist/
│   ├── Album (Year)/
│   │   ├── 01 - Track Name.m4a
│   │   ├── 01 - Track Name.lrc
│   │   └── cover.jpg
│   └── artist_info.json
```

## 🤝 Contribución

1. Haz fork del proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcion`)
3. Haz commit de tus cambios (`git commit -am 'Añade nueva función'`)
4. Haz push a la rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request

## 📄 Licencia

MIT © [TGabriel Baute](https://github.com/gabrielbaute)

## 🤝 Contribución
¡PRs son bienvenidos! Por favor abre un issue primero para discutir cambios grandes.
