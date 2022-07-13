from river import datasets
from river import compose
from river import evaluate
from river import feature_extraction
from river import linear_model
from river import model_selection
from river import metrics
from river import preprocessing
from river import stats
from river import optim
from model_utils import get_date_features

import numbers
from google.cloud import storage
from typing import Union, List
import os, logging, json, pickle, argparse, datetime

MODEL_BUCKET="river-online-ml-models"
STORAGE_CLIENT = storage.Client()

# https://cloud.google.com/vertex-ai/docs/training/create-custom-job
# https://codelabs.developers.google.com/codelabs/vertex-ai-custom-code-training#3
# https://cloud.google.com/ai-platform/training/docs/training-scikit-learn#cloud-shell

# feature selection.  The FEATURE list defines what features are needed from the training data.
# as well as the types of those features. We will perform different feature engineering depending on the type

# List all column names for binary features: 0,1 or True,False or Male,Female etc
BINARY_FEATURES = [
    'is_holiday']

# List all column names for numeric features
NUMERIC_FEATURES = [
    'latitude',
    'longitude']

# List all column names for categorical features 
CATEGORICAL_FEATURES = [
    'area_name',
    'genre_name',
    'store_id']

# List all column names to discard from the model
DISCARD = [
    'date']

# Clean missing numerics: https://riverml.xyz/0.11.1/api/preprocessing/StatImputer/
# Model selection: https://riverml.xyz/0.11.1/api/model-selection/EpsilonGreedyRegressor/
# Train: https://riverml.xyz/0.11.1/api/evaluate/progressive-val-score/
# Others: https://riverml.xyz/0.11.1/api/compose/TransformerUnion/


def upload_blob(client, bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    logging.info(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

def save_model(model):
    with open('model.pkl', 'wb') as f:
       pickle.dump(model, f)

def run():

    models = [
        linear_model.LinearRegression(optimizer=optim.SGD(lr=lr))
        for lr in [0.0001, 0.001, 1e-05, 0.01]
    ]

    model = get_date_features

    for n in [7, 14, 21]:
        model += feature_extraction.TargetAgg(by='store_id', how=stats.RollingMean(n))

    num = compose.SelectType(numbers.Number) | preprocessing.StandardScaler()
    cat = compose.SelectType(str) | preprocessing.OneHotEncoder()

    model |= compose.Discard(*DISCARD)
    model |= (num + cat)
    model |= preprocessing.StandardScaler()
    model |= model_selection.EpsilonGreedyRegressor(
                models,
                epsilon=0.1,
                decay=0.001,
                burn_in=100,
                seed=1
            )

    logging.info(model)

    evaluate.progressive_val_score(
        dataset=datasets.Restaurants(),
        model=model,
        metric=metrics.MAE(),
        print_every=1000
    )

    logging.info("Saving model and artifacts")
    save_model(model)
    upload_blob(
        client=STORAGE_CLIENT,
        bucket_name=MODEL_BUCKET,
        source_file_name="model.pkl",
        destination_blob_name="model.pkl")


# Define all the command line arguments your model can accept for training
if __name__ == '__main__':

    ''' 
    Vertex AI automatically populates a set of environment variables in the container that executes 
    your training job. those variables include:
        * AIP_MODEL_DIR - Directory selected as model dir
        * AIP_DATA_FORMAT - Type of dataset selected for training (can be csv or bigquery)
    
    Vertex AI will automatically split selected dataset into training,validation and testing
    and 3 more environment variables will reflect the location of the data:
        * AIP_TRAINING_DATA_URI - URI of Training data
        * AIP_VALIDATION_DATA_URI - URI of Validation data
        * AIP_TEST_DATA_URI - URI of Test data
        
    Notice that those environment variables are default. If the user provides a value using CLI argument,
    the environment variable will be ignored. If the user does not provide anything as CLI  argument
    the program will try and use the environment variables if those exist. Otherwise will leave empty.
    '''
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")

    args = parser.parse_args()
    arguments = args.__dict__

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
        
        
    logging.info('Model artifacts will be exported here: {}'.format(MODEL_BUCKET))

    logging.info('Training job starting...')

    run()

    logging.info('Training job completed. Exiting...')