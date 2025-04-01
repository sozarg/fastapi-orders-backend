from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
@app.head("/")  # Añade soporte para HEAD
async def read_root():
    return {"message": "Hola, Detta3D"}