FROM alpine:3.7

MAINTAINER Christophe Tafani-Dereeper <christophe@tafani-dereeper.me>

RUN apk add --no-cache --virtual persistent python3 libxslt libxml2 && \
    apk add --no-cache --virtual build-deps py3-pip git libxml2-dev gcc python3-dev musl-dev libxslt-dev && \
    mkdir /data && \
    cd /data && \
    git clone --depth=1 https://github.com/christophetd/CloudFlair.git . && \
    pip3 install --no-cache-dir --requirement requirements.txt && \
    apk del --virtual build-deps

ENTRYPOINT ["/usr/bin/python3", "-u", "/data/cloudflair.py"]
CMD ["--help"]
