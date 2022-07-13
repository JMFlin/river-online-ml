PROJECT_ID=$(gcloud config list --format 'value(core.project)')

#python main.py \
#    --streaming \
#    --input_subscription projects/$PROJECT_ID/subscriptions/river-online-ml-subscription \
#    --output_table $PROJECT_ID:river.river_predictions \
#    --window_interval_sec 60

python main.py \
    --streaming \
    --runner DataflowRunner \
    --project $PROJECT_ID \
    --region europe-west1 \
    --temp_location gs://river-online-ml-dataflow/ \
    --job_name river-online-ml-dataflow \
    --max_num_workers 2 \
    --subnetwork https://www.googleapis.com/compute/v1/projects/$PROJECT_ID/regions/europe-west1/subnetworks/default \
    --parameters \
        --input_subscription projects/$PROJECT_ID/subscriptions/river-online-ml-subscription \
        --output_table $PROJECT_ID:river.river_predictions

