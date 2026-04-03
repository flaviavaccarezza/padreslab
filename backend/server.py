from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Tuple
import uuid
from datetime import datetime


app = FastAPI()
api_router = APIRouter(prefix="/api")


# =========================
# MODELS
# =========================

class SituationInput(BaseModel):
    text: str
    user_id: Optional[str] = None
    lang: Optional[str] = "es"      # es | en | it
    variant: Optional[str] = "tu"   # tu | vos


class SituationSection(BaseModel):
    que_podria_estar_pasando: str
    como_hablar: dict
    senales_de_alerta: dict
    proximos_pasos: dict
    reconexion: dict


class SituationResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    categoria_detectada: str
    intensidad_emocional: str
    riesgo_alto: bool
    mensaje_ayuda_profesional: Optional[str] = None
    secciones: SituationSection
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RewriteInput(BaseModel):
    original_text: str
    context: Optional[str] = None
    lang: Optional[str] = "es"
    variant: Optional[str] = "tu"


class RewriteResponse(BaseModel):
    versiones: List[str]


class FrequentSituation(BaseModel):
    id: str
    titulo: str
    descripcion: str
    emoji: str


class HelpResource(BaseModel):
    tipo: str
    nombre: str
    telefono: Optional[str] = None
    descripcion: str


# =========================
# LANGUAGE / VARIANT HELPERS
# =========================

LANG_TEXT = {
    "es": {
        "root_message": "PadresLab API funcionando 🚀",
        "urgent_help": (
            "Lo que describes puede implicar una situación de riesgo serio. "
            "No lo abordes en soledad: busca ayuda profesional o institucional de inmediato."
        ),
        "rewrite_1_prefix": "Quiero decirte esto de una manera más clara y respetuosa: ",
        "rewrite_2_prefix": "No busco pelearme contigo; necesito que podamos hablar mejor sobre esto: ",
    },
    "en": {
        "root_message": "PadresLab API is running 🚀",
        "urgent_help": (
            "What you describe may involve a serious risk situation. "
            "Do not handle it alone: seek professional or institutional support immediately."
        ),
        "rewrite_1_prefix": "I want to say this in a clearer and more respectful way: ",
        "rewrite_2_prefix": "I am not trying to fight with you; I need us to talk better about this: ",
    },
    "it": {
        "root_message": "PadresLab API attiva 🚀",
        "urgent_help": (
            "Quello che descrivi può implicare una situazione di rischio serio. "
            "Non affrontarla da solo/a: cerca subito aiuto professionale o istituzionale."
        ),
        "rewrite_1_prefix": "Vorrei dire questo in modo più chiaro e rispettoso: ",
        "rewrite_2_prefix": "Non voglio litigare con te; ho bisogno che possiamo parlare meglio di questo: ",
    },
}


def get_lang(lang: Optional[str]) -> str:
    if lang in ("es", "en", "it"):
        return lang
    return "es"


def get_variant(variant: Optional[str]) -> str:
    if variant in ("tu", "vos"):
        return variant
    return "tu"


