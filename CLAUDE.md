# DoMa Marketing · Publicación automática

Contexto para Claude Code. Este repositorio publica solo en Instagram y Facebook
(@crececondoma / DOMA Marketing) mediante GitHub Actions + Graph API.

## Qué es cada cosa

- `contenido/calendario.json` — la fuente de verdad. 33 publicaciones con fecha
  (`programado_et`, hora de Nueva York), canales, texto e imágenes.
- `contenido/publicado.json` — registro de lo ya publicado. **Nunca lo edites a
  mano** salvo para des-marcar un post que se quiera republicar.
- `contenido/graficos/` — PNG listos (1080×1350, historias 1080×1920).
- `src/publicar.py` — el publicador (cron cada 15 min vía `.github/workflows/publicar.yml`).
- `src/generar_reel.py` + `src/prompts_reels.py` — Reels con Veo 3.1.
- `voces/` — audios de Arturo (`p01.m4a`...) que se montan sobre los Reels.

## Comandos

```bash
pip install -r requirements.txt
python src/publicar.py --seco            # qué publicaría ahora (sin credenciales OK)
python src/publicar.py --seco --id p05   # ensayar un post concreto
python src/publicar.py --probar          # verificar token y cuentas (pide secrets)
python src/generar_reel.py --listar      # Reels pendientes
```

Secrets (solo en GitHub Actions, jamás en el repo ni en commits):
`META_ACCESS_TOKEN`, `IG_USER_ID`, `FB_PAGE_ID`, `GEMINI_API_KEY`.

## Reglas editoriales — OBLIGATORIAS al tocar textos

La estrategia actual es **crecimiento** (seguidores, guardados, compartidos).
La venta llega después con publicaciones aparte.

1. **Nada que sugiera que la agencia es nueva o tiene pocos clientes.** Prohibido:
   "estoy empezando", "tengo dos clientes", conteos bajos de nada. Genera
   desconfianza (decisión de Arturo, 30-jul-2026).
2. **CTA de crecimiento, no de venta**: "sígueme", "guárdalo", "compárteselo a un
   dueño de negocio", "comenta X y te mando Y por mensaje". Máximo 1 post de
   oferta por cada 5.
3. **Cada post lleva un ancla verificable**: lugar (The Melby, Hialeah), proceso
   ("videollamada de 30 minutos"), número (465,000 · Census 2022, precios) o
   fecha (10 ago clases Brevard, 21 ago Business Social).
4. **Lista negra** (suenan a IA): desbloquea, potencia, siguiente nivel,
   transforma, revoluciona, sinergia, empodera, maximiza, optimiza, era digital,
   soluciones integrales. Sin guiones largos (—) en los copys. Máximo 2 emojis.
5. **Tono**: de tú, español neutro (público mexicano, puertorriqueño, cubano,
   venezolano, colombiano), cero jerga de marketing. Servicio 100% virtual:
   nunca asumir la ciudad del lector.
6. **Visuales**: caras solo en fotos reales. La IA (Veo) solo genera manos,
   objetos, comida, texturas — nunca caras, gente hablando ni texto en pantalla.
   La voz siempre es la de Arturo.

## Cómo hacer cambios típicos

- **Cambiar hora/texto de un post**: editar `contenido/calendario.json`
  (`programado_et` formato `2026-08-14T12:30:00`, hora ET).
- **Saltarse un post**: `"estado": "manual"`.
- **Publicar algo ya**: Actions → "Publicar en Instagram y Facebook" →
  Run workflow → `publicar_ahora` + id.
- **Nuevo post**: añadir objeto al JSON con id nuevo (`p34`...), respetando las
  reglas editoriales de arriba. Los PNG nuevos van a `contenido/graficos/` y se
  referencian por nombre de archivo.
- **Verificar antes de commit**: correr `--seco` y releer el texto en voz alta;
  si no suena a una persona hablando, reescribir.

## Cosas que NO hacer

- No convertir el repo en privado (Instagram lee las imágenes por URL pública).
- No tocar `publicado.json` en PRs de contenido.
- No subir tokens, .env con valores, ni credenciales en ningún archivo.
- No publicar los gráficos de precios (17, 18, 19, 20) por ahora: la campaña de
  venta se hará aparte, más elaborada.
