python -m apache_beam.examples.wordcount \
    --region DATAFLOW_REGION \
    --input gs://dataflow-samples/shakespeare/kinglear.txt \
    --output gs://STORAGE_BUCKET/results/outputs \
    --runner DataflowRunner \
    --project $PROJECT_ID \
    --temp_location gs://STORAGE_BUCKET/tmp/

# https://github.com/apache/beam/blob/master/sdks/python/apache_beam/examples/wordcount.py
# https://cloud.google.com/dataflow/docs/quickstarts/create-pipeline-python