#!/usr/bin/env python3
import time
import datetime
import numpy as np
import boto3
from dlr import DLRModel
import greengrasssdk
import PIL.Image

mqtt_client = greengrasssdk.client('iot-data')
model_resource_path =  ('/ml_model')
dlr_model = DLRModel(model_resource_path, 'gpu')

cloudwatch = boto3.client('cloudwatch')
prev_class = -1

dino_names = [
    'Spinosaurus',
    'Dilophosaurus',
    'Stegosaurus',
    'Triceratops',
    'Brachiosaurus',
    'Unknown']

def push_to_cloudwatch(name, value):
    try:
        response = cloudwatch.put_metric_data(
            Namespace='dino-detect',
            MetricData=[
                {
                    'MetricName': name,
                    'Value': value,
                    'Unit': 'Percent'
                },
            ]
        )
        #print("Metric pushed: {}".format(response))
    except Exception as e:
        print("Unable to push to cloudwatch\n e: {}".format(e))
        return True

def predict(change):
    img = change['new'] 
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.asarray(img)
    img = np.rollaxis(img, axis=2, start=0)[np.newaxis,:]
    flattened_data = img.astype(np.float32)

    prediction_scores = dlr_model.run({'data' : flattened_data})
    max_score_id = np.argmax(prediction_scores)
    max_score = np.max(prediction_scores)
    print(max_score_id)
    return max_score, max_score_id

def send_mqtt_message(message):
    mqtt_client.publish(topic='dino-detect',
                        payload=message)

file_name = "/test.jpg"
# test image
image = PIL.Image.open(file_name)
image = np.asarray(image.resize((224, 224)))

# Normalize
mean_vec = np.array([0.485, 0.456, 0.406])
stddev_vec = np.array([0.229, 0.224, 0.225])
image = (image/255- mean_vec)/stddev_vec

# Transpose
if len(image.shape) == 2:  # for greyscale image
    image = np.expand_dims(image, axis=2)
    
image = np.rollaxis(image, axis=2, start=0)[np.newaxis, :]

while True:
    probs, classes = predict(image) 
    msg = "Start..."
    s3url = ""
    if probs > 0.6 and prev_class != classes:
        prev_class = classes
        if classes == 5:
            msg = '{"dinosaur":"unknown"' + ',"confidence":"' + str(probs) +'","url":"'+ s3url +'"}'
        else:
            msg = '{"dinosaur":"' + dino_names[classes] + '"' + ',"confidence":"' + str(probs) +'"}'
        print(msg)
        send_mqtt_message(msg)
        push_to_cloudwatch(dino_names[classes], round(probs.item(), 2))

# The lambda to be invoked in Greengrass
def handler(event, context):
    pass
