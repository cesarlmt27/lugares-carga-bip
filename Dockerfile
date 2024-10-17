FROM python:3.12.3-slim

WORKDIR /app

COPY requirements.txt /app

COPY main.sh /app

RUN pip install --no-cache-dir -r requirements.txt

# ENTRYPOINT ["../entrypoint.sh"]