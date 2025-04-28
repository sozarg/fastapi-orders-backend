import os
import logging
from xata.client import XataClient

logger = logging.getLogger(__name__)

required_env_vars = ["XATA_API_KEY", "XATA_WORKSPACE_ID", "XATA_DB_NAME"]
for var in required_env_vars:
    if not os.getenv(var):
        logger.error(f"Missing environment variable: {var}")
        raise Exception(f"Missing environment variable: {var}")

try:
    xata = XataClient(
        api_key=os.getenv("XATA_API_KEY"),
        workspace_id=os.getenv("XATA_WORKSPACE_ID"),
        db_name=os.getenv("XATA_DB_NAME"),
        branch_name=os.getenv("XATA_BRANCH", "main"),
        region=os.getenv("XATA_REGION", "us-west-2")
    )
    logger.info("Xata client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Xata client: {e}")
    raise