import datetime
import json
import os
import random
import time

import pika


def run_worker():
    worker = RabbitWorker()


class RabbitWorker:
    def __init__(self, worker_name="that_default_worker"):
        self.task_number_from_worker = 0
        self.worker_name = worker_name
        # Sleep for 20 sec to ensure that rabbit server started
        print(" [*] Sleeping for 40 seconds.")
        time.sleep(40)
        print(" [*] After sleep")
        print(" [*] Connecting to server ...")

        self.user = os.getenv("RABBIT_USER")
        self.password = os.getenv("RABBIT_PASSWORD")
        self.host = os.getenv("RABBIT_HOST")

        self.credentials = pika.PlainCredentials(self.user, self.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, credentials=self.credentials)
        )

        self.channel = self.connection.channel()
        print(f" [?] Channel at RabbitWorker : {self.channel}")
        print(f" [?] IS IT OPEN : {self.channel.is_open}")
        #print(f" [?] ITS DIR : {dir(self.channel)}")
        print(f" [?] ITS NUMBER : {self.channel.channel_number}")
        

        # Declare default queue to get messages from RabbitClient
        self.channel.queue_declare(queue="message_q_0", durable=True)
        self.channel.queue_declare(queue="message_q_1", durable=True)
        self.channel.queue_declare(queue="message_q_2", durable=True)

        ## Declare queue that contains messages for worker
        ## to declare to newly created queue
        ## So queues can be created at RabbitClient
        ## and then worker can declare it to and start consuming
        # queue_to_create_queues = "create_queue"
        ##self.rabbit_queue_list.append(queue_to_create_queues)
        # self.channel.queue_declare(queue=queue_to_create_queues, durable=True)

        def callback(ch, method, properties, body):
            print(f" [x] Received {body} of id {properties.correlation_id}")
            with open("temp.txt", "a") as file:
                file.write(f"{datetime.datetime.now()} \n")

            random_delay = random.randint(10, 20)
            print(f" [x] Delaing for {random_delay} sec")
            time.sleep(random_delay)

            print(f"Num - {self.task_number_from_worker}")
            self.task_number_from_worker += 1
            new_body = (
                body.decode() + f" {self.task_number_from_worker}, from {worker_name}"
            )
            new_body = new_body.encode()
            ch.basic_publish(
                exchange="",
                routing_key=properties.reply_to,
                body=new_body,
                properties=pika.BasicProperties(
                    correlation_id=properties.correlation_id
                ),
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue="message_q_0", on_message_callback=callback)
        self.channel.basic_consume(queue="message_q_1", on_message_callback=callback)
        self.channel.basic_consume(queue="message_q_2", on_message_callback=callback)

        print(" [*] Waiting for messages. To exit press CTRL+C")

        self.channel.start_consuming()

        print("End of worker")


if __name__ == "__main__":
    run_worker()
