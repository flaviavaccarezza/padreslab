from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/api/")
def home():
    return {"message": "PadresLab API funcionando 🚀"}