def apply_variant(text: str, lang: str, variant: str) -> str:
    if lang != "es":
        return text

    if variant == "vos":
        replacements = [
            ("contigo", "vos"),
            ("tú", "vos"),
            ("Tu", "Vos"),
            ("eres", "sos"),
            ("Eres", "Sos"),
            ("tienes", "tenés"),
            ("Tienes", "Tenés"),
            ("puedes", "podés"),
            ("Puedes", "Podés"),
            ("quieres", "querés"),
            ("Quieres", "Querés"),
            ("necesitas", "necesitás"),
            ("Necesitas", "Necesitás"),
            ("sientes", "sentís"),
            ("Sientes", "Sentís"),
            ("muestras", "mostrás"),
            ("Muestras", "Mostrás"),
            ("describes", "describís"),
            ("Describes", "Describís"),
            ("busca", "buscá"),
            ("Busca", "Buscá"),
            ("habla", "hablá"),
            ("Habla", "Hablá"),
            ("actúa", "actuá"),
            ("Actúa", "Actuá"),
            ("elige", "elegí"),
            ("Elige", "Elegí"),
            ("prioriza", "priorizá"),
            ("Prioriza", "Priorizá"),
            ("sostén", "sostené"),
            ("Sostén", "Sostené"),
            ("pon", "poné"),
            ("Pon", "Poné"),
            ("retoma", "retomá"),
            ("Retoma", "Retomá"),
            ("haz", "hacé"),
            ("Haz", "Hacé"),
            ("tranquilo", "tranquilo"),
            ("tranquila", "tranquila"),
        ]
    else:
        replacements = [
            ("vos", "tú"),
            ("Vos", "Tú"),
            ("sos", "eres"),
            ("Sos", "Eres"),
            ("tenés", "tienes"),
            ("Tenés", "Tienes"),
            ("podés", "puedes"),
            ("Podés", "Puedes"),
            ("querés", "quieres"),
            ("Querés", "Quieres"),
            ("necesitás", "necesitas"),
            ("Necesitás", "Necesitas"),
            ("sentís", "sientes"),
            ("Sentís", "Sientes"),
            ("mostrás", "muestras"),
            ("Mostrás", "Muestras"),
            ("describís", "describes"),
            ("Describís", "Describes"),
            ("buscá", "busca"),
            ("Buscá", "Busca"),
            ("hablá", "habla"),
            ("Hablá", "Habla"),
            ("actuá", "actúa"),
            ("Actuá", "Actúa"),
            ("elegí", "elige"),
            ("Elegí", "Elige"),
            ("priorizá", "prioriza"),
            ("Priorizá", "Prioriza"),
            ("sostené", "sostén"),
            ("Sostené", "Sostén"),
            ("poné", "pon"),
            ("Poné", "Pon"),
            ("retomá", "retoma"),
            ("Retomá", "Retoma"),
            ("hacé", "haz"),
            ("Hacé", "Haz"),
        ]

    result = text
    for old, new in replacements:
        result = result.replace(old, new)
    return result


def apply_variant_to_list(items: List[str], lang: str, variant: str) -> List[str]:
    return [apply_variant(item, lang, variant) for item in items]


