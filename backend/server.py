from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


app = FastAPI()
api_router = APIRouter(prefix="/api")


class SituationInput(BaseModel):
    text: str
    user_id: Optional[str] = None


class SituationSection(BaseModel):
    que_podria_estar_pasando: str
    como_hablar: dict
    senales_de_alerta: dict
    proximos_pasos: dict
    reconexion: dict


class SituationResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    intensidad_emocional: str
    riesgo_alto: bool
    mensaje_ayuda_profesional: Optional[str] = None
    secciones: SituationSection
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RewriteInput(BaseModel):
    original_text: str
    context: Optional[str] = None


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


def detect_intensity_and_risk(text: str):
    t = text.lower()

    high_risk_keywords = [
        "suicidio", "matarme", "matarse", "autolesión", "autolesion", "cortarse",
        "abuso", "violación", "violacion", "pedofilia", "golpe", "violencia",
        "sobredosis", "arma", "amenaza", "explotación sexual", "explotacion sexual"
    ]

    medium_keywords = [
        "droga", "drogas", "marihuana", "cocaína", "cocaina", "alcohol", "robo",
        "bullying", "ciberbullying", "sexting", "anorexia", "bulimia",
        "depresión", "depresion", "aislado", "aislada", "agresivo", "agresiva"
    ]

    if any(k in t for k in high_risk_keywords):
        return "alta", True

    if any(k in t for k in medium_keywords):
        return "media", False

    if len(t.strip()) > 140:
        return "media", False

    return "baja", False


def build_guidance(text: str):
    intensidad, riesgo_alto = detect_intensity_and_risk(text)

    mensaje_ayuda = (
        "La situación que describís merece apoyo profesional inmediato. "
        "Si hay riesgo actual o peligro, buscá ayuda urgente y acudí a un servicio de emergencia o a un profesional."
        if riesgo_alto else None
    )

    que_podria_estar_pasando = (
        "Tu hijo/a podría estar atravesando algo que no sabe cómo expresar con palabras. "
        "A veces la distancia, el enojo o el silencio son formas de mostrar malestar, confusión o necesidad de cuidado."
    )

    como_hablar = {
        "frases_sugeridas": [
            "Te noto distinto/a y me importa saber cómo estás.",
            "No quiero juzgarte; quiero entender mejor qué te está pasando.",
            "Podemos hablar de a poco, cuando te sientas listo/a."
        ],
        "que_evitar": [
            "No exageres ni minimices lo que siente.",
            "No empieces acusando o interrogando.",
            "No uses comparaciones ni amenazas para abrir la conversación."
        ],
        "tono_recomendado": "Calmo, empático, breve y disponible. Más escucha que discurso."
    }

    senales_de_alerta = {
        "signos": [
            "Aislamiento sostenido o cambios bruscos de conducta.",
            "Irritabilidad intensa, miedo, tristeza persistente o apatía.",
            "Señales físicas, consumo, amenazas, autolesiones o situaciones de violencia."
        ],
        "cuando_actuar": (
            "Buscá ayuda profesional si esto se intensifica, se sostiene en el tiempo "
            "o aparece riesgo para su integridad o la de otras personas."
        )
    }

    proximos_pasos = {
        "que_hacer_ahora": (
            "Elegí un momento tranquilo, hablá con pocas palabras y mostrale disponibilidad real."
        ),
        "que_observar": [
            "Cambios en el sueño, apetito o hábitos.",
            "Qué situaciones empeoran o alivian el malestar.",
            "Cómo reacciona cuando se siente escuchado/a sin presión."
        ],
        "como_seguir": (
            "No busques resolver todo en una sola charla. Lo importante es abrir una puerta "
            "y sostener la presencia con constancia."
        )
    }

    reconexion = {
        "preguntas": [
            "¿Qué te está costando más en este momento?",
            "¿Qué sentís que necesitarías de mí hoy?",
            "¿Hay algo que te gustaría que yo entendiera mejor?"
        ],
        "actividades": [
            "Salir a caminar sin forzar la conversación.",
            "Compartir una comida o una tarea simple juntos.",
            "Proponer un rato breve de conexión sin pantallas ni reproches."
        ]
    }

    return SituationResponse(
        intensidad_emocional=intensidad,
        riesgo_alto=riesgo_alto,
        mensaje_ayuda_profesional=mensaje_ayuda,
        secciones=SituationSection(
            que_podria_estar_pasando=que_podria_estar_pasando,
            como_hablar=como_hablar,
            senales_de_alerta=senales_de_alerta,
            proximos_pasos=proximos_pasos,
            reconexion=reconexion
        )
    )


def rewrite_versions(text: str):
    limpio = text.strip()

    return [
        f"Quiero hablar con vos de algo que me preocupa. No busco retarte, sino entender mejor lo que está pasando. {limpio}",
        f"Me gustaría decirte esto de una manera que nos ayude a hablar mejor: {limpio} Quiero escucharte y acompañarte."
    ]


@api_router.get("/")
async def root():
    return {"message": "PadresLab API funcionando 🚀"}


@api_router.get("/frequent-situations", response_model=List[FrequentSituation])
async def get_frequent_situations():
    return [
        FrequentSituation(id="1", titulo="Distancia o silencio", descripcion="Mi hijo/a está muy distante y no me habla", emoji="🤐"),
        FrequentSituation(id="2", titulo="Respuestas agresivas", descripcion="Me responde mal y de forma agresiva", emoji="😤"),
        FrequentSituation(id="3", titulo="Uso excesivo del celular", descripcion="Pasa todo el día con el celular", emoji="📱"),
        FrequentSituation(id="4", titulo="Sospecha de consumo", descripcion="Sospecho que está consumiendo sustancias", emoji="⚠️"),
        FrequentSituation(id="5", titulo="Tristeza o aislamiento", descripcion="Lo/la veo muy triste y aislado/a", emoji="😢"),
        FrequentSituation(id="6", titulo="Mentiras u ocultamiento", descripcion="Me miente o me oculta cosas", emoji="🤥"),
        FrequentSituation(id="7", titulo="Malas juntas", descripcion="Me preocupan sus amistades", emoji="👥"),
        FrequentSituation(id="8", titulo="Conversaciones sexuales / sexting", descripcion="Temas relacionados con sexualidad", emoji="💬"),
        FrequentSituation(id="9", titulo="Desinterés por el estudio", descripcion="No le importa la escuela", emoji="📚"),
        FrequentSituation(id="10", titulo="Pelea fuerte / cómo reparar", descripcion="Tuvimos una pelea y no sé cómo arreglarlo", emoji="💔"),
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
            descripcion="Considerá consultar con un psicólogo, trabajador social o terapeuta familiar"
        ),
    ]


@api_router.post("/analyze-situation", response_model=SituationResponse)
async def analyze_situation(input_data: SituationInput):
    return build_guidance(input_data.text)


@api_router.post("/rewrite-message", response_model=RewriteResponse)
async def rewrite_message(input_data: RewriteInput):
    return RewriteResponse(versiones=rewrite_versions(input_data.original_text))


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
