from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time
import io
import logging
import os

'''
Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key = os.environ["vision_sub_key"]
endpoint = os.environ["endpoint_vision"]

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


def get_plates(img_bytes_value):
    # img_bytes_value - buf.getvalue()

    byte_im = io.BytesIO(img_bytes_value)

    read_response = computervision_client.read_in_stream(byte_im,  raw=True)

    read_operation_location = read_response.headers["Operation-Location"]

    operation_id = read_operation_location.split("/")[-1]

    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    licences = []

    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                licences.append(line.text)
    return licences
