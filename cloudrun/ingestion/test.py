#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
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
    "area_name": "1", 
    "date": "2022-01-01",
    "genre_name": "1",
    "is_holiday": True,
    "latitude": 1.0,
    "longitude": 1.0,
    "store_id": "1",
    "y": 1
}

publish_to_topic(PUBSUBS_TOPIC, message)