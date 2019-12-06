FROM alpine:3.8

RUN apk update && apk upgrade && apk add --no-cache pdftk
RUN apk add python3 py-pip

COPY src/requirements.txt /src/requirements.txt

RUN pip3 install -r src/requirements.txt

COPY src /src

WORKDIR /src
CMD python3 server.py