from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from xata.client import XataClient
from datetime import datetime
from typing import Optional, List
import os
from enum import Enum

# Configuración de la aplicación
app = FastAPI(title="Detta3D API", version="1.0.0")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://react-orders-frontend.onrender.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente Xata
xata = XataClient(
    api_key=os.getenv("XATA_API_KEY"),
    workspace_id=os.getenv("XATA_WORKSPACE_ID"),
    db_name=os.getenv("XATA_DB_NAME"),
    branch_name=os.getenv("XATA_BRANCH", "main"),
    region=os.getenv("XATA_REGION", "us-west-2")
)

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
@app.get("/")
async def read_root():
    return {"message": "Detta3D API - v1.0.0"}

@app.post("/orders/", response_model=dict)
async def create_order(order: OrderCreate):
    try:
        new_order = order.dict(exclude_none=True)
        resp = xata.records().insert("orders", new_order)

        if not resp.is_success():
            raise HTTPException(
                status_code=500,
                detail="Error al crear el pedido en la base de datos"
            )

        inserted_id = resp.get("id")
        if not inserted_id:
            raise HTTPException(
                status_code=500,
                detail="No se pudo obtener el ID del pedido creado"
            )

        # Obtener el registro completo
        full_record = xata.records().get("orders", inserted_id)
        if not full_record.is_success():
            raise HTTPException(
                status_code=500,
                detail="No se pudo recuperar el pedido creado"
            )

        return full_record

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )

@app.get("/orders/", response_model=list[dict])
async def get_all_orders():
    try:
        response = xata.data().query("orders", {
            "page": {
                "size": 100  # Puedes ajustar este número según necesites
            }
        })
        if not response.is_success():
            raise HTTPException(
                status_code=500,
                detail="Error al obtener pedidos"
            )
        return response["records"]  # Xata devuelve los registros en la clave "records"
    except Exception as e:
        print("Error al obtener todos los pedidos:", e)
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos: {str(e)}")

@app.get("/orders/{order_id}", response_model=dict)
async def get_order(order_id: str):
    try:
        record = xata.records().get("orders", order_id)
        if not record.is_success():
            raise HTTPException(
                status_code=404,
                detail="Pedido no encontrado"
            )
        return record
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el pedido: {str(e)}"
        )

@app.patch("/orders/{order_id}", response_model=dict)
async def update_order(order_id: str, order_update: OrderUpdate):
    try:
        # Verificar si el pedido existe
        existing_order = xata.records().get("orders", order_id)
        if not existing_order.is_success():
            raise HTTPException(
                status_code=404,
                detail="Pedido no encontrado"
            )

        # Actualizar solo los campos proporcionados
        update_data = order_update.dict(exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar"
            )

        resp = xata.records().update("orders", order_id, update_data)
        if not resp.is_success():
            raise HTTPException(
                status_code=500,
                detail="Error al actualizar el pedido"
            )

        return resp["record"]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )

@app.get("/orders/completed/", response_model=List[dict])
async def get_completed_orders():
    try:
        # Aquí puedes definir tu criterio de "completado"
        # Por ejemplo, pedidos con cierto status
        completed_orders = xata.data().query(
            "orders",
            {
                "filter": {
                    "status": "completed"  # Ajusta según tu lógica de negocio
                }
            }
        )
        
        if not completed_orders.is_success():
            raise HTTPException(
                status_code=500,
                detail="Error al obtener los pedidos completados"
            )
            
        return completed_orders["records"]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los pedidos completados: {str(e)}"
        )