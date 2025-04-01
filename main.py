from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Modelos para validar datos
class OrderCreate(BaseModel):
    user_id: str
    product: str

class MessageCreate(BaseModel):
    order_id: str
    user_id: str
    content: str

# Simulación de base de datos (reemplaza con Xata más adelante)
orders = []
messages = []

@app.get("/")
@app.head("/")
async def read_root():
    return {"message": "Hola, Detta3D"}

@app.post("/orders/")
async def create_order(order: OrderCreate):
    new_order = {
        "id": str(len(orders) + 1),
        "user_id": order.user_id,
        "product": order.product,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    orders.append(new_order)
    return new_order

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    for order in orders:
        if order["id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")

@app.post("/messages/")
async def create_message(message: MessageCreate):
    new_message = {
        "id": str(len(messages) + 1),
        "order_id": message.order_id,
        "user_id": message.user_id,
        "content": message.content,
        "created_at": datetime.utcnow().isoformat()
    }
    messages.append(new_message)
    return new_message