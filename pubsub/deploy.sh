PROJECT_ID=$(gcloud config list --format 'value(core.project)')

gcloud iam service-accounts create cloud-run-pubsub-invoker \
     --display-name "Cloud Run Pub/Sub Invoker"

gcloud run services add-iam-policy-binding river-online-ml-ingestion \
   --member=serviceAccount:cloud-run-pubsub-invoker@$PROJECT_ID.iam.gserviceaccount.com \
   --region=europe-west1 \
   --role=roles/run.invoker

gcloud projects add-iam-policy-binding $PROJECT_ID \
   --member=serviceAccount:cloud-run-pubsub-invoker@$PROJECT_ID.iam.gserviceaccount.com \
   --role=roles/iam.serviceAccountTokenCreator \
   --condition=None

gcloud pubsub topics create river-online-ml-topic

gcloud pubsub subscriptions create river-online-ml-subscription \
   --topic river-online-ml-topic \
   --push-endpoint=https://river-online-ml-ingestion-axswvbmypa-ew.a.run.app \
   --push-auth-service-account=cloud-run-pubsub-invoker@$PROJECT_ID.iam.gserviceaccount.com \
   --ack-deadline 30 \
   --expiration-period never \
   --message-retention-duration 15m \
   --max-retry-delay 50 \
   --min-retry-delay 10
