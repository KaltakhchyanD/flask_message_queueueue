import datetime

import redis



r = redis.Redis(host="redis", port=6379)

p = r.pubsub()
p.subscribe('my-first-channel')

for message in p.listen():
    print(f"Got message! Its content - {message['data']}")# do something with the message
    with open("temp.txt", "a") as file:
        file.write(f"{datetime.datetime.now()}, {message['data']} \n")
