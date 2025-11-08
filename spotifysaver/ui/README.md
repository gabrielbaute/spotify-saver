# SpotifySaver UI

Interfaz gráfica web para SpotifySaver que ejecuta tanto la API como el frontend.

## Características

- **Interfaz web moderna y responsiva**: Fácil de usar desde cualquier navegador
- **Configuración completa**: Todos los parámetros de descarga disponibles
- **Monitoreo en tiempo real**: Progreso de descarga y logs de actividad
- **Servidor integrado**: Ejecuta automáticamente la API y el frontend

## Uso

### Comando básico

```bash
spotifysaver-ui
```

Esto iniciará:
- **API Server**: `http://localhost:8000`
- **Web Interface**: `http://localhost:3000`

### Parámetros configurables

En la interfaz web puedes configurar:

- **URL de Spotify**: Pega cualquier URL de Spotify (playlist, álbum, canción)
- **Directorio de salida**: Donde se guardarán las descargas
- **Formato de audio**: M4A (recomendado) o MP3
- **Bitrate**: Desde 96 kbps hasta 258 kbps o "Mejor calidad"
- **Incluir letras**: Descargar letras sincronizadas cuando estén disponibles
- **Crear archivos NFO**: Para integración con Jellyfin/Kodi

### Características de la interfaz

1. **Validación de URLs**: Verifica que la URL sea válida de Spotify
2. **Monitoreo de progreso**: Barra de progreso y estado en tiempo real
3. **Registro de actividad**: Log detallado de todas las operaciones
4. **Notificaciones visuales**: Estados de éxito, error y advertencia
5. **Diseño responsivo**: Funciona en desktop y móvil

### Puertos por defecto

- **Frontend**: Puerto 3000
- **API**: Puerto 8000

## Arquitectura

El comando `spotifysaver-ui` ejecuta:

1. **Servidor API**: FastAPI backend que maneja las descargas
2. **Servidor Web**: Sirve la interfaz HTML/CSS/JavaScript
3. **Apertura automática**: Abre el navegador automáticamente

## Detener el servidor

Usa `Ctrl+C` para detener ambos servidores de manera segura.

## Dependencias

El comando utiliza las mismas dependencias que el resto de SpotifySaver:
- FastAPI para la API
- Servidor HTTP integrado de Python para el frontend
- Todas las dependencias de descarga y procesamiento

## Desarrollo

Los archivos del frontend están en:
- `spotifysaver/ui/frontend/index.html`
- `spotifysaver/ui/frontend/styles.css`
- `spotifysaver/ui/frontend/script.js`

El servidor está en:
- `spotifysaver/ui/server.py`