# =========================
# CATEGORIES
# =========================

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "salud_mental_autolesion": [
        "cutting", "autolesión", "autolesion", "autolesiones", "se corta", "suicidio",
        "matarme", "matarse", "no quiero vivir", "ahorcar", "ahorcamiento",
        "brote psicótico", "brote psicotico", "psicótico", "psicotico",
        "inestabilidad psiquiátrica", "inestabilidad psiquiatrica",
        "medicación", "medicacion"
    ],
    "sobreadaptacion_ocultamiento_emocional": [
        "no quiere preocupar", "no quiere preocuparme", "no quiere preocuparnos",
        "para no preocupar", "oculta para no preocupar", "se lo guarda",
        "se guarda todo", "dice que está bien", "dice que esta bien",
        "siempre está bien", "siempre esta bien", "hace todo bien",
        "aparenta estar bien", "aparenta que está bien", "aparenta que esta bien",
        "sobreadaptación", "sobreadaptacion", "no quiere molestar",
        "no quiere ser una carga", "no quiere decepcionar",
        "minimiza lo que siente", "finge estar bien", "disimula",
        "no muestra lo que le pasa", "se hace el fuerte", "se hace la fuerte",
        "oculta lo que siente"
    ],
    "aislamiento_silencio": [
        "no me habla", "no nos habla", "silencio", "distante", "aislado", "aislada",
        "encerrado", "encerrada", "no quiere hablar", "se cierra", "apatía", "apatia",
        "nada le importa", "desconectado", "desconectada"
    ],
    "agresividad_autocontrol": [
        "agresivo", "agresiva", "grita", "insulta", "explota", "ira", "enojo",
        "autocontrol", "autorregulación", "autorregulacion", "desborde", "violento",
        "violenta", "golpea", "rompe cosas", "reacciones abruptas"
    ],
    "consumo_adicciones": [
        "droga", "drogas", "alcohol", "porro", "marihuana", "cocaína", "cocaina",
        "vape", "vapear", "tabaquismo", "fumando", "fuma", "anabólicos", "anabolicos",
        "suplementos", "gimnasio", "esteroides", "abuso de drogas"
    ],
    "alimentacion_cuerpo_imagen": [
        "anorexia", "bulimia", "atracón", "atracon", "cuerpo", "peso", "gordo", "gorda",
        "flaco", "flaca", "ropa", "zapatillas", "celular nuevo", "último teléfono", "ultimo telefono",
        "fomo", "nomofobia", "imagen", "comparación", "comparacion", "aspecto físico", "aspecto fisico"
    ],
    "bullying_discriminacion_odio": [
        "bullying", "ciberbullying", "burla", "burlas", "acoso", "humillación", "humillacion",
        "odio", "insultos masivos", "rechazo a la diversidad", "diversidad sexual", "racismo",
        "xenofobia", "inmigrantes", "otras creencias", "otras religiones", "politicas", "países vecinos", "paises vecinos"
    ],
    "digital_online_riesgo": [
        "gaming", "apuestas online", "apuestas", "casino online", "estafa", "estafar",
        "ventas digitales ilegales", "online", "chat", "discord", "onlyfans", "pornhub",
        "sugar daddy", "dama de compañía", "dama de compañia", "sexting", "grooming",
        "amigos de juegos online", "peleas online"
    ],
    "vinculos_afectivos_sexualidad": [
        "noviazgo tóxico", "noviazgo toxico", "novio", "novia", "celos", "controla",
        "embarazo", "aborto", "relaciones amorosas entre menores y adultos", "adulto", "menor",
        "sexualidad", "rechazo a las diversidades sexuales", "dependencia emocional"
    ],
    "familia_autoridad_mentira": [
        "incomunicación intrafamiliar", "incomunicacion intrafamiliar", "violencia intrafamiliar",
        "falta de respeto", "adultos", "referentes escolares", "referentes familiares", "mentira",
        "mentiras compulsivas", "chantaje", "adoctrinamiento", "autoridad policial", "abandono",
        "fingir", "exagerar"
    ],
    "delito_vandalismo_crueldad": [
        "robo", "ladrón", "ladron", "vandalismo", "maltrato animal", "amenaza", "denuncia penal",
        "trata de blancas", "delito", "incitación al odio", "incitacion al odio", "ventas ilegales"
    ],
    "escuela_proyecto_vida": [
        "no quiere estudiar", "escuela", "colegio", "docente", "maestra", "director", "directora",
        "no le importa la escuela", "abandono escolar", "apatía escolar", "apatia escolar", "desmotivación", "desmotivacion"
    ],
    "duelo_abandono_vacio": [
        "abandono", "pérdida", "perdida", "duelo", "seres queridos", "vacío", "vacio",
        "sin sentido", "espiritual", "crisis de fe", "desesperanza"
    ],
}


CRITICAL_KEYWORDS = [
    "suicidio", "matarme", "matarse", "no quiero vivir", "autolesión", "autolesion",
    "se corta", "cutting", "abuso sexual", "violación", "violacion", "grooming",
    "trata de blancas", "adulto y menor", "relación con un adulto", "relacion con un adulto",
    "brote psicótico", "brote psicotico", "arma", "amenaza de muerte", "ahorcar"
]

HIGH_RISK_KEYWORDS = [
    "violencia", "golpea", "agresivo", "agresiva", "droga", "drogas", "anorexia",
    "bulimia", "apuestas online", "estafa", "onlyfans", "pornhub", "sugar daddy",
    "maltrato animal", "vandalismo", "denuncia penal", "abandono de medicación", "abandono de medicacion"
]


