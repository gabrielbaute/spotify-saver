# SpotifySaver 🎵✨

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PyPI Version](https://img.shields.io/pypi/v/spotifysaver?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/spotifysaver/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-orange?logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-2023.7.6%2B-red)](https://github.com/yt-dlp/yt-dlp)
[![YouTube Music](https://img.shields.io/badge/YouTube_Music-API-yellow)](https://ytmusicapi.readthedocs.io/)
[![Spotify](https://img.shields.io/badge/Spotify-API-1ED760?logo=spotify)](https://developer.spotify.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> ⚠️ Este repositorio está bajo una fuerte etapa de desarrollo, espere cambios constantes. Si encuentra algún error o bug, por favor abra un issue.

Herramienta todo-en-uno para descargar y organizar música con metadata de Spotify para Jellyfin.

La app se conecta a las API's de Spotify y de YoutubeMusic. El objetivo es generar un archivo .nfo en xml para completar la metadata que requiere jellyfin cuando construye las librerías de música.

Lee este archivo en [inglés](README.md)

## 🌟 Características
- ✅ Descarga audio de YouTube Music con metadata de Spotify
- ✅ Letras sincronizadas (.lrc) desde LRC Lib
- ✅ Generación de archivos `.info` compatibles con Jellyfin
- ✅ Estructura automática de carpetas (Artista/Álbum)
- ✅ Interfaz de línea de comandos (CLI)
- ✅ Soporte para playlist

### Requisitos
- Python 3.8+
- FFmpeg
- [Cuenta de desarrollador en Spotify](https://developer.spotify.com/dashboard/)

```bash
# Instalación con Poetry (recomendado)
git clone https://github.com/gabrielbaute/spotify-saver.git
cd spotify-saver
poetry install

# O con pip
pip install git+https://github.com/gabrielbaute/spotify-saver.git
```

⚠️ IMPORTANTE: Debes acceder a tu cuenta de spotify como desarrollador, crear una app y obtener así una "client id" y un "client secret", debes colocar esa info en un archivo .env en el directorio raíz del proyecto.

## ⚙️ Configuración

Crear archivo `.env`:

```ini
SPOTIFY_CLIENT_ID=tu_id
SPOTIFY_CLIENT_SECRET=tu_secreto
YTDLP_COOKIES_PATH="cookies.txt"  # Para contenido con restricción de edad
```

La variable `YTDLP_COOKIES_PATH` indicará la ubicación del archivo con las cookies de Youtube Music (importante, no usar las de Youtube, sino Youtube Music), en caso de que tengamos problemas con restricciones a yt-dlp.

También puedes consultar el archivo .example.env

## 💻 Uso de la CLI

### Comandos disponibles

| Comando                | Descripción                                      | Ejemplo                                      |
|------------------------|--------------------------------------------------|----------------------------------------------|
| `download [URL]`       | Descarga track/álbum de Spotify                  | `spotifysaver download "URL_SPOTIFY"`        |
| `inspect`              | Muestra la metadata de spotify (album, playlist) | `spotifysaver inspect "URL_SPOTIFY"`         |
| `show-log`             | Muestra el log de la aplicación                  | `spotifysaver show-log`                      |
| `version`              | Muestra la versión instalada                     | `spotifysaver version`                       |

### Opciones de download

| Opción               | Descripción                              | Valores aceptados            |
|----------------------|------------------------------------------|------------------------------|
| `--lyrics`           | Descargar letras sincronizadas (.lrc)    | Flag (sin valor)             |
| `--output DIR`       | Directorio de salida                     | Ruta válida                  |
| `--format FORMATO`   | Formato de audio                         | `m4a` (default), `mp3`       |
| `--cover`            | Descarga la portada del album (.jpg)     | Flag (no value)              |
| `--nfo`              | Genera un archivo .nfo con la metadata (para Jellyfin)| Flag (no value) |

### Opciones de show-log

| Opción            | Descripción                              | Valores aceptados       |
|-------------------|------------------------------------------|-------------------------|
| `--lines`         | Número de líneas del log que mostrar     | `--lines 25`            |
| `--level`         | Filtra por nivel de log                  | `--level WARNING`       |
| `--path`          | Muestra la ubicación del archivo de log  | Flag (sin valor)        |

## 💡 Ejemplos de uso
```bash
# Descargar álbum con letras sincronizadas
spotifysaver download "https://open.spotify.com/album/..." --lyrics

# Descargar album con archivo de metadata e imagen de portada
spotifysaver download "https://open.spotify.com/album/..." --nfo --cover

# Descargar canción en formato MP3 (aún en desarrollo 🚧)
spotifysaver download "https://open.spotify.com/track/..." --format mp3
```

## 📂 Estructura de salida
```
Music/
├── Artista/
│   ├── Álbum (Año)/
│   │   ├── 01 - Canción.m4a
│   │   ├── 01 - Canción.lrc
│   │   └── portada.jpg
│   └── artist_info.nfo
```

## 🤝 Contribuciones
1. Haz fork del proyecto
2. Crea tu rama (`git checkout -b feature/nueva-funcion`)
3. Haz commit de tus cambios (`git commit -m 'Agrega función increíble'`)
4. Push a la rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request

## 📄 Licencia

MIT © [TGabriel Baute](https://github.com/gabrielbaute)