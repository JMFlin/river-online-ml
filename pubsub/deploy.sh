(
   gcloud pubsub topics create river-online-ml-topic
) &
(
gcloud pubsub subscriptions create river-online-ml-subscriptions \
   --topic river-online-ml-topic \
   --push-endpoint=INSERT_CLOUDRUN_URL_HERE \
   --push-auth-service-account=cloud-run-pubsub-invoker@$PROJECT_ID.iam.gserviceaccount.com \
   --ack-deadline 70 \
   --expiration-period never \
   --message-retention-duration 15m \
   --max-retry-delay 10 \
   --min-retry-delay 5
) &