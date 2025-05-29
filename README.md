# SpotifySaver

![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue) ![image](https://img.shields.io/badge/Spotify-1ED760?&style=for-the-badge&logo=spotify&logoColor=white) ![image](https://img.shields.io/badge/YouTube_Music-FF0000?style=for-the-badge&logo=youtube-music&logoColor=white)

Herramienta todo-en-uno para descarga y organización de música, diseñada para integración con Jellyfin.

## ✨ Características principales
- Descarga de audio desde YouTube Music con metadata de Spotify ✔️
- Obtención de letras sincronizadas (.lrc) desde LRC Lib ✔️
- Generación de archivos `.info` para Jellyfin 🚧
- Estructura de carpetas automática (Artista/Álbum) ✔️
- CLI 🚧

La app se conecta a las API's de Spotify y de YoutubeMusic. El objetivo es generar un archivo .info en xml para completar la metadata que requiere jellyfin cuando construye las librerías de música.

## 🛠 Instalación
```bash
pip install -r requirements.txt
```
⚠️ IMPORTANTE: Debes acceder a tu cuenta de spotify como desarrollador, crear una app y obtener así una "client id" y un "client secret", debes colocar esa info en un archivo .env en el directorio raíz del proyecto.
## 🚀 Uso básico
⚠️ Esta parte aún está en desarrollo
```bash
python -m spotifysaver [URL de Spotify] --format m4a --lyrics
```

## 📦 Estructura de archivos
```
Music/
├── Artist Name/
│   ├── Album Name (Year)/
│   │   ├── 01 - Track Name.m4a
│   │   ├── 01 - Track Name.lrc
│   │   └── album.info
│   └── artist.info
```

## 🤝 Contribución
¡PRs son bienvenidos! Por favor abre un issue primero para discutir cambios grandes.
