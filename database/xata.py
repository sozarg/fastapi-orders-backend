import os
from xata import XataClient
from config import settings

xata_client = XataClient(api_key=settings.XATA_API_KEY, base_url=settings.XATA_BASE_URL)
