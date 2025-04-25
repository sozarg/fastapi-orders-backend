from fastapi import APIRouter, HTTPException
from models.order import OrderCreate, OrderUpdate
from services.xata_service import XataService
from typing import List

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

xata = XataService()

@router.post("/", response_model=dict, summary="Crear un nuevo pedido")
async def create_order(order: OrderCreate):
    new_order = order.model_dump(exclude_none=True)
    new_order["created_at"] = new_order["created_at"].isoformat()

    record = await xata.create_order(new_order)
    if not record:
        raise HTTPException(status_code=500, detail="Error al crear el pedido")
    return record

@router.get("/", response_model=List[dict], summary="Obtener todos los pedidos")
async def get_orders():
    orders = await xata.get_all_orders()
    return orders

@router.get("/{order_id}", response_model=dict, summary="Obtener un pedido específico")
async def get_order(order_id: str):
    order = await xata.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return order

@router.patch("/{order_id}", response_model=dict, summary="Actualizar un pedido")
async def update_order(order_id: str, order_update: OrderUpdate):
    updated_order = await xata.update_order(order_id, order_update.dict(exclude_none=True))
    if not updated_order:
        raise HTTPException(status_code=500, detail="Error al actualizar el pedido")
    return updated_order
