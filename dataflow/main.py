import logging
import argparse
import json

from datetime import datetime
from typing import Any, Dict, List

from apache_beam import DoFn, io, Pipeline, ParDo, Map, WindowInto
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.gcp.internal.clients import bigquery
import apache_beam.transforms.window as window

SCHEMA = {
    'fields': [{
        "name": "area_name", "type": "STRING", "mode": "NULLABLE"
    }, { 
        "name": "date", "type": "DATE", "mode": "NULLABLE"
    }, { 
        "name": "genre_name", "type": "STRING", "mode": "NULLABLE"
    }, { 
        "name": "is_holiday", "type": "BOOL", "mode": "NULLABLE"
    }, { 
        "name": "latitude", "type": "FLOAT", "mode": "NULLABLE"
    }, { 
        "name": "longitude", "type": "FLOAT", "mode": "NULLABLE"
    }, { 
        "name": "store_id", "type": "STRING", "mode": "NULLABLE"
    }, { 
        "name": "y", "type": "INT64", "mode": "NULLABLE"
    }, { 
        "name": "pubsub_timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"
    }]
}


class FromBytesToJSON(DoFn):
    def process(self, element):
        yield (
            json.loads(element)
        )


class AddTimestamp(DoFn):
    def process(self, element, publish_time=DoFn.TimestampParam):
        """Processes each windowed element by extracting the message body and its
        publish time into a tuple.
        """
        element["pubsub_timestamp"] = datetime.utcfromtimestamp(float(publish_time)).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )
        logging.info(type(element))
        yield (
            element
        )


def log_msg(msg):
    try:
        logging.info(f'msg is {msg}')
    except ValueError:
        logging.info("Parsed: %s", msg)
    return msg


def parse_json_message(message: str) -> Dict[str, Any]:
    """Parse the input json message and add 'score' & 'processing_time' keys."""
    return json.loads(message)


def run(
    input_subscription: str,
    output_table: str,
    window_interval_sec: str,
    pipeline_args: List[str] = None
    ) -> None:
    """Build and run the pipeline."""

    # Set `save_main_session` to True so DoFns can access globally imported modules.
    pipeline_options = PipelineOptions(
        pipeline_args, streaming=True, save_main_session=True
    )

    with Pipeline(options=pipeline_options) as pipeline:
        messages = (
            pipeline
            | "Read from Pub/Sub" >> io.ReadFromPubSub(
                subscription=input_subscription
            ).with_output_types(bytes)
            | "UTF-8 bytes to string" >> Map(lambda msg: msg.decode("utf-8"))
            #| "Parse JSON messages" >> Map(parse_json_message)
            | "Parse JSON messages" >> ParDo(FromBytesToJSON())
            | "AddTimestamp" >> ParDo(AddTimestamp())
            | "Log Message" >> Map(log_msg)
            | "Fixed-size windows" >> WindowInto(window.FixedWindows(window_interval_sec, 0))
        )

        # Output the results into BigQuery table.
        _ = messages | "Write to Big Query" >> io.WriteToBigQuery(
            known_args.output_table,
            schema=SCHEMA,
            write_disposition=io.BigQueryDisposition.WRITE_APPEND,
        )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_subscription",
        type=str,
        help='Input PubSub subscription of the form "projects/<PROJECT>/subscriptions/<SUBSCRIPTION>."',
    )
    parser.add_argument(
        "--output_table",
        type=str,
        help="Output BigQuery Table"
    )
    parser.add_argument(
        "--window_interval_sec",
        default=60,
        type=int,
        help="Window interval in seconds for grouping incoming messages.",
    )
    known_args, pipeline_args = parser.parse_known_args()

    run(
        known_args.input_subscription,
        known_args.output_table,
        known_args.window_interval_sec,
        pipeline_args,
    )