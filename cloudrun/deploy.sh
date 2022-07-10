(
gcloud run deploy river-online-ml-api \
	--cpu 1 \
	--memory 2Gi \
	--image eu.gcr.io/$PROJECT_ID/river-online-ml/cloud-run/model-api:latest \
	--concurrency 1 \
	--ingress internal \
	--max-instances 5 \
	--min-instances 0 \
	--platform managed \
	--service-account \
	--timeout 600 \
	--region europe-west1 \
	--port 5000 
) &