CATEGORY_RESPONSES = {
    "sobreadaptacion_ocultamiento_emocional": {
        "es": {
            "que_podria_estar_pasando": (
                "Podría estar intentando sostener una imagen de que todo está bien cuando en realidad siente angustia, miedo o agotamiento. "
                "A veces ocultar o minimizar lo que pasa no es una forma de manipular, sino de no preocupar, no decepcionar o no mostrarse vulnerable."
            ),
            "frases": [
                "No necesito que estés siempre bien; me importa que puedas ser sincero/a con lo que te pasa.",
                "Si estás tratando de cuidarnos ocultando algo, igual quiero que sepas que podemos sostenerlo juntos.",
                "No tienes que resolver solo/a lo que te angustia."
            ],
            "evitar": [
                "Entonces me mentiste todo este tiempo.",
                "Si no cuentas todo, no puedo confiar en ti.",
                "Deja de actuar como si no pasara nada."
            ],
            "tono": "Muy cuidadoso, receptivo y sin acusación.",
            "signos": [
                "Aparente fortaleza o perfección con mucho cansancio interno.",
                "Minimización constante del malestar.",
                "Dificultad para pedir ayuda o mostrarse vulnerable."
            ],
            "cuando": (
                "Actúa si el ocultamiento sostiene un sufrimiento importante, aislamiento, autolesiones o una caída marcada del bienestar."
            ),
            "ahora": "Abre una puerta de sinceridad sin convertir la conversación en un interrogatorio.",
            "observar": [
                "Si siente que tiene que estar siempre bien.",
                "Qué cosas evita contar por miedo a preocupar.",
                "Si hay agotamiento, angustia o tristeza detrás del funcionamiento aparente."
            ],
            "seguir": (
                "Transmití que decir la verdad o mostrarse mal no lo/la convierte en una carga. "
                "La meta no es desenmascarar, sino ofrecer un espacio donde no necesite actuar fortaleza todo el tiempo."
            ),
            "preguntas": [
                "¿Sientes que tienes que mostrar que todo está bien aunque no sea así?",
                "¿Hay algo que te estés guardando para no preocupar a los demás?",
                "¿Qué te daría más seguridad para poder decir cómo estás de verdad?"
            ],
            "actividades": [
                "Conversaciones breves sin presión ni tono policial.",
                "Momentos de presencia tranquila sin exigir explicaciones inmediatas.",
                "Validar explícitamente que no necesita estar siempre fuerte o bien."
            ],
        }
    },

    "familia_autoridad_mentira": {
        "es": {
            "que_podria_estar_pasando": (
                "Puede haber una dificultad para decir con claridad lo que le pasa, y eso puede expresarse como ocultamiento, distancia o versiones parciales de lo que siente. "
                "No siempre se trata de mala intención: a veces aparece por miedo, vergüenza, cansancio o por no querer preocupar."
            ),
            "frases": [
                "Quiero entender mejor qué te está costando decir o mostrar.",
                "Necesitamos reconstruir confianza sin convertir esto en una pelea permanente.",
                "No se trata solo de lo que pasó hoy, sino de cómo nos estamos pudiendo hablar."
            ],
            "evitar": [
                "Con vosotros no se puede nunca.",
                "Entonces todo lo que dices es mentira.",
                "Yo mando y no se discute."
            ],
            "tono": "Firme, claro y sin humillar.",
            "signos": [
                "Ocultamiento sostenido o versiones cambiantes.",
                "Escalada crónica con adultos de referencia.",
                "Violencia intrafamiliar o chantaje emocional."
            ],
            "cuando": "Actúa si ya no hay trato posible, si hay violencia o si la convivencia quedó dañada de forma sostenida.",
            "ahora": "Baja la intensidad, ordena límites básicos y evita discutir todo al mismo tiempo.",
            "observar": [
                "Qué temas disparan más pelea o evitación.",
                "Si el ocultamiento nace del miedo o del conflicto.",
                "Cómo viene funcionando la confianza familiar."
            ],
            "seguir": "Trabaja acuerdos claros y busca ayuda si la convivencia está muy dañada.",
            "preguntas": [
                "¿En qué momento sientes que dejamos de poder hablar bien?",
                "¿Qué te cuesta más mostrar o decir?",
                "¿Qué necesitarías para sentirte tratado/a con más justicia sin romper los límites?"
            ],
            "actividades": [
                "Pactar una conversación breve con reglas claras.",
                "Suspender escenas de gritos como forma habitual de vínculo.",
                "Consultar si la dinámica familiar está muy dañada."
            ],
        }
    },

    "aislamiento_silencio": {
        "es": {
            "que_podria_estar_pasando": (
                "El silencio o el encierro suelen ser formas de protegerse cuando algo duele, abruma o avergüenza. "
                "No necesariamente significan rechazo hacia ti: muchas veces muestran que no encuentra cómo decir lo que le pasa."
            ),
            "frases": [
                "Te noto más cerrado/a y me importa saber cómo estás.",
                "No quiero invadirte, pero sí hacerte saber que estoy disponible.",
                "Podemos hablar poco a poco, sin presión."
            ],
            "evitar": [
                "Ya no eres el de antes.",
                "Si no hablas, no te ayudo.",
                "Dramatizas por nada."
            ],
            "tono": "Sereno, disponible y sin perseguirlo/a con preguntas.",
            "signos": [
                "Aislamiento cada vez mayor.",
                "Abandono de rutinas, estudio o amistades.",
                "Cambios en sueño, apetito o higiene."
            ],
            "cuando": "Actúa si el aislamiento se prolonga, empeora o se combina con tristeza intensa o desesperanza.",
            "ahora": "Elige un momento breve y tranquilo para acercarte sin invadir.",
            "observar": [
                "Qué momentos lo/la cierran más.",
                "Si hay algo que todavía disfruta mínimamente.",
                "Cómo reacciona cuando se siente escuchado/a."
            ],
            "seguir": "No busques resolver todo en una sola charla: sostén presencia, rutina y pequeñas oportunidades de encuentro.",
            "preguntas": [
                "¿Qué es lo que más te está costando últimamente?",
                "¿Qué necesitas de mí para sentirte un poco más acompañado/a?",
                "¿Hay algo que te gustaría que yo entendiera mejor?"
            ],
            "actividades": [
                "Salir a caminar unos minutos.",
                "Compartir una comida sin hablar del problema al principio.",
                "Hacer una tarea simple juntos."
            ],
        }
    },

    "agresividad_autocontrol": {
        "es": {
            "que_podria_estar_pasando": (
                "La agresividad o el desborde suelen esconder frustración, impotencia o sensación de amenaza. "
                "No justifica el maltrato, pero ayuda a entender que muchas veces el problema de fondo es la falta de autorregulación."
            ),
            "frases": [
                "No voy a seguir esta charla si nos lastimamos, pero sí quiero retomarla mejor.",
                "Necesitamos encontrar una forma más segura de hablar.",
                "Veo que estás muy desbordado/a; cuando baje la intensidad, te escucharé."
            ],
            "evitar": [
                "Eres imposible.",
                "Siempre haces lo mismo.",
                "Si sigues así, te arruino."
            ],
            "tono": "Firme, breve y sin entrar en escalada.",
            "signos": [
                "Golpes, amenazas o daño a objetos.",
                "Reacciones desproporcionadas frecuentes.",
                "Incapacidad de frenar aun cuando ve que lastima."
            ],
            "cuando": "Actúa rápido si hay riesgo físico, amenazas o miedo en casa o en la escuela.",
            "ahora": "Corta la escalada, protege el contexto y retoma cuando todos estén más regulados.",
            "observar": [
                "Qué situaciones detonan el enojo.",
                "Cuánto tarda en regularse.",
                "Si hay consumo, falta de sueño o abandono de tratamiento."
            ],
            "seguir": "Pon límites claros a la violencia y busca ayuda si el patrón se repite.",
            "preguntas": [
                "¿Qué te hace explotar más rápido?",
                "¿Qué podríamos hacer antes de llegar a ese punto?",
                "¿Cómo puedo marcar un límite sin que sientas que te ataco?"
            ],
            "actividades": [
                "Acordar una pausa de 10 minutos antes de seguir hablando.",
                "Caminar o descargar energía sin violencia.",
                "Escribir antes de hablar."
            ],
        }
    },
}


