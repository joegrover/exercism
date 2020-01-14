import pika
import argparse
import sys
import time
import database

# This client is only meant to connect to the "extract_requests"
# exchange, so this stuff is all global, but it wouldn't be too
# much work to make this a bit more generic and import "exchange"
# like objects from some predefined collection.
exchange_name = "extract_requests"

# Collect credentials, ideally this aren't actually stored like this...
_user = "jgrover"
_pass = "MjFaQRk2Cp2Ky69c"
credentials = pika.credentials.PlainCredentials(_user, _pass)
# Define parameters for connection
host = "jgrover.hiring.ipums.org"
port = 5675
params = pika.ConnectionParameters(
    host="jgrover.hiring.ipums.org", port=5675, credentials=credentials
)

# Connect:
# Why do we choose the BlockingConnection?
connection = pika.BlockingConnection(params)
channel = connection.channel()

# Even though we expect the extract_requests exchange to have already been declared
# it is safe to also declare it here, if it exists it binds, if not it creates it.
# Based on the RabbitMQ dashboard, the extract_requests exchange is durable and
# of type "topic" so I will declare that here as well.
channel.exchange_declare(exchange=exchange_name, exchange_type="topic", durable=True)
# Exclusive means only this connection can use it and it will be deleted when the
# connection is lost.
q = channel.queue_declare("extract_request_client", exclusive=True)
q_name = q.method.queue


def parser(args_list):
    # The RabbitMQ tutorial had the bindings being declared as a command line argument.
    # I like that idea so let's argparse it:
    p = argparse.ArgumentParser(
        description="""
        Collect IPUMS data product(s) extract defintions and save them to a database.
        """
    )
    p.add_argument(
        "-p",
        "--product",
        choices=["usa", "nhgis"],
        type=str.lower,
        action="append",
        required=True,
        help="""
        IPUMS data products. Can be passed multiple times.
        A binding will be created for each product passed.
        [USA or NHGIS]
        """,
    )
    return p.parse_args(args_list)


def products_to_bindings(products):
    """Right now routing keys are the same as product names but this could be a
    mapper for any future desire to name things differently, or accommodate more
    topic routing key parameters and using wildcards. We just return the list
    right now though.

    Args:
        products ([str]): List of IPUMS product short names (just usa and nhgis).

    Returns:
        [str]: List of routing keys associated with passed IPUMS products.
    """
    return products


def print_extract_request(ch, method, properties, body):
    t = time.localtime()
    print(f"Request: {body}, sent: {t.tm_hour}:{t.tm_min}:{t.tm_sec}", flush=True)
    # There apears to be some kind of a mandatory wait time between
    # extract request submissions so that they don't all end up printing to my screen
    # right now... Let's do some real acknowledging to see if that helps.
    # database.save(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def send_to_db(ch, method, properties, body):
    print(body)
    extract_request = database.ExtractRequestMessage(body)
    extract_request.save()
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main(args):
    global channel
    bindings = products_to_bindings(args.product)
    for b in bindings:
        channel.queue_bind(exchange=exchange_name, queue=q_name, routing_key=b)
    print("Open for business. Send me some Extract Requests to store!")
    channel.basic_consume(queue=q_name, on_message_callback=send_to_db)
    channel.start_consuming()


if __name__ == "__main__":
    args = parser(sys.argv[1:])
    sys.exit(main(args))
