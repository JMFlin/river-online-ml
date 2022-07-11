import os
import logging
import flask
import river
from six.moves import http_client
from google.cloud import storage
from flask import Flask, request, jsonify

logging.basicConfig(format='%(asctime)s %(levelname)-8s:%(message)s', 
                    level=logging.DEBUG, 
                    datefmt='%Y-%m-%d %H:%M:%S') 
logger = logging.getLogger()

MODEL_BUCKET="river-online-ml-models"

app = flask.Flask(__name__)

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your GCS object
    # source_blob_name = "storage-object-name"

    # The path to which the file should be downloaded
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    logging.info(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name
        )
    )

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    logging.info(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )


def load_model():
    with open('model.pkl', 'rb') as f:
       model = pickle.load(f)
    return model

def save_model(model):
    with open('model.pkl', 'wb') as f:
       pickle.dump(model, f)


@app.route('/api/health_check', methods=['GET'])
def health_check():
    resp = flask.jsonify(success=True)
    return resp

@app.route("/predict", methods=["GET"])
def predict():
    """ Get a prediction from the river model """
    payload = flask.request.args.to_dict()
    logger.info(f"Received payload {payload['area_name']}")

    download_blob(
        bucket_name=MODEL_BUCKET,
        source_file_name="model.pkl",
        destination_file_name="model.pkl")

    river_model = load_model()
    return river_model.predict_proba_one(payload)

@app.route('/learn', methods=['POST'])
def learn():
    """ A model can be updated whenever a request arrives """
    
    payload = flask.request.get_json()
    logger.info(f"Received payload {payload}")

    download_blob(
        bucket_name=MODEL_BUCKET,
        source_blob_name="model.pkl",
        destination_file_name="model.pkl")

    river_model = load_model()
    river_model.learn_one(payload['features'], payload['target'])

    save_model(model=river_model)
    upload_blob(
        bucket_name=MODEL_BUCKET,
        source_file_name="model.pkl",
        destination_blob_name="model.pkl")

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
    # This is used when running locally. Gunicorn is used to run the
    # application on Google Cloud Run. See entrypoint in Dockerfile.
    app.run(host='127.0.0.1', port=int(os.environ.get("PORT", 8080)), debug=True)
