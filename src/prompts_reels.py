# -*- coding: utf-8 -*-
"""Prompts de Veo 3.1 para los Reels de DoMa Marketing.

TRES REGLAS QUE NO SE ROMPEN, y aquí está el por qué:

1. CERO CARAS. Manos, espaldas, siluetas, objetos, comida, herramientas, luz.
   Una cara generada se detecta en dos segundos: la piel de cera, los ojos
   muertos, los dientes imposibles. Y para una agencia que vende autenticidad,
   que te caigan con eso es peor que no publicar.

2. CERO TEXTO EN EL VIDEO. La IA escribe mal. Los letreros, los rótulos y las
   pantallas salen con letras inventadas. El texto se pone después con la
   tipografía de la marca, encima.

3. CERO VOZ GENERADA. Los clips son apoyo visual. La voz es la de Arturo,
   grabada con el celular, con sus muletillas y su respiración. Eso es lo que
   ninguna IA falsifica y lo que hace que el Reel se sienta de una persona.

Cada lista de abajo son los clips de 8 segundos en orden. Cinco clips = 40
segundos de video, que es justo el largo bueno para un Reel.
"""

# Lo que le prohibimos a Veo en todos los clips. Es la mitad del trabajo.
NEGATIVO = (
    "faces, human face, close-up of face, portrait, people talking, mouth "
    "moving, lip sync, text, letters, words, signage, logos, watermark, "
    "subtitles, captions, oversaturated colors, glossy plastic look, "
    "perfect symmetry, stock photo look, cgi, 3d render, cartoon, "
    "smooth gimbal camera movement, slow motion"
)

# Sufijo que va en todos los prompts. Aquí vive el realismo.
REAL = (
    "shot on a handheld iPhone, slight camera shake, natural available light, "
    "visible sensor grain, imperfect off-center framing, cluttered real "
    "background, shallow depth of field, unretouched documentary footage, "
    "muted realistic colors"
)


def _p(*partes: str) -> str:
    return ", ".join(p.strip().rstrip(",") for p in partes if p.strip()) + ", " + REAL


