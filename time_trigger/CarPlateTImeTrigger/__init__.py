import datetime
import logging
import uuid

import azure.functions as func

from azure.cosmos import CosmosClient

from azure.servicebus import ServiceBusClient, ServiceBusMessage
import base64
import json
from .vision_utils import get_plates
import os

CONNECTION_STR = os.environ["CONNECTION_STR"]
QUEUE_NAME = os.environ["QUEUE_NAME"]

endpoint = os.environ["endpoint"]
key = os.environ["key"]


# <create_cosmos_client>
client = CosmosClient(endpoint, key)
# </create_cosmos_client>

database_name = 'CarLocations'
database = client.get_database_client(database_name)

container_name = 'Plates'
container = database.get_container_client(container_name)

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('Start processing queue of images.\n')
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
    
        msg_list = []
        
        with servicebus_client:
            receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=5)
            with receiver:
                for msg in receiver:
                    msg_list.append(json.loads(str(msg)))
                    receiver.complete_message(msg)

        results = []
        for msg in msg_list:
            row = {}
            row['plates'] = get_plates(base64.b64decode(msg["img_bytes"]))
            print(msg["camera_id"])
            print(msg["time"])
            print(row['plates'])
            logging.info("Processing image")
            logging.info(str(row['plates']))

            results.append(msg)

            row['id'] = str(uuid.uuid4())
            row["camera_id"] = msg["camera_id"]
            row["time"] = msg["time"]
            row["img"] = msg["img_bytes"]

            container.create_item(body=row)



    logging.info('Python timer trigger function ran at %s', utc_timestamp)
