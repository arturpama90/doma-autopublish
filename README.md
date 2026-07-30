# DoMa Marketing · Publicación automática

Publica solo en Instagram y Facebook, a la hora exacta, sin que nadie toque nada.
Corre en GitHub Actions (gratis) y no necesita que tu computadora esté prendida.

---

## Lo primero: los permisos que necesito

Tú los creas, tú los pegas en GitHub. **Yo nunca veo ninguno de estos valores** —
van en los "Secrets" del repositorio, que es una caja que GitHub encripta y que
ni yo ni nadie puede leer después de guardarla. Es el mismo principio que un
gestor de contraseñas: tú lo pones, el programa lo usa, nadie lo ve.

**No me pegues ninguno de estos en el chat.** Si me mandas un token por mensaje,
queda escrito en la conversación y hay que revocarlo. Van directo a GitHub.

### En Meta (developers.facebook.com)

Crea una app de tipo **Business** y activa el producto **Instagram**. Los permisos
(scopes) que la app tiene que pedir son estos cinco:

| Permiso | Para qué sirve |
|---|---|
| `instagram_basic` | Leer qué cuenta de Instagram es. Es el requisito previo de todo lo demás. |
| `instagram_content_publish` | **El importante.** Es el que permite subir posts, carruseles y Reels. |
| `pages_show_list` | Ver la página de Facebook a la que está conectado el Instagram. |
| `pages_read_engagement` | Leer datos de la página (necesario para publicar en ella). |
| `pages_manage_posts` | Publicar y programar en la página de Facebook. |

Si en tu panel aparecen con los nombres nuevos, son estos: `instagram_business_basic`
y `instagram_business_content_publish`. Meta está migrando los nombres, sirven igual.

**Sobre el App Review:** para publicar en **tus propias** cuentas normalmente basta
con la app en modo desarrollo, contigo como administrador. El App Review completo y
la verificación de negocio solo hacen falta el día que publiques para cuentas de
clientes. Cuando llegues a eso, avísame y lo preparamos con tiempo, porque tarda
semanas.

**Sobre el token, y esto importa:** el token normal de página caduca a los 60 días,
o sea que en octubre esto se te para sin avisar. Genera mejor un **token de usuario
del sistema** (Business Settings → System Users → crear uno → Generate New Token,
con los cinco permisos de arriba). Ese no caduca. Es diez minutos más de trabajo
y te ahorra el susto.

### En Google (para los Reels con Veo 3.1)

Saca una **GEMINI_API_KEY** en `aistudio.google.com/apikey`. Necesita facturación
activa porque Veo no está en el nivel gratis.

---

## Los cuatro secretos que hay que pegar en GitHub

Ve a tu repositorio → **Settings** → **Secrets and variables** → **Actions** →
**New repository secret**. Uno por uno:

| Nombre del secreto | De dónde sale |
|---|---|
| `META_ACCESS_TOKEN` | El token de usuario del sistema que generaste arriba |
| `IG_USER_ID` | El id de tu cuenta de Instagram (abajo te digo cómo sacarlo) |
| `FB_PAGE_ID` | El id de tu página. **Probablemente sea `102617588196317`** — lo vi en la URL de tu Business Suite. Verifícalo con la prueba. |
| `GEMINI_API_KEY` | La llave de Google AI Studio |

### Cómo saco el IG_USER_ID

Pega esto en el navegador cambiando `TU_TOKEN`:

```
https://graph.facebook.com/v21.0/102617588196317?fields=instagram_business_account&access_token=TU_TOKEN
```

Te devuelve algo así: `{"instagram_business_account":{"id":"178414..."}}`.
Ese número es el `IG_USER_ID`.

---

## Instalación, paso a paso

1. **Crea el repositorio en GitHub.** Ponle `doma-autopublish`. Y tiene que ser
   **público**. Ahora te explico por qué, porque es la parte contraintuitiva.

2. **Sube todo el contenido de esta carpeta** al repositorio. Puedes arrastrar los
   archivos en la web de GitHub ("Add file" → "Upload files"), no necesitas saber
   usar git.

3. **Pega los cuatro secretos** como te expliqué arriba.

