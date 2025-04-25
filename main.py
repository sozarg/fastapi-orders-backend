from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import orders

app = FastAPI(title="Detta3D API", version="1.0.0")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://react-orders-frontend.onrender.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(orders.router)


@app.get("/", summary="Verificar estado del backend")
async def root():
    return {"message": "Detta3D API - v1.0.0"}
