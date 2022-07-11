import os
import logging
import flask
import json
import base64
from six.moves import http_client
from google.cloud import bigquery

logging.basicConfig(format='%(asctime)s %(levelname)-8s:%(message)s', 
                    level=logging.DEBUG, 
                    datefmt='%Y-%m-%d %H:%M:%S') 
logger = logging.getLogger()

BQ_TABLE_ID = "river.river_predictions"

BIGQUERY_CLIENT = bigquery.Client(
    project=os.environ["PROJECT_ID"]
)

app = flask.Flask(__name__)

def write_to_bq(row_to_insert): 

    errors = BIGQUERY_CLIENT.insert_rows_json(BQ_TABLE_ID, row_to_insert)
    if errors == []:
        return "Added new row to BQ."
    else:
        return "Encountered errors while inserting rows: {}".format(errors)

def validate_message(message, param):
    var = message.get(param)
    if not var:
        raise ValueError(
            "{} is not provided. Make sure you have \
                          property {} in the request".format(
                param, param
            )
        )
    return var

@app.route('/api/health_check', methods=['GET'])
def health_check():
    resp = flask.jsonify(success=True)
    return resp

@app.route("/", methods=["POST"])
def index():
    """  """

    envelope = flask.request.get_json()
    if not envelope:
        msg = "No Pub/Sub message received"
        logger.error(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = f"Invalid Pub/Sub message format {envelope}, {type(envelope)}"
        logger.error(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    logger.info(f"Received envelope with message")
    pubsub_message = envelope["message"]

    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        try:
            logger.info("Decoding message")
            logger.info(f"Message was published at {pubsub_message['publishTime']}")
            message = json.loads(base64.b64decode(pubsub_message["data"]).decode("utf-8").strip())
            logger.info(f"Message: {message}")
        except Exception as e:
            msg = (
                "Invalid Pub/Sub message: "
                "data property is not valid base64 encoded JSON"
                )
            logger.info(f"error: {e}")
            return f"Bad Request: {msg}", 400
    else:
        msg = f"Invalid Pub/Sub message format when decoding message {pubsub_message}, {type(pubsub_message)}"
        logger.error(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    # Call river ml api

    # Insert to bq

    # Send to others
    
    return ("", 204)

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
