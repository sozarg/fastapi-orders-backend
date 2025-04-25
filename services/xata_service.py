from xata.client import XataClient
import os

class XataService:
    def __init__(self):
        self.client = XataClient(
            api_key=os.getenv("XATA_API_KEY"),
            workspace_id=os.getenv("XATA_WORKSPACE_ID"),
            db_name=os.getenv("XATA_DB_NAME"),
            branch_name=os.getenv("XATA_BRANCH", "main"),
            region=os.getenv("XATA_REGION", "us-west-2")
        )

    def insert_order(self, order_data: dict):
        response = self.client.records().insert("orders", order_data)
        return response

    def get_all_orders(self):
        response = self.client.data().query("orders", {
            "page": {
                "size": 100
            }
        })
        return response

    def get_order(self, order_id: str):
        response = self.client.records().get("orders", order_id)
        return response

    def update_order(self, order_id: str, order_data: dict):
        response = self.client.records().update("orders", order_id, order_data)
        return response

    def get_completed_orders(self):
        response = self.client.data().query(
            "orders",
            {
                "filter": {
                    "status": "Envío a domicilio"
                },
                "page": {
                    "size": 100
                }
            }
        )
        return response
