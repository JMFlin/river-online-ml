def write_to_bq(client, table, row_to_insert): 
    """ Streaming insert a row to q BigQuery table """
    errors = client.insert_rows_json(table, row_to_insert)
    if errors == []:
        logger.info("Added new row to BQ")
    else:
        logger.error("Encountered errors while inserting rows: {}".format(errors))

def validate_message(message, param):
    """ Validate and return variables from pubsub messages """
    var = message.get(param)
    if not var:
        raise ValueError(
            "{} is not provided. Make sure you have \
                          property {} in the request".format(
                param, param
            )
        )
    return var