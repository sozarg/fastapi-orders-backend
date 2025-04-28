import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Detta3D API", version="1.0.0")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.routers import orders as orders_router
app.include_router(orders_router.router)

@app.get("/", summary="Verificar estado del backend")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Detta3D API - v1.0.0"}
