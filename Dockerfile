FROM python

WORKDIR /src
COPY requirements.txt /src/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ADD plexcollector /src/plexcollector
COPY config.ini /src/config.ini

CMD ["python3", "plex-to-influx"]
