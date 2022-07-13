#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import subprocess
import datetime
import logging
import json
import base64
import subprocess
from google.cloud import pubsub_v1

PROJECT_ID = subprocess.run(["gcloud", "config", "get-value", "project"],
                            stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip("\n")
PUBSUBS_TOPIC = "river-online-ml-topic"

logger = logging.getLogger()
logger.info(f"Starting process")

def publish_to_topic(topic, message):
    """ Publish message to topic """

    logger.info(f"Preparing to publish to {topic} topic")

    # Construct a PubSub client object.
    publisher_client = pubsub_v1.PublisherClient()

    futures = []
    
    message_data = json.dumps(message).encode("utf-8")
    topic_path = publisher_client.topic_path(PROJECT_ID, topic)
    
    try:
        future = publisher_client.publish(topic_path, data=message_data)
        
        logger.info(f"Message publish to {topic} topic")

        futures.append(future)

        for future in futures:
            future.result()
        return 'Message published.'
    except Exception as e:
        logger.error(e)
        return (e, 500)


message = {
    'features': 
        {
        'area_name': 'Tōkyō-to Nerima-ku Toyotamakita',
        'date': '2016-01-01 00:00:00',
        'genre_name': 'Izakaya',
        'is_holiday': True,
        'latitude': 35.7356234,
        'longitude': 139.6516577,
        'store_id': 'air_04341b588bde96cd'
        }
    }

publish_to_topic(PUBSUBS_TOPIC, message)
