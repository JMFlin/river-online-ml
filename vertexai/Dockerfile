# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the logs.
ENV PYTHONUNBUFFERED True

# Copy application dependency manifests to the container image.
# Copying this separately prevents re-running pip install on every code change.
COPY /trainer/*.* /trainer/

WORKDIR /trainer

# Install requirements
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "task.py" ]