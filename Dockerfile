FROM python

WORKDIR /src
COPY requirements.txt /src/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ADD plex-to-influx /src/plex-to-influx
COPY config.ini /src/config.ini

CMD ["python3", "plex-to-influx"]
