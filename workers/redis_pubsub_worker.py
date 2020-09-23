import datetime
import json

import redis


#def subscribe_to_result_once(r):

class RedisUniquePubSub():

    pubsub = None

    def __init__(self, r):
        self.r=r

    def subscribe_to_result_once(self):
        if not RedisUniquePubSub.pubsub:
            print('Called SUBSCRIBE!!!')
            RedisUniquePubSub.pubsub = self.r.pubsub()
            RedisUniquePubSub.pubsub.subscribe('result_channel')
        else:
            pass

        return RedisUniquePubSub.pubsub


def run_worker():

    r = redis.Redis(host="redis", port=6379)
    #r = redis.Redis(host="localhost", port=6379)

    p = r.pubsub()
    p.subscribe('my-first-channel')

    for message in p.listen():
        print(f"Got message! Its content - {message['data']}")# do something with the message
        #with open("temp.txt", "a") as file:
        #    file.write(f"{datetime.datetime.now()}, {message['data']} \n")
        
        message_str = message['data'].decode() if message['data']!=1 else "some_string"

        result_dict = {'finished':True, 'message':message_str}
        result_json = json.dumps(result_dict)
        print('Publishing to result_channel...')
        r.publish('result_channel', result_json)

if __name__ == '__main__':
    run_worker()