import time

# r = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

def get_wait_time(ip, max_capacity, refill_rate, redis_client):
    
    key = f"bucket:{ip}"
    now = time.time()
    
    bucket = redis_client.hgetall(key)
    
    if not bucket:
        current_tokens = float(max_capacity)
        last_refill = now
    else:
        last_refill = float(bucket.get('last_refill', now))
        saved_tokens = float(bucket.get('tokens', max_capacity))
        
        elapsed_time = now - last_refill
        earned_tokens = elapsed_time / refill_rate
        
        current_tokens = min(max_capacity, saved_tokens + earned_tokens)
    
    if current_tokens >= 1:
        current_tokens -= 1
        redis_client.hset(key, mapping={'tokens': current_tokens, 'last_refill': now})
        return 0
    else:
        redis_client.hset(key, mapping={'tokens': current_tokens, 'last_refill': now})
        return (1 - current_tokens) * refill_rate
    