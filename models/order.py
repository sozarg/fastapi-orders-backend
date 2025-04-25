from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class DeliveryMethod(str, Enum):
    IN_PERSON = "Retira en persona"
    DELIVERY = "Envío a domicilio"
    POST_OFFICE = "Retiro en correo"
    UNSURE = "No estoy seguro"

class PaymentMethod(str, Enum):
    INSTAGRAM = "Instagram"
    WHATSAPP = "Whatsapp"
    MERCADOLIBRE = "Mercadolibre"
    ONLINE_STORE = "Tienda online"

class OrderBase(BaseModel):
    user_id: str = Field(..., description="Nombre de la persona")
    product: str = Field(..., description="Nombre del producto")
    price: float = Field(..., gt=0, description="Precio del producto")
    status: Optional[DeliveryMethod] = Field(None, description="Método de entrega")
    payment_status: Optional[PaymentMethod] = Field(None, description="Medio de pago")
    address: Optional[str] = Field(None, description="Dirección de entrega")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Fecha de creación")

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    user_id: Optional[str] = None
    product: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    status: Optional[DeliveryMethod] = None
    payment_status: Optional[PaymentMethod] = None
    address: Optional[str] = None
    notes: Optional[str] = None