4. **Activa Actions.** Pestaña "Actions" → "I understand my workflows, go ahead
   and enable them".

5. **Prueba antes de que salga nada.** Actions → "Publicar en Instagram y Facebook"
   → "Run workflow" → modo **probar**. Si el token está bien, te va a decir el
   nombre de tu Instagram y de tu Facebook. Si falla, el error te dice exactamente
   qué permiso falta.

6. **Ensayo en seco.** Vuelve a lanzarlo en modo **seco**. Te dice qué publicaría
   y con qué imagen, sin publicar nada.

7. **Suéltalo.** Desde ese momento revisa cada 15 minutos y publica lo que toque.
   No tienes que hacer nada más.

### ¿Por qué el repositorio tiene que ser público?

Porque la API de Instagram **no acepta que le subas un archivo**. Solo acepta una
dirección web pública de donde ella misma baja la imagen. GitHub sirve los archivos
del repositorio por HTTPS, y eso es justo lo que Instagram necesita.

Si el repositorio es privado, esas direcciones piden contraseña, Instagram no puede
entrar, y todo falla con un error que no dice nada útil.

Los 23 gráficos son material de marketing que de todas formas va a ser público el
día que se publique, así que no hay nada que esconder. Lo que sí queda a la vista
es tu calendario de contenido. Si eso te molesta, hay dos salidas: un repositorio
público solo para las imágenes y otro privado para el resto, o subir las imágenes a
Cloudflare R2 (tiene nivel gratis) y cambiar `BASE_URL_MEDIOS`. Dime y lo armo.

---

## Cómo se usa el día a día

### Publicar
No haces nada. Ya está programado.

### Cambiar un texto o una hora
Edita `contenido/calendario.json`. El campo `programado_et` es hora de Nueva York
en formato `2026-08-14T12:30:00`. Guarda y ya.

### Forzar una publicación ahora mismo
Actions → "Publicar" → Run workflow → modo `publicar_ahora` + el id (`p05`).

### Saltarse una publicación
Ponle `"estado": "manual"` en el JSON y el publicador la ignora.

### Generar un Reel
Actions → "Generar un Reel con Veo 3.1" → Run workflow → el id + calidad.
Empieza siempre en **lite con 4 segundos** para ver los encuadres: cuesta centavos.
Cuando te guste, repítelo en **fast con 8 segundos**.

El video queda guardado en `contenido/videos/p05.mp4` y el publicador lo recoge
solo cuando llegue su hora.

### Ponerle tu voz a un Reel
Graba el audio con el celular (la grabadora de voz sirve), llámalo igual que la
publicación (`p05.m4a`) y súbelo a la carpeta `voces/`. El generador lo detecta y
lo mete encima automáticamente.

---

## Lo que este sistema NO hace, para que no te agarre desprevenido

- **TikTok no.** No tiene API abierta de publicación para cuentas normales. Los
  Reels que se generen los subes a mano a TikTok, que además es mejor: TikTok
  castiga el video que llega con marca de agua de Instagram.
- **Google Business no.** Es otra API distinta. Son 4 publicaciones al mes, se
  hacen a mano en 5 minutos.
- **WhatsApp no.** Los Estados de WhatsApp no se pueden automatizar, y de hecho no
  querrías: la gracia del Estado es que se ve hecho a mano.
- **Instagram no programa por su cuenta.** Su API publica en el momento, no acepta
  una fecha futura. Por eso el cron de cada 15 minutos: ese cron *es* el
  programador. Facebook sí acepta programación nativa y el código la usa.
- **El cron puede retrasarse.** GitHub no garantiza el minuto exacto cuando hay
  mucha carga. Un post de las 7:15 puede salir 7:20 o 7:30. Para este uso da igual.

---

## Sobre los Reels con IA. Lee esto antes de gastar dinero.

Quieres Reels con IA que parezcan reales. Se puede, pero hay que saber dónde está
la línea, porque hay dos riesgos concretos y ninguno es teórico.

**Uno: Meta detecta el video generado y le baja el alcance.** No solo lee los
metadatos del archivo; también corre sus propios clasificadores sobre los píxeles.
Borrar los metadatos no sirve de nada. Y el contenido sintético que Meta considera
engañoso puede perder hasta cerca del 80% de su alcance. En publicidad pagada la
declaración ya es obligatoria y un anuncio se puede pausar retroactivamente por no
haberla hecho.

