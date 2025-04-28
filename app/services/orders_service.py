import logging
from typing import List
from fastapi import HTTPException
from datetime import datetime
from enum import Enum

from app.database import xata
from app.models.orders import OrderCreate, OrderUpdate

logger = logging.getLogger(__name__)

def create_order(order: OrderCreate) -> dict:
    """Crea un nuevo pedido en la base de datos Xata."""
    logger.info(f"Creating order: {order.model_dump(exclude_none=True)}")
    try:
        new_order = order.model_dump(exclude_none=True)
        if "created_at" not in new_order:
            new_order["created_at"] = datetime.utcnow().isoformat() + "Z"
        else:
            new_order["created_at"] = new_order["created_at"].isoformat() + "Z"
        if isinstance(new_order.get("status"), Enum):
            new_order["status"] = new_order["status"].value
        if isinstance(new_order.get("payment_status"), Enum):
            new_order["payment_status"] = new_order["payment_status"].value

        resp = xata.records().insert("orders", new_order)
        if not resp.is_success():
            logger.error(f"Failed to create order: {resp.get('message', 'Unknown error')}")
            raise HTTPException(status_code=500, detail="Error al crear el pedido en la base de datos")
        
        inserted_id = resp.get("id")
        if not inserted_id:
            logger.error("No ID returned for created order")
            raise HTTPException(status_code=500, detail="No se pudo obtener el ID del pedido creado")
        
        full_record = xata.records().get("orders", inserted_id)
        if not full_record.is_success():
            logger.error(f"Failed to retrieve created order: {inserted_id}")
            raise HTTPException(status_code=500, detail="No se pudo recuperar el pedido creado")
        
        logger.info(f"Order created successfully: {inserted_id}")
        return full_record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating order: {e}")
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")

def get_all_orders() -> List[dict]:
    """Obtiene la lista de todos los pedidos."""
    logger.info("Fetching all orders")
    try:
        response = xata.data().query("orders", {"page": {"size": 100}})
        if not response.is_success():
            logger.error(f"Failed to fetch orders: {response.get('message', 'Unknown error')}")
            raise HTTPException(status_code=500, detail="Error al obtener pedidos")
        
        orders = response.get("records", [])
        logger.info(f"Fetched {len(orders)} orders")
        return orders
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos: {e}")

def get_order(order_id: str) -> dict:
    """Obtiene un pedido específico por ID."""
    logger.info(f"Fetching order: {order_id}")
    try:
        record = xata.records().get("orders", order_id)
        if not record.is_success():
            logger.warning(f"Order not found: {order_id}")
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        logger.info(f"Order fetched: {order_id}")
        return record
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener el pedido: {e}")

def update_order(order_id: str, order_update: OrderUpdate) -> dict:
    """Actualiza un pedido existente identificado por ID con los datos proporcionados."""
    logger.info(f"Updating order: {order_id}")
    try:
        existing = xata.records().get("orders", order_id)
        if not existing.is_success():
            logger.warning(f"Order not found for update: {order_id}")
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        update_data = order_update.model_dump(exclude_none=True)
        if not update_data:
            logger.warning("No update data provided")
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        if isinstance(update_data.get("status"), Enum):
            update_data["status"] = update_data["status"].value
        if isinstance(update_data.get("payment_status"), Enum):
            update_data["payment_status"] = update_data["payment_status"].value

        resp = xata.records().update("orders", order_id, update_data)
        if not resp.is_success():
            logger.error(f"Failed to update order: {resp.get('message', 'Unknown error')}")
            raise HTTPException(status_code=500, detail="Error al actualizar el pedido")
        
        updated_record = resp.get("record")
        logger.info(f"Order updated: {order_id}")
        return updated_record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")

def get_completed_orders() -> List[dict]:
    """Obtiene todos los pedidos marcados como 'completados' (entregados)."""
    logger.info("Fetching completed orders")
    try:
        completed = xata.data().query(
            "orders",
            {
                "filter": {"status": {"$is": "Envío a domicilio"}},
                "page": {"size": 100}
            }
        )
        if not completed.is_success():
            logger.error(f"Failed to fetch completed orders: {completed.get('message', 'Unknown error')}")
            raise HTTPException(status_code=500, detail="Error al obtener los pedidos completados")
        
        records = completed.get("records", [])
        logger.info(f"Fetched {len(records)} completed orders")
        return records
    except Exception as e:
        logger.error(f"Error fetching completed orders: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener los pedidos completados: {e}")
