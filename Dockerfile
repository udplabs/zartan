FROM python:3.7-alpine

WORKDIR /app
COPY . /app

RUN apk --no-cache add \
        gcc \
        musl-dev \
        python3-dev \
        libffi-dev \
        openssl-dev \
    && pip3 install --no-cache-dir -r requirements/dev.txt

ENTRYPOINT ["python3"]
CMD ["app.py"]