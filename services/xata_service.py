from xata.client import XataClient
import os
import logging

# Configuración de logs
logger = logging.getLogger(__name__)

# Inicialización del cliente Xata
try:
    xata = XataClient(
        api_key=os.getenv("XATA_API_KEY"),
        workspace_id=os.getenv("XATA_WORKSPACE_ID"),
        db_name=os.getenv("XATA_DB_NAME"),
        branch_name=os.getenv("XATA_BRANCH", "main"),
        region=os.getenv("XATA_REGION", "us-west-2")
    )
except Exception as e:
    logger.error(f"Error inicializando Xata client: {str(e)}")
    raise Exception(f"Error inicializando Xata client: {str(e)}")


def create_order(order_data: dict):
    """Crea un nuevo pedido en Xata."""
    try:
        response = xata.records().insert("orders", order_data)
        if not response.is_success():
            logger.error(f"Error creando pedido: {response.get('message', 'Unknown error')}")
            return None
        return response
    except Exception as e:
        logger.error(f"Excepción al crear pedido: {str(e)}")
        return None


def get_all_orders():
    """Obtiene todos los pedidos."""
    try:
        response = xata.data().query("orders", {
            "page": {
                "size": 100
            }
        })
        if not response.is_success():
            logger.error(f"Error obteniendo pedidos: {response.get('message', 'Unknown error')}")
            return None
        return response["records"]
    except Exception as e:
        logger.error(f"Excepción al obtener pedidos: {str(e)}")
        return None


def get_order(order_id: str):
    """Obtiene un pedido por ID."""
    try:
        record = xata.records().get("orders", order_id)
        if not record.is_success():
            logger.warning(f"Pedido no encontrado: {order_id}")
            return None
        return record
    except Exception as e:
        logger.error(f"Excepción al obtener pedido {order_id}: {str(e)}")
        return None


def update_order(order_id: str, order_update_data: dict):
    """Actualiza un pedido existente."""
    try:
        response = xata.records().update("orders", order_id, order_update_data)
        if not response.is_success():
            logger.error(f"Error actualizando pedido: {response.get('message', 'Unknown error')}")
            return None
        return response["record"]
    except Exception as e:
        logger.error(f"Excepción al actualizar pedido {order_id}: {str(e)}")
        return None


def get_completed_orders():
    """Obtiene los pedidos completados (entregados)."""
    try:
        response = xata.data().query(
            "orders",
            {
                "filter": {
                    "status": "Envío a domicilio"
                },
                "page": {
                    "size": 100
                }
            }
        )
        if not response.is_success():
            logger.error(f"Error obteniendo pedidos completados: {response.get('message', 'Unknown error')}")
            return None
        return response["records"]
    except Exception as e:
        logger.error(f"Excepción al obtener pedidos completados: {str(e)}")
        return None
