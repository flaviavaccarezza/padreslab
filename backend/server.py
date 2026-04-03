from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (para que Vercel pueda hablar con Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router principal
api_router = APIRouter(prefix="/api")

# -----------------------------
# DATOS SIMULADOS (mejorables después con IA)
# -----------------------------

FREQUENT_SITUATIONS = [
    "No quiere hablar conmigo",
    "Se encierra en su cuarto",
    "Está agresivo",
    "Miente o oculta cosas",
    "Uso excesivo del celular",
]

HELP_RESOURCES = [
    "Habla con un orientador escolar",
    "Consulta con un psicólogo",
    "Líneas de ayuda emocional",
]

# -----------------------------
# ENDPOINTS
# -----------------------------

@api_router.get("/")
def root():
    return {"message": "API PadresLab funcionando"}

@api_router.get("/frequent-situations")
def get_frequent_situations():
    return FREQUENT_SITUATIONS

@api_router.get("/help-resources")
def get_help_resources():
    return HELP_RESOURCES

@api_router.post("/analyze")
def analyze(data: dict):
    text = data.get("text", "").lower()

    if not text:
        return {"error": "No se envió texto"}

    # Lógica simple (luego la mejoramos con IA)
    if "no habla" in text or "callado" in text:
        return {
            "severity": "media",
            "message": "Puede estar atravesando una etapa de cierre emocional. Es importante abrir espacios de escucha sin presión."
        }

    if "agresivo" in text or "violento" in text:
        return {
            "severity": "alta",
            "message": "La agresividad puede ser expresión de frustración o desborde emocional. Es importante intervenir con calma y buscar apoyo."
        }

    return {
        "severity": "baja",
        "message": "Podría ser una situación cotidiana. Acompañar con presencia y diálogo suele ser suficiente."
    }

# 🔥 ESTO ES LO QUE TE FALTABA
app.include_router(api_router)
