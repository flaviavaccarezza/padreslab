from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Tuple
import uuid
from datetime import datetime


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")


# =========================
# MODELOS
# =========================

class SituationInput(BaseModel):
    text: str
    user_id: Optional[str] = None
    lang: Optional[str] = "es"


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
# TEXTOS
# =========================

LANG_TEXT = {
    "es": {
        "root_message": "PadresLab API funcionando 🚀",
        "urgent_help": (
            "Lo que describís puede implicar una situación de riesgo serio. "
            "No lo abordes en soledad: buscá ayuda profesional o institucional de inmediato."
        ),
        "rewrite_1_prefix": "Quiero decirte esto de una manera más clara y respetuosa: ",
        "rewrite_2_prefix": "No busco pelearme con vos; necesito que podamos hablar mejor sobre esto: ",
    }
}


def get_lang(lang: Optional[str]) -> str:
    return "es"


# =========================
# DETECCIÓN SIMPLE
# =========================

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
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
        "vape", "vapear", "tabaquismo", "fumando", "fuma"
    ],
    "familia_autoridad_mentira": [
        "mentira", "mentiras compulsivas", "chantaje", "falta de respeto",
        "incomunicación intrafamiliar", "incomunicacion intrafamiliar", "violencia intrafamiliar"
    ]
}


CRITICAL_KEYWORDS = [
    "suicidio", "matarme", "matarse", "no quiero vivir", "autolesión", "autolesion",
    "se corta", "cutting", "abuso sexual", "violación", "violacion", "grooming",
    "brote psicótico", "brote psicotico", "arma", "amenaza de muerte"
]

HIGH_RISK_KEYWORDS = [
    "violencia", "golpea", "agresivo", "agresiva", "droga", "drogas", "anorexia",
    "bulimia", "apuestas online", "estafa", "onlyfans", "pornhub", "maltrato animal"
]


