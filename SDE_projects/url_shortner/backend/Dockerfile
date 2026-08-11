FROM python:3.11-slim

WORKDIR /url_shortner

COPY url_shortner/backend/requirements.txt .
RUN pip install -r requirements.txt

COPY rate_limiter/ /rate_limiter/
RUN pip install -e /rate_limiter

COPY url_shortner/backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]