PROMPTS: dict[str, list[str]] = {

    # ---------------------------------------------- p01 · El anuncio (3 ago)
    # Va sobre tú a cámara. Los clips son SOLO apoyo entre tus tomas reales.
    # Graba tú el inicio y el final; esto rellena el medio.
    "p01": [
        _p("A pair of hands turning the key in an old car ignition at dawn",
           "worn steering wheel, dashboard dust, windshield fogged at the edges",
           "warm low sunrise light through the side window"),
        _p("Close-up of a hand flipping a small cardboard OPEN sign on a glass door",
           "fingerprints on the glass, reflection of a quiet street",
           "early morning light"),
        _p("Overhead shot of two worn hands kneading dough on a scratched metal counter",
           "flour dust in the air, small family bakery back kitchen",
           "hard side light from one window"),
        _p("A hand in a work glove picking up a hammer from a plywood workbench",
           "sawdust, coiled extension cord, a coffee cup with a ring stain",
           "overcast light from an open garage door"),
        _p("Empty plastic chairs and folded tablecloths in a small family restaurant "
           "before opening",
           "mop bucket in the corner, one ceiling fan turning slowly",
           "fluorescent light mixed with daylight"),
    ],

    # ------------------------------- p05 · El link de reseñas (5 ago, 8 pm)
    # Este Reel es grabación de pantalla tuya. Solo necesita 2 clips de apoyo.
    "p05": [
        _p("Close-up over the shoulder of a hand holding a phone with a blank "
           "bright screen, blurred small shop interior behind",
           "shelves out of focus, a counter with a card reader"),
        _p("A hand setting down a phone next to a used receipt spike and a "
           "pen on a diner counter",
           "coffee stain rings on the formica"),
    ],

    # ----------------------------- p09 · Por qué es gratis (7 ago, 12:30 pm)
    "p09": [
        _p("An open spiral notebook on a cluttered desk with handwritten notes, "
           "unreadable scribbled handwriting, a pen resting on the page",
           "afternoon window light across the paper"),
        _p("A hand pouring coffee into a chipped mug next to a laptop, "
           "steam rising, papers scattered around"),
        _p("Close-up of a laptop trackpad and a hand scrolling, "
           "blurred bright screen, evening desk lamp light"),
    ],

    # ------------------------------------ p13 · WhatsApp (11 ago, 8 pm)
    "p13": [
        _p("A phone face down on the passenger seat of a work van, "
           "screen lighting up, ladder visible through the rear window",
           "dusk light, dirty windshield"),
        _p("A hand holding a phone at chest height inside a small bakery, "
           "trays of bread out of focus behind, blank bright screen"),
        _p("Close-up of a thumb resting on a phone screen edge, "
           "kitchen counter behind with a cutting board and a knife"),
        _p("A phone charging on a nightstand at night, cable tangled, "
           "screen glowing faintly, a glass of water beside it"),
    ],

    # ------------------------- p15 · La foto de producto (13 ago, 7:15 am)
    # Aquí Veo demuestra la técnica: es el Reel donde la IA suma más.
    "p15": [
        _p("A single loaf of bread on a wooden board placed beside a window, "
           "hard directional side light, deep shadow on the far side",
           "dust motes visible in the light beam"),
        _p("Same loaf of bread lit flatly from above by a yellow ceiling bulb, "
           "ugly flat shadow, dull color, unappetizing"),
        _p("A hand holding a white sheet of paper next to a plate of food to "
           "bounce window light, shadow softening on the near side"),
        _p("Low angle close-up of a plate of tacos at table height, "
           "window light from the left, blurred kitchen behind"),
        _p("A phone held low at product height photographing a pastry, "
           "the phone screen out of focus, marble counter"),
    ],

    # --------------------------- p20 · 3 frases que espantan (18 ago, 12:30)
    "p20": [
        _p("A hand crumpling a printed sheet of paper on a desk", "no readable text"),
        _p("Close-up of a hand tapping a phone screen impatiently, "
           "blurred office background, harsh overhead light"),
        _p("A closed shop door seen from outside at night, "
           "empty street reflection, a chain across the handle"),
    ],

    # ------------------------------- p24 · Lo que pasó anoche (22 ago, 11 am)
    # OJO: este Reel es material REAL del evento del 21. La IA aquí solo
    # rellena si te faltan tomas. Si tienes video del evento, no uses estos.
    "p24": [
        _p("A stack of business cards spread on a bar counter, "
           "one card slightly bent, low warm bar lighting"),
        _p("A hand writing notes in a small notebook under dim bar light, "
           "unreadable handwriting, a glass beside it"),
        _p("Empty glasses and folded napkins on a high table after an event, "
           "string lights out of focus in the background"),
    ],

    # ------------------ p27 · Por qué tu competencia sale primero (25 ago)
    "p27": [
        _p("Close-up of a hand holding a phone showing a blurred map screen, "
           "car dashboard visible below, daylight through windshield"),
        _p("A row of small storefronts on a suburban street shot from a moving car, "
           "palm trees, power lines, slightly out of focus"),
        _p("A hand placing a phone into a dashboard mount, "
           "sunlight glare across the screen"),
    ],

    # --------------------------- p29 · El error del mes (27 ago, 7:15 am)
    # Este es tu cara y tu voz, una sola toma. Los clips son puente.
    "p29": [
        _p("A phone screen full of unanswered message threads, held at an angle, "
           "blurred, no readable text, evening light"),
        _p("A hand crossing out a line in a notebook with a pen, "
           "unreadable handwriting, desk lamp light"),
        _p("An empty chair at a small table in a cafe, "
           "two coffee cups, one untouched, afternoon light"),
    ],

    # ---------------- p33 · El primer negocio patrocinado (31 ago, 7:15 am)
    # Si ya tienes el negocio elegido, GRABA AHÍ. Esto es solo respaldo.
    "p33": [
        _p("Hands untying an apron string behind the back in a small kitchen, "
           "steam and warm light"),
        _p("A hand turning a hanging OPEN sign on a small shop door, "
           "morning light, dusty glass"),
        _p("Overhead of a small business counter: a card reader, a jar of pens, "
           "a plant, a handwritten note pinned to the wall with unreadable text"),
        _p("A wide shot of a small storefront from across a quiet street at "
           "golden hour, no visible signage text, one car passing"),
    ],
}


# ---------------------------------------------------------------------------
# Cuánto cuesta esto, para que no te sorprenda la factura
#
# Veo 3.1 en la API: $0.40/seg estándar, $0.15/seg fast, $0.05/seg lite.
# Los clips son de 8 segundos.
#
#   Modo Lite  → $0.40 por clip  → un Reel de 5 clips = $2.00
#   Modo Fast  → $1.20 por clip  → un Reel de 5 clips = $6.00
#   Estándar   → $3.20 por clip  → un Reel de 5 clips = $16.00
#
# Los 10 Reels de agosto son 34 clips en total:
#   Lite  ≈ $14      Fast  ≈ $41      Estándar ≈ $109
#
# Recomendación: genera en Lite para probar el encuadre, y solo repite en
# Fast los clips que de verdad vayan a salir. Y pon VEO_SEGUNDOS=4 en las
# pruebas: cuesta la mitad.
# ---------------------------------------------------------------------------
