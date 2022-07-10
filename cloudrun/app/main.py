import logging
import flask
import river
from six.moves import http_client

logging.basicConfig(format='%(asctime)s %(levelname)-8s:%(message)s', 
                    level=logging.DEBUG, 
                    datefmt='%Y-%m-%d %H:%M:%S') 
logger = logging.getLogger()


app = flask.Flask(__name__)

def _validate_message(message, param):
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

@app.route("/", methods=["GET"])
def predict():
    """ Get a prediction from the river model """
    payload = flask.request.json
    river_model = load_model()
    return river_model.predict_proba_one(payload)

@app.route('/', methods=['POST'])
def learn():
    """ A model can be updated whenever a request arrives """
    payload = flask.request.json
    river_model = load_model()
    river_model.learn_one(payload['features'], payload['target'])
    return {}, 201

@app.errorhandler(http_client.INTERNAL_SERVER_ERROR)
def unexpected_error(e):
    """Handle exceptions by returning swagger-compliant json."""
    logging.exception('An error occured while processing the request.')
    response = flask.jsonify({
        'code': http_client.INTERNAL_SERVER_ERROR,
        'message': 'Exception: {}'.format(e)})
    response.status_code = http_client.INTERNAL_SERVER_ERROR
    return response


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google Cloud Run. See entrypoint in Dockerfile.
    app.run(host='127.0.0.1', port=int(os.environ.get("PORT", 8080)), debug=True)
