# https://cloud.google.com/api-gateway/docs/get-started-cloud-run

gcloud services enable apigateway.googleapis.com
gcloud services enable servicemanagement.googleapis.com
gcloud services enable servicecontrol.googleapis.com

PROJECT_ID=$(gcloud config list --format 'value(core.project)')
USER_EMAIL=$(gcloud config list account --format "value(core.account)")
TOKEN=$(gcloud auth print-identity-token)

gcloud api-gateway api-configs create river-online-ml-api-config \
  --api=river-online-ml-api --openapi-spec=openapi2-run.yaml \
  --project=$PROJECT_ID --backend-auth-service-account=api-gateway-backend-auth-sa@$PROJECT_ID.iam.gserviceaccount.com

gcloud api-gateway api-configs describe river-online-ml-api-config \
  --api=river-online-ml-api --project=$PROJECT_ID


gcloud api-gateway gateways create river-online-ml-gateway \
  --api=river-online-ml-api --api-config=river-online-ml-api-config \
  --location=europe-west1 --project=$PROJECT_ID

gcloud api-gateway gateways describe river-online-ml-gateway \
  --location=europe-west1 --project=$PROJECT_ID

gcloud run services add-iam-policy-binding river-online-ml-api \
  --member="user:${USER_EMAIL}" \
  --role='roles/run.invoker' \
  --region=europe-west1

curl -H "Authorization: Bearer $TOKEN" \
    https://river-online-ml-api-axswvbmypa-ew.a.run.app/api/health_check