# =========================
# HELPERS
# =========================

def normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def detect_category(text: str) -> str:
    t = normalize_text(text)

    priority_order = [
        "salud_mental_autolesion",
        "sobreadaptacion_ocultamiento_emocional",
        "consumo_adicciones",
        "digital_online_riesgo",
        "vinculos_afectivos_sexualidad",
        "bullying_discriminacion_odio",
        "agresividad_autocontrol",
        "alimentacion_cuerpo_imagen",
        "aislamiento_silencio",
        "delito_vandalismo_crueldad",
        "escuela_proyecto_vida",
        "duelo_abandono_vacio",
        "familia_autoridad_mentira",
    ]

    for category in priority_order:
        keywords = CATEGORY_KEYWORDS.get(category, [])
        for kw in keywords:
            if kw in t:
                return category

    return "familia_autoridad_mentira"


def detect_risk(text: str, category: str) -> Tuple[str, bool]:
    t = normalize_text(text)

    if any(k in t for k in CRITICAL_KEYWORDS):
        return "alta", True

    if any(k in t for k in HIGH_RISK_KEYWORDS):
        return "media", True if category in [
            "salud_mental_autolesion",
            "digital_online_riesgo",
            "delito_vandalismo_crueldad",
            "vinculos_afectivos_sexualidad"
        ] else False

    if len(t) > 200:
        return "media", False

    if category in ["salud_mental_autolesion", "consumo_adicciones", "digital_online_riesgo"]:
        return "media", False

    return "baja", False


