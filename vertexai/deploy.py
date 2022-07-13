from google.cloud import aiplatform
import argparse
import logging

# https://cloud.google.com/vertex-ai/docs/training/create-custom-job#create_custom_job-python

def create_custom_job_sample(
    project: str,
    display_name: str,
    container_image_uri: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.JobServiceClient(client_options=client_options)
    custom_job = {
        "display_name": display_name,
        "job_spec": {
            "worker_pool_specs": [
                {
                    "machine_spec": {
                        "machine_type": "n1-standard-4",
                    },
                    "replica_count": 1,
                    "container_spec": {
                        "image_uri": container_image_uri,
                        "command": [],
                        "args": ["-v"],
                    },
                }
            ]
        },
    }
    parent = f"projects/{project}/locations/{location}"
    response = client.create_custom_job(parent=parent, custom_job=custom_job)
    print("response:", response)


parser = argparse.ArgumentParser()


parser.add_argument(
    '--project_id',
    help = 'GCP project id',
    type = str
)
parser.add_argument(
    '--display_name',
    help = 'Job display name',
    type = str
)
parser.add_argument(
    '--container_image_uri',
    help = 'Uri to container registry for image',
    type = str
)
parser.add_argument(
    '--location',
    help = 'location',
    type = str
)

parser.add_argument("-v", "--verbose", help="increase output verbosity",
                action="store_true")

args = parser.parse_args()
arguments = args.__dict__

if args.verbose:
    logging.basicConfig(level=logging.INFO)

create_custom_job_sample(
    project=arguments["project_id"],
    display_name=arguments["display_name"],
    container_image_uri=arguments["container_image_uri"],
    location=arguments["location"],
    api_endpoint=f'{arguments["location"]}-aiplatform.googleapis.com',
)