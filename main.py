from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import orders

app = FastAPI(
    title="Detta3D Orders API",
    version="1.0.0"
)

# Configuración CORS
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

# Incluir rutas
app.include_router(orders.router)
