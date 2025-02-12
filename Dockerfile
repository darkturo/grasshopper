FROM alpine:edge
ADD . /tracker
WORKDIR /tracker

RUN apk add --no-cache python3 py3-pip poetry python3-dev \
    gcc musl-dev linux-headers

RUN poetry install

CMD ["flask", "--app", "tracker", "run"]