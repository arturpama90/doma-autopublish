# -*- coding: utf-8 -*-
"""Generador de Reels con Veo 3.1 (Gemini API).

Cómo está pensado, y esto es a propósito:

Veo hace clips de máximo 8 segundos. Un Reel de 35 segundos son 5 clips
pegados. Y la parte más importante: **los clips se generan SIN gente hablando
y sin caras**. Encima va TU voz, grabada con el celular.

Ese es el único camino para que un Reel con IA no se detecte como IA. El video
generado con personas hablando se cae en el primer segundo: la boca, los ojos y
la cadencia de la voz sintética son lo que todo el mundo reconoce ya. En cambio
manos, herramientas, comida, texturas y luz sí aguantan.

Uso:
    python src/generar_reel.py --id p01                  # genera el Reel del post p01
    python src/generar_reel.py --id p01 --voz voces/p01.m4a
    python src/generar_reel.py --listar                  # ve qué Reels faltan
    python src/generar_reel.py --id p01 --solo-clips     # sin pegar ni audio
"""
from __future__ import annotations

import argparse
import io
import json
import logging
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prompts_reels import PROMPTS, NEGATIVO  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("veo")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALENDARIO = os.path.join(RAIZ, "contenido", "calendario.json")
DIR_VIDEOS = os.path.join(RAIZ, "contenido", "videos")
DIR_CLIPS = os.path.join(RAIZ, "contenido", "clips")

MODELO = os.environ.get("VEO_MODELO", "veo-3.1-generate-preview")
RESOLUCION = os.environ.get("VEO_RESOLUCION", "1080p")
SEGUNDOS = os.environ.get("VEO_SEGUNDOS", "8")


def cliente():
    """Importa el SDK aquí para que --listar funcione sin credenciales."""
    if not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError(
            "Falta GEMINI_API_KEY. Ponla en los Secrets del repositorio "
            "(Settings → Secrets and variables → Actions)."
        )
    from google import genai
    return genai.Client()


def generar_clip(prompt: str, destino: str) -> str:
    """Un clip vertical de 8 segundos, sin caras y sin voz."""
    from google.genai import types

    if os.path.exists(destino):
        log.info("  ya existe, lo reuso: %s", os.path.basename(destino))
        return destino

    c = cliente()
    log.info("  generando: %s", os.path.basename(destino))
    op = c.models.generate_videos(
        model=MODELO,
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio="9:16",          # vertical, para Reels y TikTok
            resolution=RESOLUCION,
            number_of_videos=1,
            duration_seconds=SEGUNDOS,
            negative_prompt=NEGATIVO,
        ),
    )
    esperas = 0
    while not op.done:
        esperas += 1
        log.info("    procesando... (%s)", esperas * 10)
        time.sleep(10)
        op = c.operations.get(op)
        if esperas > 60:
            raise RuntimeError("Veo tardó demasiado en este clip")

    v = op.response.generated_videos[0]
    c.files.download(file=v.video)
    v.video.save(destino)
    log.info("  listo: %s", os.path.basename(destino))
    return destino


def ffmpeg(args: list[str]) -> None:
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg falló: {' '.join(args[:6])}...")


def pegar_clips(clips: list[str], destino: str) -> str:
    lista = destino + ".txt"
    io.open(lista, "w", encoding="utf-8").write(
        "".join(f"file '{os.path.abspath(c)}'\n" for c in clips)
    )
    ffmpeg(["-f", "concat", "-safe", "0", "-i", lista,
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", "30", destino])
    os.remove(lista)
    return destino


def poner_voz(video: str, audio_voz: str, destino: str) -> str:
    """Cambia el audio generado por tu voz real. Recorta al más corto."""
    ffmpeg(["-i", video, "-i", audio_voz,
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", destino])
    return destino


def grano(entrada: str, destino: str) -> str:
    """Grano de película y un poco menos de saturación.
    Suena a tontería y es lo que más rompe el look de IA: el video generado
    sale demasiado limpio y demasiado saturado.
    """
    ffmpeg(["-i", entrada,
            "-vf", "noise=alls=7:allf=t+u,eq=saturation=0.92:contrast=1.04",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "copy", destino])
    return destino


def pendientes() -> list[dict]:
    cal = json.load(io.open(CALENDARIO, encoding="utf-8"))
    return [p for p in cal["posts"] if p.get("necesita_video")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", help="id de la publicación (p01, p05, ...)")
    ap.add_argument("--voz", help="archivo de audio con tu voz (m4a, mp3, wav)")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--solo-clips", action="store_true")
    ap.add_argument("--sin-grano", action="store_true")
    args = ap.parse_args()

    if args.listar:
        for p in pendientes():
            tiene = "sí" if p["id"] in PROMPTS else "NO"
            log.info("%s · %s  (prompts: %s)", p["id"], p["titulo"], tiene)
        return 0

    if not args.id:
        ap.error("dime --id, o usa --listar")

    if args.id not in PROMPTS:
        log.error("No hay prompts para %s. Están en src/prompts_reels.py", args.id)
        return 1

    os.makedirs(DIR_VIDEOS, exist_ok=True)
    os.makedirs(DIR_CLIPS, exist_ok=True)

    prompts = PROMPTS[args.id]
    log.info("Reel %s · %s clips de %ss", args.id, len(prompts), SEGUNDOS)

    clips = []
    for n, pr in enumerate(prompts, 1):
        destino = os.path.join(DIR_CLIPS, f"{args.id}_c{n:02d}.mp4")
        clips.append(generar_clip(pr, destino))

    if args.solo_clips:
        log.info("Clips listos en %s. Revísalos antes de pegarlos.", DIR_CLIPS)
        return 0

    crudo = os.path.join(DIR_CLIPS, f"{args.id}_pegado.mp4")
    log.info("Pegando %s clips", len(clips))
    pegar_clips(clips, crudo)

    if args.voz:
        if not os.path.exists(args.voz):
            log.error("No encuentro el audio %s", args.voz)
            return 1
        log.info("Poniendo tu voz encima: %s", args.voz)
        con_voz = os.path.join(DIR_CLIPS, f"{args.id}_voz.mp4")
        poner_voz(crudo, args.voz, con_voz)
        crudo = con_voz
    else:
        log.warning("Sin --voz: se queda el audio que generó Veo. "
                    "Para publicar, mejor graba tu voz y vuelve a correrlo.")

    final = os.path.join(DIR_VIDEOS, f"{args.id}.mp4")
    if args.sin_grano:
        os.replace(crudo, final)
    else:
        log.info("Metiendo grano y bajando saturación")
        grano(crudo, final)

    mb = os.path.getsize(final) / 1e6
    log.info("Reel listo: contenido/videos/%s.mp4 (%.1f MB)", args.id, mb)
    log.info("Ahora súbelo al repositorio y el publicador lo recoge solo "
             "a la hora programada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
