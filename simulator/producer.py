import datetime as dt
import json
import random

import pandas as pd
import pika

from simulator import consts


def produce(connection_params, start, freq):
    """Message producer into consts.QUEUE_NAME.
    Each message has a body containing a timestamp
    and a random value between 1 and 9000. This value
    simulates a real household consumption.

    :param connection_params: pika.ConnectionParameters for RabbitMQ
    :param start: datetime. First timestamp to be generated
    :param freq: str. Sampling frequency in format %ds (e.g. "2s", "3s")
    :return: nothing. Messages are sent to RabbitMQ
    """
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue=consts.QUEUE_NAME)

    time_range = pd.date_range(start=start, end=start + dt.timedelta(
        hours=23, minutes=59, seconds=59), freq=freq, tz="CET")
    for t in time_range:
        body = {'timestamp': str(t), 'value': random.randrange(1, 9000)}
        channel.basic_publish(exchange='', routing_key=consts.QUEUE_NAME,
                              body=json.dumps(body))

    channel.basic_publish(exchange='', routing_key=consts.QUEUE_NAME,
                          body=json.dumps({"value": consts.STOP_MSG}))
    connection.close()
