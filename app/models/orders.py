from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.enums.enums import DeliveryMethod, PaymentMethod

class OrderBase(BaseModel):
    """Modelo base de Pedido con campos comunes."""
    user_id: str = Field(..., description="ID del usuario asociado al pedido")
    product: str = Field(..., description="Nombre del producto")
    price: float = Field(..., gt=0, description="Precio del producto")
    status: Optional[DeliveryMethod] = Field(None, description="Método de entrega")
    payment_status: Optional[PaymentMethod] = Field(None, description="Canal de pago/venta")
    address: Optional[str] = Field(None, description="Dirección de entrega, si aplica")
    notes: Optional[str] = Field(None, description="Notas adicionales del pedido")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Fecha de creación del pedido")

class OrderCreate(OrderBase):
    """Modelo para crear un nuevo pedido (mismos campos que OrderBase)."""
    pass

class OrderUpdate(BaseModel):
    """Modelo para actualizar un pedido (todos los campos opcionales)."""
    user_id: Optional[str] = None
    product: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    status: Optional[DeliveryMethod] = None
    payment_status: Optional[PaymentMethod] = None
    address: Optional[str] = None
    notes: Optional[str] = None
