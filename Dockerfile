FROM python:3.7-alpine

WORKDIR /app
COPY . /app

RUN apk --no-cache add \
        gcc=~10.3.1 \
        musl-dev=~1.2.2\
        python3-dev=~3.9.7 \
        libffi-dev=~3.4.2 \
        openssl-dev=~1.1.1 \
    && pip3 install --no-cache-dir -r requirements/dev.txt

ENTRYPOINT ["python3"]
CMD ["app.py"]