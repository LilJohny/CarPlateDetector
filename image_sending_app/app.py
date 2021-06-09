from flask import Flask, request, render_template
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import json
import os

CONNECTION_STR = os.environ["CONNECTION_STR"]
QUEUE_NAME = os.environ["QUEUE_NAME"]

servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)

app = Flask(__name__)


def send_single_message(sender, msg):
    message = ServiceBusMessage(msg)
    sender.send_messages(message)


@app.route("/")
def main_page():
    return {"status": 200}


@app.route('/send_image', methods=['POST'])
def send_message():
    res = request.json
    img_bytes = res['img_bytes']
    cam_id = res['camera_id']
    cur_time = res['time']

    with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        with sender:
            send_single_message(sender, json.dumps({"img_bytes": img_bytes, "camera_id": cam_id, "time": cur_time}))

    return {"status": 200}


if __name__ == '__main__':
    app.run()
