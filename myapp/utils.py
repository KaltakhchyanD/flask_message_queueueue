import functools
import json
import random
import time
import uuid

from flask import current_app
import pika


def catch_connection_error(inner):
    @functools.wraps(inner)
    def outer(self, *args, **kwargs):
        try:
            result = inner(self, *args, **kwargs)
        except pika.exceptions.AMQPError as e:
            print(" [Rabbit Client] There was some AMPQ Exception")
            print(f"{e}")
            self.rabbit_connected = False
        else:
            return result

    return outer
    


def reconnect_on_failure(tries=8, start_interval=5):
    def decorator(inner):
        @functools.wraps(inner)
        def outer(obj, *args, **kwargs):
            delay = start_interval
            for i in range(tries):

                if i > 0:
                    print(f"Calling {i+1} time")

                result = inner(obj, *args, **kwargs)
                if obj.rabbit_connected == False:
                    print("There was some error, reconnect is needed")
                    print(f" [Rabbit Client] Reconnecting for the {i+1} time")
                    power = random.uniform(1.1, 1.3)
                    delay **= power
                    print(f"New delay is {delay} sec")
                    print(f"Channel number is {obj.rabbit_channel.channel_number}")
                    time.sleep(delay)
                    obj.connect_to_rabbit()
                else:
                    if i > 0:
                        print(" [Rabbit Client] Successfuly reconnected")
                    return result

            print(f" [Rabbit Client] Ran {tries} times, no connection was established")

        return outer

    return decorator


class RabbitClient:
    def __init__(self, rabbit_host, rabbit_user, rabbit_password):
        self.response = None
        self.rabbit_host = rabbit_host
        self.rabbit_credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
        self.rabbit_connected = False
        self.rabbit_queue_list = []
        self.correlation_id_set = set()
        self.response_dict = dict()
        self.rabbit_channel = None

    @catch_connection_error
    def connect_to_rabbit(self):
        """Connect to RabbitMQ if its not connected aready"""
        if self.rabbit_connected:
            return

        print(" [Rabbit Client] Connecting to RabbitMQ")
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.rabbit_host, credentials=self.rabbit_credentials
            )
        )
        self.rabbit_connected = True

        self.rabbit_channel = self.connection.channel()

        # Declare queues to send messages
        self.rabbit_queue_list.append("message_q_0")
        self.rabbit_queue_list.append("message_q_1")
        self.rabbit_queue_list.append("message_q_2")

        for q in self.rabbit_queue_list:
            self.rabbit_channel.queue_declare(queue=q, durable=True)

        ## Declare queue that contains messages for worker
        ## to declare to newly created queue
        ## So queues can be created at RabbitClient
        ## and then worker can declare it to and start consuming
        # self.queue_to_create_queues = "create_queue"
        ## 'Tis a list of queues to send real messages on
        ## not the maintenance ones like one below
        ## self.rabbit_queue_list.append(queue_to_create_queues)
        # self.rabbit_channel.queue_declare(
        #    queue=self.queue_to_create_queues, durable=True
        # )

        result = self.rabbit_channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.rabbit_channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.response_callback,
            auto_ack=True,
        )

        # self.rabbit_channel.start_consuming()

        # connection.close()

    def response_callback(self, ch, method, properties, body):
        print(f"ANYTHIIIING {properties.correlation_id}")
        if properties.correlation_id in self.correlation_id_set:
            # self.response = {"body": body, "task_id": properties.correlation_id}
            self.response_dict[properties.correlation_id] = {
                "body": body,
                "task_id": properties.correlation_id,
            }

    @catch_connection_error
    def check_response_once(self):
        # Non blocking check for result once
        self.connection.process_data_events()
        return self.response

    @catch_connection_error
    def check_response_blocking(self, task_id):
        # Blocking check for result until its ready
        # while self.response is None:
        while self.response_dict[task_id] is None:
            print("Still nothing")
            self.connection.process_data_events()
            time.sleep(1)
        print(
            f' [c] RabbitClient: Got {self.response_dict[task_id]["body"].decode()}, id - {self.response_dict[task_id]["task_id"]}'
        )
        # response_to_return = self.response
        # self.response = None
        # return self.response
        return self.response_dict[task_id]

    @reconnect_on_failure()
    @catch_connection_error
    def send_message(self, message, task_id=None, queue_name="message_q_0"):
        corr_id = task_id or str(uuid.uuid4())
        self.correlation_id_set.add(corr_id)
        self.response_dict[task_id] = None

        def publish_message():
            self.rabbit_channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    reply_to=self.callback_queue,
                    correlation_id=corr_id,
                ),
            )

        try:
            publish_message()
        # except pika.exceptions.ChannelWrongStateError as e:
        #    print(f"There was a ChannelWrongStateError exception, reopening it")
        #    self.rabbit_channel = self.connection.channel()
        #    publish_message()
        except pika.exceptions.StreamLostError as e:
            print(f"There was a StreamLostError exception, reconnecting")
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.rabbit_host, credentials=self.rabbit_credentials
                )
            )
            print(f"Alse reopen channel so there is no ChannelWrongStateError")
            self.rabbit_channel = self.connection.channel()
            publish_message()

            # try:
            # except pika.exceptions.ChannelWrongStateError as e:
            #    self.rabbit_channel = self.connection.channel()
            #    publish_message()

        print(" [Rabbit Client] Sent 'Hello World!'")

        # connection.close()
