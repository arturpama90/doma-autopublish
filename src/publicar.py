# -*- coding: utf-8 -*-
"""Publicador automático de DoMa Marketing.

Corre cada 15 minutos en GitHub Actions. Mira el calendario, busca las
publicaciones cuya hora ya llegó y que todavía no se han publicado, y las
sube a Instagram y Facebook.

Uso:
    python src/publicar.py                 # publica lo que toque ahora
    python src/publicar.py --seco          # solo dice qué haría, no publica
    python src/publicar.py --probar        # verifica el token y las cuentas
    python src/publicar.py --id p05        # fuerza una publicación concreta
"""
from __future__ import annotations

import argparse
import io
import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meta_api as meta  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("doma")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALENDARIO = os.path.join(RAIZ, "contenido", "calendario.json")
REGISTRO = os.path.join(RAIZ, "contenido", "publicado.json")

TZ = ZoneInfo("America/New_York")
# Margen: si el cron se retrasa, igual publicamos. Pero no resucitamos
# publicaciones viejas de hace días.
VENTANA = timedelta(hours=6)

# URL pública de los gráficos. GitHub sirve los archivos del repo por HTTPS,
# que es justo lo que exige la API de Instagram (no acepta subir bytes).
REPO = os.environ.get("GITHUB_REPOSITORY", "usuario/doma-autopublish")
RAMA = os.environ.get("GITHUB_REF_NAME", "main")
BASE_URL = os.environ.get(
    "BASE_URL_MEDIOS",
    f"https://raw.githubusercontent.com/{REPO}/{RAMA}/contenido",
)


def url_grafico(nombre: str) -> str:
    return f"{BASE_URL}/graficos/{nombre}"


def url_video(nombre: str) -> str:
    return f"{BASE_URL}/videos/{nombre}"


def cargar(path, defecto):
    if not os.path.exists(path):
        return defecto
    return json.load(io.open(path, encoding="utf-8"))


def guardar(path, data):
    io.open(path, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=2)
    )


def ahora() -> datetime:
    return datetime.now(TZ)


def hora_programada(post) -> datetime | None:
    if not post.get("programado_et"):
        return None
    return datetime.fromisoformat(post["programado_et"]).replace(tzinfo=TZ)


def toca_ahora(post, registro) -> bool:
    if post["id"] in registro:
        return False
    if post.get("estado") != "listo" and not post.get("video"):
        return False
    t = hora_programada(post)
    if not t:
        return False
    return t <= ahora() <= t + VENTANA


# ------------------------------------------------------------------ publicar
def publicar_post(post, seco=False) -> dict:
    texto = post["texto"]
    canales = post.get("canales_automaticos", [])
    imgs = [url_grafico(n) for n in post.get("imagenes", [])]
    video = post.get("video")
    resultado = {}

    log.info("→ %s · %s", post["id"], post["titulo"])
    log.info("   canales: %s", ", ".join(canales) or "ninguno")
    for u in imgs:
        log.info("   imagen: %s", u)
    if video:
        log.info("   video: %s", url_video(video))

    if seco:
        log.info("   [SECO] no se publica nada")
        return {"seco": True}

    # ---------------- Instagram
    if "instagram_reel" in canales and video:
        resultado["ig_reel"] = meta.ig_reel(
            url_video(video), texto,
            cover_url=imgs[0] if imgs else None,
        )
    elif "instagram_feed" in canales and imgs:
        if len(imgs) == 1:
            resultado["ig"] = meta.ig_imagen(imgs[0], texto)
        else:
            resultado["ig"] = meta.ig_carrusel(imgs[:10], texto)
    elif "instagram_story" in canales:
        if video:
            resultado["ig_story"] = meta.ig_historia(video_url=url_video(video))
        elif imgs:
            resultado["ig_story"] = meta.ig_historia(image_url=imgs[0])

    # ---------------- Facebook
    if "facebook" in canales:
        if video:
            log.info("   (el Reel de Facebook se sube aparte, no por esta vía)")
        elif len(imgs) == 1:
            resultado["fb"] = meta.fb_foto(imgs[0], texto)
        elif len(imgs) > 1:
            resultado["fb"] = meta.fb_album(imgs, texto)
        else:
            resultado["fb"] = meta.fb_texto(texto)

    for k, v in resultado.items():
        log.info("   ✓ %s → %s", k, v)
    return resultado


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seco", action="store_true", help="no publica, solo muestra")
    ap.add_argument("--probar", action="store_true", help="verifica token y cuentas")
    ap.add_argument("--id", help="fuerza una publicación por id")
    args = ap.parse_args()

    if args.probar:
        try:
            info = meta.verificar_credenciales()
        except Exception as e:  # noqa: BLE001
            log.error("No se pudo verificar: %s", e)
            log.error("")
            log.error("Revisa en GitHub: Settings → Secrets and variables → Actions")
            log.error("Tienen que existir META_ACCESS_TOKEN, IG_USER_ID y FB_PAGE_ID.")
            return 1
        log.info("Credenciales OK")
        log.info("  Instagram: @%s (%s seguidores) id=%s",
                 info["instagram"].get("username"),
                 info["instagram"].get("followers_count"),
                 info["instagram"].get("id"))
        log.info("  Facebook: %s (%s seguidores) id=%s",
                 info["facebook"].get("name"),
                 info["facebook"].get("fan_count"),
                 info["facebook"].get("id"))
        log.info("  Base de medios: %s", BASE_URL)
        return 0

    cal = cargar(CALENDARIO, {"posts": []})
    registro = cargar(REGISTRO, {})
    posts = cal["posts"]

    if args.id:
        pendientes = [p for p in posts if p["id"] == args.id]
        if not pendientes:
            log.error("No existe la publicación %s", args.id)
            return 1
    else:
        pendientes = [p for p in posts if toca_ahora(p, registro)]

    log.info("Hora actual (ET): %s", ahora().strftime("%Y-%m-%d %H:%M"))
    if not pendientes:
        log.info("Nada que publicar ahora. Todo en orden.")
        return 0

    log.info("Publicaciones que toca subir: %s", len(pendientes))
    fallos = 0
    for p in pendientes:
        try:
            res = publicar_post(p, seco=args.seco)
            if not args.seco:
                registro[p["id"]] = {
                    "titulo": p["titulo"],
                    "publicado_utc": datetime.now(timezone.utc).isoformat(),
                    "resultado": res,
                }
        except Exception as e:  # noqa: BLE001
            fallos += 1
            log.error("   ✗ falló %s: %s", p["id"], e)
            registro.setdefault("_errores", []).append({
                "id": p["id"],
                "cuando_utc": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
            })

    if not args.seco:
        guardar(REGISTRO, registro)
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
