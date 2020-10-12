import time
import uuid

from flask import current_app
import pika


class RabbitClient:
    def __init__(self, rabbit_host, rabbit_user, rabbit_password):
        self.response = None
        self.rabbit_host = rabbit_host
        self.rabbit_credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.rabbit_host, credentials=self.rabbit_credentials
            )
        )

        self.rabbit_channel = self.connection.channel()
        self.rabbit_channel.queue_declare(queue="hello", durable=True)

        #
        result = self.rabbit_channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        print("B4")
        self.rabbit_channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.response_callback,
            auto_ack=True,
        )
        print("After")

        # self.rabbit_channel.start_consuming()

        # connection.close()

    def response_callback(self, ch, method, properties, body):
        print(f"ANYTHIIIING {self.corr_id}")
        if self.corr_id == properties.correlation_id:
            self.response = body

    def check_response_once(self):
        # Non blocking check for result once
        self.connection.process_data_events()
        return self.response

    def check_response_loop(self):
        # Blocking check for result until its ready
        while self.response is None:
            print("Still nothing")
            self.connection.process_data_events()
            time.sleep(1)
        return self.response


    def send_message(self, message):
        # connection = pika.BlockingConnection(
        #    pika.ConnectionParameters(host=self.rabbit_host, credentials=self.rabbit_credentials)
        # )
        # rabbit_channel = connection.channel()
        self.response = None
        self.corr_id = str(uuid.uuid4())

        self.rabbit_channel.basic_publish(
            exchange="",
            routing_key="hello",
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
        )
        print(" [x] Sent 'Hello World!'")

        # connection.close()
