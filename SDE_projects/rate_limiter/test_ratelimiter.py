import os
import redis
from fastapi import FastAPI, Depends
from SDE_projects.rate_limiter.rate_limiter.dependency import rate_limiter_dependency

app = FastAPI()

r = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

    
@app.post("/login", dependencies=[Depends(rate_limiter_dependency(3, 20, redis_client=r))])
def login():
    return {'message': 'login successfull'}

@app.get("/test", dependencies=[Depends(rate_limiter_dependency(5, 1, redis_client= r))])
def test_endpoint():
    return {'message': 'test successful'}