**Dos, y este es peor para ti:** DoMa vende autenticidad a negocios hispanos. Que
te salga la etiqueta "Hecho con IA" en un Reel donde sales "tú" hablando no es un
problema de alcance, es un problema de credibilidad. Es la única cosa que no se
arregla con otro post.

**Por eso el generador está armado así, y no es una limitación técnica sino una
decisión:**

| | |
|---|---|
| Los clips de IA | manos, herramientas, comida, texturas, luz, calles, objetos |
| Nunca | caras, gente hablando, texto dentro de la imagen |
| La voz | siempre la tuya, grabada con el celular |
| El acabado | grano y menos saturación por ffmpeg, porque Veo entrega demasiado limpio |

Así el Reel es **IA de verdad** (el video lo generó una máquina, que es lo que
pediste) y a la vez **no se ve hecho con IA**, porque lo que la gente detecta son
las caras y las voces, no un plano de unas manos amasando pan.

Y una recomendación de estrategia: cuando publiques uno, **di que es con IA**. En
tus redes eso no te resta, te suma. Un post de "así hice este video con IA en 20
minutos y me costó 2 dólares" es exactamente el contenido que tu cliente quiere
ver de su agencia de marketing. Conviertes el riesgo en el argumento de venta.

### Lo que cuesta

Clips de 8 segundos. Un Reel son 3 a 5 clips.

| Modo | Por clip | Un Reel | Los 10 Reels (34 clips) |
|---|---|---|---|
| Lite (720p) | $0.40 | ~$2 | ~$14 |
| Fast | $1.20 | ~$6 | ~$41 |
| Estándar | $3.20 | ~$16 | ~$109 |

Con `segundos: 4` cuesta la mitad. Prueba siempre en lite y 4 segundos.

---

## Si algo se rompe

| Error | Qué pasó |
|---|---|
| `Faltan estas variables de entorno` | Falta un secreto, o está mal escrito el nombre |
| `code=190` | El token caducó o lo revocaron. Genera otro. |
| `code=200` | Falta un permiso. Compara con la tabla de arriba. |
| `The image_url is not accessible` | El repositorio está privado, o el nombre del PNG no coincide |
| `Media upload has failed` en un Reel | El video pesa mucho o no es 9:16. Debe ser vertical y menos de 100 MB. |
| Se publicó dos veces | Falló el commit de `publicado.json`. Revisa que el workflow tenga `contents: write`. |

El registro de todo lo publicado vive en `contenido/publicado.json`, y los errores
se guardan ahí mismo con su fecha.

---

## Qué hay en cada carpeta

```
.github/workflows/
  publicar.yml        el cron de cada 15 minutos
  generar-reel.yml    el generador de Reels, se lanza a mano
contenido/
  calendario.json     las 33 publicaciones con fecha, hora, texto e imagen
  publicado.json      registro de lo que ya salió (se escribe solo)
  graficos/           los 23 PNG
  videos/             los Reels terminados
  clips/              los clips de 8 seg sueltos
voces/                tus audios grabados con el celular
src/
  publicar.py         el publicador
  meta_api.py         el cliente de la Graph API
  generar_reel.py     el generador con Veo
  prompts_reels.py    los prompts de video, con las reglas anti-IA
```

---

## Antes de que salga la primera publicación

- [ ] Cambiar el usuario de Instagram a **@crececondoma** (hoy es `@marketing_doma`).
      Los 23 gráficos ya dicen crececondoma; si no lo cambias, apuntan a una cuenta
      que no existe.
- [ ] Cambiar también el nombre de usuario de la página de Facebook.
- [ ] Correr el workflow en modo `probar` y ver que devuelve tus dos cuentas.
- [ ] Correr en modo `seco` y leer qué publicaría.
- [ ] Rellenar los datos entre corchetes `[ ]` de tres publicaciones: el testimonio
      del 26 de agosto, el cierre del mes del 30, y el anuncio del negocio
      patrocinado del 31.
