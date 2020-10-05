import os

class Config:
    REDIS_HOST = os.getenv('REDIS_HOST')
    RABBIT_HOST = os.getenv('RABBIT_HOST')
    RABBIT_USER = os.getenv('RABBIT_USER')
    RABBIT_PASSWORD = os.getenv('RABBIT_PASSWORD')


class LocalConfig:
    REDIS_HOST = "localhost"
    RABBIT_HOST = "localhost"
    RABBIT_USER = "guest"
    RABBIT_PASSWORD = "guest"
