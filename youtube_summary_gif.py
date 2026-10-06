#!/usr/bin/env python3

import argparse
import os
import subprocess
import tempfile


def run(cmd, capture=False):
    print("->", " ".join(cmd))
    return subprocess.run(cmd, check=True, capture_output=capture, text=True)


def download_video(url, workdir):
    output_template = os.path.join(workdir, "source.%(ext)s")
    run(["yt-dlp", "-f", "mp4[height<=720]/mp4/best", "-o", output_template, url])
    for f in os.listdir(workdir):
        if f.startswith("source."):
            return os.path.join(workdir, f)
    raise RuntimeError("No se pudo descargar el video")


def get_duration(video_path):
    result = run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", video_path],
        capture=True
    )
    return float(result.stdout.strip())


def detect_scenes(video_path, threshold=0.3):
    cmd = ["ffmpeg", "-i", video_path,
           "-vf", f"select='gt(scene,{threshold})',showinfo",
           "-f", "null", "-"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    timestamps = []
    for line in result.stderr.splitlines():
        if "pts_time:" in line:
            for part in line.split():
                if part.startswith("pts_time:"):
                    try:
                        timestamps.append(float(part.split(":", 1)[1]))
                    except ValueError:
                        pass
                    break
    return timestamps


def pick_timestamps(duration, num_clips, scene_timestamps, margin=1.0):
    usable = [t for t in scene_timestamps if margin < t < duration - margin]
    if len(usable) >= num_clips:
        step = len(usable) / num_clips
        chosen = [usable[int(i * step)] for i in range(num_clips)]
    else:
        span = max(duration - 2 * margin, 0.1)
        denom = max(num_clips - 1, 1)
        chosen = [margin + i * span / denom for i in range(num_clips)]
    return sorted(chosen)


def extract_clips(video_path, timestamps, clip_length, workdir):
    clip_paths = []
    for i, ts in enumerate(timestamps):
        clip_path = os.path.join(workdir, f"clip_{i:02d}.mp4")
        run(["ffmpeg", "-y", "-ss", f"{ts:.3f}", "-i", video_path,
             "-t", str(clip_length), "-vf", "scale=480:-2", "-an", clip_path])
        clip_paths.append(clip_path)
    return clip_paths


def concat_clips(clip_paths, workdir):
    list_path = os.path.join(workdir, "list.txt")
    with open(list_path, "w") as f:
        for p in clip_paths:
            f.write(f"file '{p}'\n")
    concat_path = os.path.join(workdir, "concat.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
         "-c", "copy", concat_path])
    return concat_path


def make_gif(video_path, output_path, fps=15):
    palette_path = os.path.splitext(output_path)[0] + "_palette.png"
    run(["ffmpeg", "-y", "-i", video_path,
         "-vf", f"fps={fps},scale=480:-1:flags=lanczos,palettegen", palette_path])
    run(["ffmpeg", "-y", "-i", video_path, "-i", palette_path,
         "-filter_complex", f"fps={fps},scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse",
         output_path])
    os.remove(palette_path)


def main():
    parser = argparse.ArgumentParser(description="Genera un GIF resumen de un video de YouTube")
    parser.add_argument("url", help="URL del video de YouTube")
    parser.add_argument("--output", default="resumen.gif")
    parser.add_argument("--duration", type=float, default=5.0,
                         help="Duracion total aproximada del GIF, en segundos")
    parser.add_argument("--clips", type=int, default=5,
                         help="Cuantos fragmentos combinar")
    parser.add_argument("--fps", type=int, default=15)
    parser.add_argument("--scene-threshold", type=float, default=0.3,
                         help="Sensibilidad de deteccion de escenas (0-1, menor = mas sensible)")
    args = parser.parse_args()

    clip_length = args.duration / args.clips

    with tempfile.TemporaryDirectory() as workdir:
        print("Descargando video...")
        video_path = download_video(args.url, workdir)

        duration = get_duration(video_path)
        print(f"Duracion del video: {duration:.1f}s")

        print("Detectando cambios de escena...")
        scene_timestamps = detect_scenes(video_path, args.scene_threshold)
        print(f"  {len(scene_timestamps)} cambios detectados")

        timestamps = pick_timestamps(duration, args.clips, scene_timestamps)
        print("Momentos elegidos:", [f"{t:.1f}s" for t in timestamps])

        print("Extrayendo fragmentos...")
        clip_paths = extract_clips(video_path, timestamps, clip_length, workdir)

        print("Uniendo fragmentos...")
        concat_path = concat_clips(clip_paths, workdir)

        print("Generando GIF...")
        make_gif(concat_path, args.output, fps=args.fps)

    print(f"Listo: {args.output}")


if __name__ == "__main__":
    main()
