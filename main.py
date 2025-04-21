from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from xata.client import XataClient
from datetime import datetime
from typing import Optional, List
import os
from enum import Enum
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validación de variables de entorno
required_env_vars = ["XATA_API_KEY", "XATA_WORKSPACE_ID", "XATA_DB_NAME"]
for var in required_env_vars:
    if not os.getenv(var):
        raise Exception(f"Missing environment variable: {var}")

# Configuración de la aplicación
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

# Cliente Xata
try:
    xata = XataClient(
        api_key=os.getenv("XATA_API_KEY"),
        workspace_id=os.getenv("XATA_WORKSPACE_ID"),
        db_name=os.getenv("XATA_DB_NAME"),
        branch_name=os.getenv("XATA_BRANCH", "main"),
        region=os.getenv("XATA_REGION", "us-west-2")
    )
except Exception as e:
    logger.error(f"Failed to initialize Xata client: {str(e)}")
    raise Exception(f"Failed to initialize Xata client: {str(e)}")

# Enums para validación
class DeliveryMethod(str, Enum):
    IN_PERSON = "Retira en persona"
    DELIVERY = "Envío a domicilio"
    POST_OFFICE = "Retiro en correo"
    UNSURE = "No estoy seguro"

class PaymentMethod(str, Enum):
    INSTAGRAM = "Instagram"
    WHATSAPP = "Whatsapp"
    MERCADOLIBRE = "Mercadolibre"
    ONLINE_STORE = "Tienda online"

# Modelos Pydantic
class OrderBase(BaseModel):
    user_id: str = Field(..., description="Nombre de la persona")
    product: str = Field(..., description="Nombre del producto")
    price: float = Field(..., gt=0, description="Precio del producto")
    status: Optional[DeliveryMethod] = Field(None, description="Método de entrega")
    payment_status: Optional[PaymentMethod] = Field(None, description="Medio de pago")
    address: Optional[str] = Field(None, description="Dirección de entrega")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Fecha de creación")

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    user_id: Optional[str] = None
    product: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    status: Optional[DeliveryMethod] = None
    payment_status: Optional[PaymentMethod] = None
    address: Optional[str] = None
    notes: Optional[str] = None

# Endpoints
@app.route("/", methods=["GET", "HEAD"], summary="Verificar estado del backend")
async def root():
    """Devuelve un mensaje indicando que el backend está funcionando."""
    logger.info("Root endpoint accessed")
    return {"message": "Detta3D API - v1.0.0"}

@app.post("/orders/", response_model=dict, summary="Crear un nuevo pedido")
async def create_order(order: OrderCreate):
    """Crea un nuevo pedido en la base de datos Xata."""
    logger.info(f"Creating order: {order.dict()}")
    try:
        new_order = order.dict(exclude_none=True)
        resp = xata.records().insert("orders", new_order)

        if not resp.is_success():
            logger.error(f"Failed to create order: {resp.get('message', 'Unknown error')}")
            raise HTTPException(
                status_code=500,
                detail="Error al crear el pedido en la base de datos"
            )

        inserted_id = resp.get("id")
        if not inserted_id:
            logger.error("No ID returned for created order")
            raise HTTPException(
                status_code=500,
                detail="No se pudo obtener el ID del pedido creado"
            )

        full_record = xata.records().get("orders", inserted_id)
        if not full_record.is_success():
            logger.error(f"Failed to retrieve created order: {inserted_id}")
            raise HTTPException(
                status_code=500,
                detail="No se pudo recuperar el pedido creado"
            )

        logger.info(f"Order created successfully: {inserted_id}")
        return full_record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating order: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )

@app.get("/orders/", response_model=List[dict], summary="Obtener todos los pedidos")
async def get_all_orders():
    """Devuelve una lista de todos los pedidos almacenados."""
    logger.info("Fetching all orders")
    try:
        response = xata.data().query("orders", {
            "page": {
                "size": 100
            }
        })
        if not response.is_success():
            logger.error(f"Failed to fetch orders: {response.get('message', 'Unknown error')}")
            raise HTTPException(
                status_code=500,
                detail="Error al obtener pedidos"
            )
        logger.info(f"Fetched {len(response['records'])} orders")
        return response["records"]
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos: {str(e)}")

@app.get("/orders/{order_id}", response_model=dict, summary="Obtener un pedido específico")
async def get_order(order_id: str):
    """Devuelve los detalles de un pedido por su ID."""
    logger.info(f"Fetching order: {order_id}")
    try:
        record = xata.records().get("orders", order_id)
        if not record.is_success():
            logger.warning(f"Order not found: {order_id}")
            raise HTTPException(
                status_code=404,
                detail="Pedido no encontrado"
            )
        logger.info(f"Order fetched: {order_id}")
        return record
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el pedido: {str(e)}"
        )

@app.patch("/orders/{order_id}", response_model=dict, summary="Actualizar un pedido")
async def update_order(order_id: str, order_update: OrderUpdate):
    """Actualiza los campos especificados de un pedido existente."""
    logger.info(f"Updating order: {order_id}")
    try:
        existing_order = xata.records().get("orders", order_id)
        if not existing_order.is_success():
            logger.warning(f"Order not found for update: {order_id}")
            raise HTTPException(
                status_code=404,
                detail="Pedido no encontrado"
            )

        update_data = order_update.dict(exclude_none=True)
        if not update_data:
            logger.warning("No update data provided")
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar"
            )

        resp = xata.records().update("orders", order_id, update_data)
        if not resp.is_success():
            logger.error(f"Failed to update order: {resp.get('message', 'Unknown error')}")
            raise HTTPException(
                status_code=500,
                detail="Error al actualizar el pedido"
            )

        logger.info(f"Order updated: {order_id}")
        return resp["record"]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )

@app.get("/orders/completed/", response_model=List[dict], summary="Obtener pedidos completados")
async def get_completed_orders():
    """Devuelve una lista de pedidos con estado 'Envío a domicilio' (entregados)."""
    logger.info("Fetching completed orders")
    try:
        completed_orders = xata.data().query(
            "orders",
            {
                "filter": {
                    "status": DeliveryMethod.DELIVERY.value
                },
                "page": {
                    "size": 100
                }
            }
        )
        
        if not completed_orders.is_success():
            logger.error(f"Failed to fetch completed orders: {completed_orders.get('message', 'Unknown error')}")
            raise HTTPException(
                status_code=500,
                detail="Error al obtener los pedidos completados"
            )
            
        logger.info(f"Fetched {len(completed-orders['records'])} completed orders")
        return completed_orders["records"]
    except Exception as e:
        logger.error(f"Error fetching completed orders: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los pedidos completados: {str(e)}"
        )