from __future__ import print_function

import json
import pika

from simulator import consts
from simulator import pvsimulator


def consume(connection_params, file_name, start, freq):
    """Consumer for messages from consts.QUEUE_NAME.
    All consumed messages are written into the file with
    "file_name" along with simulated PV value for the same
    timestamp.

    :param connection_params: pika.ConnectionParameters for RabbitMQ
    :param file_name: str. Output file for results.
    :param start: datetime. First timestamp to be written to file
    :param freq: str. Sampling frequency in format %ds (e.g. "2s", "3s")
    :return: nothing. The result is written to the output file
    """

    print('Generating PV data')
    data = pvsimulator.get_perfect_voltage_for_a_day(start, freq)
    print('Generating is finished. Start consuming')

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue=consts.QUEUE_NAME)
    fd = open(file_name, 'w')

    def callback(ch, method, properties, body):
        msg = json.loads(body)
        if msg['value'] == consts.STOP_MSG:
            channel.stop_consuming()
            print("Please find the result in " + file_name)
            return
        timestamp = msg['timestamp']
        value = msg['value']
        pv_value = data[timestamp]

        fd.write(timestamp + ' ' + str(value) + ' ' + str(pv_value) + ' ' +
                 str(value + pv_value) + '\n')

    channel.basic_consume(callback,
                          queue=consts.QUEUE_NAME,
                          no_ack=True)
    channel.start_consuming()
    connection.close()
    fd.close()
