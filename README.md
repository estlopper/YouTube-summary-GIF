youtube_summary_gif.py


# Español

Descarga un video de YouTube y genera automáticamente un GIF:
varios fragmentos cortos tomados de distintos momentos del video (elegidos
por detección de cambios de escena) unidos en un solo GIF.

Requisitos:
    pip install yt-dlp --break-system-packages   (o sin esa bandera según tu sistema)
    ffmpeg y ffprobe deben estar instalados y en el PATH

Usos posibles:
    python youtube_summary_gif.py "https://www.youtube.com/watch?v=XXXX"
    python youtube_summary_gif.py "URL" --output resumen.gif --duration 5 --clips 5

Si no funciona la primera vez ejecutar en cmd: winget install Gyan.FFmpeg


# English

Downloads a YouTube video and automatically generates a GIF:
several short clips taken from different points in the video (chosen
through scene-change detection) joined into a single GIF.

Requirements:
    pip install yt-dlp --break-system-packages   (or without that flag, depending on your system)
    ffmpeg and ffprobe must be installed and on the PATH

Example usage:
    python youtube_summary_gif.py "https://www.youtube.com/watch?v=XXXX"
    python youtube_summary_gif.py "URL" --output summary.gif --duration 5 --clips 5

If it doesn't work the first time, run this in cmd: winget install Gyan.FFmpeg