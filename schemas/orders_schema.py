from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class OrderBase(BaseModel):
    product: str = Field(..., example="Mate MESSI PSG")
    price: float = Field(..., gt=0, example=7500)
    payment_status: str = Field(..., example="Instagram")
    user_id: str = Field(..., example="Mateo Terrile")
    status: str = Field(..., example="Retira en persona")
    address: Optional[str] = Field(None, example="Avellaneda 123")
    notes: Optional[str] = Field(None, example="Solo puede retirar de noche")

class OrderCreate(OrderBase):
    """Modelo para crear un nuevo pedido."""
    pass

class OrderUpdate(BaseModel):
    """Modelo para actualizar parcialmente un pedido."""
    product: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    payment_status: Optional[str] = None
    user_id: Optional[str] = None
    status: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class OrderOut(OrderBase):
    """Modelo de salida de un pedido."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True