FROM alpine:edge AS builder
ADD . /app
WORKDIR /app

RUN apk add --no-cache python3 py3-pip poetry python3-dev \
    gcc musl-dev linux-headers

RUN poetry install

RUN poetry build

RUN pip install /app/dist/grasshopper-*.whl --break-system-packages

EXPOSE 5000

CMD ["flask", "--app", "tracker", "run"]
