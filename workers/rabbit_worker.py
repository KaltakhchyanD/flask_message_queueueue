import time
import datetime
import pika

# Sleep for 20 sec to ensure that rabbit server started
print(' [*] Sleeping for 120 seconds.')
time.sleep(120)
print(' [*] After sleep')
print(' [*] Connecting to server ...')

##def start_consuming():
credentials = pika.PlainCredentials('rabbit', 'mq')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbit', credentials = credentials))
channel = connection.channel()

channel.queue_declare(queue='hello', durable=True)


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    with open('temp.txt', 'a') as file:
        file.write(f"{datetime.datetime.now()} \n")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(
    queue='hello', on_message_callback=callback)#, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()

print("End of worker")
