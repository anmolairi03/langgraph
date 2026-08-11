from fastapi import Request, HTTPException
# from fastapi.responses import JSONResponse
from .core import get_wait_time
import math

# app = FastAPI()

# def create_rate_limiter(max_capacity, refill_rate): #  <= closure..... calls inner func with parameters, these parameters are learnt by the inner func and use them for every call
#     async def rate_limit_middleware(request: Request, call_next):
#         client_ip = request.client.host
        
#         wait_time = math.ceil(get_wait_time(client_ip, max_capacity, refill_rate))
        
#         if wait_time:
#             return JSONResponse(status_code=429, content={"detail": f"Too many requests, wait for {wait_time} before retrying"}, headers={'Retry-After': str(wait_time)})
        
#         response = await call_next(request)
#         return response
    
#     return rate_limit_middleware

    
def rate_limiter_dependency(max_capacity, refill_rate, redis_client):
    def check_limit(request: Request):
        wait_time = math.ceil(get_wait_time(request.client.host, max_capacity, refill_rate, redis_client= redis_client))
        if wait_time:
            raise HTTPException(status_code=429, detail={'message':  f"Too many requests, wait for {wait_time} before retrying"}, headers={"Retry-After": str(wait_time)})
    return check_limit

# app.middleware('http')(create_rate_limiter(5, 2))

# @app.post("/login", dependencies=[Depends(rate_limiter_dependency(3, 20))])
# def login():
#     return {'message': 'login successfull'}

# @app.get("/test", dependencies=[Depends(rate_limiter_dependency(5, 1))])
# def test_endpoint():
#     return {'message': 'test successful'}
