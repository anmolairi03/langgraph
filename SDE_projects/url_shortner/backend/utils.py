
from pydantic import BaseModel, Field, HttpUrl
import string
import random
from db import URL

def generate_short_code(db, s):
    pool = string.ascii_letters + string.digits
    rand_id = random.choices(pool, k=6)
    rand_id = ''.join(rand_id)
    if db.query(URL).filter(URL.short_code == rand_id).first():
        return generate_short_code(db, s)
    new_row = URL(short_code=rand_id, long_url= str(s))
    db.add(new_row)
    db.commit()
    return rand_id

    

class ShortenRequest(BaseModel):
    long_url: HttpUrl = Field(..., description='The long url provided by the user')
    
class ShortenResponse(BaseModel):
    long_url: HttpUrl = Field(..., description='The long url provided by the user')
    short_url: HttpUrl = Field(..., description='The short url that consists of domain + short code')
    short_code: str = Field(..., description='Short code after processing the long url')
