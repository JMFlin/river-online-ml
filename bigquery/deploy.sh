bq rm -f -t $PROJECT_ID:river.river_predictions

bq --location=EU mk -d \
 $PROJECT_ID:river

bq mk --table \
  --schema schema.json \
$PROJECT_ID:river.river_predictions
