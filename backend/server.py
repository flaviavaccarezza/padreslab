from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Tuple
import uuid
from datetime import datetime


app = FastAPI()
api_router = APIRouter(prefix="/api")


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


LANG_TEXT = {
    "es": {
        "root_message": "PadresLab API funcionando 🚀",
        "urgent_help": (
            "Lo que describís puede implicar una situación de riesgo serio. "
            "No lo abordes en soledad: buscá ayuda profesional o institucional de inmediato."
        ),
        "rewrite_1_prefix": "Quiero decirte esto de una manera más clara y respetuosa: ",
        "rewrite_2_prefix": "No busco pelearme con vos; necesito que podamos hablar mejor sobre esto: ",
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
            "cuando": (
                "Actuá si el ocultamiento sostiene un sufrimiento importante, aislamiento, autolesiones o una caída marcada del bienestar."
            ),
            "ahora": "Abrí una puerta de sinceridad sin convertir la conversación en un interrogatorio.",
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
                "¿Sentís que tenés que mostrar que todo está bien aunque no sea así?",
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
            "cuando": "Actuá si ya no hay trato posible, si hay violencia o si la convivencia quedó dañada de forma sostenida.",
            "ahora": "Bajá la intensidad, ordená límites básicos y evitá discutir todo al mismo tiempo.",
            "observar": [
                "Qué temas disparan más pelea o evitación.",
                "Si el ocultamiento nace del miedo o del conflicto.",
                "Cómo viene funcionando la confianza familiar."
            ],
            "seguir": "Trabajá acuerdos claros y buscá ayuda si la convivencia está muy dañada.",
            "preguntas": [
                "¿En qué momento sentís que dejamos de poder hablar bien?",
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
                "No necesariamente significan rechazo hacia vos: muchas veces muestran que no encuentra cómo decir lo que le pasa."
            ),
            "frases": [
                "Te noto más cerrado/a y me importa saber cómo estás.",
                "No quiero invadirte, pero sí hacerte saber que estoy disponible.",
                "Podemos hablar de a poco, sin presión."
            ],
            "evitar": [
                "No me hables así / ya no sos el de antes.",
                "Si no hablás, no te ayudo.",
                "Dramatizás por nada."
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
            "seguir": "No busques resolver todo en una sola charla: sostené presencia, rutina y pequeñas oportunidades de encuentro.",
            "preguntas": [
                "¿Qué es lo que más te está costando últimamente?",
                "¿Qué necesitás de mí para sentirte un poco más acompañado/a?",
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
            "ahora": "Cortá la escalada, protegé el contexto y retomá cuando todos estén más regulados.",
            "observar": [
                "Qué situaciones detonan el enojo.",
                "Cuánto tarda en regularse.",
                "Si hay consumo, falta de sueño o abandono de tratamiento."
            ],
            "seguir": "Poné límites claros a la violencia y buscá ayuda si el patrón se repite.",
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
            "Podemos hablar de a poco."
        ],
        "evitar": [
            "Estás exagerando.",
            "Sos imposible.",
            "No es para tanto."
        ],
        "tono": "Calmo, respetuoso y claro.",
        "signos": [
            "Cambios de conducta sostenidos.",
            "Aislamiento, agresividad o desesperanza.",
            "Escalada del conflicto o del riesgo."
        ],
        "cuando": "Actuá si empeora, se repite o compromete la seguridad.",
        "ahora": "Elegí un momento tranquilo y priorizá el vínculo por sobre el control.",
        "observar": [
            "Qué dispara el problema.",
            "Qué lo mejora o empeora.",
            "Si está deteriorándose el funcionamiento general."
        ],
        "seguir": "No intentes resolver todo de una vez: sostené presencia y coherencia.",
        "preguntas": [
            "¿Qué es lo que más te está costando últimamente?",
            "¿Qué necesitás de mí ahora?",
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


def build_guidance(text: str, lang: str) -> SituationResponse:
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


def rewrite_versions(original_text: str, lang: str) -> List[str]:
    txt = original_text.strip()
    return [
        f"{LANG_TEXT['es']['rewrite_1_prefix']}{txt}. Quiero entender qué está pasando sin atacarte.",
        f"{LANG_TEXT['es']['rewrite_2_prefix']}{txt}. Me importás y quiero que podamos hablar con respeto."
    ]


@api_router.get("/")
async def root():
    return {"message": LANG_TEXT["es"]["root_message"]}


@api_router.get("/frequent-situations", response_model=List[FrequentSituation])
async def get_frequent_situations():
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
async def get_help_resources():
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
async def analyze_situation(input_data: SituationInput):
    lang = get_lang(input_data.lang)
    return build_guidance(input_data.text, lang)


@api_router.post("/rewrite-message", response_model=RewriteResponse)
async def rewrite_message(input_data: RewriteInput):
    lang = get_lang(input_data.lang)
    return RewriteResponse(versiones=rewrite_versions(input_data.original_text, lang))


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
