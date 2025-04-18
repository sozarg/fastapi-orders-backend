from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from xata.client import XataClient
from datetime import datetime
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://react-orders-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

xata = XataClient(
    api_key=os.getenv("XATA_API_KEY"),
    workspace_id=os.getenv("XATA_WORKSPACE_ID"),
    db_name=os.getenv("XATA_DB_NAME"),
    branch_name=os.getenv("XATA_BRANCH", "main"),
    region=os.getenv("XATA_REGION", "us-west-2")
)

print("Workspace ID:", os.getenv("XATA_WORKSPACE_ID"))
print("DB Name:", os.getenv("XATA_DB_NAME"))

@app.get("/test-xata")
async def test_xata():
    try:
        resp = xata.data().query("orders", {"page": {"size": 1}})
        if resp.is_success():
            return {"message": "Conexión exitosa", "table_exists": "orders"}
        return {"error": "Fallo al consultar tabla", "details": resp}
    except Exception as e:
        return {"error": str(e)}


class OrderCreate(BaseModel):
    user_id: str
    product: str
    price: float
    payment_status: str

class MessageCreate(BaseModel):
    order_id: str
    sender: str  # Cambiado de user_id a sender para coincidir con el esquema de Xata
    content: str

class OrderUpdate(BaseModel):
    status: str

@app.get("/")
@app.head("/")
async def read_root():
    return {"message": "Hola, Detta3D - API Key Fixed"}

@app.post("/orders/", response_model=dict)
async def create_order(order: OrderCreate):
    new_order = {
        "user_id": order.user_id,
        "product": order.product,
        "price": order.price,
        "payment_status": order.payment_status,
        "status": "pending"
    }

    try:
        resp = xata.records().insert("orders", new_order)

        if resp.is_success():
            inserted_id = resp.get("id")
            if inserted_id:
                # Traemos el registro por ID
                full_record = xata.records().get("orders", inserted_id)
                print("Respuesta de get():", full_record)

                if full_record.is_success():
                    return full_record  # <- este es el fix
                else:
                    raise HTTPException(status_code=500, detail="Insert ok, pero no se pudo recuperar el registro")
            else:
                raise HTTPException(status_code=500, detail="Insert ok, pero no se devolvió el ID")

        print("Xata insert error response:", resp)
        error_details = resp.get("errors", [{}])[0]
        error_message = error_details.get("message", "Unknown error")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {error_message}")

    except Exception as e:
        print("Error inesperado en /orders/:", e)
        raise HTTPException(status_code=500, detail=f"Exception occurred: {str(e)}")

@app.get("/orders/{order_id}", response_model=dict)
async def get_order(order_id: str):
    record = xata.records().get("orders", order_id)
    print(record)

    if record is not None:
        return record
    else:
        raise HTTPException(status_code=404, detail="Order not found")


@app.patch("/orders/{order_id}", response_model=dict)
async def update_order(order_id: str, order_update: OrderUpdate):
    update_data = {"status": order_update.status}
    resp = xata.records().update("orders", order_id, update_data)
    if resp.is_success():
        return resp["record"]
    raise HTTPException(status_code=404, detail="Order not found")

@app.post("/messages/", response_model=dict)
async def create_message(message: MessageCreate):
    new_message = {
        "order_id": message.order_id,
        "sender": message.sender,  # Cambiado de user_id a sender
        "content": message.content,
        "created_at": datetime.utcnow().isoformat()
    }
    try:
        resp = xata.records().insert("messages", new_message)
        if resp.is_success():
            return resp["record"]
        error_details = resp.get("errors", [{}])[0] if "errors" in resp else resp
        error_message = error_details.get("message", "Unknown error")
        raise HTTPException(status_code=500, detail=f"Failed to create message: {error_message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception occurred: {str(e)}")

@app.get("/orders/", response_model=list[dict])
async def get_all_orders():
    try:
        records = xata.records().get_all("orders")
        return records
    except Exception as e:
        print("Error al obtener todos los pedidos:", e)
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos: {str(e)}")
