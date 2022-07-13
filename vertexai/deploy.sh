PROJECT_ID=$(gcloud config list --format 'value(core.project)')

# Build docker image with cloudbuild
gcloud builds submit --config cloudbuild.yaml --machine-type=e2-highcpu-8 .

# Submit training job to VertexAI
python deploy.py -v \
    --project_id=$PROJECT_ID \
    --display_name="river-online-ml-training-job" \
    --container_image_uri="eu.gcr.io/$PROJECT_ID/river-online-ml/vertexai/trainer:latest" \
    --location="europe-west1"