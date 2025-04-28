from fastapi import APIRouter, HTTPException
from schemas.orders_schema import OrderCreate, OrderUpdate, OrderOut
from services.orders_service import create_order, list_orders, update_order, list_completed_orders
from typing import List

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.post("/", response_model=OrderOut, status_code=201)
async def create_new_order(order: OrderCreate):
    """Crear un nuevo pedido."""
    try:
        new_order = await create_order(order)
        return new_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[OrderOut])
async def get_all_orders():
    """Obtener todos los pedidos."""
    try:
        orders = await list_orders()
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{order_id}", response_model=OrderOut)
async def update_existing_order(order_id: str, update_data: OrderUpdate):
    """Actualizar un pedido existente."""
    try:
        updated_order = await update_order(order_id, update_data)
        return updated_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/completed/", response_model=List[OrderOut])
async def get_completed_orders():
    """Obtener pedidos completados."""
    try:
        completed = await list_completed_orders()
        return completed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))