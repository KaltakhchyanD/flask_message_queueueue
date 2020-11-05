import json
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

        self.rabbit_queue_list = []
        self.correlation_id_set = set()
        self.response_dict = dict()

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
        #self.queue_to_create_queues = "create_queue"
        ## 'Tis a list of queues to send real messages on
        ## not the maintenance ones like one below
        ## self.rabbit_queue_list.append(queue_to_create_queues)
        #self.rabbit_channel.queue_declare(
        #    queue=self.queue_to_create_queues, durable=True
        #)

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

    def check_response_once(self):
        # Non blocking check for result once
        self.connection.process_data_events()
        return self.response

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

    def send_message(self, message, task_id=None, queue_name='message_q_0'):
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
        #except pika.exceptions.ChannelWrongStateError as e:
        #    print(f"There was a ChannelWrongStateError exception, reopening it")
        #    self.rabbit_channel = self.connection.channel()
        #    publish_message()
        except pika.exceptions.StreamLostError as e:
            print(f'There was a StreamLostError exception, reconnecting')
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                host=self.rabbit_host, credentials=self.rabbit_credentials
                )
            )
            print(f"Alse reopen channel so there is no ChannelWrongStateError")
            self.rabbit_channel = self.connection.channel()
            publish_message()

            #try:
            #except pika.exceptions.ChannelWrongStateError as e:
            #    self.rabbit_channel = self.connection.channel()
            #    publish_message()

        print(" [x] Sent 'Hello World!'")

        # connection.close()

    #def send_create_queue_message(self, queue_name):
    #    message_json = {"name": queue_name}
    #    message_string = json.dumps(message_json)
    #
    #    self.rabbit_channel.basic_publish(
    #        exchange="",
    #        routing_key=self.queue_to_create_queues,
    #        body=message_string,
    #        properties=pika.BasicProperties(delivery_mode=2),  # make message persistent
    #    )
