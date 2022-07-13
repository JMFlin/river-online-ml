# River online-ml on GCP
Example of using and deploying river to gcp for streaming data. The River API is hosted on Cloud Run and it can be called with a GET to get the prediction and POST to train the model incrementally.

### Architecture
The flow is divided so that a message gets published to Pub/Sub where it is pushed to Cloud Run for processing. This Cloud Run container then calls an API also hosted on Cloud Run for predictions for the incoming message data. The data and prediction get saved to a BigQuery table and sent forward to a third party API.

A custom container is built with Cloud Build for the river model training and the job gets deployed on Vertex AI Custom Jobs to train an initial River model on available data. The model is then saved to Cloud Storage, where a custom container deployed to Cloud Run fetches the model for prediction and incremental learning.

![Alt text](/docs/img/architecture.svg "GCP Architecture")