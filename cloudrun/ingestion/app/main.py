import os
import logging
import flask
import json
import base64
import datetime
import urllib
import google.auth.transport.requests
import google.oauth2.id_token
from six.moves import http_client
from google.cloud import bigquery
from flask import Flask, request, jsonify
from utils import write_to_bq
import urllib
import google.auth.transport.requests
import google.oauth2.id_token

logging.basicConfig(format='%(asctime)s %(levelname)-8s:%(message)s', 
                    level=logging.DEBUG, 
                    datefmt='%Y-%m-%d %H:%M:%S') 
logger = logging.getLogger()

# Set urls for make_authorized_get_request to authenticate with google-auth
ENDPOINT="https://river-online-ml-api-axswvbmypa-ew.a.run.app/predict"
AUDIENCE="https://river-online-ml-api-axswvbmypa-ew.a.run.app"

# Set GCP specific variables
PROJECT_ID = os.environ["PROJECT_ID"]
BQ_TABLE_ID = f"{PROJECT_ID}.river.river_predictions"

# Set clients
BIGQUERY_CLIENT = bigquery.Client(
    project=PROJECT_ID
)

app = flask.Flask(__name__)


def make_authorized_get_request(endpoint, audience, data):
    """
    make_authorized_get_request makes a POST request to the specified HTTP endpoint
    by authenticating with the ID token obtained from the google-auth client library
    using the specified audience value.
    """

    # Cloud Run uses your service's hostname as the `audience` value
    # audience = 'https://my-cloud-run-service.run.app/'
    # For Cloud Run, `endpoint` is the URL (hostname + path) receiving the request
    # endpoint = 'https://my-cloud-run-service.run.app/my/awesome/url'

    data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data)

    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)

    req.add_header("Authorization", f"Bearer {id_token}")
    req.add_header("Content-Type", "application/json")

    response = urllib.request.urlopen(req).read().decode('UTF-8')

    return json.loads(response)

@app.route('/api/health_check', methods=['GET'])
def health_check():
    resp = flask.jsonify(success=True)
    return resp

@app.route("/", methods=["POST"])
def index():
    """ Main entrypoint to the API """

    envelope = flask.request.get_json()
    if not envelope:
        msg = "No Pub/Sub message received"
        logger.error(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict):
        msg = f"Invalid Pub/Sub message format {envelope}, {type(envelope)}"
        logger.error(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    logger.info(f"Received envelope with message")
    pubsub_message = envelope["message"]

    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        try:
            logger.info("Decoding message")
            
            if 'publishTime' not in pubsub_message:
                pubsub_message['publishTime'] = datetime.datetime.now()
            
            logger.info(f"Message was published at {pubsub_message['publishTime']}")

            message = json.loads(base64.b64decode(pubsub_message["data"]).decode("utf-8").strip())
            
            logger.info(f"Message: {message}")
        except Exception as e:
            msg = (
                "Invalid Pub/Sub message: "
                "features property is not valid base64 encoded JSON"
                )
            logger.info(f"error: {e}")
            return f"Bad Request: {msg}", 400
    else:
        msg = f"Invalid Pub/Sub message format when decoding message {pubsub_message}, {type(pubsub_message)}"
        logger.error(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    # Call river ml api
    prediction = make_authorized_get_request(
        endpoint=ENDPOINT,
        audience=AUDIENCE,
        data=message)

    logger.info(f"River API response: {prediction}")

    logger.info("Preparing to send data to BigQuery")
    row = message["features"]
    row["y"] = prediction["prediction"]
    row["pubsub_timestamp"] = str(pubsub_message['publishTime'])

    write_to_bq(BQ_TABLE_ID, BIGQUERY_CLIENT, [row])

    logger.info("Sending to third party API")
    logger.info("Received code 201")
    
    return flask.jsonify(success=True)

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
    # This is used when running locally. Gunicorn is used to run the
    # application on Google Cloud Run. See entrypoint in Dockerfile.
    app.run(host='127.0.0.1', port=int(os.environ.get("PORT", 8080)), debug=True)
