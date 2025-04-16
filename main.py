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
        resp = xata.tables().list_tables()
        if resp.is_success():
            return {"message": "Conexión exitosa", "tables": resp["tables"]}
        return {"error": "Fallo al listar tablas", "details": resp}
    except Exception as e:
        return {"error": str(e)}


class OrderCreate(BaseModel):
    user_id: str
    product: str

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
        "status": "pending"
    }
    try:
        resp = xata.records().insert("orders", new_order)
        if resp.is_success():
            return resp["record"]
        error_details = resp.get("errors", [{}])[0] if "errors" in resp else resp
        error_message = error_details.get("message", "Unknown error")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {error_message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception occurred: {str(e)}")

@app.get("/orders/{order_id}", response_model=dict)
async def get_order(order_id: str):
    resp = xata.records().get("orders", order_id)
    if resp.is_success():
        return resp["record"]
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
        