CATEGORY_RESPONSES = {
    "sobreadaptacion_ocultamiento_emocional": {
        "que_podria_estar_pasando": (
            "Podría estar intentando sostener una imagen de que todo está bien cuando en realidad siente angustia, miedo o agotamiento. "
            "A veces ocultar o minimizar lo que pasa no es una forma de manipular, sino de no preocupar, no decepcionar o no mostrarse vulnerable."
        ),
        "frases": [
            "No necesito que estés siempre bien; me importa que puedas ser sincero/a con lo que te pasa.",
            "Si estás tratando de cuidarnos ocultando algo, igual quiero que sepas que podemos sostenerlo juntos.",
            "No tenés que resolver solo/a lo que te angustia."
        ],
        "evitar": [
            "Entonces me mentiste todo este tiempo.",
            "Si no contás todo, no puedo confiar en vos.",
            "Dejá de actuar como si no pasara nada."
        ],
        "tono": "Muy cuidadoso, receptor y sin acusación.",
        "signos": [
            "Aparente fortaleza o perfección con mucho cansancio interno.",
            "Minimización constante del malestar.",
            "Dificultad para pedir ayuda o mostrarse vulnerable."
        ],
        "cuando": "Actuá si el ocultamiento sostiene un sufrimiento importante, aislamiento, autolesiones o una caída marcada del bienestar.",
        "ahora": "Abrí una puerta de sinceridad sin convertir la conversación en un interrogatorio.",
        "observar": [
            "Si siente que tiene que estar siempre bien.",
            "Qué cosas evita contar por miedo a preocupar.",
            "Si hay agotamiento, angustia o tristeza detrás del funcionamiento aparente."
        ],
        "seguir": "Transmití que mostrarse mal no lo/la convierte en una carga.",
        "preguntas": [
            "¿Sentís que tenés que mostrar que todo está bien aunque no sea así?",
            "¿Hay algo que te estés guardando para no preocupar a los demás?",
            "¿Qué te daría más seguridad para poder decir cómo estás de verdad?"
        ],
        "actividades": [
            "Conversaciones breves sin presión ni tono policial.",
            "Momentos de presencia tranquila sin exigir explicaciones inmediatas.",
            "Validar explícitamente que no necesita estar siempre fuerte o bien."
        ]
    },
    "aislamiento_silencio": {
        "que_podria_estar_pasando": (
            "El silencio o el encierro suelen ser formas de protegerse cuando algo duele, abruma o avergüenza. "
            "No necesariamente significan rechazo hacia vos."
        ),
        "frases": [
            "Te noto más cerrado/a y me importa saber cómo estás.",
            "No quiero invadirte, pero sí hacerte saber que estoy disponible.",
            "Podemos hablar de a poco, sin presión."
        ],
        "evitar": [
            "Si no hablás, no te ayudo.",
            "Dramatizás por nada.",
            "Ya no sos el de antes."
        ],
        "tono": "Sereno, disponible y sin perseguirlo/a con preguntas.",
        "signos": [
            "Aislamiento cada vez mayor.",
            "Abandono de rutinas, estudio o amistades.",
            "Cambios en sueño, apetito o higiene."
        ],
        "cuando": "Actuá si el aislamiento se prolonga, empeora o se combina con tristeza intensa o desesperanza.",
        "ahora": "Elegí un momento breve y tranquilo para acercarte sin invadir.",
        "observar": [
            "Qué momentos lo/la cierran más.",
            "Si hay algo que todavía disfruta mínimamente.",
            "Cómo reacciona cuando se siente escuchado/a."
        ],
        "seguir": "No busques resolver todo en una sola charla: sostené presencia y pequeñas oportunidades de encuentro.",
        "preguntas": [
            "¿Qué es lo que más te está costando últimamente?",
            "¿Qué necesitás de mí para sentirte un poco más acompañado/a?",
            "¿Hay algo que te gustaría que yo entendiera mejor?"
        ],
        "actividades": [
            "Salir a caminar unos minutos.",
            "Compartir una comida sin hablar del problema al principio.",
            "Hacer una tarea simple juntos."
        ]
    },
    "agresividad_autocontrol": {
        "que_podria_estar_pasando": (
            "La agresividad o el desborde suelen esconder frustración, impotencia o sensación de amenaza. "
            "Muchas veces el problema de fondo es la falta de autorregulación."
        ),
        "frases": [
            "No voy a seguir esta charla si nos lastimamos, pero sí quiero retomarla mejor.",
            "Necesitamos encontrar una forma más segura de hablar.",
            "Veo que estás muy desbordado/a; cuando baje la intensidad, te escucho."
        ],
        "evitar": [
            "Sos imposible.",
            "Siempre hacés lo mismo.",
            "Si seguís así, te arruino."
        ],
        "tono": "Firme, breve y sin entrar en escalada.",
        "signos": [
            "Golpes, amenazas o daño a objetos.",
            "Reacciones desproporcionadas frecuentes.",
            "Incapacidad de frenar aun cuando ve que lastima."
        ],
        "cuando": "Actuá rápido si hay riesgo físico, amenazas o miedo en casa o en la escuela.",
        "ahora": "Cortá la escalada y retomá cuando todos estén más regulados.",
        "observar": [
            "Qué situaciones detonan el enojo.",
            "Cuánto tarda en regularse.",
            "Si hay consumo o falta de sueño."
        ],
        "seguir": "Poné límites claros a la violencia y buscá ayuda si el patrón se repite.",
        "preguntas": [
            "¿Qué te hace explotar más rápido?",
            "¿Qué podríamos hacer antes de llegar a ese punto?",
            "¿Cómo puedo marcar un límite sin que sientas que te ataco?"
        ],
        "actividades": [
            "Acordar una pausa antes de seguir hablando.",
            "Caminar o descargar energía sin violencia.",
            "Escribir antes de hablar."
        ]
    },
    "consumo_adicciones": {
        "que_podria_estar_pasando": (
            "El consumo puede estar cumpliendo una función: pertenecer, calmar ansiedad, escapar de algo o probar límites."
        ),
        "frases": [
            "Prefiero hablar de esto con vos antes que suponer.",
            "Me preocupa lo que puede hacerte daño, no quiero atacarte.",
            "Necesitamos entender qué lugar ocupa esto en tu vida."
        ],
        "evitar": [
            "Sos un desastre.",
            "Sé todo lo que hacés.",
            "Te voy a vigilar todo el tiempo."
        ],
        "tono": "Serio, sin moralizar y sin negar la gravedad.",
        "signos": [
            "Cambios en grupos, hábitos, sueño o dinero.",
            "Mentiras frecuentes o deterioro funcional.",
            "Consumo cada vez más frecuente."
        ],
        "cuando": "Actuá con rapidez si hay riesgo físico o dependencia creciente.",
        "ahora": "Abrí el tema con claridad, sin humillación.",
        "observar": [
            "Frecuencia, contexto y función del consumo.",
            "Relación con pares y con la escuela.",
            "Impacto en conducta y salud."
        ],
        "seguir": "Poné límites claros y buscá ayuda si el problema no cede.",
        "preguntas": [
            "¿Qué te da eso que sentís que hoy te falta?",
            "¿Cuándo empezaste y con quién te pasa más?",
            "¿Qué parte de esto te preocupa a vos?"
        ],
        "actividades": [
            "Hablar en un momento de calma.",
            "Revisar con un profesional el nivel de riesgo.",
            "Acordar medidas concretas de cuidado."
        ]
    },
    "familia_autoridad_mentira": {
        "que_podria_estar_pasando": (
            "Puede haber una dificultad para decir con claridad lo que le pasa, y eso puede expresarse como ocultamiento, distancia o versiones parciales."
        ),
        "frases": [
            "Quiero entender mejor qué te está costando decir o mostrar.",
            "Necesitamos reconstruir confianza sin convertir esto en una pelea permanente.",
            "No se trata solo de lo que pasó hoy, sino de cómo nos estamos pudiendo hablar."
        ],
        "evitar": [
            "Con vos no se puede nunca.",
            "Entonces todo lo que decís es mentira.",
            "Yo mando y no se discute."
        ],
        "tono": "Firme, claro y sin humillar.",
        "signos": [
            "Ocultamiento sostenido o versiones cambiantes.",
            "Escalada crónica con adultos de referencia.",
            "Violencia intrafamiliar o chantaje emocional."
        ],
        "cuando": "Actuá si ya no hay trato posible o si hay violencia.",
        "ahora": "Bajá la intensidad y evitá discutir todo al mismo tiempo.",
        "observar": [
            "Qué temas disparan más pelea o evitación.",
            "Si el ocultamiento nace del miedo o del conflicto.",
            "Cómo viene funcionando la confianza familiar."
        ],
        "seguir": "Trabajá acuerdos claros y buscá ayuda si la convivencia está muy dañada.",
        "preguntas": [
            "¿En qué momento sentís que dejamos de poder hablar bien?",
            "¿Qué te cuesta más mostrar o decir?",
            "¿Qué necesitarías para sentirte tratado/a con más justicia?"
        ],
        "actividades": [
            "Pactar una conversación breve con reglas claras.",
            "Suspender escenas de gritos como forma habitual de vínculo.",
            "Consultar si la dinámica familiar está muy dañada."
        ]
    }
}


def normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def detect_category(text: str) -> str:
    t = normalize_text(text)

    priority_order = [
        "salud_mental_autolesion",
        "sobreadaptacion_ocultamiento_emocional",
        "consumo_adicciones",
        "agresividad_autocontrol",
        "aislamiento_silencio",
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
        return "media", True

    if len(t) > 200:
        return "media", False

    return "baja", False


def get_category_content(category: str) -> dict:
    return CATEGORY_RESPONSES.get(category, CATEGORY_RESPONSES["familia_autoridad_mentira"])


def build_guidance(text: str) -> SituationResponse:
    category = detect_category(text)
    intensity, high_risk = detect_risk(text, category)
    content = get_category_content(category)

    urgent_message = LANG_TEXT["es"]["urgent_help"] if high_risk else None

    return SituationResponse(
        categoria_detectada=category,
        intensidad_emocional=intensity,
        riesgo_alto=high_risk,
        mensaje_ayuda_profesional=urgent_message,
        secciones=SituationSection(
            que_podria_estar_pasando=content["que_podria_estar_pasando"],
            como_hablar={
                "frases_sugeridas": content["frases"],
                "que_evitar": content["evitar"],
                "tono_recomendado": content["tono"]
            },
            senales_de_alerta={
                "signos": content["signos"],
                "cuando_actuar": content["cuando"]
            },
            proximos_pasos={
                "que_hacer_ahora": content["ahora"],
                "que_observar": content["observar"],
                "como_seguir": content["seguir"]
            },
            reconexion={
                "preguntas": content["preguntas"],
                "actividades": content["actividades"]
            }
        )
    )


def rewrite_versions(original_text: str) -> List[str]:
    txt = original_text.strip()
    return [
        f"{LANG_TEXT['es']['rewrite_1_prefix']}{txt}. Quiero entender qué está pasando sin atacarte.",
        f"{LANG_TEXT['es']['rewrite_2_prefix']}{txt}. Me importás y quiero que podamos hablar con respeto."
    ]


@api_router.get("/")
def root():
    return {"message": LANG_TEXT["es"]["root_message"]}


@api_router.get("/frequent-situations", response_model=List[FrequentSituation])
def get_frequent_situations():
    return [
        FrequentSituation(id="1", titulo="Distancia o silencio", descripcion="Mi hijo/a está muy distante y no me habla", emoji="🤐"),
        FrequentSituation(id="2", titulo="Respuestas agresivas", descripcion="Me responde mal, se enoja o explota fácilmente", emoji="😤"),
        FrequentSituation(id="3", titulo="Uso excesivo del celular", descripcion="Pasa todo el día con el celular o aislado/a online", emoji="📱"),
        FrequentSituation(id="4", titulo="Sospecha de consumo", descripcion="Sospecho que está consumiendo sustancias o vapeando", emoji="⚠️"),
        FrequentSituation(id="5", titulo="Tristeza o aislamiento", descripcion="Lo/la veo apagado/a, triste o aislado/a", emoji="😢"),
        FrequentSituation(id="6", titulo="Mentiras u ocultamiento", descripcion="Miente, exagera o me oculta cosas", emoji="🤥"),
        FrequentSituation(id="7", titulo="Bullying o conflictos con pares", descripcion="Hay burlas, acoso, discriminación o peleas", emoji="👥"),
        FrequentSituation(id="8", titulo="Relaciones tóxicas / sexualidad", descripcion="Me preocupa una relación, presión sexual o sexting", emoji="💬"),
        FrequentSituation(id="9", titulo="Desinterés por el estudio", descripcion="No le importa la escuela o se desconectó", emoji="📚"),
        FrequentSituation(id="10", titulo="Crisis grave / cómo actuar", descripcion="Hay autolesiones, amenazas o riesgo serio", emoji="💔"),
    ]


@api_router.get("/help-resources", response_model=List[HelpResource])
def get_help_resources():
    return [
        HelpResource(
            tipo="emergencia",
            nombre="Emergencias",
            telefono="911",
            descripcion="Para situaciones de peligro inmediato"
        ),
        HelpResource(
            tipo="violencia",
            nombre="Línea 144 - Violencia de Género",
            telefono="144",
            descripcion="Atención telefónica para víctimas de violencia de género"
        ),
        HelpResource(
            tipo="adicciones",
            nombre="SEDRONAR - Orientación en Adicciones",
            telefono="141",
            descripcion="Orientación sobre consumo problemático de sustancias"
        ),
        HelpResource(
            tipo="salud_mental",
            nombre="Centro de Atención al Suicida",
            telefono="135",
            descripcion="Atención para crisis y prevención del suicidio (CABA)"
        ),
        HelpResource(
            tipo="general",
            nombre="Consulta con profesional",
            descripcion="Considerá consultar con un psicólogo, psiquiatra, trabajador social o terapeuta familiar"
        ),
    ]


@api_router.post("/analyze-situation", response_model=SituationResponse)
def analyze_situation(input_data: SituationInput):
    return build_guidance(input_data.text)


@api_router.post("/rewrite-message", response_model=RewriteResponse)
def rewrite_message(input_data: RewriteInput):
    return RewriteResponse(versiones=rewrite_versions(input_data.original_text))


app.include_router(api_router)
