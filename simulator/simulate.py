#!/usr/bin/env python
# encoding: utf-8

import argparse
import datetime as dt
import threading

import pika

from simulator import consumer
from simulator import producer
from simulator import consts

_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def main(start, output, frequency, host, port, vhost, username, password):
    """Main method for PV simulation.
    Simulation is started from "start" timestamp. Samples are generated every
    "frequency" seconds during the next 24 hours.
    There are several steps to be done:
    1. Produce random values into a RabbitMQ queue
    2. Consume these messages, generate PV simulated value for
       each of received messages' timestamps and write the result message into
       the "output" file
    These two processes are running in 2 separate threads.

    :param start: datetime. Starting point
    :param output: str. Output file for results
    :param frequency: int. Sampling frequency
    :param host: str. RabbitMQ host
    :param port: str. RabbitMQ port
    """

    frq = str(frequency) + 's'
    credentials = pika.PlainCredentials(username, password)
    params = pika.ConnectionParameters(host=host,
                                       port=port,
                                       virtual_host=vhost,
                                       credentials=credentials)
    clean_up(params)

    producer_thread = threading.Thread(target=producer.produce,
                                       args=(params, start, frq))
    producer_thread.start()

    consumer_thread = threading.Thread(target=consumer.consume,
                                       args=(params, output, start, frq))
    consumer_thread.start()


def clean_up(params):
    """
    In case the queue contains messages from previous runs, it is required to
    clean them up.

    :param params: pika.ConnectionParameters for RabbitMQ
    """
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=consts.QUEUE_NAME)
    channel.queue_purge(queue=consts.QUEUE_NAME)
    connection.close()


def valid_date(s):
    """
    Validate that the string can be converted into datetime with format
    _DATE_FORMAT.

    :param s: str. A string to be validated
    :return: datetime
    :raises: ArgumentTypeError if a string cannot be parsed
    """
    try:
        return dt.datetime.strptime(s, _DATE_FORMAT)
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def valid_file(f):
    """
    Validate that the file is writable.

    :param f: str. A file path
    :return: str. A file path
    :raises: ArgumentTypeError if the corresponding file is not writable
    """
    try:
        open(f, 'w')
        return f
    except IOError:
        msg = "Not a writable file"
        raise argparse.ArgumentTypeError(msg)


def valid_frq(i):
    """
    Validate that "i" can be used as a frequency.

    :param i: int or str. A number to be validated
    :return: int. Valid frequency
    :raises: ArgumentTypeError if the given number cannot be used as a
    frequency, i.e. if it is less than 1 or greater than 1 hour.
    """
    try:
        i = int(i)
    except ValueError:
        msg = "Cannot convert to int"
        raise argparse.ArgumentTypeError(msg)
    if i < 1 or i > 60 * 60:
        msg = "Not valid frequency"
        raise argparse.ArgumentTypeError(msg)
    return i


def init():
    parser = argparse.ArgumentParser(description="PVSimulator for 1 day")

    parser.add_argument('start_date', type=valid_date,
                        help='Start date for simulation in format '
                             '"YYYY-mm-dd HH:MM:SS"')

    parser.add_argument('output', type=valid_file,
                        help='Output file')

    parser.add_argument('--frequency', metavar='fq', type=valid_frq,
                        help='How often sampling should happen(in seconds). '
                             'Default is 3 seconds. The maximum value is '
                             '3600(1 hour), the minimum value is 1 second.',
                        default=3)

    parser.add_argument('--rabbit_host', metavar='host', type=str,
                        help="RabbitMQ host. Default is 127.0.0.1",
                        default="127.0.0.1")
    parser.add_argument('--rabbit_port', metavar='port', type=int,
                        help="RabbitMQ port. Default is 5672",
                        default=5672)

    parser.add_argument('--rabbit_vhost', metavar='vhost', type=str,
                        help="RabbitMQ vhost. Default is /",
                        default="/")

    parser.add_argument('--rabbit_username', metavar='username', type=str,
                        help="RabbitMQ username. Default is 'guest'",
                        default="guest")

    parser.add_argument('--rabbit_password', metavar='password', type=str,
                        help="RabbitMQ password. Default is 'guest'",
                        default="guest")

    args = parser.parse_args()

    main(args.start_date, args.output, args.frequency, args.rabbit_host,
         args.rabbit_port, args.rabbit_vhost, args.rabbit_username,
         args.rabbit_password)


if __name__ == '__main__':
    init()
