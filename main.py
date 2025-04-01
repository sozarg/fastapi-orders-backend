from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from xata.client import XataClient
from datetime import datetime
import os

app = FastAPI()

xata = XataClient(
    api_key=os.getenv("XATA_API_KEY"),
    db_url=os.getenv("XATA_DATABASE_URL")
)

class OrderCreate(BaseModel):
    user_id: str
    product: str

class MessageCreate(BaseModel):
    order_id: str
    user_id: str
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
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    resp = xata.records().insert("orders", new_order)
    if resp.is_success():
        return resp["record"]
    # Mostrar el mensaje de error de Xata para depurar
    error_message = resp.get("message", "Failed to create order")
    raise HTTPException(status_code=500, detail=f"Failed to create order: {error_message}")

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
        "user_id": message.user_id,
        "content": message.content,
        "created_at": datetime.utcnow().isoformat()
    }
    resp = xata.records().insert("messages", new_message)
    if resp.is_success():
        return resp["record"]
    raise HTTPException(status_code=500, detail="Failed to create message")