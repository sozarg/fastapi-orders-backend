from enum import Enum

class DeliveryMethod(str, Enum):
    """Métodos de entrega disponibles para los pedidos."""
    IN_PERSON = "Retira en persona"
    DELIVERY = "Envío a domicilio"
    POST_OFFICE = "Retiro en correo"
    UNSURE = "No estoy seguro"

class PaymentMethod(str, Enum):
    """Métodos de pago o canales de venta para los pedidos."""
    INSTAGRAM = "Instagram"
    WHATSAPP = "Whatsapp"
    MERCADOLIBRE = "Mercadolibre"
    ONLINE_STORE = "Tienda online"
