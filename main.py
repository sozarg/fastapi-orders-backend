from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import orders

app = FastAPI(
    title="Orders Management API",
    description="API para gestionar pedidos (crear, listar, actualizar, completados).",
    version="1.0.0",
)

# Configurar CORS
origins = [
    "http://localhost:3000",  # Frontend local
    "https://tu-frontend-en-render.com",  # Frontend desplegado
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(orders.router)

# Ruta de prueba (opcional)
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la Orders Management API 🚀"}
