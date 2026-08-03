from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from utils import generate_short_code, ShortenRequest, ShortenResponse
from sqlalchemy.orm import Session
from db import get_db, URL
from caching import r

app = FastAPI()


@app.get('/')
def home():
    return {'message': 'This is homepage'}

@app.post('/shorten')
def shorten_url(request: ShortenRequest, db: Session = Depends(get_db)):
    rand_id = generate_short_code(db, request.long_url)
    shortURL = f"http://localhost:8888/{rand_id}"
    ShortResponse = ShortenResponse(long_url= request.long_url, short_url= shortURL, short_code=rand_id)
    return ShortResponse

@app.get("/{short_code}")
def redirect_short_url(short_code: str, db: Session = Depends(get_db)):
    long_url = ''
    if r.get(short_code):
        long_url = r.get(short_code)
        url_row = db.query(URL).filter(URL.short_code == short_code).first()
        url_row.click_count += 1
        db.commit()
    else:
        url_row = db.query(URL).filter(URL.short_code == short_code).first()
        if url_row:
            long_url = url_row.long_url
            r.set(short_code, long_url, ex = 3600)
            url_row.click_count += 1
            db.commit()
    if long_url:
        return RedirectResponse(status_code= 302, url = long_url)
    else:
        raise HTTPException(status_code= 404, detail= 'Item not found')
