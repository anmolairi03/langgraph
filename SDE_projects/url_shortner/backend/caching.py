import redis
import os

r = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=6379, decode_responses=True)