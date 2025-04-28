from schemas.orders_schema import OrderCreate, OrderUpdate
from database.xata import xata_client
from typing import List
from datetime import datetime

ORDERS_TABLE = "orders"

async def create_order(order_data: OrderCreate) -> dict:
    """Crea un nuevo pedido en Xata."""
    order_dict = order_data.dict()
    order_dict['created_at'] = datetime.utcnow().isoformat()
    order_dict['updated_at'] = datetime.utcnow().isoformat()

    created_record = await xata_client.records().create(ORDERS_TABLE, order_dict)
    
    return {
        "id": created_record["id"],
        **created_record["fields"]
    }

async def list_orders() -> List[dict]:
    """Obtiene todos los pedidos."""
    records = await xata_client.records().get_all(ORDERS_TABLE)
    return [
        {
            "id": record["id"],
            **record["fields"]
        }
        for record in records
    ]

async def update_order(order_id: str, update_data: OrderUpdate) -> dict:
    """Actualiza un pedido existente."""
    update_fields = {k: v for k, v in update_data.dict(exclude_unset=True).items()}
    update_fields['updated_at'] = datetime.utcnow().isoformat()

    updated_record = await xata_client.records().update(ORDERS_TABLE, order_id, update_fields)

    return {
        "id": updated_record["id"],
        **updated_record["fields"]
    }

async def list_completed_orders() -> List[dict]:
    """Obtiene todos los pedidos con status 'completado'."""
    query = {
        "filter": {
            "status": {
                "$equals": "Completado"
            }
        }
    }
    records = await xata_client.records().query(ORDERS_TABLE, query)
    return [
        {
            "id": record["id"],
            **record["fields"]
        }
        for record in records.get("records", [])
    ]