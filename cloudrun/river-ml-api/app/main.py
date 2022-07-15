import os
import sys
import logging
import flask
import river
import pickle
import datetime
import signal

from model_utils import get_date_features
from utils import download_blob, upload_blob, load_model, save_model
from model_utils import get_date_features

from six.moves import http_client
from google.cloud import storage
from flask import Flask, request, jsonify
from types import FrameType
from google.auth import jwt

# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/3558b7caac0b8bc03f785c47a120437a686f4ad8/run/idp-sql/main.py

logging.basicConfig(format='%(asctime)s %(levelname)-8s:%(message)s', 
                    level=logging.DEBUG, 
                    datefmt='%Y-%m-%d %H:%M:%S') 
logger = logging.getLogger()

MODEL_BUCKET="river-online-ml-models"

STORAGE_CLIENT = storage.Client()

app = flask.Flask(__name__)


def receive_authorized_post_request(request):
    """
    receive_authorized_post_request takes the "Authorization" header from a
    request, decodes it using the google-auth client library, and returns
    back the email from the header to the caller.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header:

        # split the auth type and value from the header.
        auth_type, creds = auth_header.split(" ", 1)

        if auth_type.lower() == "bearer":
            claims = jwt.decode(creds, verify=False)
            logger.info(f"Hello, {claims['email']}!\n")
            return 200

        else:
            logger.error(f"Unhandled header format ({auth_type}).\n")
            return 400
    return 400


def shutdown_handler(signal: int, frame: FrameType) -> None:
    """ Upload model to cloud storage on shutdown """
    logger.info("Signal received, safely shutting down")
    upload_blob(
        client=STORAGE_CLIENT,
        bucket_name=MODEL_BUCKET,
        source_file_name="model.pkl",
        destination_blob_name="model.pkl")
    logger.info("Exiting process")
    sys.exit(0)


@app.before_first_request
def download_model() -> None:
    """ We need to download the model before the request """
    download_blob(
        client=STORAGE_CLIENT,
        bucket_name=MODEL_BUCKET,
        source_blob_name="model.pkl",
        destination_file_name="model.pkl")

@app.route('/api/health_check', methods=['GET'])
def health_check():
    resp = flask.jsonify(success=True)
    return resp

@app.route("/predict", methods=["POST"])
def predict():
    """ Get a prediction from the river model """
    
    if receive_authorized_post_request(request) == 400:
        return {}, 400

    payload = flask.request.get_json()
    logger.info(f"Received payload {type(payload)} {payload}")

    features = payload["features"]

    river_model = load_model()
    features["date"] = datetime.datetime.strptime(features["date"], '%Y-%m-%d %H:%M:%S')

    pred = river_model.predict_one(features)
    logger.info(f"Predicted value is {pred}")

    return jsonify({'prediction': pred}), 201

@app.route('/learn', methods=['POST'])
def learn():
    """ A model can be updated whenever a request arrives """
    
    if receive_authorized_post_request(request) == 400:
        return {}, 400

    payload = flask.request.get_json()
    logger.info(f"Received payload {type(payload)} {payload}")

    river_model = load_model()
    payload["features"]["date"] = datetime.datetime.strptime(payload["features"]["date"], '%Y-%m-%d %H:%M:%S')
    river_model.learn_one(payload['features'], payload["target"])

    logger.info(f"Successfully learned from payload")

    save_model(model=river_model)

    return {}, 201


@app.errorhandler(http_client.INTERNAL_SERVER_ERROR)
def unexpected_error(e):
    """Handle exceptions by returning swagger-compliant json."""
    logging.exception('An error occurred while processing the request.')
    response = flask.jsonify({
        'code': http_client.INTERNAL_SERVER_ERROR,
        'message': 'Exception: {}'.format(e)})
    response.status_code = http_client.INTERNAL_SERVER_ERROR
    return response


if __name__ == '__main__':
    # This is used when running locally.

    # Handles Ctrl-C locally
    signal.signal(signal.SIGINT, shutdown_handler)

    # Run app locally
    app.run(host='127.0.0.1', port=int(os.environ.get("PORT", 8080)), debug=True)
else:
    # Gunicorn is used to run the application on Google Cloud Run.
    # See entrypoint in Dockerfile.

    # Handles Cloud Run container termination
    signal.signal(signal.SIGTERM, shutdown_handler)
