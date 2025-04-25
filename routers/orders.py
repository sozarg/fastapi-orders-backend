from fastapi import APIRouter, HTTPException
from models.order import OrderCreate, OrderUpdate
from services.xata_service import XataService

router = APIRouter()
xata_service = XataService()

@router.get("/", summary="Verificar estado del backend")
async def root():
    return {"message": "Detta3D API - v1.0.0"}

@router.post("/orders/", summary="Crear un nuevo pedido")
async def create_order(order: OrderCreate):
    try:
        result = xata_service.insert_order(order.model_dump(exclude_none=True))
        if not result.is_success():
            raise HTTPException(status_code=500, detail="Error al crear el pedido en la base de datos")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

@router.get("/orders/", summary="Obtener todos los pedidos")
async def get_all_orders():
    try:
        result = xata_service.get_all_orders()
        if not result.is_success():
            raise HTTPException(status_code=500, detail="Error al obtener pedidos")
        return result["records"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

@router.get("/orders/{order_id}", summary="Obtener un pedido específico")
async def get_order(order_id: str):
    try:
        result = xata_service.get_order(order_id)
        if not result.is_success():
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

@router.patch("/orders/{order_id}", summary="Actualizar un pedido")
async def update_order(order_id: str, order_update: OrderUpdate):
    try:
        update_data = order_update.model_dump(exclude_none=True)
        result = xata_service.update_order(order_id, update_data)
        if not result.is_success():
            raise HTTPException(status_code=500, detail="Error al actualizar el pedido")
        return result["record"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

@router.get("/orders/completed/", summary="Obtener pedidos completados")
async def get_completed_orders():
    try:
        result = xata_service.get_completed_orders()
        if not result.is_success():
            raise HTTPException(status_code=500, detail="Error al obtener pedidos completados")
        return result["records"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