def fallback_response():
    return {
        "que_podria_estar_pasando": (
            "Esto puede reflejar malestar emocional, confusión o dificultad para poner en palabras lo que ocurre."
        ),
        "frases": [
            "Me importa lo que te está pasando.",
            "Quiero entender mejor antes de suponer.",
            "Podemos hablar poco a poco."
        ],
        "evitar": [
            "Estás exagerando.",
            "Eres imposible.",
            "No es para tanto."
        ],
        "tono": "Calmo, respetuoso y claro.",
        "signos": [
            "Cambios de conducta sostenidos.",
            "Aislamiento, agresividad o desesperanza.",
            "Escalada del conflicto o del riesgo."
        ],
        "cuando": "Actúa si empeora, se repite o compromete la seguridad.",
        "ahora": "Elige un momento tranquilo y prioriza el vínculo por encima del control.",
        "observar": [
            "Qué dispara el problema.",
            "Qué lo mejora o empeora.",
            "Si se está deteriorando el funcionamiento general."
        ],
        "seguir": "No intentes resolver todo de una vez: sostén presencia y coherencia.",
        "preguntas": [
            "¿Qué es lo que más te está costando últimamente?",
            "¿Qué necesitas de mí ahora?",
            "¿Qué haría que esta conversación se sintiera más segura?"
        ],
        "actividades": [
            "Salir a caminar un poco.",
            "Compartir una actividad simple.",
            "Hablar en momentos breves y tranquilos."
        ],
    }


def get_category_content(category: str) -> dict:
    if category in CATEGORY_RESPONSES and "es" in CATEGORY_RESPONSES[category]:
        return CATEGORY_RESPONSES[category]["es"]
    return fallback_response()


def localize_content_variant(content: dict, lang: str, variant: str) -> dict:
    localized = {
        "que_podria_estar_pasando": apply_variant(content["que_podria_estar_pasando"], lang, variant),
        "frases": apply_variant_to_list(content["frases"], lang, variant),
        "evitar": apply_variant_to_list(content["evitar"], lang, variant),
        "tono": apply_variant(content["tono"], lang, variant),
        "signos": apply_variant_to_list(content["signos"], lang, variant),
        "cuando": apply_variant(content["cuando"], lang, variant),
        "ahora": apply_variant(content["ahora"], lang, variant),
        "observar": apply_variant_to_list(content["observar"], lang, variant),
        "seguir": apply_variant(content["seguir"], lang, variant),
        "preguntas": apply_variant_to_list(content["preguntas"], lang, variant),
        "actividades": apply_variant_to_list(content["actividades"], lang, variant),
    }
    return localized


def build_guidance(text: str, lang: str, variant: str) -> SituationResponse:
    category = detect_category(text)
    intensity, high_risk = detect_risk(text, category)
    content = get_category_content(category)
    content = localize_content_variant
