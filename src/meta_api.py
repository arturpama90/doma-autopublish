# -*- coding: utf-8 -*-
"""Cliente mínimo de la Graph API de Meta para publicar en Instagram y Facebook.

Nada de credenciales en el código: todo sale de variables de entorno que
GitHub Actions inyecta desde los Secrets del repositorio.
"""
from __future__ import annotations

import os
import time
import logging

import requests

log = logging.getLogger("meta")

VERSION = os.environ.get("META_API_VERSION", "v21.0")
BASE = f"https://graph.facebook.com/{VERSION}"

TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
IG_USER_ID = os.environ.get("IG_USER_ID", "")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "")


class MetaError(RuntimeError):
    pass


def _check_env():
    faltan = [k for k, v in {
        "META_ACCESS_TOKEN": TOKEN,
        "IG_USER_ID": IG_USER_ID,
        "FB_PAGE_ID": FB_PAGE_ID,
    }.items() if not v]
    if faltan:
        raise MetaError(
            "Faltan estas variables de entorno: " + ", ".join(faltan) +
            ". Revisa los Secrets del repositorio en GitHub."
        )


def _post(path: str, data: dict) -> dict:
    _check_env()
    data = {**data, "access_token": TOKEN}
    r = requests.post(f"{BASE}/{path}", data=data, timeout=120)
    try:
        j = r.json()
    except Exception:
        raise MetaError(f"Respuesta no-JSON de {path}: {r.text[:300]}")
    if r.status_code >= 400 or "error" in j:
        err = j.get("error", {})
        raise MetaError(
            f"Graph API {r.status_code} en {path}: "
            f"{err.get('message', j)} (code={err.get('code')}, "
            f"subcode={err.get('error_subcode')})"
        )
    return j


def _get(path: str, params: dict | None = None) -> dict:
    _check_env()
    params = {**(params or {}), "access_token": TOKEN}
    r = requests.get(f"{BASE}/{path}", params=params, timeout=60)
    j = r.json()
    if r.status_code >= 400 or "error" in j:
        err = j.get("error", {})
        raise MetaError(f"Graph API {r.status_code} en {path}: {err.get('message', j)}")
    return j


# --------------------------------------------------------------- diagnóstico
def verificar_credenciales() -> dict:
    """Comprueba que el token sirve y devuelve a qué cuentas apunta.
    Úsalo con el workflow 'probar' antes de programar nada.
    """
    ig = _get(IG_USER_ID, {"fields": "id,username,name,followers_count"})
    fb = _get(FB_PAGE_ID, {"fields": "id,name,fan_count"})
    return {"instagram": ig, "facebook": fb}


# --------------------------------------------------------------- Instagram
def _ig_crear_contenedor(**params) -> str:
    j = _post(f"{IG_USER_ID}/media", params)
    return j["id"]


def _ig_esperar_listo(creation_id: str, intentos: int = 40, espera: int = 15) -> None:
    """Los videos tardan en procesarse. Hay que esperar a FINISHED."""
    for n in range(intentos):
        j = _get(creation_id, {"fields": "status_code,status"})
        estado = j.get("status_code")
        if estado == "FINISHED":
            return
        if estado == "ERROR":
            raise MetaError(f"Instagram falló al procesar el medio: {j.get('status')}")
        log.info("  procesando video (%s) intento %s/%s", estado, n + 1, intentos)
        time.sleep(espera)
    raise MetaError("Instagram no terminó de procesar el video a tiempo")


def _ig_publicar(creation_id: str) -> str:
    j = _post(f"{IG_USER_ID}/media_publish", {"creation_id": creation_id})
    return j["id"]


def ig_imagen(image_url: str, caption: str) -> str:
    cid = _ig_crear_contenedor(image_url=image_url, caption=caption)
    return _ig_publicar(cid)


def ig_carrusel(image_urls: list[str], caption: str) -> str:
    if not 2 <= len(image_urls) <= 10:
        raise MetaError(f"Un carrusel lleva entre 2 y 10 imágenes, llegaron {len(image_urls)}")
    hijos = [
        _ig_crear_contenedor(image_url=u, is_carousel_item="true")
        for u in image_urls
    ]
    padre = _ig_crear_contenedor(
        media_type="CAROUSEL", children=",".join(hijos), caption=caption
    )
    return _ig_publicar(padre)


def ig_reel(video_url: str, caption: str, cover_url: str | None = None,
            compartir_al_feed: bool = True) -> str:
    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": "true" if compartir_al_feed else "false",
    }
    if cover_url:
        params["cover_url"] = cover_url
    cid = _ig_crear_contenedor(**params)
    _ig_esperar_listo(cid)
    return _ig_publicar(cid)


def ig_historia(image_url: str | None = None, video_url: str | None = None) -> str:
    params = {"media_type": "STORIES"}
    if image_url:
        params["image_url"] = image_url
    elif video_url:
        params["video_url"] = video_url
    else:
        raise MetaError("Una historia necesita image_url o video_url")
    cid = _ig_crear_contenedor(**params)
    if video_url:
        _ig_esperar_listo(cid)
    return _ig_publicar(cid)


# --------------------------------------------------------------- Facebook
def fb_foto(image_url: str, mensaje: str,
            programar_unix: int | None = None) -> str:
    """Facebook sí acepta programación nativa con scheduled_publish_time."""
    params = {"url": image_url, "caption": mensaje}
    if programar_unix:
        params["published"] = "false"
        params["scheduled_publish_time"] = str(programar_unix)
    j = _post(f"{FB_PAGE_ID}/photos", params)
    return j.get("post_id") or j["id"]


def fb_texto(mensaje: str, programar_unix: int | None = None) -> str:
    params = {"message": mensaje}
    if programar_unix:
        params["published"] = "false"
        params["scheduled_publish_time"] = str(programar_unix)
    j = _post(f"{FB_PAGE_ID}/feed", params)
    return j["id"]


def fb_album(image_urls: list[str], mensaje: str,
             programar_unix: int | None = None) -> str:
    """Varias fotos en un solo post de Facebook."""
    ids = []
    for u in image_urls:
        j = _post(f"{FB_PAGE_ID}/photos",
                  {"url": u, "published": "false", "temporary": "true"})
        ids.append(j["id"])
    params = {"message": mensaje}
    for n, mid in enumerate(ids):
        params[f"attached_media[{n}]"] = f'{{"media_fbid":"{mid}"}}'
    if programar_unix:
        params["published"] = "false"
        params["scheduled_publish_time"] = str(programar_unix)
    j = _post(f"{FB_PAGE_ID}/feed", params)
    return j["id"]
