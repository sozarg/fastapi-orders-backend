from fastapi import APIRouter, HTTPException
from typing import List
from app.models.orders import OrderCreate, OrderUpdate
from app.services import orders_service

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.post("/", response_model=dict, summary="Crear un nuevo pedido")
async def create_order(order: OrderCreate):
    """
    Crea un nuevo pedido con la información proporcionada.
    """
    return orders_service.create_order(order)

@router.get("/", response_model=List[dict], summary="Obtener todos los pedidos")
async def get_all_orders():
    """
    Retorna la lista de todos los pedidos registrados.
    """
    return orders_service.get_all_orders()

@router.get("/{order_id}", response_model=dict, summary="Obtener un pedido específico")
async def get_order(order_id: str):
    """
    Retorna los detalles de un pedido específico por su ID.
    """
    return orders_service.get_order(order_id)

@router.patch("/{order_id}", response_model=dict, summary="Actualizar un pedido")
async def update_order(order_id: str, order_update: OrderUpdate):
    """
    Actualiza los campos de un pedido existente. Solo se modifican los campos provistos.
    """
    return orders_service.update_order(order_id, order_update)

@router.get("/completed/", response_model=List[dict], summary="Obtener pedidos completados")
async def get_completed_orders():
    """
    Retorna todos los pedidos marcados como completados.
    """
    return orders_service.get_completed_orders()
