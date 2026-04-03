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
    lang: Optional[str] = "es"   # es | en | it


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
# LANGUAGE LABELS
# =========================

LANG_TEXT = {
    "es": {
        "root_message": "PadresLab API funcionando 🚀",
        "urgent_help": (
            "Lo que describís puede implicar una situación de riesgo serio. "
            "No lo abordes en soledad: buscá ayuda profesional o institucional de inmediato."
        ),
        "talk_title": "Cómo hablar",
        "warning_signs": "Señales de alerta",
        "next_steps": "Próximos pasos",
        "reconnection": "Reconexión",
        "default_tone": "Calmo, firme, sin humillar y con escucha real.",
        "professional_note": (
            "Si esto se agrava, se repite o compromete la seguridad, buscá apoyo profesional."
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
        "talk_title": "How to talk",
        "warning_signs": "Warning signs",
        "next_steps": "Next steps",
        "reconnection": "Reconnection",
        "default_tone": "Calm, firm, without humiliation, and with real listening.",
        "professional_note": (
            "If this worsens, repeats, or compromises safety, seek professional support."
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
        "talk_title": "Come parlarne",
        "warning_signs": "Segnali di allarme",
        "next_steps": "Prossimi passi",
        "reconnection": "Riconnessione",
        "default_tone": "Calmo, fermo, senza umiliare e con ascolto reale.",
        "professional_note": (
            "Se la situazione peggiora, si ripete o compromette la sicurezza, cerca supporto professionale."
        ),
        "rewrite_1_prefix": "Vorrei dire questo in modo più chiaro e rispettoso: ",
        "rewrite_2_prefix": "Non voglio litigare con te; ho bisogno che possiamo parlare meglio di questo: ",
    },
}


def get_lang(lang: Optional[str]) -> str:
    if lang in ("es", "en", "it"):
        return lang
    return "es"


# =========================
# CATEGORY KEYWORDS
# =========================

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
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
    "salud_mental_autolesion": [
        "cutting", "autolesión", "autolesion", "autolesiones", "se corta", "suicidio",
        "matarme", "matarse", "no quiero vivir", "ahorcar", "ahorcamiento", "fantasias sexuales",
        "brote psicótico", "brote psicotico", "psicótico", "psicotico", "psicopatía", "psicopatia",
        "obsesiones", "inestabilidad psiquiátrica", "inestabilidad psiquiatrica", "medicación", "medicacion"
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
        "sobreadaptación", "sobreadaptacion", "siempre está bien", "siempre esta bien", "fingir", "exagerar"
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


# =========================
# CATEGORY RESPONSES
# =========================

CATEGORY_RESPONSES = {
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
        },
        "en": {
            "que_podria_estar_pasando": (
                "Silence or withdrawal is often a way of protecting oneself when something feels painful, overwhelming, or shameful. "
                "It does not always mean rejection: often it means they do not know how to say what is happening."
            ),
            "frases": [
                "I notice you seem more closed off, and I care about how you are doing.",
                "I do not want to invade your space, but I want you to know I am here.",
                "We can talk little by little, without pressure."
            ],
            "evitar": [
                "You are not the same anymore.",
                "If you do not talk, I will not help.",
                "You are overreacting."
            ],
            "tono": "Calm, available, and not pushy.",
            "signos": [
                "Increasing isolation.",
                "Dropping routines, school, or friendships.",
                "Changes in sleep, appetite, or hygiene."
            ],
            "cuando": "Act if isolation lasts, worsens, or combines with intense sadness or hopelessness.",
            "ahora": "Choose a short, calm moment to approach them without invading.",
            "observar": [
                "What situations shut them down more.",
                "Whether there is still something they enjoy a little.",
                "How they respond when they feel listened to."
            ],
            "seguir": "Do not try to solve everything in one talk: offer presence, routine, and small chances for connection.",
            "preguntas": [
                "What has been hardest for you lately?",
                "What do you need from me to feel a little more supported?",
                "Is there something you wish I understood better?"
            ],
            "actividades": [
                "Take a short walk together.",
                "Share a meal without starting with the problem.",
                "Do a simple task together."
            ],
        },
        "it": {
            "que_podria_estar_pasando": (
                "Il silenzio o il ritiro spesso sono un modo per proteggersi quando qualcosa fa male, pesa o genera vergogna. "
                "Non significa sempre rifiuto verso di te: spesso indica che non sa come dire ciò che prova."
            ),
            "frases": [
                "Ti vedo più chiuso/a e mi importa sapere come stai.",
                "Non voglio invaderti, ma farti sapere che ci sono.",
                "Possiamo parlarne poco alla volta, senza pressione."
            ],
            "evitar": [
                "Non sei più quello/a di prima.",
                "Se non parli, non ti aiuto.",
                "Stai esagerando."
            ],
            "tono": "Calmo, disponibile e senza inseguirlo/a con domande.",
            "signos": [
                "Isolamento crescente.",
                "Abbandono di routine, scuola o amicizie.",
                "Cambiamenti nel sonno, appetito o igiene."
            ],
            "cuando": "Intervieni se l'isolamento dura, peggiora o si unisce a tristezza intensa o disperazione.",
            "ahora": "Scegli un momento breve e tranquillo per avvicinarti senza invadere.",
            "observar": [
                "Quali momenti lo/la chiudono di più.",
                "Se c'è ancora qualcosa che gli/le piace un po'.",
                "Come reagisce quando si sente ascoltato/a."
            ],
            "seguir": "Non cercare di risolvere tutto in una sola conversazione: offri presenza, routine e piccole occasioni di incontro.",
            "preguntas": [
                "Che cosa ti sta pesando di più ultimamente?",
                "Di cosa avresti bisogno da me per sentirti un po' più accompagnato/a?",
                "C'è qualcosa che vorresti che io capissi meglio?"
            ],
            "actividades": [
                "Fare una breve passeggiata insieme.",
                "Condividere un pasto senza iniziare dal problema.",
                "Fare una piccola attività insieme."
            ],
        },
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

    "salud_mental_autolesion": {
        "es": {
            "que_podria_estar_pasando": (
                "Lo que describís puede estar vinculado a un sufrimiento emocional o psiquiátrico que excede una simple pelea o etapa. "
                "Si hay autolesión, verbalizaciones suicidas, brotes o abandono de medicación, la prioridad es la seguridad y la intervención profesional."
            ),
            "frases": [
                "No quiero minimizar esto: me importa tu seguridad y quiero acompañarte.",
                "Necesitamos buscar ayuda ahora, no para castigarte sino para cuidarte.",
                "No estás solo/a con esto."
            ],
            "evitar": [
                "Lo hacés para llamar la atención.",
                "Ya se te va a pasar.",
                "Si hacés eso, sos egoísta."
            ],
            "tono": "Contenedor, serio y orientado a la protección.",
            "signos": [
                "Autolesiones, ideación suicida o verbalizaciones de muerte.",
                "Desorganización marcada, brotes o desconexión con la realidad.",
                "Abandono de medicación con empeoramiento conductual."
            ],
            "cuando": "Actuá de inmediato si hay riesgo de autoagresión, suicidio, brote o pérdida de contacto con la realidad.",
            "ahora": "No lo dejes solo/a si hay riesgo actual. Contactá ayuda profesional o servicios de emergencia si hace falta.",
            "observar": [
                "Cambios abruptos en conducta, sueño o contacto con la realidad.",
                "Mensajes de despedida o desesperanza extrema.",
                "Presencia de objetos o medios para dañarse."
            ],
            "seguir": "La prioridad no es convencer sino proteger, contener y derivar.",
            "preguntas": [
                "¿Te sentís en peligro o con ganas de lastimarte ahora?",
                "¿Qué te ayudaría a estar un poco más seguro/a en este momento?",
                "¿A quién aceptás que llamemos o avisemos ahora?"
            ],
            "actividades": [
                "Permanecer acompañado/a.",
                "Retirar objetos peligrosos del entorno inmediato.",
                "Ir a una guardia o contactar a un profesional."
            ],
        }
    },

    "consumo_adicciones": {
        "es": {
            "que_podria_estar_pasando": (
                "El consumo puede estar cumpliendo una función: pertenecer, calmar ansiedad, escapar de algo o probar límites. "
                "No conviene reducirlo solo a desobediencia: hay que mirar qué necesidad está intentando resolver."
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
                "Consumo cada vez más frecuente o mezcla de sustancias."
            ],
            "cuando": "Actuá con rapidez si hay riesgo físico, dependencia creciente o conductas ilegales asociadas.",
            "ahora": "Abrí el tema con claridad, sin escena ni humillación, y evaluá apoyo especializado si se confirma.",
            "observar": [
                "Frecuencia, contexto y función del consumo.",
                "Relación con pares y con la escuela.",
                "Impacto en conducta, salud y límites."
            ],
            "seguir": "Poné límites claros y buscá ayuda si el problema no cede o empeora.",
            "preguntas": [
                "¿Qué te da eso que sentís que hoy te falta?",
                "¿Cuándo empezaste y con quién te pasa más?",
                "¿Qué parte de esto te preocupa a vos, si es que te preocupa?"
            ],
            "actividades": [
                "Hablar en un momento de calma, no en medio del conflicto.",
                "Revisar con un profesional el nivel de riesgo.",
                "Acordar medidas concretas de cuidado y seguimiento."
            ],
        }
    },

    "alimentacion_cuerpo_imagen": {
        "es": {
            "que_podria_estar_pasando": (
                "La preocupación por el cuerpo, el consumo o la apariencia puede estar ligada a vergüenza, comparación social o necesidad de pertenecer. "
                "Cuando se vuelve obsesiva, deja de ser un gusto y pasa a organizar el malestar."
            ),
            "frases": [
                "No quiero reducirte a tu cuerpo ni a tu imagen; me importa cómo te estás sintiendo.",
                "Sé que esto puede ser muy sensible y quiero hablarlo con cuidado.",
                "No necesito que estés perfecto/a; necesito que estés bien."
            ],
            "evitar": [
                "Estás exagerando con tu cuerpo.",
                "Con lo bien que te ves, no entiendo el problema.",
                "Eso es una tontería."
            ],
            "tono": "Delicado, no invasivo y sin comentar el cuerpo innecesariamente.",
            "signos": [
                "Obsesión con peso, comida, ropa, marcas o comparación.",
                "Restricción, atracones, purgas o ejercicio compulsivo.",
                "Vergüenza intensa por no tener el mismo nivel económico del entorno."
            ],
            "cuando": "Actuá si hay conductas alimentarias peligrosas, consumo de anabólicos o caída fuerte de autoestima.",
            "ahora": "Corré el foco del cuerpo y del objeto de consumo; priorizá el sufrimiento que hay debajo.",
            "observar": [
                "Cambios en alimentación o ejercicio.",
                "Comparación constante con pares o redes.",
                "Desgaste emocional por imagen o estatus."
            ],
            "seguir": "Si el malestar se rigidiza, buscá evaluación especializada.",
            "preguntas": [
                "¿Qué sentís que pasaría si no tuvieras eso o no te vieras así?",
                "¿En qué momentos te comparás más?",
                "¿Qué te haría sentir más seguro/a sin depender tanto de eso?"
            ],
            "actividades": [
                "Reducir conversaciones centradas en imagen.",
                "Buscar espacios de pertenencia no basados en consumo.",
                "Revisar hábitos con un profesional si hay riesgo."
            ],
        }
    },

    "bullying_discriminacion_odio": {
        "es": {
            "que_podria_estar_pasando": (
                "Puede haber una dinámica de crueldad, exclusión o intolerancia que esté dañando seriamente el vínculo con pares y la convivencia. "
                "No conviene minimizarlo como 'cosas de chicos' cuando hay humillación, odio o persecución."
            ),
            "frases": [
                "Necesitamos hablar de esto en serio porque puede lastimar mucho a otros y también traer consecuencias para vos.",
                "Quiero entender qué lugar ocupás en esta situación: si la sufrís, la reproducís o ambas.",
                "No voy a justificar humillaciones ni violencia verbal."
            ],
            "evitar": [
                "Son bromas nada más.",
                "Todos hacen eso.",
                "Mientras no te denuncien, no pasa nada."
            ],
            "tono": "Claro, ético y sin banalizar.",
            "signos": [
                "Humillación repetida, hostigamiento o aislamiento social.",
                "Mensajes masivos de odio o discriminación.",
                "Negación total del daño causado."
            ],
            "cuando": "Actuá rápido si hay riesgo escolar, digital, legal o emocional serio para alguien.",
            "ahora": "Frená la conducta, protegé a quien está siendo dañado y articulá con escuela o adultos responsables.",
            "observar": [
                "Si se trata de un episodio aislado o patrón sostenido.",
                "Qué rol ocupa tu hijo/a: víctima, agresor, cómplice o testigo.",
                "El impacto concreto en otros."
            ],
            "seguir": "Trabajá empatía, responsabilidad y reparación.",
            "preguntas": [
                "¿Qué pensabas que iba a generar eso en el otro?",
                "¿Cómo te sentirías si te lo hicieran a vos?",
                "¿Qué podrías hacer para reparar parte del daño?"
            ],
            "actividades": [
                "Conversar con la escuela si corresponde.",
                "Retirar publicaciones o mensajes dañinos.",
                "Trabajar acciones concretas de reparación."
            ],
        }
    },

    "digital_online_riesgo": {
        "es": {
            "que_podria_estar_pasando": (
                "El mundo digital puede mezclar pertenencia, impulsividad, anonimato y desinhibición. "
                "Eso aumenta el riesgo de apuestas, conflictos, exposición sexual, estafas o conductas ilegales."
            ),
            "frases": [
                "No quiero demonizar internet, pero sí hablar del riesgo real que puede haber ahí.",
                "Necesito entender qué está pasando online y qué lugar ocupa para vos.",
                "Algunas cosas digitales tienen consecuencias muy reales."
            ],
            "evitar": [
                "Apagá todo y se termina.",
                "Eso no importa porque es virtual.",
                "No sabés nada, te van a denunciar igual."
            ],
            "tono": "Serio, curioso y orientado a seguridad.",
            "signos": [
                "Secretismo con dispositivos, apuestas o dinero.",
                "Exposición sexual, extorsión o contactos con adultos.",
                "Conflictos online que escalan fuera de la pantalla."
            ],
            "cuando": "Actuá rápido si hay grooming, apuestas, extorsión, estafas o explotación sexual.",
            "ahora": "Pedí información concreta, preservá evidencia si hace falta y buscá apoyo adulto/profesional.",
            "observar": [
                "Frecuencia, horarios y tipos de interacción online.",
                "Uso de dinero, transferencias o cuentas ocultas.",
                "Presión de pares o adultos."
            ],
            "seguir": "Poné límites digitales claros y revisá seguridad, legalidad y exposición.",
            "preguntas": [
                "¿Con quién hablás o jugás más online?",
                "¿Alguna vez sentiste presión para hacer algo que no querías?",
                "¿Hay algo que te dé vergüenza contar sobre lo que pasa ahí?"
            ],
            "actividades": [
                "Revisar seguridad de cuentas y dispositivos.",
                "Hablar de consentimiento y riesgos digitales.",
                "Consultar si hay explotación, extorsión o delito."
            ],
        }
    },

    "vinculos_afectivos_sexualidad": {
        "es": {
            "que_podria_estar_pasando": (
                "Puede haber dependencia afectiva, confusión, presión sexual o vínculos desiguales que afectan mucho la autonomía emocional. "
                "Cuando hay diferencias de edad, coerción o embarazo no planificado, la complejidad aumenta y no debe banalizarse."
            ),
            "frases": [
                "Quiero hablar de esto sin juzgarte, pero sí cuidarte.",
                "Un vínculo no debería dejarte con miedo, culpa o control constante.",
                "Lo importante no es castigarte sino entender el riesgo y acompañarte."
            ],
            "evitar": [
                "Es culpa tuya por meterte ahí.",
                "Eso no es amor, dejalo y listo.",
                "No quiero saber nada de ese tema."
            ],
            "tono": "Cuidado, respeto y claridad moral sin humillar.",
            "signos": [
                "Control, celos, presión, aislamiento o manipulación.",
                "Vínculos entre menor y adulto.",
                "Embarazo, aborto posible o coerción sexual."
            ],
            "cuando": "Actuá de inmediato si hay adulto involucrado, coerción, abuso o explotación.",
            "ahora": "Separá el cuidado del juicio y priorizá seguridad, información y adultos responsables.",
            "observar": [
                "Si hay miedo, vergüenza o dependencia extrema.",
                "Si perdió autonomía o cambió mucho por la relación.",
                "Si hay secreto, diferencia de poder o manipulación."
            ],
            "seguir": "Acompañá con adultez, no desde el escándalo.",
            "preguntas": [
                "¿Te sentís libre o sentís que te controlan?",
                "¿Qué te cuesta más de esta relación o situación?",
                "¿Hay algo que te haga sentir inseguro/a o presionado/a?"
            ],
            "actividades": [
                "Conversar con un profesional si el vínculo es riesgoso.",
                "Mapear red de apoyo segura.",
                "Priorizar salud física, emocional y legal."
            ],
        }
    },

    "familia_autoridad_mentira": {
        "es": {
            "que_podria_estar_pasando": (
                "Puede haber una dinámica vincular deteriorada: mentira, chantaje, incomunicación o rechazo a la autoridad. "
                "A veces la conducta visible es solo la punta de una crisis más profunda en la confianza y en el lugar de los adultos."
            ),
            "frases": [
                "Quiero reconstruir un modo de hablar que no dependa de gritos, mentiras o amenazas.",
                "Necesitamos volver a un marco de confianza y límites.",
                "No se trata solo de lo que pasó hoy, sino de cómo nos estamos tratando."
            ],
            "evitar": [
                "Con vos no se puede nunca.",
                "No te creo nada de nada.",
                "Yo mando y no se discute."
            ],
            "tono": "Firme, ordenado y sin humillación.",
            "signos": [
                "Mentira compulsiva o manipulación constante.",
                "Escalada crónica con adultos de referencia.",
                "Violencia intrafamiliar o chantaje emocional."
            ],
            "cuando": "Actuá si ya no hay trato posible, si hay violencia o si la convivencia quedó dañada de forma sostenida.",
            "ahora": "Bajá la intensidad, ordená límites básicos y evitá discutir todo al mismo tiempo.",
            "observar": [
                "Qué temas detonan más engaño o pelea.",
                "Si hay sobreadaptación o aparente perfección que tapa malestar.",
                "Si la familia está sosteniendo una dinámica nociva."
            ],
            "seguir": "Trabajá acuerdos claros y buscá ayuda si la convivencia está rota.",
            "preguntas": [
                "¿En qué momento sentís que dejamos de poder hablar bien?",
                "¿Qué parte de esta relación te cuesta más sostener?",
                "¿Qué necesitarías para sentirte tratado/a con más justicia sin romper los límites?"
            ],
            "actividades": [
                "Pactar una conversación breve con reglas claras.",
                "Suspender gritos y escenas como forma habitual de vínculo.",
                "Consultar si la dinámica familiar está muy dañada."
            ],
        }
    },

    "delito_vandalismo_crueldad": {
        "es": {
            "que_podria_estar_pasando": (
                "Puede haber impulsividad, búsqueda de impacto, presión de pares o desconexión del daño causado. "
                "Cuando aparecen robo, vandalismo, maltrato animal o amenazas, ya no es solo mala conducta: también hay dimensión ética y legal."
            ),
            "frases": [
                "Esto no es un detalle menor: puede lastimar a otros y tener consecuencias serias.",
                "Necesitamos hablar de responsabilidad, daño y reparación.",
                "No voy a minimizarlo ni tampoco reducirte solo a esto."
            ],
            "evitar": [
                "Todos alguna vez hacen eso.",
                "Mientras no te agarren, no importa.",
                "Sos un delincuente y listo."
            ],
            "tono": "Muy claro, con responsabilidad y sin etiquetar a la persona como irreparable.",
            "signos": [
                "Crueldad, daño, amenazas o disfrute del sufrimiento ajeno.",
                "Reincidencia o falta total de registro.",
                "Escalada hacia riesgo legal o físico."
            ],
            "cuando": "Actuá rápido si hay delito, amenaza, crueldad o posibilidad de denuncia.",
            "ahora": "Frená la conducta, evaluá el riesgo legal y pensá en contención + reparación + límites.",
            "observar": [
                "Si fue episodio aislado o patrón.",
                "Si hubo grupo, coerción o impulso.",
                "Si hay falta de empatía persistente."
            ],
            "seguir": "No banalices ni moralices solamente: hacé foco en responsabilidad, empatía y consecuencias.",
            "preguntas": [
                "¿Qué pensaste que iba a pasar cuando hiciste eso?",
                "¿Qué daño creés que causaste?",
                "¿Qué haría falta para reparar aunque sea una parte?"
            ],
            "actividades": [
                "Ordenar consecuencias concretas.",
                "Hablar de reparación y legalidad.",
                "Buscar apoyo profesional si hay crueldad o escalada."
            ],
        }
    },

    "escuela_proyecto_vida": {
        "es": {
            "que_podria_estar_pasando": (
                "El rechazo a la escuela o la apatía académica puede expresar frustración, vacío, humillación o pérdida de sentido. "
                "No siempre es pereza: a veces es la forma visible de un malestar más amplio."
            ),
            "frases": [
                "No quiero reducir esto a notas o rendimiento; quiero entender qué te está pasando con todo esto.",
                "Necesitamos pensar cómo ayudarte a sostener algo posible.",
                "No te exijo perfección, pero sí que no te quedes solo/a con esto."
            ],
            "evitar": [
                "No vas a llegar a nada.",
                "Sos un vago / una vaga.",
                "Mientras vivas acá, estudiás y punto."
            ],
            "tono": "Exigencia justa, sin humillar ni resignarse.",
            "signos": [
                "Desconexión total del estudio o del futuro.",
                "Vergüenza escolar, conflictos o expulsión del grupo.",
                "Apatía sostenida con pérdida de proyecto."
            ],
            "cuando": "Actuá si el derrumbe escolar es brusco, sostenido o se asocia a otros riesgos.",
            "ahora": "Separá el síntoma académico del problema de fondo y buscá una conversación real.",
            "observar": [
                "Si el rechazo es a la escuela, al grupo o a sí mismo/a.",
                "Cuándo empezó y con qué se relaciona.",
                "Qué todavía logra sostener."
            ],
            "seguir": "Buscá un plan gradual, posible y acompañado.",
            "preguntas": [
                "¿Qué es lo que más te está costando de la escuela hoy?",
                "¿Te sentís frustrado/a, aburrido/a o humillado/a?",
                "¿Qué te resultaría un primer paso más posible?"
            ],
            "actividades": [
                "Hablar con la escuela si corresponde.",
                "Armar metas cortas y realistas.",
                "Volver a conectar esfuerzo con sentido."
            ],
        }
    },

    "duelo_abandono_vacio": {
        "es": {
            "que_podria_estar_pasando": (
                "Puede haber una vivencia de pérdida, abandono o vacío que esté organizando gran parte del malestar. "
                "Cuando un adolescente se siente dejado, rechazado o sin sentido, eso impacta en muchas áreas al mismo tiempo."
            ),
            "frases": [
                "No quiero apurarte a estar bien si algo te duele profundamente.",
                "Quiero acompañarte también en lo que no se puede resolver rápido.",
                "Aunque no sepa exactamente qué decir, quiero estar."
            ],
            "evitar": [
                "Ya tendrías que haberlo superado.",
                "Tenés que ponerle onda.",
                "No pienses más en eso."
            ],
            "tono": "Muy humano, paciente y presente.",
            "signos": [
                "Desesperanza o vacío persistente.",
                "Aislamiento o apatía después de una pérdida.",
                "Reacciones intensas a rechazos o ausencias."
            ],
            "cuando": "Actuá si el vacío deriva en autolesión, ideación suicida o deterioro marcado.",
            "ahora": "No llenes el dolor con discursos: acompañá, nombrá y sostené.",
            "observar": [
                "Qué pérdidas o abandonos siguen activos emocionalmente.",
                "Cómo aparece el tema en su conducta.",
                "Qué cosas alivian aunque sea un poco."
            ],
            "seguir": "El duelo necesita tiempo, presencia y, si hace falta, acompañamiento profesional.",
            "preguntas": [
                "¿Qué es lo que más te duele o te pesa de esto?",
                "¿Qué extrañás o sentís que perdiste?",
                "¿Qué te ayuda un poco a no sentirte tan solo/a?"
            ],
            "actividades": [
                "Rituales de recuerdo o despedida si corresponde.",
                "Espacios de conversación sin apuro.",
                "Acompañamiento profesional si el dolor se cronifica."
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

    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in t:
                score += 1
        if score > 0:
            scores[category] = score

    if not scores:
        return "familia_autoridad_mentira"

    return max(scores, key=scores.get)


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


def fallback_response(lang: str):
    if lang == "en":
        return {
            "que_podria_estar_pasando": (
                "This may reflect emotional distress, confusion, or difficulty expressing what is happening."
            ),
            "frases": [
                "I care about what is happening to you.",
                "I want to understand better before assuming.",
                "We can talk step by step."
            ],
            "evitar": [
                "You are overreacting.",
                "You are impossible.",
                "This is nothing."
            ],
            "tono": "Calm, respectful, and clear.",
            "signos": [
                "Sustained behavioral changes.",
                "Isolation, aggression, or hopelessness.",
                "Escalation in conflict or risk."
            ],
            "cuando": "Take action if it worsens, repeats, or threatens safety.",
            "ahora": "Choose a calm moment and prioritize connection over control.",
            "observar": [
                "What triggers the problem.",
                "What makes it better or worse.",
                "Whether functioning is deteriorating."
            ],
            "seguir": "Do not solve everything at once: stay present and consistent.",
            "preguntas": [
                "What has been hardest for you lately?",
                "What do you need from me right now?",
                "What would help this conversation feel safer?"
            ],
            "actividades": [
                "Take a short walk.",
                "Share a simple task.",
                "Talk in brief and calm moments."
            ],
        }

    if lang == "it":
        return {
            "que_podria_estar_pasando": (
                "Questo può riflettere sofferenza emotiva, confusione o difficoltà a esprimere ciò che sta succedendo."
            ),
            "frases": [
                "Mi importa quello che ti sta succedendo.",
                "Voglio capire meglio prima di supporre.",
                "Possiamo parlarne poco alla volta."
            ],
            "evitar": [
                "Stai esagerando.",
                "Sei impossibile.",
                "Non è niente."
            ],
            "tono": "Calmo, rispettoso e chiaro.",
            "signos": [
                "Cambiamenti comportamentali persistenti.",
                "Isolamento, aggressività o disperazione.",
                "Aumento del conflitto o del rischio."
            ],
            "cuando": "Intervieni se peggiora, si ripete o mette a rischio la sicurezza.",
            "ahora": "Scegli un momento tranquillo e dai priorità al legame più che al controllo.",
            "observar": [
                "Cosa scatena il problema.",
                "Cosa lo migliora o peggiora.",
                "Se il funzionamento generale sta peggiorando."
            ],
            "seguir": "Non cercare di risolvere tutto subito: resta presente e coerente.",
            "preguntas": [
                "Che cosa ti sta pesando di più ultimamente?",
                "Di cosa hai bisogno da me adesso?",
                "Cosa renderebbe questa conversazione più sicura?"
            ],
            "actividades": [
                "Fare una breve passeggiata.",
                "Condividere un'attività semplice.",
                "Parlare in momenti brevi e tranquilli."
            ],
        }

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


def get_category_content(category: str, lang: str) -> dict:
    if category in CATEGORY_RESPONSES:
        if lang in CATEGORY_RESPONSES[category]:
            return CATEGORY_RESPONSES[category][lang]
        if "es" in CATEGORY_RESPONSES[category]:
            return CATEGORY_RESPONSES[category]["es"]
    return fallback_response(lang)


def build_guidance(text: str, lang: str) -> SituationResponse:
    category = detect_category(text)
    intensity, high_risk = detect_risk(text, category)
    content = get_category_content(category, lang)
    lang_pack = LANG_TEXT[get_lang(lang)]

    urgent_message = lang_pack["urgent_help"] if high_risk else None

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
    lang_pack = LANG_TEXT[get_lang(lang)]

    if get_lang(lang) == "en":
        return [
            f"{lang_pack['rewrite_1_prefix']}{txt}. I want to understand what is happening without attacking you.",
            f"{lang_pack['rewrite_2_prefix']}{txt}. I care about you and I want us to speak with respect."
        ]

    if get_lang(lang) == "it":
        return [
            f"{lang_pack['rewrite_1_prefix']}{txt}. Voglio capire cosa sta succedendo senza attaccarti.",
            f"{lang_pack['rewrite_2_prefix']}{txt}. Mi importa di te e voglio che possiamo parlarne con rispetto."
        ]

    return [
        f"{lang_pack['rewrite_1_prefix']}{txt}. Quiero entender qué está pasando sin atacarte.",
        f"{lang_pack['rewrite_2_prefix']}{txt}. Me importás y quiero que podamos hablar con respeto."
    ]


# =========================
# API ENDPOINTS
# =========================

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


# =========================
# APP CONFIG
# =========================

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
