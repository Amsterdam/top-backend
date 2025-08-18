FROM python:3.13-trixie
LABEL maintainer="datapunt@amsterdam.nl"

ENV PYTHONUNBUFFERED=1

# Setup Certificates for ADP/Motiv
COPY certificates/adp_rootca.crt /usr/local/share/ca-certificates/extras/adp_rootca.crt
RUN chmod 644 /usr/local/share/ca-certificates/extras/adp_rootca.crt \
  && update-ca-certificates --fresh

# Setup datapunt directories and user
RUN adduser --system datapunt
ENV DIRECTORYLIST "/static /app /downloads /certificates /deploy /var/log/uwsgi"
RUN mkdir -p ${DIRECTORYLIST} && chown datapunt ${DIRECTORYLIST}

# Setup application
WORKDIR /app
COPY requirements.txt /app/

RUN apt-get update && apt-get install -y \
  gdal-bin \
  libgdal-dev \
  graphviz \
  graphviz-dev \
  postgresql-client \
  tzdata

RUN pip install --upgrade pip
RUN pip install uwsgi
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN chmod +x /app/wait-for.sh
RUN chmod +x /app/celery.sh
RUN chmod +x /app/celery-beat.sh
RUN chmod +x /app/deploy/entrypoint.sh
RUN chmod +x /app/deploy/entrypoint.development.sh

ENTRYPOINT ["/app/deploy/entrypoint.sh"]
CMD ["uwsgi", "--ini", "/app/deploy/config.ini"]
