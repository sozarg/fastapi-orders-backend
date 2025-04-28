import os
from xata import XataClient
from config import settings

xata_client = XataClient(api_key=settings.XATA_API_KEY)
