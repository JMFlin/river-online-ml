gcloud builds submit --config cloudbuild.yaml --machine-type=e2-highcpu-8 .

gcloud run deploy river-online-ml-ingestion \
	--cpu 1 \
	--memory 2Gi \
	--image eu.gcr.io/$PROJECT_ID/river-online-ml/cloud-run/ingestion:latest \
	--concurrency 1 \
	--ingress internal \
	--no-allow-unauthenticated \
	--max-instances 5 \
	--min-instances 0 \
	--platform managed \
	--timeout 600 \
	--region europe-west1 \
	--port 5000 
