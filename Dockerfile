FROM python:3.6-alpine

RUN apk add --no-cache linux-headers musl-dev gcc tzdata postgresql-dev libstdc++ git && \
    rm -rf /var/cache/apk/*

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app/

CMD ["python", "/app/run.py"]
