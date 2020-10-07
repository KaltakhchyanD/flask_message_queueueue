import datetime
import os
import random
import time

import pika


def run_worker():
    user = os.getenv("RABBIT_USER")
    password = os.getenv("RABBIT_PASSWORD")
    host = os.getenv("RABBIT_HOST")

    # Sleep for 20 sec to ensure that rabbit server started
    print(" [*] Sleeping for 120 seconds.")
    time.sleep(120)
    print(" [*] After sleep")
    print(" [*] Connecting to server ...")

    user = os.getenv("RABBIT_USER")
    password = os.getenv("RABBIT_PASSWORD")
    host = os.getenv("RABBIT_HOST")

    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, credentials=credentials)
    )

    channel = connection.channel()

    channel.queue_declare(queue="hello", durable=True)

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
        with open("temp.txt", "a") as file:
            file.write(f"{datetime.datetime.now()} \n")

        random_delay = random.randint(10, 20)
        print(f" [x] Delaing for {random_delay} sec")
        time.sleep(random_delay)

        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            body=body,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue="hello", on_message_callback=callback
    )  # , auto_ack=True)

    print(" [*] Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()

    print("End of worker")


if __name__ == "__main__":
    run_worker()
